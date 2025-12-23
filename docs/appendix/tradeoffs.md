---
title: "Tradeoffs"
permalink: /appendix/tradeoffs/
---

# Tradeoff Analysis

Detailed analysis of key architectural decisions and the reasoning behind them.

---

## 1. No MCP Server — Direct Service Integration

**Decision:** Agent tools call services directly rather than through an MCP server.

| Chose | Over |
|:------|:-----|
| Simplicity, fewer moving parts | Standardized tool protocol |
| Lower latency (no extra network hop) | Interoperability with other AI clients |
| Easier debugging and deployment | Future extensibility to external consumers |

**Rationale:** MCP solves a multi-client interoperability problem. BrightThread controls the entire stack with a single agent use case. If requirements expand (e.g., exposing tools to partner AI systems), this decision can be revisited.

**Risk:** If BrightThread later wants multiple AI systems consuming the same tools, we'd need to extract an MCP layer or accept duplication.

---

## 2. Single Agent vs. Multi-Agent Orchestration

**Decision:** One LangGraph agent with a comprehensive toolset, rather than an orchestrator delegating to specialized sub-agents.

| Chose | Over |
|:------|:-----|
| Lower latency (fewer LLM calls) | Separation of concerns across agents |
| Simpler debugging and tracing | Independent scaling/iteration of sub-agents |
| Sufficient for narrow domain scope | Handling unbounded domain complexity |

**Rationale:** The order-change domain is well-defined and bounded. A single Claude call with good tools and a clear system prompt can handle the reasoning. Sub-agents add latency and operational complexity without clear benefit at this scope.

**Risk:** If the agent's responsibilities expand significantly (e.g., handling returns, invoicing, sales inquiries), decomposition into sub-agents would be warranted.

---

## 3. Business Logic in Services, Not in Agent

**Decision:** Tools are thin wrappers that call services. All validation, policy enforcement, and state mutation logic lives in the service layer.

| Chose | Over |
|:------|:-----|
| Single source of truth for business rules | Agent-embedded logic (faster to prototype) |
| Consistency across all clients (API, agent, CS tools) | Agent-specific optimizations |
| Testable services independent of LLM | Tighter agent-to-DB coupling |

**Rationale:** The web portal, potential CS internal tools, and the agent should all enforce the same rules. Duplicating logic in the agent creates drift and bugs. Services are testable without invoking an LLM.

---

## 4. Agent Exposed via Same API

**Decision:** The agent is accessed through a `/agent/chat` endpoint on the same API that serves the web portal, rather than as a separate service.

| Chose | Over |
|:------|:-----|
| Unified auth, rate limiting, observability | Independent agent deployment/scaling |
| Simpler infrastructure | Isolation of agent failures |
| Agent is just another client of services | Separate service boundary |

**Rationale:** The agent doesn't need special infrastructure treatment. It's a feature of the product, not a separate product. Keeping it in the same API boundary simplifies operations.

**Risk:** A misbehaving or slow agent could impact API performance. Mitigation: timeouts, async processing, or breaking it out later if needed.

---

## 5. Graph-Based Workflow Agent vs. Autonomous ReAct Agent

**Decision:** Use a graph-based workflow agent (LangGraph StateGraph) rather than an autonomous ReAct-style agent where the LLM decides when to call tools.

| Chose | Over |
|:------|:-----|
| Predictable, deterministic flow every time | Flexible LLM-driven tool selection |
| Guaranteed mandatory steps (policy check before execute) | LLM might skip steps |
| Each node testable in isolation | Must trace LLM reasoning to debug |
| Token-efficient (no reasoning loops) | Adaptable to novel scenarios |
| Complete audit trail of state transitions | Variable reasoning traces |

**Rationale:**

Order modifications are a **workflow**, not an open-ended task. The "tools" (fetch order, evaluate policy, execute change) are *mandatory steps* in a process, not options the LLM chooses between. The graph guarantees:

1. **Policy evaluation happens before execution** — no path bypasses this check
2. **Customer confirmation before changes** — required for financial accountability
3. **Deterministic behavior** — same request produces same flow, enabling validation
4. **Clear audit trail** — essential for B2B dispute resolution and compliance

An autonomous agent that "usually" checks policy is unacceptable when incorrect changes could cost thousands of dollars or delay critical orders.

**Risk:** New conversation flows require graph changes rather than prompt updates. Acceptable given the safety requirements of order modification.

