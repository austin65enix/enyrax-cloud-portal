# 271ops Demo Data Fixtures

These files are safe demo fixtures for the 271ops readiness and security governance dashboard.

* They are not production compliance records.
* They do not represent ISO27001 certification status.
* They use safe references and short summaries only.
* They must not contain secrets, raw logs, raw prompt / response, raw command output, credentials, private keys, DATABASE_URL, rclone config, full home paths, or sensitive personal data.
* They are intended for future read-only fixture API prototype.

這些檔案是 271ops readiness 與 security governance dashboard 的安全 demo fixtures，不是正式合規紀錄，也不代表 ISO27001 認證狀態。資料只使用 safe references 與短摘要，不保存 secrets、raw logs、raw prompt / response、credentials 或敏感個資。

## Collection Queue and Audit Calendar Fixtures

* `demo_collection_queue.json`
* `demo_audit_calendar_tasks.json`
* `demo_evidence_requirements.json`

These fixtures model monthly evidence collection, audit calendar tasks, and evidence requirements. They are demo data only. They do not represent real ISO27001 audit records. They do not contain real personal data, secrets, raw logs, credentials, screenshots, raw prompts, raw responses, or raw command output. They are intended for a future read-only API prototype.

這些 fixtures 用於模擬 271ops 的每月證據收集、稽核行事曆與證據需求。資料僅供 demo，不代表正式稽核紀錄，也不保存敏感原始內容。
