You’ll need to save this yourself as  
`/Users/kita/Desktop/BreakIntoAI/Let-It-Fly/Documents/bedrock-vs-custom-architecture.md`.

---

## Bedrock vs. Fully Custom Open‑Source – 2‑Week Hackathon Comparison

---

## Option A – Amazon Bedrock–Centric Architecture

**Description**  
Use Amazon Bedrock for managed LLMs (Claude / Llama 3), optional Knowledge Bases, and a serverless backend (API Gateway + Lambda + DynamoDB) to orchestrate NLU, RAG, guardrails, and mock CRM.

**Region choice for Kuala Lumpur (sandbox)**  
Hackathon sandbox accounts have access to `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1`, `eu-west-3`, `eu-central-1`, and `eu-north-1` only.  
For users in Kuala Lumpur, **`eu-central-1` (Frankfurt)** is geographically the closest of these available regions, so we would default to **Bedrock in `eu-central-1`** for lower latency in the sandbox setup (with `ap-southeast-1`/Singapore as the natural production-region option later if allowed).

### Pros

- **Delivery speed in 2 weeks**
  - No need to host or scale models or GPUs yourself.
  - Bedrock SDKs make LLM + KB calls straightforward.
  - API Gateway + Lambda gives a quick, managed backend.

- **Quality & multilingual support**
  - Strong multilingual models out of the box (EN, BM, code‑mix, slang via prompt design).
  - Higher likelihood of hitting:
    - **Intent F1 ≥ 0.85**
    - **Tool‑call success ≥ 95%**
    - **Grounding rate ≥ 90%**
    - **Hallucination < 3%**

- **Reliability & performance**
  - AWS manages model availability and scaling.
  - Easier to achieve **P95 latency ≤ 2.5 s** with tuned managed infra.

- **Security & governance**
  - Data stays within AWS; fits enterprise and telco expectations.
  - IAM, KMS, CloudWatch, and VPC integration are standard.

- **Ops & maintenance**
  - Minimal MLOps burden.
  - Team can focus on flows, guardrails, evaluation, and UX instead of infra.

### Cons

- **Vendor lock‑in**
  - Strong coupling to AWS services (Bedrock, Lambda, DynamoDB).
  - Migration to another cloud/provider later will require some re‑work.

- **Cost model**
  - Pay‑per‑token; need monitoring and budgeting for production.
  - For hackathon/demo this is minor but relevant for long‑term planning.

- **Model flexibility**
  - Limited to models Bedrock exposes and its fine‑tune options.
  - Less low‑level control over inference internals and customization.

- **Access / region constraints**
  - Requires Bedrock availability in the account and region.
  - Regulatory or account setup issues may delay start if not pre‑approved.

### 2‑Week Fit

- **Very strong fit** for the hackathon:
  - Most effort goes into:
    - Designing and measuring guardrails and safety flows.
    - Implementing robust, idempotent CRM interactions and audit logs.
    - Building clean web/mobile frontends for a polished client demo.

---

## Option B – Fully Custom Open‑Source (Self‑Hosted + Optional Training)

**Description**  
Self‑host open‑source multilingual models (e.g., Llama 3, Mistral, Qwen) via Ollama/vLLM or HuggingFace, build your own RAG stack (vector DB + embeddings), and optionally train a dedicated intent classifier using `nlu_training_data.json` and augmented slang data.

### Pros

- **Full control & flexibility**
  - Choose and switch models freely (size, architecture, quantization).
  - Tune decoding, caching, and routing exactly for your use case.
  - Can fine‑tune:
    - Intent classifier for higher F1.
    - LLM or adapters on telco‑style EN/BM slang if needed (later phases).

- **Cost & ownership**
  - Potentially lower per‑request cost at scale (especially with owned hardware).
  - No dependence on a single cloud vendor’s pricing or roadmap.
  - Strong data‑residency and IP‑ownership story if hosted on‑prem.

- **Custom NLU & evaluation**
  - Dedicated intent classifier can be trained and iterated quickly.
  - Direct access to embeddings, similarity scores, and logits for analysis.
  - Easier to publish a “white‑box” technical story (how intent F1 was achieved).

- **Strategic positioning**
  - Attractive for clients that value open‑source, self‑reliance, or hybrid/on‑prem deployments.

### Cons

- **Engineering load within 2 weeks**
  - Need to stand up and stabilize:
    - LLM serving (Ollama/vLLM/HF server),
    - Vector DB (Chroma/Qdrant),
    - API orchestration and scaling.
  - Any fine‑tuning loop (even light) consumes valuable hackathon time.

- **Reliability & latency risk**
  - You are responsible for:
    - Latency tuning,
    - Concurrency handling,
    - Memory and GPU/CPU bottlenecks.
  - Getting to **P95 ≤ 2.5 s** reliably can be challenging if infra is new.

- **DevOps complexity**
  - Requires skills in containers, GPUs, observability, and scaling.
  - Debugging performance or deployment issues can easily cost days.

- **Out‑of‑the‑box quality**
  - Smaller OSS models may be weaker on noisy EN/BM slang and code‑mix.
  - More prompt + data engineering is needed to hit target KPIs:
    - **Intent F1 ≥ 0.85**
    - **Tool‑call success ≥ 95%**
    - **Low hallucination with good grounding**

### 2‑Week Fit

- **Moderate to risky** as a primary path:
  - Very feasible if:
    - You already have a working OSS LLM stack and infra, or
    - You narrow scope (fewer intents, low concurrency, no fine‑tuning).
  - Otherwise, time spent on infra and model tuning reduces time for:
    - Guardrails and safety logic,
    - Proper audit logging and metrics,
    - Polished UI/UX for client demo.

---

## Side‑by‑Side Comparison (Hackathon Lens)

### Speed to Working Demo

- **Bedrock**
  - High: focus on flows, guardrails, KB integration, and UI.
- **Custom Open‑Source**
  - Medium/Low: infra setup and stability can consume a large part of the 2 weeks.

### Risk of Missing KPIs in 2 Weeks

- **Bedrock**
  - Lower risk: strong models + managed infra out of the box.
- **Custom Open‑Source**
  - Higher risk: latency, robustness, and F1 may lag if starting fresh.

### Control & Long‑Term Flexibility

- **Bedrock**
  - Lower control, higher convenience.
  - Great for rapid pilots and early production.
- **Custom Open‑Source**
  - High control, high responsibility.
  - Better for long‑term sovereignty and deep customization.

### Enterprise Telco Story

- **Bedrock**
  - “AWS‑native, secure, scalable, and fast to go live.”
  - Fits clients already standardized on AWS.
- **Custom Open‑Source**
  - “Own the full AI stack, avoid vendor lock‑in, and support hybrid/on‑prem.”
  - Stronger story where sovereignty and cost control trump speed.

---

## Recommendation for the 2‑Week Hackathon

- **Primary recommendation**: Lead with the **Bedrock‑centric option** as the main implementation path to reliably hit:
  - Intent F1,
  - Tool‑call success,
  - Grounding/hallucination targets,
  - Latency constraints.
- **Strategic roadmap**:
  - Position the **fully custom open‑source architecture** as a **Phase 2+ evolution**:
    - Once there is more time for infra, fine‑tuning, and on‑prem/hybrid deployment,
    - While reusing the same business flows, guardrails design, and frontend from the Bedrock prototype.