---
title: "BrightThread Order Support Agent"
permalink: /
---

# Order Support Agent for BrightThread Apparel

An agentic conversational assistant that enables B2B customers to request order modifications through natural language, with AI-powered validation against policies, inventory, and operational constraints.

---

## Executive Summary

BrightThread's customers frequently need to modify orders after placement—adjusting quantities, changing sizes, updating shipping addresses, or swapping artwork. Today, these changes require manual email/ticket handling by a CX team that must interpret requests, check policies, coordinate with operations, and update multiple systems.

**This design proposes an AI-powered Order Support Agent** that:

1. **Understands** customer requests in natural language
2. **Validates** changes against order status, inventory, and policies
3. **Presents** options with clear tradeoffs (cost, delay)
4. **Executes** confirmed changes via existing backend services
5. **Escalates** to human CX agents when appropriate

---

## Documentation

### Primary Deliverables

| Document | Description |
|:---------|:------------|
| [Design Document](design-document/) | Architecture overview, key decisions, and system design |
| [Proof of Concept](poc/) | What was built, technology choices, and how to run it |

### Supporting Documentation

| Document | Description |
|:---------|:------------|
| [Assumptions](appendix/assumptions/) | What we assume about BrightThread's existing systems |
| [Tradeoffs](appendix/tradeoffs/) | Detailed analysis of architectural decisions |
| [Data Model](appendix/data-model/) | Entity relationships and schema |
| [Order Lifecycle](appendix/order-lifecycle/) | Order states and change policies |
| [Interactive API Docs](https://brandonvio.github.io/brightthread/api/) | Swagger UI for API exploration |

---

## Key Design Principles

| Principle | Description |
|:----------|:------------|
| **Agent as Interface** | The agent handles conversation; business rules live in existing services |
| **Fail Safe** | When uncertain, escalate to humans rather than take incorrect action |
| **Transparency** | Customers always know what's happening and why |
| **Explicit Confirmation** | No changes applied without customer approval |

---

## Technology Stack

| Component | Technology |
|:----------|:-----------|
| Agent Framework | LangGraph |
| LLM | Claude via Amazon Bedrock |
| Backend | FastAPI (Python) on ECS Fargate (Production) / Lambda (PoC) |
| Conversation Store | DynamoDB |
| Policy RAG | OpenSearch (vector search) |
| Infrastructure | Python CDK |

---

## Quick Links

- **GitHub Repository**: [github.com/brandonvio/brightthread](https://github.com/brandonvio/brightthread)
- **Live Documentation**: [brandonvio.github.io/brightthread](https://brandonvio.github.io/brightthread)
- **API Documentation**: [brandonvio.github.io/brightthread/api](https://brandonvio.github.io/brightthread/api/)
