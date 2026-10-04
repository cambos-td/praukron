# Owner responses

What the owner said, verbatim. Append-only: an agent never edits, reorders,
normalizes, or clears an entry. When the owner answers anywhere else, the agent
records the answer here verbatim, with `Via: relayed by <agent> from
<channel>`, before acting on it. `praukron dashboard --serve` and
`praukron respond` append here for the owner.

Format:

    ## R-001: A-001 REVISE
    - By: owner name
    - Date: 2026-10-02
    - Via: dashboard

    > Default by 7 days, not 30.

The heading names one target, an assumption (`A-`) or a task (`T-`), and one
action. `CONFIRM`, `REVISE`, and `REJECT` apply to assumptions. `GUIDE` applies
to either and never changes a status, a criterion, or an ADR. A response is
reconciled when the agent has set the assumption's status to match and, for
`REVISE` and `REJECT`, named the records that carry it out in `Reconciled by`.

No responses recorded yet.
