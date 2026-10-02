# Anomaly and Failed Attempt Template

Create in `docs/reviews/anomalies/` or the run's evidence record. Keep the original output immutable.

## Freeze

Anomaly ID; task/experiment/run; date; exact expected versus observed behavior; source/environment/config/data hashes; seed; output/partial-output paths; resources; MCLF/comparison status. Include favorable anomalies as well as failures.

## Classify before concluding

Input/convention; source-data gap; resource; numerical convergence; model domain; conservation/control volume; control/optimization; experimental disagreement; reproduction; CI; missing review. Selected F-playbook and D-branch:

## Investigation log

| Attempt ID | Single change and reason | New run/config identity | Expected diagnostic | Observed result | Interpretation / remaining uncertainty |
|---|---|---|---|---|---|
| Preserve every attempt | | | | | |

After two failed cycles for the same cause, document the root-cause hypothesis and the discriminating next check before a third feature attempt. State attempt/compute caps and eligible unrelated work.

## Resolution

Actual cause/evidence or INDETERMINATE; corrected code/model/input; independent regression/reference checks; impact on existing runs/claims; preserved negative evidence; re-entry criterion and whether met; reviewer/date; next task.
