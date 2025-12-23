<p align="center">
  <img src="https://img.shields.io/badge/🧵_BrightThread-Order_Support_Agent-5E81AC?style=for-the-badge&labelColor=2E3440" alt="BrightThread">
</p>

<p align="center">
  <strong>An agentic conversational assistant for B2B apparel order management</strong>
</p>

<p align="center">
  <a href="https://brandonvio.github.io/brightthread/">
    <img src="https://img.shields.io/badge/📖_Documentation-GitHub_Pages-88C0D0?style=flat-square&logo=github&logoColor=white" alt="Documentation">
  </a>
  <a href="https://brandonvio.github.io/brightthread/api/">
    <img src="https://img.shields.io/badge/🔌_API_Reference-Swagger_UI-85BB65?style=flat-square&logo=swagger&logoColor=white" alt="API Reference">
  </a>
  <img src="https://img.shields.io/badge/status-PoC_Complete-A3BE8C?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-B48EAD?style=flat-square" alt="License">
</p>

---

## Overview

BrightThread is a B2B apparel commerce platform with an AI-powered CX agent that handles order modifications through natural language conversation. Customers can request changes to quantities, sizes, shipping addresses, and more—the agent validates against policies, checks inventory, and executes approved changes.

<p align="center">
  <a href="https://brandonvio.github.io/brightthread/">
    <img src="https://img.shields.io/badge/📖_Read_the_Full_Documentation-5E81AC?style=for-the-badge&labelColor=2E3440" alt="Read Documentation">
  </a>
</p>

---

## Tech Stack

<table align="center">
<tr>
<td align="center"><b>Backend</b></td>
<td align="center"><b>AI/ML</b></td>
<td align="center"><b>Infrastructure</b></td>
<td align="center"><b>Data</b></td>
</tr>
<tr>
<td align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"><br>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"><br>
<img src="https://img.shields.io/badge/uv-DE5FE9?style=flat-square&logo=astral&logoColor=white" alt="uv">
</td>
<td align="center">
<img src="https://img.shields.io/badge/Claude-191919?style=flat-square&logo=anthropic&logoColor=white" alt="Claude"><br>
<img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white" alt="LangGraph"><br>
<img src="https://img.shields.io/badge/Bedrock-FF9900?style=flat-square&logo=amazonaws&logoColor=white" alt="Bedrock">
</td>
<td align="center">
<img src="https://img.shields.io/badge/AWS_Lambda-FF9900?style=flat-square&logo=awslambda&logoColor=white" alt="Lambda"><br>
<img src="https://img.shields.io/badge/AWS_CDK-232F3E?style=flat-square&logo=amazonaws&logoColor=white" alt="CDK"><br>
<img src="https://img.shields.io/badge/API_Gateway-FF4F8B?style=flat-square&logo=amazonapigateway&logoColor=white" alt="API Gateway">
</td>
<td align="center">
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"><br>
<img src="https://img.shields.io/badge/DynamoDB-4053D6?style=flat-square&logo=amazondynamodb&logoColor=white" alt="DynamoDB">
</td>
</tr>
</table>

---

## Architecture

```mermaid
flowchart LR
    %% PoC architecture: no OpenSearch, no external systems.

    subgraph Portal["Customer Portal"]
        UI[Chat Widget]
    end

    subgraph PoC["PoC Runtime (Local / Dev)"]
        API[FastAPI Agent API]
        Agent[LangGraph Agent]

        Bedrock[Claude via Bedrock]
        Policy[["Policy Markdown (full doc in context)"]]
        MockSvc[Emulated Platform Services (mock order + policy enforcement)]

        DDB[(DynamoDB: Conversation State)]
        CW[CloudWatch]
        LS[LangSmith]
    end

    UI --> API --> Agent

    Agent <--> Bedrock
    Agent --> Policy
    Agent --> MockSvc
    Agent <--> DDB

    API --> CW
    Agent -. traces .-> LS
```

---

