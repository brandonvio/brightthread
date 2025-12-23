---
title: "Architecture Diagrams"
permalink: /appendix/architecture-diagrams/
---

# Architecture Diagrams (Appendix)

This appendix contains additional diagrams used to explore the design in more depth. The **Design Document** intentionally includes only the diagrams required to explain the core approach.

---

## 1. Current State vs. Future State

### 1.1 Current State: Manual Change Request Flow

Today, order changes require manual coordination across multiple systems:

```mermaid
sequenceDiagram
    participant C as Customer
    participant Z as Zendesk
    participant CX as CX Agent
    participant P as Portal
    participant S as Services
    participant E as ERP

    C->>Z: Email: "Change 20 mediums to large"
    Z->>CX: Ticket assigned
    CX->>CX: Read policy docs
    CX->>P: Log in, find order
    P->>S: Get order details
    S->>E: Check inventory
    E-->>S: Available
    S-->>P: Order + inventory
    CX->>CX: Determine if allowed
    CX->>P: Apply change manually
    P->>S: Update order
    S->>E: Adjust inventory
    CX->>Z: Reply to customer
    Z->>C: Confirmation email

    Note over C,E: Time: 4+ hours typical
```

### 1.2 Future State: Agent-Assisted Flow

With the Order Support Agent, routine changes are handled in minutes:

```mermaid
sequenceDiagram
    participant C as Customer
    participant A as Agent
    participant S as Services
    participant E as ERP
    participant Z as Zendesk

    C->>A: "Change 20 mediums to large in order #1234"
    A->>S: Get order #1234
    S-->>A: Order details (status: APPROVED)
    A->>S: Check change feasibility
    S->>E: Check inventory
    E-->>S: Available
    S-->>A: Allowed, no delay
    A->>C: "I can change 20 mediums to large. No extra cost. Confirm?"
    C->>A: "Yes"
    A->>S: Apply change
    S->>E: Update inventory
    S-->>A: Success
    A->>C: "Done. Confirmation email sent."

    Note over C,E: Time: < 3 minutes

    rect rgb(100, 80, 80)
    Note over A,Z: If complex/denied:
    A-->>Z: Create escalation ticket
    Z-->>C: "Support team will contact you"
    end
```

---

## 2. AWS Infrastructure (Compute, Storage, Observability)

```mermaid
flowchart TB
    subgraph Portal["Customer Portal"]
        UI[Chat Widget]
    end

    subgraph AWS["AWS Infrastructure"]
        APIGW[API Gateway]

        subgraph Compute["Compute Layer"]
            ECS[Agent API<br/>ECS Fargate]
            LG[LangGraph Agent]
        end

        subgraph AI["AI Services"]
            Bedrock[Amazon Bedrock<br/>Claude]
            OS[(OpenSearch<br/>Policy Vectors)]
        end

        subgraph Storage["Data Stores"]
            DDB[(DynamoDB<br/>Conversations)]
        end

        subgraph Observability["Observability"]
            CW[CloudWatch Logs]
            XR[X-Ray Traces]
        end
    end

    subgraph Existing["Existing BrightThread"]
        Services[Python Services]
        RDS[(RDS PostgreSQL)]
    end

    UI --> APIGW
    APIGW --> ECS
    ECS --> LG
    LG <--> Bedrock
    LG <--> OS
    LG <--> DDB
    LG --> Services
    Services --> RDS

    ECS --> CW
    ECS --> XR
```

### 2.1 Policy Knowledge: Source of Truth + Indexing

Policy documents are authored and versioned in an internal repository (e.g., **Confluence**). The agent runtime uses **OpenSearch vector retrieval** for policy *explanations*; it does not require direct Confluence access.

An offline/scheduled ingestion job:
- Exports the latest policy documents + metadata (including version)
- Chunks and embeds the content
- Upserts chunks + embeddings into OpenSearch

```mermaid
flowchart LR
    CONF[Confluence / Versioned Policy Repo] --> JOB[Ingestion Job<br/>export → chunk → embed]
    JOB --> OS[(OpenSearch<br/>Policy Vector Index)]
    OS --> ECS[Agent Runtime<br/>retrieval for explanations]
```

---

## 3. Agent Internal Architecture (Tools + State Machine)

