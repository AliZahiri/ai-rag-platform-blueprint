# Add retention policy CLI fixture gate

<!-- daily-pr-task: retention-policy-cli-fixture-gate -->

Add a committed, non-sensitive example policy and a deterministic CLI contract test so teams can adopt the retention gate in CI without embedding real retention records.

## Portfolio Value

Makes the executable retention-policy release gate directly reproducible in CI without committing organizational or customer data.

## Validation

Run `python3 -m unittest discover -s tests` and confirm the public example emits a passing JSON report.
