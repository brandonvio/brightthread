---
title: "Proof of Concept"
permalink: /poc/
---

# Proof of Concept Implementation

This document describes the proof-of-concept (PoC) implementation that demonstrates key aspects of the Order Support Agent design.

---

## 1. PoC Scope

### What Was Built

| Component | Implementation | Notes |
|:----------|:---------------|:------|
| **LangGraph Agent** | Functional | Conversation flow with state management |
| **AWS Bedrock Integration** | Functional | Claude Haiku via LangChain |
| **DynamoDB Checkpointer** | Functional | Conversation state persistence |
| **FastAPI Backend** | Functional | REST endpoints for agent + services |
| **Service Layer** | Functional | Order, inventory, and policy services backed by real database tables (seeded/demo data) |
| **PostgreSQL** | Functional | Real database used by services (local Postgres or RDS in AWS) |
| **CDK Infrastructure** | Complete | Lambda, API Gateway, DynamoDB, RDS stacks |

### What Was NOT Built (Production Requirements)

| Component | Status | Rationale |
|:----------|:-------|:----------|
| Real ERP integration | Not built | Out of scope for PoC |
| CRM integration | Not built | Out of scope for PoC |
| Shipping API integration | Not built | Out of scope for PoC |
| Policy RAG (OpenSearch) | Not built | PoC loads the full policy document into model context instead of vector retrieval |
| React frontend | Not started | Backend-first approach |
| Authentication | Simplified | Dev/test bearer token containing a user_id |
| Zendesk escalation | Stubbed | API call placeholder only |

---

## 2. Architecture Comparison

### Production Architecture

```mermaid
flowchart LR
    subgraph Client
        UI[React Portal]
    end

    subgraph Auth
        Cognito["Cognito (JWT)"]
    end

    subgraph Edge
        CDN[CloudFront + WAF]
        ALB[Load Balancer]
    end

    subgraph Services
        AgentSvc["CX Order Agent<br/>(ECS Fargate)"]
        PlatformSvc["B2B Platform Services<br/>(ECS Fargate)"]
    end

    subgraph AI
        Bedrock[Claude via Bedrock]
        OS[(OpenSearch<br/>Policy Vectors)]
    end

    subgraph Data
        DDB[(DynamoDB)]
        RDS[(PostgreSQL)]
    end

    subgraph External
        ERP[ERP]
        CRM[CRM]
        Shipping[Shipping]
    end

    UI --> Cognito
    UI --> CDN --> ALB
    ALB --> AgentSvc
    ALB --> PlatformSvc
    AgentSvc --> Bedrock
    AgentSvc --> OS
    AgentSvc --> DDB
    AgentSvc --> PlatformSvc
    PlatformSvc --> RDS
    PlatformSvc --> ERP
    PlatformSvc --> CRM
    PlatformSvc --> Shipping
```

### PoC Architecture

```mermaid
flowchart LR
    subgraph Client
        CLI[curl / Postman]
    end

    subgraph API
        APIGW[API Gateway]
        Lambda["Lambda (FastAPI)"]
    end

    subgraph Agent
        LG["LangGraph Agent"]
        Bedrock[Claude via Bedrock]
    end

    subgraph Data
        DDB[(DynamoDB)]
        DB[(PostgreSQL)]
    end

    subgraph Services
        Svc["Functional Services<br/>(Orders, Inventory, Policies)"]
    end

    CLI --> APIGW --> Lambda
    Lambda --> LG
    LG --> Bedrock
    LG --> DDB
    Lambda --> Svc
    Svc --> DB

    style Svc fill:#EBCB8B,stroke:#D08770,color:#2E3440
```

**Key Differences:**
- PoC uses **Lambda** instead of ECS Fargate
- PoC uses **real database-backed services** (PostgreSQL) for orders/inventory/policies
- PoC does **not** integrate with external systems (no ERP/CRM/shipping)
- CLI/curl testing instead of React frontend

---

## 3. Technology Stack

### 3.1 Backend (Python)

