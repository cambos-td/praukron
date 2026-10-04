# Assumptions

Choices an agent made provisionally, without an owner decision, so work could
continue. An assumption holds no authority by itself: the ADR, task, criterion,
or document it is applied in does. Record an assumption before relying on it,
cite its id wherever it is applied and in any criterion evidence that rests on
it, and never present an `OPEN` one as decided. Researched is not confirmed.

Some choices may never be assumed. The project's assumption policy (the newest
accepted ADR with `Policy: assumptions`) names them; without one, permission,
security, external disclosure, legal, and source-of-truth choices are reserved.
Destructive or irreversible actions, and anything that contradicts an accepted
ADR or a frozen criterion, are always reserved. A reserved choice becomes a task
with `Authority: owner` that the work depends on.

Format:

    ## A-001: Each client has one payment term, default 30 days
    - Status: OPEN
    - Tasks: T-FIN-01, T-FIN-06
    - Impact: HIGH
    - Recorded: 2026-10-01 · claude/primary
    - Assumption: Each client has one payment term in days, default 30.
    - Basis: No payment term exists in the data. Researched, not confirmed:
      30 days is common B2B practice (source).
    - Applied in: ADR-018, AC-T-FIN-01-02, `clients.payment_terms_days`
    - Permissions: none
    - Responses: none
    - Reconciled by: none

Status is `OPEN` (assumed, not reviewed), `CONFIRMED` (the owner confirmed
it), `REVISED` or `REJECTED` (the owner changed or refused it and the records
named in `Reconciled by` carry that out), or `WITHDRAWN` (the agent retracted
it because authority or a fact resolved it). Impact is `HIGH` when the choice
changes money, permissions, data shape or authority, or external behaviour, or
reverting it would need a data migration; `MEDIUM` when it changes behaviour
and is reversible in code; `LOW` for presentation or wording. `Permissions:`
states the access rule assumed, when the policy allows assuming one; such an
assumption is always `HIGH`. Phase and module come from the tasks.

No assumptions recorded yet.
