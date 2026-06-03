# RuntimeOps Lab Evidence Validator CI Workflow Prototype

## 1. Task Summary

Task #330 adds a GitHub Actions workflow prototype for validating RuntimeOps lab safe evidence examples. The workflow checks the validator script, parses the lab evidence JSON, and runs default, strict, runtime-family filtered, and JSON-output validation.

The workflow is limited to repository files. It does not access production systems, run diagnostics, install diagnostic tools, or collect runtime artifacts.

## 2. Workflow Path

Workflow file:

* `.github/workflows/runtimeops-evidence-validator.yml`

Workflow name:

* `RuntimeOps Evidence Validator`

Job name:

* `runtimeops-evidence-validator`

## 3. Trigger Scope

The workflow runs on pull requests that modify:

* `data/runtimeops/lab-evidence/**`
* `scripts/validate_runtimeops_evidence.py`
* `.github/workflows/runtimeops-evidence-validator.yml`

The workflow also runs on pushes to `main` that modify the same paths.

## 4. Files Checked

The workflow checks:

* `scripts/validate_runtimeops_evidence.py`
* `data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json`

It does not check production logs, production processes, production databases, runtime dump files, trace files, or unrelated AgentOps snapshots.

## 5. Commands Executed

The workflow runs:

```bash
python3 -m py_compile scripts/validate_runtimeops_evidence.py
```

```bash
python3 -m json.tool data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json >/dev/null
```

```bash
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json
```

```bash
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --strict
```

```bash
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --runtime-family Python --strict
```

```bash
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --runtime-family .NET --strict
```

```bash
python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --json-output
```

## 6. Failure Policy

The workflow fails if:

* The validator script does not compile.
* The lab evidence JSON is invalid.
* Default validator execution fails.
* Strict validator execution fails.
* Python runtime-family validation fails.
* .NET runtime-family validation fails.
* JSON-output validation fails.

Strict mode is included so warning-level schema drift can fail early before unsafe or low-quality evidence becomes normal.

## 7. Safety Boundary

Workflow safety boundary:

* Does not access secrets.
* Does not use production credentials.
* Does not run curl against production.
* Does not install diagnostic tools.
* Does not collect dump, trace, or command output.
* Reads only repository files.
* Uses read-only repository permissions.
* Does not deploy.
* Does not remediate.

## 8. What This Workflow Intentionally Does Not Do

This workflow intentionally does not:

* Scan production files.
* Inspect production processes.
* Connect to production databases.
* Read production logs.
* Collect runtime dumps.
* Collect traces.
* Upload diagnostic artifacts.
* Handle AgentOps snapshot files.
* Validate unrelated RuntimeOps fixture files.
* Modify evidence files.

## 9. Validation Performed

Local validation requested for this task:

* `git diff --check`
* `python3 -m py_compile scripts/validate_runtimeops_evidence.py`
* `python3 -m json.tool data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json >/dev/null`
* `python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --strict`
* `python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --runtime-family Python --strict`
* `python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --runtime-family .NET --strict`
* `python3 scripts/validate_runtimeops_evidence.py data/runtimeops/lab-evidence/demo_runtimeops_safe_evidence_examples.json --json-output`

If any prerequisite file is not yet committed in the local branch, the command can run locally only when that file exists in the working tree.

## 10. Limitations

* Workflow prototype only.
* Checks one lab evidence JSON file.
* Does not implement multi-file glob validation.
* Does not validate production evidence.
* Does not add pre-commit hooks.
* Does not upload artifacts.
* Depends on the validator script and lab evidence examples being present in the branch.

## 11. Recommended Next Task

Task #331: RuntimeOps Lab Evidence Validator CI QA