| Package | Version | Purpose |
|:--------|:--------|:--------|
| `fastapi` | 0.115+ | REST API framework |
| `langgraph` | 0.2+ | Agent state machine |
| `langchain-aws` | 0.2+ | Bedrock integration |
| `pydantic` | 2.0+ | Data validation |
| `loguru` | 0.7+ | Structured logging |
| `uvicorn` | 0.30+ | ASGI server |

### 3.2 Infrastructure (AWS CDK)

| Stack | Resources |
|:------|:----------|
| `BackendServiceStack` | Lambda function, API Gateway |
| `DynamoDBStack` | Conversations table with TTL |
| `RDSStack` | PostgreSQL instance |
| `IAMStack` | Execution roles, Bedrock/DynamoDB/RDS permissions |
| `Route53Stack` | DNS configuration |
| `CertificateStack` | SSL certificates |

### 3.3 AI/ML

| Service | Configuration |
|:--------|:--------------|
| **Model** | Claude Haiku 4.5 (`us.anthropic.claude-haiku-4-5-20251001-v1:0`) |
| **Region** | us-west-2 |
| **Framework** | LangGraph + LangChain |

---

## 4. Implementation Details

### 4.1 Agent Implementation

The agent is implemented as a LangGraph `StateGraph` with conversation persistence:

```python
# backend/src/agents/cx_order_support_agent.py

class CXOrderSupportAgent:
    def __init__(self, prompt_service: PromptService,
                 checkpointer: BaseCheckpointSaver):
        self.model = ChatBedrock(
            model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            region_name="us-west-2"
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        workflow.add_node("process", self._process_message)
        workflow.set_entry_point("process")
        workflow.set_finish_point("process")
        return workflow.compile(checkpointer=self.checkpointer)

    def process_message(self, message: str, session_id: str) -> str:
        config = {"configurable": {"thread_id": session_id}}
        result = self.graph.invoke(initial_state, config)
        return result["response"]
```

### 4.2 Service Layer (Functional)

Services are implemented as functional Python services backed by repositories and a real PostgreSQL database (seeded/demo data). They cover core domain flows such as order retrieval, inventory checks, and applying modifications under policy constraints.

```python
# backend/src/services/order_service.py (conceptual)
#
# OrderService composes repositories (OrderRepository, InventoryRepository, ...)
# and enforces lifecycle rules + inventory constraints using real database data.
```

### 4.3 DynamoDB Checkpointer

Conversation state is persisted to DynamoDB for multi-turn conversations:

```python
# Uses langgraph-checkpoint-dynamodb (langgraph_checkpoint_dynamodb).
# The agent checkpointer persists LangGraph checkpoints to DynamoDB.
```

---

## 5. API Endpoints

### 5.1 Agent Endpoint

```
POST /v1/chat/completions
```

**Request:**
```json
{
  "model": "brightthread-cx-agent",
  "messages": [
    { "role": "user", "content": "I need to change 20 mediums to large in order #1234" }
  ],
  "order_id": "order-1234",
  "session_id": "session-optional"
}
```

**Response:**
```json
{
  "id": "chatcmpl-xxxxxxxx",
  "object": "chat.completion",
  "created": 1730000000,
  "model": "brightthread-cx-agent",
  "choices": [
    {
      "index": 0,
      "message": { "role": "assistant", "content": "I can help you with that. Let me check if we have 20 large shirts available..." },
      "finish_reason": "stop"
    }
  ],
  "usage": { "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0 },
  "session_id": "session-returned"
}
```

### 5.2 Service Endpoints (PoC)

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/v1/orders/{id}` | GET | Get order details |
| `/v1/orders/{id}/check-change` | POST | Check if change is allowed |
| `/v1/orders/{id}/apply-change` | POST | Apply confirmed change |
| `/v1/inventory/check-availability` | POST | Check inventory availability |

---

## 6. Running the PoC

### 6.1 Local Development

```bash
# Navigate to backend
cd backend

# Install dependencies
uv sync

# Set environment variables
export AWS_REGION=us-west-2
export BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
export CHECKPOINTS_TABLE_NAME=brightthread-checkpoints
export CONVERSATIONS_TABLE_NAME=brightthread-conversations
export DATABASE_URL=postgresql://user:pass@localhost:5432/brightthread

