# Final Intent List

## Core Voicemail Intents

### 1. `deactivate_voicemail`
**Description**: Customer wants to disable/turn off their voicemail service

**Required Slots**:
- `phone_number` (required)
- `security_pin` or `otp` (required for verification)
- `language_preference` (optional, auto-detected)

**Example Utterances**:
- EN: "turn off my voicemail", "i want to disable voicemail", "can you deactivate voicemail for me?", "please switch off voicemail"
- BM: "matikan mel suara saya", "saya nak nyahaktifkan mel suara", "bolehkah anda nyahaktifkan mel suara untuk saya?", "sila tutup mel suara"
- Slang: "nk off vm skrg", "pls matikan mel suara saya", "vm x jln, nak tutup"

**Action**: Calls CRM API to deactivate voicemail

**Confidence Threshold**: High (≥ 0.85) - requires PIN verification

---

### 2. `activate_voicemail`
**Description**: Customer wants to enable/activate their voicemail service

**Required Slots**:
- `phone_number` (required)
- `security_pin` or `otp` (required for verification)
- `language_preference` (optional, auto-detected)

**Example Utterances**:
- EN: "activate my voicemail", "turn on voicemail", "enable voicemail service", "i want voicemail"
- BM: "aktifkan mel suara saya", "buka mel suara", "nak hidupkan mel suara"
- Slang: "nk on vm", "aktifkan vm pls"

**Action**: Calls CRM API to activate voicemail

**Confidence Threshold**: High (≥ 0.85) - requires PIN verification

---

### 3. `query_voicemail_info`
**Description**: Customer wants information about voicemail service (what it is, how it works, costs, etc.)

**Required Slots**:
- `phone_number` (optional, for personalized info)
- `query_type` (optional: general, pricing, features, access)
- `language_preference` (optional, auto-detected)

**Example Utterances**:
- EN: "what is voicemail?", "how does voicemail work?", "tell me about voicemail service", "voicemail charges", "how to access voicemail"
- BM: "apa itu mel suara?", "bagaimana mel suara berfungsi?", "beritahu saya tentang perkhidmatan mel suara", "caj mel suara"
- Slang: "vm apa?", "vm brapa harga?"

**Action**: Retrieves information from Knowledge Base (KB)

**Confidence Threshold**: Medium (≥ 0.75)

---

### 4. `check_voicemail_status`
**Description**: Customer wants to check if their voicemail is currently active or inactive

**Required Slots**:
- `phone_number` (required)
- `language_preference` (optional, auto-detected)

**Example Utterances**:
- EN: "is my voicemail active?", "check voicemail status", "is voicemail on or off?"
- BM: "adakah mel suara saya aktif?", "semak status mel suara", "mel suara saya hidup ke?"
- Slang: "vm saya on ke?", "check vm status"

**Action**: Queries CRM API for voicemail status

**Confidence Threshold**: Medium (≥ 0.75)

---

### 5. `query_voicemail_access`
**Description**: Customer wants to know how to access/listen to their voicemail messages

**Required Slots**:
- `phone_number` (optional)
- `language_preference` (optional, auto-detected)

**Example Utterances**:
- EN: "how do i check my voicemail?", "how to listen to voicemail?", "voicemail access number", "dial code for voicemail"
- BM: "bagaimana nak dengar mel suara?", "nombor untuk akses mel suara", "cara dengar mesej mel suara"
- Slang: "cara dgr vm?", "nombor vm?"

**Action**: Retrieves information from Knowledge Base (KB) - typically dial 1313

**Confidence Threshold**: Medium (≥ 0.75)

---

## System Intents (Guardrails)

### 6. `greeting`
**Description**: Customer greeting or initial contact

**Required Slots**: None

**Example Utterances**:
- EN: "hello", "hi", "good morning"
- BM: "selamat pagi", "hai", "assalamualaikum"
- Slang: "hi", "hey"

**Action**: Responds with greeting and offers assistance

**Confidence Threshold**: Low (≥ 0.60)

---

### 7. `out_of_scope`
**Description**: Query is outside the scope of voicemail service (billing, plan changes, roaming, etc.)

**Required Slots**:
- `language_preference` (optional, auto-detected)

**Example Utterances**:
- EN: "what's my bill?", "change my plan", "roaming charges", "hotspot usage"
- BM: "berapa bil saya?", "tukar plan", "caj roaming"
- Slang: "bill brapa?", "nak tukar plan"

**Action**: Politely redirects to human agent or provides escalation path

**Confidence Threshold**: Medium (≥ 0.70)

---

### 8. `escalate_to_agent`
**Description**: Customer explicitly requests human agent or complex issue requires escalation

**Required Slots**:
- `language_preference` (optional, auto-detected)
- `reason` (optional, extracted from context)

**Example Utterances**:
- EN: "i want to speak to an agent", "transfer me to human", "this is too complicated"
- BM: "saya nak cakap dengan agent", "pindahkan kepada manusia", "susah sangat ni"
- Slang: "nk agent", "pindah ke human"