## Key Features

| Feature | Description |
|:--------|:------------|
| 🗣️ **Natural Language Orders** | Customers describe changes in plain English |
| ✅ **Policy Validation** | Agent checks what's allowed based on order state |
| 📦 **Inventory Awareness** | Real-time availability checks before proposing changes |
| 📄 **Policy Context (PoC)** | PoC loads the full policy markdown document into agent context (no vector search) |
| 👤 **Human-in-the-Loop** | Escalation path for complex requests |
| 🔗 **Unified Service Layer** | Agent uses same services as web portal |
| 📈 **Observability** | CloudWatch metrics/logs + optional LangSmith tracing for step-by-step agent debugging |

---

## Documentation

| Section | Description |
|:--------|:------------|
| [📖 Design Document](https://brandonvio.github.io/brightthread/design-document/) | Architecture overview, key decisions, assumptions |
| [🏗️ Architecture Diagrams](https://brandonvio.github.io/brightthread/appendix/architecture-diagrams/) | System diagrams, agent state machine, data flows |
| [🧪 Proof of Concept](https://brandonvio.github.io/brightthread/poc/) | What was built and how to run it |
| [⚖️ Tradeoffs](https://brandonvio.github.io/brightthread/appendix/tradeoffs/) | Architectural decisions and reasoning |
| [🔄 Order Lifecycle](https://brandonvio.github.io/brightthread/appendix/order-lifecycle/) | Order states and change policies |
| [📊 Data Model](https://brandonvio.github.io/brightthread/appendix/data-model/) | Entity relationships and schema |
| [🔌 API Reference](https://brandonvio.github.io/brightthread/api/) | Interactive Swagger UI documentation |

---

## Project Structure

```
brightthread/
├── backend/
│   ├── src/
│   │   ├── models/          # Pydantic data models
│   │   ├── services/        # Business logic layer
│   │   ├── repositories/    # Data access layer
│   │   ├── routers/         # FastAPI routers
│   │   └── agents/          # LangGraph agent + tools
│   ├── tests/
│   ├── alembic/             # Database migrations
│   └── pyproject.toml       # uv/Python dependencies
├── infrastructure/
│   ├── app.py               # CDK app entry point
│   ├── config.py            # Environment configuration
│   └── stacks/              # AWS CDK stacks
├── docs/                    # GitHub Pages documentation
└── internal/                # Internal specs and designs
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [AWS CLI](https://aws.amazon.com/cli/) configured with credentials
- [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
- PostgreSQL (local or RDS)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/brandonvio/brightthread.git
cd brightthread

# Navigate to backend
cd backend

# Install dependencies with uv
uv sync

# Set environment variables
export AWS_REGION=us-west-2
export DATABASE_URL=postgresql://user:pass@localhost:5432/brightthread

# Run database migrations
uv run alembic upgrade head

# Run the development server
uv run uvicorn src.main:app --reload --port 8000

# Run tests
uv run pytest
```

### Infrastructure Setup

```bash
# Navigate to infrastructure
cd infrastructure

# Install CDK dependencies
uv sync

# Bootstrap CDK (first time only)
cdk bootstrap

# Review changes
cdk diff

# Deploy all stacks
cdk deploy --all
```

### Environment Variables

| Variable | Description | Required |
|:---------|:------------|:---------|
| `AWS_REGION` | AWS region (e.g., `us-west-2`) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `DYNAMODB_TABLE_NAME` | DynamoDB table for conversations | Yes |
| `BEDROCK_MODEL_ID` | Claude model ID | Yes |

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_order_service.py -v

# Run integration tests
uv run pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable lint issues
uv run ruff check --fix .
```

---

## API Documentation

The API is documented using OpenAPI/Swagger. When running locally:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

For the deployed API documentation, visit the [API Reference](https://brandonvio.github.io/brightthread/api/).

---

## License

MIT

---

<p align="center">
  <sub>Built with ❤️ and Claude Code</sub>
</p>