# Run the API server
uv run uvicorn src.main:app --reload --port 8000
```

### 6.2 Test the Agent

```bash
# Send a message to the agent (OpenAI-compatible)
# Auth is a simple base64-encoded JSON bearer token: {"user_id":"user-123"}
AUTH_TOKEN=$(printf '{"user_id":"user-123"}' | base64)

curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{
    "model": "brightthread-cx-agent",
    "messages": [{ "role": "user", "content": "I want to change my order" }],
    "order_id": "00000000-0000-0000-0000-000000000000"
  }'
```

### 6.3 Deploy to AWS

```bash
# Navigate to infrastructure
cd infrastructure

# Deploy all stacks
cdk deploy --all
```

---

## 7. What the PoC Demonstrates

### 7.1 Core Agent Capabilities

| Capability | Demonstrated |
|:-----------|:-------------|
| Natural language understanding | ✅ Via Claude |
| Multi-turn conversation | ✅ Via DynamoDB checkpointer |
| State machine flow | ✅ Via LangGraph |
| Service integration pattern | ✅ Via real, DB-backed services (orders/inventory/policies) |

### 7.2 Infrastructure Patterns

| Pattern | Demonstrated |
|:--------|:-------------|
| Serverless deployment | ✅ Lambda + API Gateway |
| Infrastructure as Code | ✅ Python CDK |
| Conversation persistence | ✅ DynamoDB with TTL |
| LLM integration | ✅ Bedrock + LangChain |
| Policy context loading | ✅ Policy document loaded into prompt context |

### 7.3 Not Demonstrated (Future Work)

| Capability | Notes |
|:-----------|:------|
| External integrations (ERP/CRM/shipping) | Not included in PoC |
| Policy RAG (vector retrieval) | Production design uses OpenSearch; PoC loads full policy doc into context |
| Escalation to Zendesk | API call is stubbed |
| Frontend UI | Backend-first approach |

---

## 8. Extending the PoC

### 8.1 Adding Tools

To add tool calling (e.g., `get_order`, `check_inventory`):

```python
# Define tools
tools = [
    Tool(name="get_order", func=order_service.get_order, ...),
    Tool(name="check_inventory", func=inventory_service.check, ...),
]

# Bind to model
model_with_tools = model.bind_tools(tools)
```

### 8.2 Adding State Transitions

To implement the full state machine:

```python
workflow = StateGraph(AgentState)
workflow.add_node("greeting", greeting_node)
workflow.add_node("identify_order", identify_order_node)
workflow.add_node("check_feasibility", check_feasibility_node)
workflow.add_node("present_options", present_options_node)
# ... add transitions
workflow.add_conditional_edges("greeting", route_from_greeting)
```

### 8.3 Policy Handling (PoC)

Instead of OpenSearch-based RAG, the PoC loads the **full policy document** into the model context. This keeps the PoC self-contained, at the cost of context size and reduced scalability compared to retrieval in production.

---

## 9. Repository Structure

```
brightthread/
├── backend/
│   ├── src/
│   │   ├── agents/
│   │   │   ├── cx_order_support_agent.py   # LangGraph agent
│   │   │   ├── prompts/                    # System prompts
│   │   │   ├── services/                   # Agent-specific services
│   │   │   └── tools/                      # Tool definitions
│   │   ├── services/                       # Business logic layer
│   │   ├── repositories/                   # Data access layer
│   │   ├── routers/                        # API endpoints
│   │   ├── models/                         # Pydantic models
│   │   ├── db/                             # Database utilities
│   │   └── main.py                         # FastAPI app entry
│   └── tests/
├── infrastructure/
│   ├── app.py                              # CDK app entry
│   ├── config.py                           # Environment config
│   └── stacks/
│       ├── backend_service_stack.py        # Lambda + API Gateway
│       ├── dynamodb_stack.py               # Conversations table
│       ├── rds_stack.py                    # PostgreSQL
│       ├── iam_stack.py                    # Permissions
│       ├── certificate_stack.py            # SSL certs
│       └── route53_stack.py                # DNS
└── docs/                                   # This documentation
```
