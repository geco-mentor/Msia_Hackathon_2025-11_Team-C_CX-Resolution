# Must-Have Capabilities

## Intent Detection + Slot Extraction

Your system must:

- Identify customer intent (e.g., `deactivate_voicemail`, `query_voicemail_info`).
- Extract essential slots:
  - `phone_number`
  - `security_pin` / OTP
  - `language_preference`
- Handle typos, English-BM code-mixing, and short-code slang, such as:
  - "nk off vm skrg"
  - "pls matikan mel suara saya"
  - "vm x jln, nak tutup"

## Multilingual Understanding (EN + BM + Slang)

Your model must be able to interpret:

- Pure English
- Pure Bahasa Malaysia
- Code-mixed EN-BM
- Malaysian SMS-style slang
- Repeated letters, omitted vowels, and phonetic spellings

## Knowledge Base Grounding

Your responses should:

- Pull from the provided KB JSON
- Maintain ≥ 90% grounding rate
- Maintain < 3% hallucination rate
- Avoid inventing facts not found in the KB

---

## Guardrails & Safety Requirements

Your solution must include guardrails to:

- Prevent unauthorized actions
- Block repeated failed PIN attempts
- Escalate to a human agent when needed
- Handle abusive language
- Manage out-of-scope queries safely

## Action Execution + Audit Log

You must integrate with the mock CRM API to deactivate voicemail and maintain audit logs with:

- `timestamp`
- `customer_id`
- `detected_intent`
- `extracted_slots`
- `API_result`
- `model_version` + `confidence_score`
- `error_details` (if any)

Audit logs must support **idempotency**, ensuring repeat calls behave safely.

## Target Metrics

Your solution will be evaluated using:

- **Intent F1 Score ≥ 0.85**
- **Tool-call (CRM API) success rate ≥ 95%**
- **P95 latency ≤ 2.5s end-to-end**
- **Grounding rate ≥ 90%**
- **Hallucination rate < 3%**

---

## Implementation Checklist

- [ ] **Intent Detection + Slots**
  - [ ] Model detects all core voicemail and system/guardrail intents (e.g., `deactivate_voicemail`, `query_voicemail_info`)
  - [ ] Correct extraction of `phone_number`
  - [ ] Correct extraction and validation of `security_pin` / OTP
  - [ ] Automatic detection or capture of `language_preference`
  - [ ] Robust to typos, EN-BM code-mixing, and SMS-style slang

- [ ] **Multilingual Understanding**
  - [ ] Tested on pure English utterances
  - [ ] Tested on pure Bahasa Malaysia utterances
  - [ ] Tested on EN-BM code-mixed examples
  - [ ] Tested on Malaysian slang (short codes, repeated letters, phonetic spellings)

- [ ] **Knowledge Base Grounding**
  - [ ] All informational responses pull from the provided KB JSON
  - [ ] Grounding rate ≥ 90% on a representative test set
  - [ ] Hallucination rate < 3% (no invented facts beyond KB)
  - [ ] Guardrails in place to avoid answering when KB is insufficient

- [ ] **Guardrails & Safety**
  - [ ] Unauthorized actions are blocked (incl. PIN/OTP failures and missing verification)
  - [ ] Repeated failed PIN attempts are rate-limited or blocked
  - [ ] Clear escalation path to human agent when needed
  - [ ] Abusive language is detected and handled safely
  - [ ] Out-of-scope queries are safely redirected or escalated

- [ ] **Action Execution + Audit Log**
  - [ ] Mock CRM API integrated for voicemail activation/deactivation
  - [ ] Audit log captures `timestamp`, `customer_id`, `detected_intent`, `extracted_slots`
  - [ ] Audit log captures `API_result`, `model_version`, `confidence_score`, and `error_details` (if any)
  - [ ] Audit log implementation is idempotent for repeat calls

- [ ] **Target Metrics & Monitoring**
  - [ ] Intent F1 Score ≥ 0.85 on an evaluation set
  - [ ] Tool-call (CRM API) success rate ≥ 95%
  - [ ] P95 end-to-end latency ≤ 2.5s
  - [ ] Grounding and hallucination rates are logged and monitored
