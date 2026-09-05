# Synthetic Data Vault for Context Before Consequence
### Hackathon Track: Inclusive Innovation (`>.hack();_'26`)

## 1. Ethical Declaration & Privacy Guarantees
All records contained within `messages.json`, `calendar.json`, `files.json`, and `contacts.json` are **100% synthetic mock records** generated explicitly for hackathon demonstration, benchmarking, and privacy-shield auditing.
- No real individual's personal identifiable information (PII) or protected health information (PHI) is present.
- All email domains and telephone numbers are non-routable simulation placeholders.
- Every entry explicitly carries the marker: `"label": "SYNTHETIC_DATA_FOR_HACKATHON_DEMO"`.

## 2. Vault Datasets & Coverage Matrix

| Dataset | Total Records | Core Action Anchors | Distractor Noise Volume | Key Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `messages.json` | 50 items | `msg_001` (Doc Request), `msg_002` (Transfer), `msg_003` (Henderson), `msg_004` (Appt) | 46 distractor threads | Tests semantic retrieval & shields 92%+ of messages |
| `calendar.json` | 15 items | `cal_001` (Dr. Smith appt), `cal_003` (Henderson review) | 13 routine events | Verifies appointment context & rescheduling guards |
| `files.json` | 20 items | `file_001` (Medical Report), `file_002` (Henderson Notes), `file_003` (temp_file) | 17 personal/work files | Verifies file sensitivity & destructive operation guard |
| `contacts.json` | 15 items | Dr. Smith, Alice Vance, Mark Davis, Sarah Miller | 11 community/external | Supports anomaly detection & trust-level verification |

## 3. Judge-Proof Privacy Metric
- Total User Vault Size: **100 items**.
- When an action is evaluated, **1 to 3 items** are retrieved and compressed into micro-facts.
- **$\ge 97\%$ of all user data is strictly shielded** and provably never passed to any AI model or external service.