---

## 6. LangGraph as Workflow Framework

**Decision:** Use LangGraph rather than a custom state machine implementation.

| Chose | Over |
|:------|:-----|
| Native checkpointing (DynamoDB) | Custom session persistence |
| Built-in human-in-the-loop support | Custom interrupt/resume logic |
| Graph visualization for debugging | Manual flow documentation |
| Ecosystem compatibility (LangChain) | Framework independence |

**Rationale:** LangGraph provides the workflow primitives we need (nodes, conditional edges, state persistence) with production-ready checkpointing. Building equivalent functionality would add significant development effort without clear benefit.

**Risk:** Framework dependency. If LangGraph's abstractions don't fit a future need, migration would require effort. Acceptable given the current fit.

---

## 7. ECS Fargate over Lambda

**Decision:** Deploy the API (including the agent endpoint) as a containerized service on **ECS Fargate**, rather than Lambda functions.

| Chose | Over |
|:------|:-----|
| Align with BrightThread’s existing ECS deployment model | Introducing a second compute paradigm (Lambda) |
| Long-running service model (streaming, higher timeouts) | Lambda timeouts and payload/runtime constraints |
| Consistent VPC networking posture with existing services | Extra integration layers for private dependencies |
| Standardized operational playbooks (deploys, dashboards) | Separate monitoring/ops model for the agent |

**Rationale:**

1. **Same compute as the existing system** — BrightThread’s e-commerce backend already runs on ECS Fargate, so the agent can reuse the same deployment patterns, IAM boundaries, and networking assumptions.

2. **Predictable runtime characteristics** — The agent can support future requirements like streaming responses and longer-running workflows without Lambda-specific limits.

3. **Simpler service-to-service connectivity** — ECS-in-VPC connectivity to internal services and data stores typically matches what’s already in place for the platform.

4. **Unified observability** — Standardize dashboards, alarms, and traces across the e-commerce services and the agent service.

**Risk:** ECS adds baseline cost and operational surface area (task sizing, deployments, autoscaling). Mitigation: keep the agent stateless, right-size tasks, and use autoscaling with conservative minimums.

---

## 8. RAG vs. Fine-Tuned Model for Policies

**Decision:** Use RAG (OpenSearch vector search) rather than fine-tuning a model on policy documents.

| Chose | Over |
|:------|:-----|
| Policies update immediately when docs change | Consistent "baked-in" knowledge |
| No training pipeline to maintain | Potentially more accurate responses |
| Source attribution for explanations | Lower per-request latency |
| Full control over embeddings and retrieval | Managed service simplicity |

**Rationale:** Policies change. RAG allows updates without retraining. In production, policy documents live in a versioned repository (e.g., Confluence) and an ingestion job exports/chunks/embeds them into OpenSearch. OpenSearch provides k-NN vector search with fine-grained control over embeddings, chunking strategy, and retrieval tuning. The agent uses retrieved context to *explain* decisions, not to *make* them—services enforce the actual rules.

**Risk:** Retrieval can miss relevant context. Mitigation: good chunking strategy and retrieval evaluation.

---

## 9. DynamoDB for Conversation History

**Decision:** Store conversation history in DynamoDB rather than PostgreSQL.

| Chose | Over |
|:------|:-----|
| Simple key-value access (session_id lookup) | Rich querying capabilities |
| Built-in TTL for retention management | Manual cleanup jobs |
| Scales without connection pooling | Connection pool tuning |

**Rationale:** Conversation history is append-only, session-scoped, and ephemeral. Access pattern is always "get/put by session_id." Doesn't benefit from relational features and doesn't belong in the transactional order database.

**Risk:** Can't easily join conversation data with order data for analytics. Mitigation: export to data warehouse for analytics use cases.

---

## 10. Binary Escalation vs. Approval Queue

**Decision:** Use binary escalation (agent handles it OR escalates fully) rather than an approval queue.

| Chose | Over |
|:------|:-----|
| Simpler to implement and explain | Granular "agent proposes, human approves" |
| Clear ownership | Middle ground flexibility |
| Faster for routine cases | Oversight on borderline cases |

**Rationale:** Start simple. Add approval queue when we understand which cases need it. Over-engineering the escalation model before we have data on agent accuracy would be premature.

**Risk:** May over-escalate initially. Mitigation: monitor escalation rate and accuracy, adjust thresholds based on data.
