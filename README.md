# Let-It-Fly – Multilingual CX Copilot (Plain English Overview)

Let-It-Fly is a demo-ready customer support copilot for telco use cases. It chats in English and Bahasa Malaysia, understands slang, and can safely take actions like deactivating voicemail after verifying the customer.

## What it does
- Answers plan and voicemail questions using the provided knowledge base.
- Speaks EN/BM and handles code-mixed SMS-style slang.
- Verifies identity (e.g., PIN on web) before account changes.
- Logs every step for auditability.
- Works across channels: Flutter mobile app and WhatsApp (via webhook/Twilio).

## How it works (simplified flow)
1) Customer sends a message from the app or WhatsApp.  
2) An API Gateway forwards it to an API Lambda that checks the phone number and session.  
3) The Orchestrator Lambda coordinates:
   - NLU & intent detection (what the user wants)
   - Guardrails (safety, abuse, and policy checks)
   - Knowledge Base lookup (Bedrock KB) for grounded answers
   - CRM mock Lambda for actions like voicemail updates
   - DynamoDB for sessions and audit logs  
4) Amazon Bedrock (Nova Pro) generates the final reply, cleaned for each channel.  
5) The response returns to the app/WhatsApp with the session continued for multi-turn flows (e.g., PIN follow-up).

## Why it’s trustworthy
- **Guardrails first:** blocks unsafe or out-of-scope requests.  
- **Grounded answers:** pulls from `Data/kb_articles.json` to reduce hallucinations.  
- **Audit trail:** DynamoDB logs who asked for what, model details, and outcomes.  
- **Channel-aware:** web requires PIN; mobile assumes logged-in; WhatsApp can be pinned/verified.

## Where things live
- `Mobile/` — Flutter app for web/iOS/Android, routes to the chatbot.  
- `backend/lambdas/` — AWS Lambdas for API entry, orchestration, guardrails, NLU, CRM mock, and WhatsApp/Twilio webhooks.  
- `Data/` — Knowledge base JSON and sample customer data.  
- `Requirements/` — Target metrics and capability checklist.  
- `Documents/` — Slides and solution comparisons (incl. Bedrock vs. custom).

## How to try it (lightweight)
- **Mobile/Web app:** set `APIKEY` in `.env` (Flutter reads it) to the API Gateway URL provided by the backend team, then run `flutter run` (or launch the existing build).  
- **WhatsApp:** point the WhatsApp/Twilio webhook to the deployed webhook Lambda URL; messages flow through the same orchestrator.  
- No GitHub commits are needed to test; stashing local changes keeps them off the remote.

## What to demo
- Ask plan questions in EN/BM and show the auto-suggested plan cards.  
- Try “turn off voicemail” in slang; show PIN verification on web vs. instant on mobile.  
- Show the audit log entries (who, what intent, what action).  
- Highlight guardrails: abusive language or repeated bad PINs are blocked/escalated.

## Target outcomes (from hackathon brief)
- Intent F1 ≥ 0.85; tool-call success ≥ 95%; grounding ≥ 90%; hallucination < 3%; P95 latency ≤ 2.5s.

## Need help?
- Team resources live at `Documents/Team-Resources.md`. Reach out to the backend owner for API URLs/secrets and to the mobile owner for Flutter build questions.