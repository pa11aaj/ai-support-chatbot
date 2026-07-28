# Project Plan (for proposal / client conversation)

The job brief asks for basic customer inquiries, product information, and
order tracking, delivered in 1-3 months. This demo covers the core
end-to-end pattern; a real engagement would go through phases like these.

## Phase 1 - Discovery & setup (weeks 1-2)

- Confirm channels (website widget only, or also email/SMS handoff).
- Get access to the client's product catalog and order-management APIs.
- Define escalation rules: what the bot should never answer on its own
  (refunds, cancellations, complaints) and who picks those up.
- Agree on tone/brand voice for the system prompt.

## Phase 2 - Core chatbot (weeks 2-5)

- Build the tool-use loop against the real product and order APIs (this
  demo's `data.py` becomes real API calls).
- Add auth so a customer can only look up their own orders.
- Conversation logging for QA and for finding gaps in bot knowledge.

## Phase 3 - Integration & polish (weeks 5-8)

- Embed the widget on the live site (script snippet, matches site styling).
- Human handoff: escalations create real tickets (Zendesk/Intercom/etc.)
  with conversation context attached.
- Rate limiting / abuse handling, error states, mobile layout.

## Phase 4 - Testing & launch (weeks 8-12)

- QA against a set of real support transcripts to check accuracy.
- Soft launch to a subset of traffic, monitor escalation rate and response
  quality.
- Handover docs + light training for the client's support team.

This maps a 1-3 month scope to concrete milestones, and phase 2 is where
most of the technical risk lives - which is exactly what this demo is built
to de-risk ahead of time.
