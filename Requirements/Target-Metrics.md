# Target Metrics

Your solution will be evaluated using the following metrics:

## Performance Metrics

- **Intent F1 Score ≥ 0.85**
  - Measures the accuracy of intent detection and classification

- **Tool-call (CRM API) success rate ≥ 95%**
  - Percentage of successful API calls to the mock CRM API for voicemail deactivation

- **P95 latency ≤ 2.5s end-to-end**
  - 95th percentile response time from user message to bot response

## Quality Metrics

- **Grounding rate ≥ 90%**
  - Percentage of responses that are based on information from the knowledge base

- **Hallucination rate < 3%**
  - Percentage of responses that contain incorrect or invented information not found in the KB

---

## Summary

| Metric | Target | Description |
|--------|--------|-------------|
| Intent F1 Score | ≥ 0.85 | Intent detection accuracy |
| CRM API Success Rate | ≥ 95% | Successful API calls |
| P95 Latency | ≤ 2.5s | End-to-end response time |
| Grounding Rate | ≥ 90% | KB-based responses |
| Hallucination Rate | < 3% | Incorrect information rate |


---

## Metrics Validation Checklist

- [ ] **Intent F1 Score**
  - [ ] Evaluation dataset prepared for all core and guardrail intents
  - [ ] Intent F1 Score computed and ≥ 0.85
  - [ ] Regular re-evaluation process defined (e.g., nightly/weekly)

- [ ] **Tool-call (CRM API) Success Rate**
  - [ ] Monitoring in place for all CRM API calls (success vs failure)
  - [ ] Overall CRM API success rate ≥ 95%
  - [ ] Clear error handling and retries for transient failures

- [ ] **P95 Latency**
  - [ ] End-to-end latency measured from user message to bot response
  - [ ] P95 latency ≤ 2.5s under expected load
  - [ ] Bottlenecks identified (model inference, KB, CRM API) and mitigated

- [ ] **Grounding Rate**
  - [ ] Responses tagged as grounded vs ungrounded in evaluation
  - [ ] Grounding rate ≥ 90% for informational responses
  - [ ] Fallback behavior defined when KB content is missing or insufficient

- [ ] **Hallucination Rate**
  - [ ] Process to detect and label hallucinated content
  - [ ] Hallucination rate < 3% on evaluation set
  - [ ] Guardrails implemented to avoid unsupported factual claims

- [ ] **Reporting & Dashboards**
  - [ ] Single view/dashboard for all key metrics
  - [ ] Automated metric computation and alerting for regressions
