# AgentOps Dashboard Metrics Design

## Overview

AgentOps Dashboard is designed to provide operational visibility into AI agent / Codex work records, token usage, preview review quality, project / task classification coverage, and safety boundary status.

AgentOps is not designed to inspect prompt / response content.

AgentOps uses safe metadata and preview review results.

Dashboard metrics are operational indicators, not billing-grade or authoritative content-level classifications.

## Dashboard Audience

Primary users:

* platform owner
* engineering reviewer
* AI workflow operator
* demo viewer
* future auditor

The first dashboard version should help non-parser developers understand:

* how many AI work records were analyzed
* whether review passed
* whether token values were normalized
* project / task classification coverage
* whether there are forbidden hits, schema pollution, unknown models, or zero token records

## KPI Cards

| Card | Source / Current Value | Display Meaning | Warning / Tooltip |
| ---- | ---------------------: | --------------- | ----------------- |
| Preview Records | 50 | Number of preview records analyzed | Preview sample size, not all historical sessions |
| Review Status | passed | Latest preview review result | Must remain passed before release |
| Total Tokens | 50,078,459 | Normalized operational token estimate | Not billing-grade cost data |
| Project Coverage | 100% | Records with non-unknown project_name | Pipeline-level metadata classification |
| Task Coverage | 100% | Records with non-unknown task_name | Pipeline-level metadata classification |
| Unknown Models | 0 | Records missing model metadata | Should stay low |
| Zero Token Records | 0 | Records with zero token usage | May indicate missing usage metadata |
| Forbidden Hits | 0 | Sensitive or forbidden preview hits | Must remain zero |
| Extra Fields | 0 | Unexpected schema fields | Must remain zero |
| Token Normalization Reduction | approx. 95.3% | Difference between original and normalized token totals | Operational estimate only |

Token normalization reference values:

* original total_tokens: 1,058,156,153
* normalized total_tokens: 50,078,459
* normalized value is about 4.7% of the original
* reduction ratio is about 95.3%

## Chart Sections

### Project Distribution

Current data:

* AgentOps: 50

This is pipeline-level operational classification based on safe metadata. It is not authoritative session-content-level project classification.

### Task Distribution

Current data:

* AgentOps Preview Generation: 50

This is pipeline-level operational task classification. It is not authoritative session-content-level task classification.

### Token Normalization Summary

Current data:

* original total_tokens: 1,058,156,153
* normalized total_tokens: 50,078,459
* normalized value is about 4.7% of the original
* reduction is about 95.3%

Token normalization reduces cumulative snapshot overcounting risk. Token values remain operational estimates, not billing-grade cost data.

### Review Health Summary

Current data:

* status: passed
* forbidden_hits: {}
* extra_fields: {}
* records_with_unknown_model: 0
* records_with_zero_tokens: 0

Review health indicates whether preview output is safe to present. Review passed does not mean content-level correctness of every underlying session.

## Dashboard Copy

Title:

AgentOps Preview Dashboard

Subtitle:

Observe AI agent work records, token usage, preview review quality, and safe metadata classification.

Description:

AgentOps summarizes AI agent / Codex work records using safe metadata and preview review checks. It helps operators understand work volume, token usage estimates, classification coverage, schema safety, and potential quality risks without inspecting prompt or response content.

Safety note:

Project and task values are operational metadata. Token values are operational estimates and are not billing-grade cost data.

Chinese semantic note for future UI translation:

AgentOps 用來觀察 AI Agent / Codex 工作紀錄，整理任務量、Token 使用量、Review 結果、分類覆蓋率與安全邊界。它不是用來讀取 prompt / response 內容，而是用安全 metadata 建立 AI 工作流可觀測性。

## Tooltip / Warning Copy

### Token tooltip

Token values are normalized operational estimates. They are not billing-grade cost data.

### Project tooltip

Project classification currently uses safe metadata and may represent pipeline-level classification, not authoritative session-content-level labeling.

### Task tooltip

Task classification currently uses safe metadata and may represent pipeline-level classification, not authoritative session-content-level labeling.

### Review tooltip

Review status checks preview safety, schema shape, forbidden hits, unknown model count, and token sanity signals.

### Forbidden hits tooltip

Forbidden hits should remain zero before preview data is presented.

### Extra fields tooltip

Extra fields indicate unexpected schema changes and should be reviewed before release.

## Metric Semantics