```mermaid
flowchart TB
    subgraph Agent["LangGraph Agent"]
        SM[State Machine]

        subgraph States["States"]
            S1[GREETING]
            S2[IDENTIFY_ORDER]
            S3[CLARIFY_REQUEST]
            S4[CHECK_FEASIBILITY]
            S5[PRESENT_OPTIONS]
            S6[AWAIT_CONFIRMATION]
            S7[EXECUTE_CHANGE]
            S8[ESCALATE]
            S9[COMPLETE]
        end

        subgraph Tools["Tools"]
            T1[get_order]
            T2[check_inventory]
            T3[evaluate_policy]
            T4[apply_change]
            T5[search_policies]
            T6[create_ticket]
        end
    end

    subgraph External["External"]
        LLM[Claude LLM]
        Services[Python Services]
        OS2[(OpenSearch)]
        Zendesk[Zendesk API]
    end

    SM --> States
    SM --> Tools

    T1 --> Services
    T2 --> Services
    T3 --> Services
    T4 --> Services
    T5 --> OS2
    T6 --> Zendesk

    States <--> LLM
```

---

## 4. Escalation Decision Tree (Reference)

```mermaid
flowchart TD
    START[Evaluate Request] --> Q1{Customer requested human?}
    Q1 -->|Yes| ESC[ESCALATE]
    Q1 -->|No| Q2{Service returned requires_human?}

    Q2 -->|Yes| ESC
    Q2 -->|No| Q3{Order status = SHIPPED?}

    Q3 -->|Yes| ESC
    Q3 -->|No| Q4{Clarification attempts > 3?}

    Q4 -->|Yes| ESC
    Q4 -->|No| Q5{Refund > threshold?}

    Q5 -->|Yes| ESC
    Q5 -->|No| Q6{Frustration detected?}

    Q6 -->|Yes| ESC
    Q6 -->|No| CONTINUE[Continue Processing]

    ESC --> TICKET[Create Zendesk Ticket]
    TICKET --> NOTIFY[Notify Customer]
```

---

## 5. Data Flow (Happy Path Example)

```mermaid
sequenceDiagram
    participant C as Customer
    participant UI as Chat Widget
    participant A as Agent
    participant B as Bedrock
    participant S as Services
    participant D as DynamoDB

    C->>UI: "Change 20 mediums to large in #1234"
    UI->>A: Message + session

    A->>D: Load conversation history
    D-->>A: Previous context

    A->>B: Parse intent
    B-->>A: {action: size_change, order: 1234, from: M, to: L, qty: 20}

    Note over A: State: IDENTIFY_ORDER → CHECK_FEASIBILITY

    A->>S: GET /orders/1234
    S-->>A: Order (status: APPROVED)

    A->>S: POST /orders/1234/check-change
    S-->>A: {allowed: true, options: [...]}

    Note over A: State: CHECK_FEASIBILITY → PRESENT_OPTIONS

    A->>B: Generate response
    B-->>A: Natural language options

    A->>D: Save state
    A->>UI: "I can do this. No delay. Confirm?"
    UI->>C: Display

    C->>UI: "Yes"
    UI->>A: Confirmation

    Note over A: State: AWAIT_CONFIRMATION → EXECUTE_CHANGE

    A->>S: POST /orders/1234/changes
    S-->>A: {success: true}

    Note over A: State: EXECUTE_CHANGE → COMPLETE

    A->>D: Save final state
    A->>UI: "Done. Email sent."
    UI->>C: Display
```

---

## 6. Observability (Reference)

Operationally, BrightThread should use a **CloudWatch Dashboard + alarms** for real-time health, and optionally add **LangSmith tracing** (especially in dev/staging) to debug LangGraph state transitions, prompts, and tool calls end-to-end.

```mermaid
flowchart LR
    subgraph Agent["Agent Runtime"]
        LG[LangGraph]
        LOGS[Structured Logs]
        METRICS[Metrics]
    end

    subgraph AWS["AWS"]
        CW[CloudWatch Logs]
        CWM[CloudWatch Metrics]
        XR[X-Ray]
    end

    subgraph Tracing["Agent Tracing"]
        LS[LangSmith Traces]
    end

    subgraph Monitoring["Dashboards"]
        DASH[Ops Dashboard]
        ALERTS[Alerts]
    end

    subgraph KPIs["Key Metrics"]
        CONTAIN[Containment Rate]
        LATENCY[Response Latency]
        ESC[Escalation Rate]
        CSAT[Customer Satisfaction]
    end

    LG --> LOGS --> CW
    LG --> METRICS --> CWM
    LG --> XR
    LG -. optional .-> LS

    CW --> DASH
    CWM --> DASH
    CWM --> ALERTS

    DASH --> CONTAIN
    DASH --> LATENCY
    DASH --> ESC
    DASH --> CSAT
```


