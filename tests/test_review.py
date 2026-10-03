"""The Assumptions tab and blocker guidance on the dashboard (T-REVIEW-TAB-01, T-REVIEW-BLOCKERS-01)."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prokron import analytics, compile as compiler, dashboard  # noqa: E402
from test_assumptions import ASSUMPTIONS, AssumptionCase  # noqa: E402

SETTLED = """
## A-3: Today is Ho Chi Minh City time
- Status: CONFIRMED
- Tasks: T-ONE
- Impact: MEDIUM
- Recorded: 2026-09-30 · claude/primary
- Assumption: Today is the date in Asia/Ho_Chi_Minh.
- Basis: The team works in Vietnam.
- Applied in: AC-T-ONE-01
- Responses: R-3
- Reconciled by: none

## A-4: Labels say Delivered Value
- Status: OPEN
- Tasks: T-THREE
- Impact: LOW
- Recorded: 2026-10-03 · claude/primary
- Assumption: Labels read Delivered Value.
- Basis: Matches the workbook.
- Applied in: T-THREE
- Responses: none
- Reconciled by: none
"""

CONFIRM = """
## R-3: A-3 CONFIRM
- By: Thien (owner)
- Date: 2026-10-01
- Via: dashboard

> Confirm HCMC time.
"""


class ReviewCase(AssumptionCase):
    def setUp(self) -> None:
        super().setUp()
        responses = (self.authority / "RESPONSES.md").read_text() + CONFIRM
        acceptance = self.authority / "ACCEPTANCE.md"
        acceptance.write_text(acceptance.read_text().replace("Measured on site.", "Measured on site under A-1."))
        self.write(assumptions=ASSUMPTIONS + SETTLED, responses=responses)
        self.render()

    def render(self, interactive: bool = False) -> None:
        self.load()
        self.report = analytics.report(self.project)
        self.compiled = compiler.as_json(self.project)
        self.html = dashboard.render(self.project, self.report, self.compiled, interactive=interactive)
        body = self.html.split('id="panel-assumptions"', 1)[1]
        self.panel = re.split(r'<section class="panel"|<footer>', body, maxsplit=1)[0]

    def section(self, heading: str) -> str:
        return self.panel.split(f"<h3>{heading}</h3>", 1)[1].split("<h3>", 1)[0]


class TestAssumptionsTab(ReviewCase):
    def test_the_queue_is_grouped_and_ordered(self) -> None:
        """AC-T-REVIEW-TAB-01-01."""
        self.assertIn('role="tab" id="tab-assumptions"', self.html)
        review = self.section("Needs your review")
        # A-1 awaits the agent (R-1 REVISE), so it is not in the owner's queue.
        self.assertNotIn('data-id="A-1"', review)
        self.assertLess(review.index('data-id="A-2"'), review.index('data-id="A-4"'))
        self.assertIn('data-id="A-1"', self.section("Waiting for the agent"))
        self.assertIn('data-id="A-3"', self.section("Settled"))
        recent = self.section("Recently changed")
        self.assertLess(recent.index("A-4"), recent.index("A-1"))
        for element in ('id="assume-search"', 'id="assume-phase"', 'id="assume-impact"', 'id="assume-status"'):
            self.assertIn(element, self.panel)
        phases = re.search(r'<select id="assume-phase".*?</select>', self.panel, re.S).group(0)
        self.assertEqual(re.findall(r'<option value="(\w[^"]*)"', phases), ["P1"])

    def test_a_card_explains_itself(self) -> None:
        """AC-T-REVIEW-TAB-01-02."""
        card = self.panel.split('id="assumption-A-1"', 1)[1].split("</details>", 1)[0]
        for fragment in ("Each client has one payment term in days, default 30.",
                         "No term exists in the data. Researched, not confirmed.",
                         ">HIGH<", "Phase P1", "M-FOUNDATION", "ADR-001, AC-T-ONE-01",
                         "(DONE)", "AC-T-ONE-01 (PASS)", "If revised:",
                         "Mặc định 7 ngày, không phải 30.", "— Thien (owner), 2026-10-02"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, card)
        self.assertIn('data-task="T-ONE"', card)

    def test_the_static_page_is_read_only(self) -> None:
        """AC-T-REVIEW-TAB-01-03."""
        self.assertIn("run <code>prokron dashboard --serve</code>", self.panel)
        self.assertIn("This page is read-only.", self.panel)
        self.assertNotIn("<textarea", self.panel)
        self.assertNotIn("<form", self.html)
        self.assertIn("Confirm HCMC time.<span class=\"who\"> — Thien (owner), 2026-10-01", self.panel)

    def test_permission_assumptions_come_first_and_can_be_filtered(self) -> None:
        """AC-T-REVIEW-TAB-01-05."""
        review = self.section("Needs your review")
        self.assertTrue(review.lstrip().startswith('<details class="group" open><summary>Permission assumptions'))
        card = self.panel.split('id="assumption-A-2"', 1)[1].split("</details>", 1)[0]
        self.assertIn('<span class="pill permission">Permission</span>', card)
        self.assertIn("The agent assumed an access rule:</strong> sales read own clients", card)
        self.assertIn('<option value="permission">Permissions</option>', self.panel)
        self.assertIn('data-kind="permission"', card)


if __name__ == "__main__":
    unittest.main(verbosity=2)
