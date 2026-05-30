# AgentOps Explainability Demo Notes

## Overview

AgentOps is an ENYRAX module for observing AI agent / Codex work records through safe metadata, preview review checks, token usage estimates, and operational classification metrics.

AgentOps is not a chat transcript viewer.

AgentOps is not designed to inspect prompt / response content.

AgentOps is an AI workflow observability and governance layer.

## One-line Positioning

AgentOps is the flight recorder and audit dashboard for AI agent work.

中文語意：AgentOps 就像 AI Agent 工作流程的飛航紀錄器與稽核儀表板。

## Demo Talk Track

Start by explaining that this dashboard shows 50 AI agent work preview records. It summarizes the latest review status, token usage estimate, project / task classification coverage, and safety boundary status so a viewer can understand the operational shape of AI work without opening prompt or response content.

Then explain why token normalization matters. The original total_tokens value was 1,058,156,153. After normalization, total_tokens is 50,078,459, a reduction of about 95.3%. This prevents cumulative session token snapshots from being misread as billing-grade cost data.

Next, explain project and task coverage carefully. Project coverage is 100% and task coverage is 100%, but the current classification is pipeline-level operational metadata. It is not authoritative session-content-level labeling, and it does not prove every underlying session was AgentOps or preview generation work.

Review health is the safety checkpoint. The review passed, forbidden_hits is {}, extra_fields is {}, unknown models is 0, and zero token records is 0. This means the preview output is safe to present and has the expected schema shape; it does not mean every underlying session is semantically perfect.

Close by stating what AgentOps is designed to prove: AI work can be tracked without reading prompt / response content, token usage can be normalized and explained, schema safety can be reviewed, project / task classification can be governed with safe metadata, and unknown is preferred over unsafe inference.

## Dashboard Reading Guide

KPI Cards show the quick facts: how many preview records were reviewed, whether the review passed, token totals after normalization, classification coverage, and safety counters such as forbidden hits and extra fields.

Project Distribution shows which project label is populated in the preview data. The current AgentOps: 50 result is a pipeline-level operational classification based on safe metadata.

Task Distribution shows which task label is populated in the preview data. The current AgentOps Preview Generation: 50 result explains the preview telemetry pipeline, not the exact content of every underlying session.

Token Normalization Summary shows the before / after token totals. It helps viewers understand why normalized operational estimates are safer than raw cumulative-looking totals.

Review Health Summary shows whether the preview output is safe to present: review status, forbidden hits, extra fields, unknown models, and zero token records.

Metric Semantics explains how to read coverage and token values. It is the place to remind viewers that operational coverage is not content-level correctness.

## Safety Boundary Explanation

AgentOps does not read or use these content sources for inference:

* prompt
* response
* shell output
* command text
* diff
* file contents
* raw JSONL line
* credentials
* full home path
* secret values
* arbitrary source code content
* arbitrary log content

AgentOps currently focuses on safe metadata and preview review results.

## Common Misunderstandings

| Misunderstanding | Correct Explanation |
| --- | --- |
| Token total equals billing cost | Token values are operational estimates, not billing-grade cost data |
| AgentOps reads prompt / response | AgentOps avoids prompt / response content and uses safe metadata |
| AgentOps: 50 means all sessions are AgentOps work | It means preview telemetry output is pipeline-level associated with AgentOps |
| Task coverage 100% means perfect task understanding | It means task fields are populated by safe metadata inference |
| Review passed means all session content is correct | Review passed means preview output passed safety/schema checks |

## Interview / Demo Explanation

AgentOps is a governance layer for AI-assisted engineering workflows. Instead of treating AI agent work as invisible chat history, AgentOps turns safe metadata into operational indicators: how many work records were produced, how token usage changed after normalization, whether preview review passed, whether schema safety was preserved, and how project/task classification is derived without content-based inference.

AgentOps 是 AI 輔助工程流程的治理層。它不是把 AI 對話內容拿出來看，而是用安全 metadata 把 AI 工作紀錄整理成可觀察、可審核、可說明的營運指標，例如任務量、Token 使用估算、Review 結果、Schema 安全性，以及 Project / Task 分類覆蓋率。

## AgentOps Dashboard Preview Release

Task #129 packages Tasks #123-#128 as AgentOps Dashboard Preview.

Suggested tag: `v0.6.22-agentops-dashboard-preview`. Preview review remains passed. This release preserves safety boundaries and semantic warnings. Future work should focus on historical snapshots and schema split design.

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

## Future Roadmap

* Task #126: AgentOps Trend Chart
* Task #127: AgentOps Release Quality Score
* Task #128: AgentOps Risk & Anomaly Detection
* future schema split:
  * `pipeline_project`
  * `session_project`
  * `pipeline_task`
  * `session_task`

These features should be built after the current Dashboard semantics are stable.
