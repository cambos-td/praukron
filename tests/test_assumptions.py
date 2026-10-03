"""Assumptions, owner responses, and owner-held tasks (P3, ADR-054, ADR-057).

Kept apart from test_prokron.py so the phase's behaviour can be read in one
place. The fixtures are shared.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prokron import analytics, compile as compiler, layout, validate  # noqa: E402
from test_prokron import build_fixture  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("permission", "security", "external-disclosure", "legal", "source-of-truth")


def _flat(text: str) -> str:
    return " ".join(text.split())


class TestAssumptionSpecification(unittest.TestCase):
    """T-ASSUME-SPEC-01: the protocol is written down before it is compiled."""

    def test_spec_and_templates_define_the_records(self) -> None:
        spec = _flat((ROOT / "docs/SPEC.md").read_text())
        for field in ("`Status`", "`Tasks`", "`Impact`", "`Recorded`", "`Assumption`", "`Basis`",
                      "`Applied in`", "`Permissions`", "`Responses`", "`Reconciled by`",
                      "`By`", "`Date`", "`Via`", "`Authority: owner`"):
            with self.subTest(field=field):
                self.assertIn(field, spec)
        for status in ("`OPEN`", "`CONFIRMED`", "`REVISED`", "`REJECTED`", "`WITHDRAWN`"):
            self.assertIn(status, spec)
        self.assertIn("holds no authority by itself", spec)
        self.assertIn("researched is not confirmed", spec)
        for name in ("ASSUMPTIONS.md", "RESPONSES.md"):
            self.assertTrue((ROOT / "templates/chronicle" / name).is_file(), name)
        self.assertIn("TECH_DEBT ASSUMPTIONS RESPONSES; do", (ROOT / "install.sh").read_text())

    def test_spec_states_the_boundary_and_the_default_policy(self) -> None:
        spec = _flat((ROOT / "docs/SPEC.md").read_text())
        for group in GROUPS:
            self.assertIn(f"`{group}`", spec)
        for rule in ("destructive or irreversible actions are reserved",
                     "Without one, all five groups are reserved and `Notify: host` applies",
                     "only by superseding its policy ADR",
                     "carries `Permissions:` and is `HIGH`",
                     "Prokron sends nothing itself"):
            with self.subTest(rule=rule):
                self.assertIn(rule, spec)

    def test_spec_separates_responded_from_reconciled(self) -> None:
        spec = _flat((ROOT / "docs/SPEC.md").read_text())
        self.assertIn("*Responded* means", spec)
        self.assertIn("*Reconciled* means", spec)
        for row in ("new → `OPEN`", "`OPEN` → `CONFIRMED`", "→ `REVISED`", "`OPEN` → `REJECTED`",
                    "`OPEN` → `WITHDRAWN`", "plus `GUIDE`"):
            self.assertIn(row, spec)

    def test_init_offers_the_optional_policy_step_on_every_host(self) -> None:
        text = _flat((ROOT / ".prokron/commands/prokron-init.md").read_text())
        for group in GROUPS:
            self.assertIn(f"`{group}`", text)
        for rule in ("offer the owner one optional step", "`- Policy: assumptions`",
                     "`- Reserved:", "`- Notify: host`", "If the owner skips the step, record nothing",
                     "always stop whatever the answer"):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)
        for host in (".claude/commands/prokron-init.md", ".opencode/commands/prokron-init.md"):
            self.assertIn(".prokron/commands/prokron-init.md", (ROOT / host).read_text())
        self.assertIn("`init`", (ROOT / ".agents/skills/prokron/SKILL.md").read_text())

    def test_a_chronicle_without_the_new_files_compiles_as_before(self) -> None:
        """AC-T-ASSUME-SPEC-01-04: nothing is migrated; empty templates change nothing."""
        outputs = []
        for with_templates in (False, True):
            directory = Path(tempfile.mkdtemp(prefix="prokron-assume-"))
            self.addCleanup(shutil.rmtree, directory, True)
            build_fixture(directory)
            authority = directory / layout.AUTHORITY_DIR
            before = {p.name: p.read_text() for p in authority.glob("*.md")}
            if with_templates:
                for name in ("ASSUMPTIONS.md", "RESPONSES.md"):
                    shutil.copy(ROOT / "templates/chronicle" / name, authority / name)
            project = compiler.load(directory)
            self.assertEqual(validate.errors(validate.check(project)), [])
            data = compiler.as_json(project)
            data["sources"] = None
            data["project"]["name"] = None
            outputs.append(json.dumps(data, sort_keys=True))
            for name, text in before.items():
                self.assertEqual((authority / name).read_text(), text)
        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
