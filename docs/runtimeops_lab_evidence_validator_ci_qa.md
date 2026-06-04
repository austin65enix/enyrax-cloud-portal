# RuntimeOps Lab Evidence Validator CI QA

## 1. QA Scope

This document defines QA coverage for the planned RuntimeOps Lab Evidence Validator CI workflow. The goal is to confirm that CI has explicit validation paths for PASS, FAIL, missing evidence field, and invalid evidence format scenarios.

This task is documentation only. It does not add or modify a GitHub Actions workflow, change validator code, create evidence fixtures, run production diagnostics, stage AgentOps snapshots, or include unrelated RuntimeOps drafts.

QA target paths:

* `scripts/validate_runtimeops_evidence.py`
* `data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json`
* Future workflow path: `.github/workflows/runtimeops-evidence-validator.yml`

Out of scope:

* Production logs
* Production process inspection
* Runtime dump or trace collection
* AgentOps snapshots
* RuntimeOps design drafts unrelated to the CI QA handoff
* `docs/runtimeops_lab_environment_setup_plan.md`

## 2. Evidence Validator Input Assumptions

The CI workflow should pass an explicit evidence JSON path to the validator. The validator should not scan the full repository by default.

Accepted evidence container formats:

* Top-level JSON list of evidence records.
* Top-level JSON object containing `records`.
* Top-level JSON object containing `items`.
* Top-level JSON object containing `evidence_examples`.

Required input assumptions:

* Evidence records are JSON objects.
* Required fields are present and non-empty.
* `production_data` is boolean `false`.
* `safety_flags` is an object.
* Required safety flags exist, are boolean values, and are `false`.
* Evidence string values do not contain secret-like, raw artifact-like, production path-like, or SQL mutation-like content.
* Optional references use safe reference prefixes.
* Runtime extension keys are allowlisted, or fail under strict mode.

CI should run the validator with `--strict` so warnings become build failures during the first CI phase.

## 3. PASS Case

PASS case objective:

* Confirm that known safe lab evidence validates successfully in CI.
* Confirm the validator exits with status `0`.
* Confirm the workflow logs show a PASS summary without dumping full evidence records.

Recommended command:

```bash
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --strict
```

Expected result:

* Command exits `0`.
* Result is `PASS`.
* Total record count is reported.
* Failure count is `0`.
* Warning count is `0` when strict mode is used.

## 4. FAIL Case

FAIL case objective:

* Confirm unsafe evidence fails CI.
* Confirm any true raw exposure or production action safety flag causes failure.
* Confirm the validator exits with status `1`.

Suggested QA fixture mutation:

* Set `safety_flags.raw_output_exposed` to `true`, or
* Set `safety_flags.production_command_executed` to `true`, or
* Add a forbidden string value such as a secret-like value or raw command output marker.

Recommended command:

```bash
python3 scripts/validate_runtimeops_evidence.py /tmp/runtimeops-evidence-fail-case.json --strict
```

Expected result:

* Command exits `1`.
* Result is `FAIL`.
* Failure output identifies the record index, evidence ref when available, field, and failure reason.
* CI job fails.

## 5. Missing Evidence Case

Missing evidence case objective:

* Confirm a missing required evidence field fails validation.
* Confirm a missing required safety flag fails validation.
* Confirm the failure message is specific enough for a maintainer to fix the evidence record.

Suggested QA fixture mutation:

* Remove required field `evidence_ref`, or
* Remove required field `runtime_family`, or
* Remove required safety flag `raw_dump_exposed`.

Recommended command:

```bash
python3 scripts/validate_runtimeops_evidence.py /tmp/runtimeops-evidence-missing-field-case.json --strict
```

Expected result:

* Command exits `1`.
* Result is `FAIL`.
* Failure output includes `Missing required field.` or the missing safety flag failure.
* CI job fails before merge.

## 6. Invalid Evidence Format Case

Invalid evidence format case objective:

* Confirm invalid JSON or unsupported top-level JSON format fails CI.
* Confirm the JSON parse step and validator step both provide clear failure behavior.

Invalid JSON command:

```bash
python3 -m json.tool /tmp/runtimeops-evidence-invalid-json-case.json >/dev/null
```

Unsupported top-level format command:

```bash
python3 scripts/validate_runtimeops_evidence.py /tmp/runtimeops-evidence-invalid-format-case.json --strict
```

Expected result:

* Invalid JSON parse command exits non-zero.
* Unsupported top-level format validator command exits `1`.
* Failure message states that JSON must be a list or an object containing `records`, `items`, or `evidence_examples`.
* CI job fails without printing full raw evidence content.

## 7. CI Workflow Expected Result

The planned CI workflow should include these checks:

```bash
python3 -m py_compile scripts/validate_runtimeops_evidence.py
python3 -m json.tool data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json >/dev/null
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --strict
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --runtime-family Python --strict
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --runtime-family .NET --strict
```

Expected CI behavior:

* PASS evidence allows the workflow to complete successfully.
* Invalid JSON fails during the parse check.
* Missing required fields fail during validator execution.
* Unsafe evidence fails during validator execution.
* Unknown runtime extension keys fail when strict mode is enabled.
* CI logs include summary counts and failure reasons only.
* CI does not upload raw dumps, traces, command output, production logs, or unsafe evidence artifacts.

## 8. Manual Verification Commands

Manual verification before enabling the workflow:

```bash
python3 -m py_compile scripts/validate_runtimeops_evidence.py
python3 -m json.tool data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json >/dev/null
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --strict
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --json-output --strict
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --runtime-family Python --strict
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --runtime-family .NET --strict
git diff --check
```

Manual negative verification should use temporary files under `/tmp` so repository fixtures are not changed for QA:

```bash
python3 scripts/validate_runtimeops_evidence.py /tmp/runtimeops-evidence-fail-case.json --strict
python3 scripts/validate_runtimeops_evidence.py /tmp/runtimeops-evidence-missing-field-case.json --strict
python3 -m json.tool /tmp/runtimeops-evidence-invalid-json-case.json >/dev/null
python3 scripts/validate_runtimeops_evidence.py /tmp/runtimeops-evidence-invalid-format-case.json --strict
```

## 9. Handoff Notes

Future CI implementation should:

* Keep validation scoped to RuntimeOps lab evidence paths.
* Run strict validation in the first CI phase.
* Fail pull requests for invalid JSON, missing fields, unsafe flags, forbidden string values, or strict-mode warnings.
* Avoid scanning production files or unrelated repository snapshots.
* Avoid staging AgentOps snapshots.
* Avoid mixing unrelated RuntimeOps drafts into the CI QA task.
* Keep `docs/runtimeops_lab_environment_setup_plan.md` separate if it remains uncommitted.
* Log concise validator summaries instead of full evidence records.