**Action**: Escalates to human agent with context summary

**Confidence Threshold**: High (≥ 0.80)

---

### 9. `abusive_language`
**Description**: Detects inappropriate, abusive, or offensive language

**Required Slots**: None

**Example Utterances**: (various inappropriate phrases)

**Action**: Responds professionally, may escalate if repeated

**Confidence Threshold**: High (≥ 0.85)

---

### 10. `unclear_intent`
**Description**: Intent cannot be determined with sufficient confidence

**Required Slots**:
- `language_preference` (optional, auto-detected)

**Example Utterances**: Ambiguous or unclear messages

**Action**: Asks clarifying questions or offers options

**Confidence Threshold**: Low (< 0.60)

---

## Intent Classification Summary

| Intent | Type | Action Required | Priority | Confidence Threshold |
|--------|------|----------------|----------|---------------------|
| `deactivate_voicemail` | Core | CRM API Call | High | ≥ 0.85 |
| `activate_voicemail` | Core | CRM API Call | High | ≥ 0.85 |
| `query_voicemail_info` | Core | KB Retrieval | Medium | ≥ 0.75 |
| `check_voicemail_status` | Core | CRM API Query | Medium | ≥ 0.75 |
| `query_voicemail_access` | Core | KB Retrieval | Medium | ≥ 0.75 |
| `greeting` | System | Response Only | Low | ≥ 0.60 |
| `out_of_scope` | Guardrail | Escalation | Medium | ≥ 0.70 |
| `escalate_to_agent` | Guardrail | Escalation | High | ≥ 0.80 |
| `abusive_language` | Guardrail | Safety Response | High | ≥ 0.85 |
| `unclear_intent` | System | Clarification | Low | < 0.60 |

---

## Intent Hierarchy

### Primary Intents (Voicemail Operations)
1. `deactivate_voicemail` ⭐ **MVP Priority**
2. `activate_voicemail`
3. `query_voicemail_info` ⭐ **MVP Priority**
4. `check_voicemail_status`
5. `query_voicemail_access`

### Secondary Intents (System & Guardrails)
6. `greeting`
7. `out_of_scope`
8. `escalate_to_agent`
9. `abusive_language`
10. `unclear_intent`

---

## Notes

- **MVP Focus**: For the 2-week timeline, prioritize `deactivate_voicemail` and `query_voicemail_info` as these are explicitly mentioned in requirements
- **Multilingual Support**: All intents must handle EN, BM, and code-mixed slang
- **Confidence Thresholds**: Adjust based on validation results to meet F1 Score ≥ 0.85 target
- **Slot Extraction**: All action intents require proper slot extraction with validation
- **Guardrails**: System intents (6-10) are critical for safety and user experience

---

## Intent Implementation Checklist

- [ ] **Training Data & Examples**
  - [ ] Sufficient labeled examples for each primary intent (`deactivate_voicemail`, `activate_voicemail`, `query_voicemail_info`, `check_voicemail_status`, `query_voicemail_access`)
  - [ ] Examples for all system/guardrail intents (`greeting`, `out_of_scope`, `escalate_to_agent`, `abusive_language`, `unclear_intent`)
  - [ ] Coverage for EN, BM, and EN-BM code-mixed slang across all intents

- [ ] **Slots & Validation**
  - [ ] Required slots implemented per intent (e.g., `phone_number`, `security_pin` / `otp`, `query_type`, `language_preference`)
  - [ ] Validation rules in place (phone format, PIN/OTP checks, retries and lockouts)
  - [ ] Graceful prompting for missing or ambiguous slots

- [ ] **Intent Routing & Actions**
  - [ ] Primary intents wired to correct actions:
    - [ ] `deactivate_voicemail` → CRM API deactivate
    - [ ] `activate_voicemail` → CRM API activate
    - [ ] `check_voicemail_status` → CRM API status query
    - [ ] `query_voicemail_info` & `query_voicemail_access` → KB retrieval
  - [ ] System intents trigger appropriate response/escalation flows
  - [ ] `out_of_scope` and `escalate_to_agent` send clear handoff context

- [ ] **Confidence Thresholds & Fallbacks**
  - [ ] Thresholds configured per intent as in the summary table
  - [ ] Behavior defined when confidence is:
    - [ ] Below threshold → clarification or `unclear_intent`
    - [ ] Ambiguous between multiple candidate intents
  - [ ] Metrics capture intent-level confidence for monitoring

- [ ] **Guardrails & Safety Intents**
  - [ ] `abusive_language` detection implemented and tested
  - [ ] Repeated abuse handling (cool-down, escalation) defined
  - [ ] `out_of_scope` routing avoids making unsupported claims
  - [ ] `escalate_to_agent` includes concise conversation summary + key slots

- [ ] **MVP Readiness**
  - [ ] `deactivate_voicemail` and `query_voicemail_info` fully implemented and demo-ready
  - [ ] End-to-end flows validated for both MVP intents (incl. KB/CRM, audit logs, guardrails)
  - [ ] Test set created to track F1, grounding, and hallucinations per intent