* records: number of preview records in current generated preview file
* status: review result from review_agentops_preview.py
* forbidden_hits: forbidden preview output signals detected by review script
* extra_fields: preview schema fields not expected by review script
* total_tokens: normalized operational token estimate
* project coverage: non-unknown project_name ratio
* task coverage: non-unknown task_name ratio
* unknown models: records where model metadata is unknown
* zero token records: records with zero token usage
* top_projects: distribution of project_name values
* top_tasks: distribution of task_name values

Project / task coverage is not the same as content-level classification accuracy. Coverage means fields are populated by safe metadata inference. High coverage can still be pipeline-level classification.

## MVP Layout Recommendation

1. Header / explanation block
2. Safety warning strip
3. KPI card grid
4. Project distribution chart
5. Task distribution chart
6. Token normalization comparison chart
7. Review health checklist
8. Metric semantics / notes section

The first UI version should use static preview JSON or already existing data only. It should not add a new API.

## AgentOps Dashboard Preview Release

Task #129 packages Tasks #123-#128 as AgentOps Dashboard Preview.

Suggested tag: `v0.6.22-agentops-dashboard-preview`. Preview review remains passed. This release preserves safety boundaries and semantic warnings. Future work should focus on historical snapshots and schema split design.

## AgentOps Historical Snapshots Schema Design

Task #130 defines the historical snapshot schema for future real Trend Chart data.

Snapshot v1 stores aggregate dashboard-level operational metrics. Snapshot v1 does not store prompt / response, shell output, command text, diff, file contents, raw JSONL, credentials, or full home paths.

Recommended MVP storage is JSON files under `data/agentops/snapshots/`. Token values remain operational estimates, not billing-grade cost data. Project / task values may remain pipeline-level metadata classifications.

Future work should implement snapshot generation in Task #131.

## AgentOps Risk & Anomaly Detection

Task #128 adds a first Risk & Anomaly Detection section to the AgentOps Preview Dashboard.

The first version uses explainable rule-based indicators. Current overall risk level: Low. Blocking risks: 0. Caution items: 3. Caution items are token estimate caution, classification semantics caution, and trend sample data caution.

Risk indicators are based on review status, forbidden hits, extra fields, unknown model count, zero token records, token normalization, project/task coverage, and trend sample status. Risk indicators are not AI answer quality. Risk indicators are not session-content-level correctness. Risk indicators are not billing-grade cost detection.

No parser, schema, backend, review script, or preview JSON changes were made.

## AgentOps Release Quality Score

Task #127 adds a first Release Quality Score section to the AgentOps Preview Dashboard.

The first score is a dashboard-level preview release/readiness indicator. Current score: 98 / 100. Score is based on review status, forbidden hits, extra fields, unknown model count, zero token records, project/task coverage, and token estimate caution.

Score is not billing-grade cost data. Score is not AI answer quality. Score is not session-content-level correctness. No parser, schema, backend, review script, or preview JSON changes were made.

## AgentOps Trend Chart

Task #126 adds a first Trend Chart / Trend Snapshot section to the AgentOps Preview Dashboard.

The first version uses static sample trend data or dashboard-local constants. No parser, schema, backend, review script, or preview JSON changes were made. Trend metrics are dashboard-level operational indicators. Token values remain operational estimates, not billing-grade cost data. Project / task coverage trend does not imply content-level classification accuracy.

Future versions may use generated historical snapshots after schema and storage design are approved.

## Future Metrics

### Task #126: Trend Chart

* daily records
* daily total tokens
* daily normalized tokens
* daily project / task coverage
* daily review pass / fail
* daily unknown model count

### Task #127: Release Quality Score

Potential scoring inputs:

* review passed
* forbidden_hits = 0
* extra_fields = 0
* records_with_unknown_model = 0
* records_with_zero_tokens = 0
* project coverage
* task coverage
* token normalization warning

### Task #128: Risk & Anomaly Detection

Potential risk signals:

* abnormal token spike
* review failed
* forbidden hits
* extra fields
* unknown model spike
* zero token records
* project / task unknown spike
* cumulative token warning
* pipeline-level classification warning

## Non-goals

* no parser changes
* no preview regeneration
* no schema change
* no backend API change
* no content-based inference
* no billing-grade cost reporting
* no session-content-level project/task accuracy claim
* no risk scoring implementation yet

## Task #124 Handoff

Task #124 should implement a simple AgentOps Preview Dashboard UI using the metrics and copy defined in this document. The first UI version should focus on readability, clear warnings, KPI cards, and simple chart sections. It should not introduce schema changes or content-based inference.
