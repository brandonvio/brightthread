---
title: "Assumptions"
permalink: /appendix/assumptions/
---

# System Assumptions

This document establishes the assumptions about BrightThread's existing technology landscape that inform the CX Agent architecture.

---

## Company Profile

**BrightThread is a B2B apparel company** — their core business is:
- Sourcing/manufacturing custom apparel
- Managing bulk orders and fulfillment
- Customer relationships with businesses

They are **not** a technology company. They are an **operations company** that needs technology to run their business.

### Engineering Capacity

BrightThread likely has:
- 0-2 internal developers (for light customization and integrations)
- No dedicated platform engineering team
- Reliance on SaaS tools and vendor support

---

## Existing Technology Landscape

### What We Know (From Requirements)

1. **A production web portal exists** with:
   - Authenticated business users
   - Order history pages
   - Self-serve ordering flow (upload logos, configure orders, pay)

2. **A relational database exists** with tables for:
   - Companies and users
   - Orders and order line items
   - Inventory (product/size/color)
   - Artwork/assets linked to companies and orders

3. **Order statuses exist**: `CREATED`, `APPROVED`, `IN_PRODUCTION`, `READY_TO_SHIP`, `SHIPPED`

4. **Change policies exist** as natural language documentation (maintained internally in a versioned knowledge base such as Confluence)

5. **CX team currently updates "multiple systems"** manually via email/tickets

---

## Assumed System Architecture

Based on company profile analysis, we assume BrightThread uses a mix of SaaS tools:

| Function | Assumed Solution | Notes |
|:---------|:-----------------|:------|
| **Ecommerce/Ordering** | BrightThread (custom-built) | Direct database access; we integrate via existing Python service APIs |
| **Inventory/Production** | NetSuite | Source of truth for stock levels; inventory + production via API |
| **CRM/Tickets** | Zendesk | Where CX logs interactions; escalation workflow lives here |
| **Payments** | Stripe | Handles charges and refunds for order modifications |

### The "Multiple Systems" Problem

When the CX team handles a change request today, they must:

1. **Update the order** in the ecommerce platform
2. **Adjust inventory reservations** in the ERP/WMS
3. **Notify production** (email, Slack, or separate system)
4. **Log the change** in the CRM/ticketing system
5. **Process financial adjustments** (refunds or additional charges)

This manual coordination across systems is the pain point the agent aims to solve.

---

## Key Assumptions for Agent Design

### Integration Model

| Assumption | Implication |
|:-----------|:------------|
| We integrate via **APIs**, not direct database access | Agent calls existing service APIs |
| Systems have **varying API quality** | Some REST, some webhooks, some polling |
| **Services are source of truth** | Agent doesn't bypass service-layer logic |

### Data Ownership

| Data | Owner | Agent Access |
|:-----|:------|:-------------|
| Orders | Ecommerce platform | Read/write via services |
| Inventory | ERP/WMS | Read via services |
| Customer data | Ecommerce + CRM | Read-only |
| Chat history | **Agent system** | Full ownership |
| Policy documents | **Internal policy repository (e.g., Confluence)** | Not accessed directly at runtime |
| Policy vector index | **Agent system (OpenSearch)** | Read at runtime; updated by ingestion job |

### Operational Boundaries

| Assumption | Rationale |
|:-----------|:----------|
| Agent **cannot bypass** production constraints | If production says "too late," it's too late |
| Agent **can check** but not unilaterally **modify** inventory | Inventory changes require service confirmation |
| Agent **can propose** changes, customer must **confirm** | No silent modifications |
| Agent **escalates** to human CX for edge cases | Graceful degradation |

---

## What the Agent System Owns

The CX Agent is designed as a **standalone service** that:

1. **Owns its own data**:
   - Chat sessions and message history
   - Agent decision traces
   - Audit log of changes

2. **Integrates with external systems** via existing Python services:
   - Order queries and modifications
   - Inventory checks
   - Policy evaluation
   - Escalation to Zendesk

3. **Provides its own API**:
   - Chat endpoint for customer portal
   - Session management

---

## Open Questions (For Discovery)

These would be clarified during actual implementation:

1. Which specific ecommerce platform does BrightThread use?
2. What ERP/inventory system is in place?
3. What are the exact API capabilities of each system?
4. Are there rate limits or sync delays we need to handle?
5. What's the current CRM/ticketing workflow for escalations?
