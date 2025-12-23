# BrightThread Order Support Agent - Architecture & Project Guide

## Overview

BrightThread is a B2B apparel commerce platform with an agentic conversational order support assistant. The system enables authenticated customers to request order modifications (quantity, size, shipping address, artwork) in natural language, with an AI agent that validates changes against policies, inventory constraints, and operational capabilities, then executes approved modifications.

**Guiding Principle**: Follow `.claude/constitution.md` strictly. Emphasize radical simplicity, fail-fast behavior, comprehensive type safety, and SOLID architecture.

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Vite + React (TypeScript) | Customer portal and chat interface |
| **Backend APIs** | Python Lambda (AWS) | Serverless order/inventory services |
| **Database** | PostgreSQL (RDS) | Orders, inventory, users, policies, chat history |
| **Infrastructure** | Python CDK | Infrastructure as code; defines lambdas, RDS, API Gateway, etc. |
| **CI/CD** | GitHub Actions | Linting, testing, deployment workflows |
| **AI/Agents** | Anthropic Claude API | Order support agent with MCP integration |
| **Secrets** | AWS Secrets Manager | API keys, DB credentials |

---

## Repository Structure

```
brightthread/
├── .claude/
│   ├── constitution.md              # Non-negotiable development principles
│   └── commands/                    # Custom slash commands
├── .github/workflows/
│   ├── deploy.yml                   # Infrastructure deployment
│   ├── test.yml                     # Python tests & linting
│   └── build-frontend.yml           # Frontend build & deploy
├── docs/
│   ├── brightthread.md              # Business requirements
│   ├── architecture.md              # Detailed architecture decisions
│   └── schema.md                    # Database schema & relationships
├── infrastructure/
│   ├── cdk/
│   │   ├── app.py                   # CDK app entry point
│   │   ├── stacks/
│   │   │   ├── rds_stack.py         # RDS Postgres database
│   │   │   ├── lambda_stack.py      # Lambda functions & IAM roles
│   │   │   ├── api_stack.py         # API Gateway configuration
│   │   │   ├── secrets_stack.py     # Secrets Manager setup
│   │   │   └── frontend_stack.py    # S3 + CloudFront for React SPA
│   │   └── requirements.txt         # CDK dependencies
│   └── docker-compose.yml           # Local dev: LocalStack + Postgres
├── backend/
│   ├── src/
│   │   ├── models/                  # Pydantic models for data
│   │   │   ├── order.py             # Order, OrderLineItem
│   │   │   ├── inventory.py         # Inventory, Product
│   │   │   ├── user.py              # User, Company
│   │   │   ├── policy.py            # ChangePolicy, PolicyRule
│   │   │   └── chat.py              # ChatMessage, ChatSession
│   │   ├── services/
│   │   │   ├── order_service.py     # Order CRUD & queries
│   │   │   ├── inventory_service.py # Inventory checks & updates
│   │   │   ├── policy_service.py    # Policy validation logic
│   │   │   ├── user_service.py      # User & company queries
│   │   │   ├── chat_service.py      # Chat history & session mgmt
│   │   │   └── agent_service.py     # AI agent orchestration
│   │   ├── repositories/
│   │   │   ├── order_repo.py        # Order data access layer
│   │   │   ├── inventory_repo.py    # Inventory DAL
│   │   │   ├── user_repo.py         # User/Company DAL
│   │   │   └── chat_repo.py         # Chat DAL
│   │   ├── lambdas/
│   │   │   ├── auth_handler.py      # JWT validation middleware
│   │   │   ├── orders_handler.py    # GET /orders, /orders/{id}
│   │   │   ├── chat_handler.py      # POST /chat (agent entry point)
│   │   │   ├── inventory_handler.py # GET /inventory endpoints
│   │   │   ├── policies_handler.py  # GET /policies
│   │   │   ├── mcp_server.py        # MCP server (tools for agent)
│   │   │   └── shared.py            # Common utils, DB connections
│   │   └── agent/
│   │       ├── agent.py             # Claude agent orchestration
│   │       ├── tools.py             # Tool definitions for agent
│   │       └── prompt.py            # System prompts & instructions
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_order_service.py
│   │   │   ├── test_inventory_service.py
│   │   │   ├── test_policy_service.py
│   │   │   ├── test_agent.py
│   │   │   └── conftest.py          # Pytest fixtures
│   │   ├── integration/
│   │   │   ├── test_order_api.py    # Lambda endpoint tests
│   │   │   └── test_chat_api.py
│   │   └── mocks/
│   │       ├── mock_db.py           # Mock database queries
│   │       └── mock_agent.py        # Mock agent responses
│   ├── requirements.txt             # Python dependencies
│   ├── pyproject.toml               # Ruff config, pytest config
│   └── Makefile                     # Development commands
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.tsx            # Auth/login page
│   │   │   ├── OrderHistory.tsx     # View existing orders
│   │   │   ├── OrderDetail.tsx      # Single order view
│   │   │   ├── ChatInterface.tsx    # Agent chat UI
│   │   │   └── Dashboard.tsx        # Order summary dashboard
│   │   ├── components/
│   │   │   ├── ChatMessage.tsx      # Chat bubble component
│   │   │   ├── OrderCard.tsx        # Order summary card
│   │   │   ├── InventoryDisplay.tsx # Show available inventory
│   │   │   └── ChangeProposal.tsx   # Proposed changes UI
│   │   ├── hooks/
│   │   │   ├── useAuth.ts           # Auth state & login
│   │   │   ├── useOrder.ts          # Order queries
│   │   │   └── useChat.ts           # Chat state & messages
│   │   ├── api/
│   │   │   ├── client.ts            # API client (axios)
│   │   │   ├── orders.ts            # Order API calls
│   │   │   ├── chat.ts              # Chat/agent API calls
│   │   │   └── auth.ts              # Auth endpoints
│   │   ├── types/
│   │   │   ├── order.ts             # TypeScript interfaces
│   │   │   ├── chat.ts
│   │   │   └── api.ts               # API response types
│   │   ├── App.tsx                  # Main app component
│   │   └── main.tsx                 # Vite entry point
│   ├── public/
│   │   ├── index.html               # Static HTML
│   │   └── favicon.ico
│   ├── vite.config.ts               # Vite configuration
│   ├── tsconfig.json
│   ├── package.json                 # Dependencies: React, axios, etc.
│   └── Makefile                     # Build commands
├── docs/
│   ├── API.md                       # Lambda endpoint documentation
│   ├── DATABASE.md                  # Schema & queries
│   ├── AGENT.md                     # Agent design & prompts
│   └── DEPLOYMENT.md                # Step-by-step deployment guide
├── CLAUDE.md                        # This file
├── README.md                        # Project overview for users
└── Makefile                         # Root-level build targets
```

---

## Architecture Overview

### High-Level Flow

1. **Authenticated Customer** logs in to React SPA (Cognito or simple JWT)
2. **Chat Interface** sends natural language request to `/api/chat` Lambda
3. **Chat Lambda** invokes Claude agent with customer context (orders, inventory, policies)
4. **Agent** uses MCP server to call tools:
   - `get_order(order_id)` → OrderService → DB query
   - `check_inventory(product, size, color)` → InventoryService
   - `validate_policy_change(order_status, change_type)` → PolicyService
   - `execute_change(order_id, modifications)` → OrderService + InventoryService
5. **Agent** reasons about feasibility, generates response, and optionally executes changes
6. **Chat Lambda** stores conversation in DB, returns response
7. **Frontend** displays agent response and allows user confirmation for execution

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    BrightThread Architecture                     │
├──────────────────┬────────────────────────────────┬──────────────┤
│   FRONTEND       │        BACKEND APIs            │   DATABASE   │
├──────────────────┼────────────────────────────────┼──────────────┤
│                  │                                │              │
│ React SPA        │   Lambda@Edge (Auth)           │  RDS         │
│ (Vite)           │         ↓                      │  Postgres    │
│   ↓              │   API Gateway                  │    ↓         │
│ Chat Component   │         ↓                      │  Tables:     │
│   │              │   Lambda Functions:            │  - users     │
│   └─→ POST       │   • OrdersHandler              │  - companies │
│      /chat       │   • ChatHandler ←──────────────→ - orders     │
│                  │   • InventoryHandler           │  - line_items│
│                  │   • PoliciesHandler            │  - inventory │
│                  │         ↓                      │  - policies  │
│                  │   Services Layer:              │  - chat_msgs │
│                  │   • OrderService               │              │
│                  │   • InventoryService           │              │
│                  │   • PolicyService              │              │
│                  │         ↓                      │              │
│                  │   MCP Server / Agent:          │              │
│                  │   • Claude Agent Runtime       │              │
│                  │   • Tool Definitions           │              │
│                  │   • System Prompts             │              │
│                  │         ↓                      │              │
│                  │   Anthropic Claude API         │              │
│                  │   (via SDK)                    │              │
│                  │                                │              │
└──────────────────┴────────────────────────────────┴──────────────┘
```

---

## Core Components

### 1. Models (Pydantic + Dataclasses)

All data transferred within the backend uses **Pydantic models** with validation. Examples:

```python
# backend/src/models/order.py
class OrderLineItem(BaseModel):
    id: str
    product_id: str
    size: str
    color: str
    quantity: int

class Order(BaseModel):
    id: str
    company_id: str
    status: str  # CREATED, APPROVED, IN_PRODUCTION, READY_TO_SHIP, SHIPPED
    line_items: list[OrderLineItem]
    shipping_address: str
    requested_delivery_date: date
    created_at: datetime
```

**Principle**: No loose dictionaries. All structured data is a model.

### 2. Services (Dependency Injection)

Services use **constructor injection** with required dependencies. No defaults, no Optional.

```python
# backend/src/services/order_service.py
class OrderService:
    def __init__(self, repo: OrderRepository, db_connection: DBConnection):
        self.repo = repo
        self.db = db_connection

    def get_order(self, order_id: str) -> Order:
        return self.repo.find_by_id(order_id)

    def update_order(self, order_id: str, updates: OrderUpdate) -> Order:
        # Fail fast: raises if order doesn't exist
        order = self.repo.find_by_id(order_id)
        # Apply updates...
        return self.repo.save(order)
```

**Principle**: All dependencies passed in, no creation inside services.

### 3. Repositories (Data Access Layer)

Repositories abstract database interactions:

```python
# backend/src/repositories/order_repo.py
class OrderRepository:
    def __init__(self, db_connection: DBConnection):
        self.db = db_connection

    def find_by_id(self, order_id: str) -> Order:
        # Direct query, fail if not found
        row = self.db.query("SELECT * FROM orders WHERE id = %s", [order_id]).one()
        return Order(**row)

    def update_status(self, order_id: str, status: str) -> None:
        self.db.execute("UPDATE orders SET status = %s WHERE id = %s", [status, order_id])
```

**Principle**: Repositories know about DB, services know about business logic.

### 4. Lambda Handlers

Each Lambda is a thin entry point:

```python
# backend/src/lambdas/chat_handler.py
def lambda_handler(event: dict, context: Any) -> dict:
    # Extract auth context
    user_id = event['requestContext']['authorizer']['principalId']

    # Parse request
    body = json.loads(event['body'])
    message = body['message']
    order_id = body['order_id']

    # Dependency injection
    db_conn = DBConnection(os.environ['DB_HOST'], os.environ['DB_PASSWORD'])
    repos = {
        'order': OrderRepository(db_conn),
        'inventory': InventoryRepository(db_conn),
        'user': UserRepository(db_conn),
        'chat': ChatRepository(db_conn),
    }
    services = {
        'order': OrderService(repos['order'], db_conn),
        'inventory': InventoryService(repos['inventory']),
        'policy': PolicyService(repos['policy']),
        'agent': AgentService(services['order'], services['inventory'], services['policy']),
    }

    # Run agent
    response = services['agent'].process_message(user_id, order_id, message)

    return {
        'statusCode': 200,
        'body': json.dumps(response.model_dump())
    }
```

**Principle**: Handlers orchestrate, services execute, fail fast on errors.

### 5. Agent & MCP Server

The **agent** (Claude via Anthropic SDK) uses an **MCP server** for tool access:

```python
# backend/src/agent/agent.py
class OrderSupportAgent:
    def __init__(self, order_service: OrderService, inventory_service: InventoryService,
                 policy_service: PolicyService, chat_service: ChatService):
        self.order_svc = order_service
        self.inventory_svc = inventory_service
        self.policy_svc = policy_service
        self.chat_svc = chat_service
        self.client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    def process_message(self, user_id: str, order_id: str, message: str) -> ChatResponse:
        order = self.order_svc.get_order(order_id)
        tools = self._build_tools()

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=self._system_prompt(order),
            tools=tools,
            messages=[
                {"role": "user", "content": message}
            ]
        )

        # Handle tool calls in response...
        # Execute tools, gather results, call agent again if needed

        return ChatResponse(...)
```

---

## Database Schema (PostgreSQL)

```sql
-- Companies
CREATE TABLE companies (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Orders
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    status VARCHAR NOT NULL,  -- CREATED, APPROVED, IN_PRODUCTION, etc.
    shipping_address TEXT NOT NULL,
    requested_delivery_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Order Line Items
CREATE TABLE order_line_items (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    product_id VARCHAR NOT NULL,
    size VARCHAR NOT NULL,
    color VARCHAR NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Inventory
CREATE TABLE inventory (
    id UUID PRIMARY KEY,
    product_id VARCHAR NOT NULL,
    size VARCHAR NOT NULL,
    color VARCHAR NOT NULL,
    available_quantity INT NOT NULL,
    reserved_quantity INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(product_id, size, color)
);

-- Change Policies
CREATE TABLE change_policies (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    from_status VARCHAR NOT NULL,
    change_type VARCHAR NOT NULL,  -- quantity, size, shipping_address, artwork
    allowed BOOLEAN NOT NULL,
    cost_impact VARCHAR,  -- none, extra_charge, delay, contact_support
    delay_days INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    order_id UUID NOT NULL,
    role VARCHAR NOT NULL,  -- user, assistant
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    order_id UUID NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

---

## API Endpoints (Lambda + API Gateway)

### Authentication
- `POST /auth/login` → JWT token
- `POST /auth/logout` → Invalidate session

### Orders
- `GET /orders` → List user's orders
- `GET /orders/{order_id}` → Order details + line items
- `PATCH /orders/{order_id}` → Update order (admin or via agent)

### Chat
- `POST /chat` → Send message to agent
  - Request: `{ order_id, message }`
  - Response: `{ response, suggested_changes, requires_confirmation }`
- `GET /chat/{order_id}` → Chat history

### Inventory
- `GET /inventory` → Available inventory (filtered by product/size/color)
- `POST /inventory/check` → Batch availability check

### Policies
- `GET /policies` → All policies
- `GET /policies/check` → Validate a specific change

---

## Frontend Architecture

### State Management
- **useAuth**: Login/logout, current user, JWT token
- **useOrder**: Current order, line items, status
- **useChat**: Chat messages, session, pending responses

### Key Pages
- **Login**: Email/password auth
- **OrderHistory**: List of user's orders with quick actions
- **OrderDetail**: Single order view with chat sidebar
- **ChatInterface**: Conversation with agent, change proposals, confirm/execute

### API Client
```typescript
// frontend/src/api/client.ts
export const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
    headers: {
        'Authorization': `Bearer ${getToken()}`
    }
});
```

---

## Infrastructure (Python CDK)

The **CDK app** defines all AWS resources:

```python
# infrastructure/cdk/app.py
from aws_cdk import App, Environment

app = App()

env = Environment(account=ACCOUNT_ID, region=REGION)

# RDS
rds_stack = RDSStack(app, 'BrightThread-RDS', env=env)

# Secrets
secrets_stack = SecretsStack(app, 'BrightThread-Secrets', env=env)

# Lambda functions
lambda_stack = LambdaStack(
    app, 'BrightThread-Lambda',
    rds_endpoint=rds_stack.db_endpoint,
    secrets=secrets_stack.secrets,
    env=env
)

# API Gateway
api_stack = APIStack(
    app, 'BrightThread-API',
    lambdas=lambda_stack.lambdas,
    env=env
)

# Frontend (S3 + CloudFront)
frontend_stack = FrontendStack(
    app, 'BrightThread-Frontend',
    api_url=api_stack.api_endpoint,
    env=env
)

app.synth()
```

---

## Development Workflow

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or Docker for LocalStack)
- AWS CDK CLI
- GitHub CLI

### Local Development with Docker Compose

```bash
# Start LocalStack + Postgres
docker-compose up -d

# Set env variables for local dev
export PYTHONPATH=backend/src
export DB_HOST=localhost
export DB_PASSWORD=password
export AWS_ENDPOINT_URL_S3=http://localhost:4566
```

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Format code (ruff)
make format

# Lint (ruff)
make lint

# Run tests
make test

# Run specific test
pytest tests/unit/test_order_service.py -v
```

### Frontend Development

```bash
cd frontend

npm install
npm run dev  # Vite dev server on :5173
```

### Deploy Infrastructure

```bash
cd infrastructure/cdk

# Install CDK dependencies
pip install -r requirements.txt

# Review changes
cdk diff

# Deploy to AWS
cdk deploy --all
```

---

## CI/CD Pipelines (GitHub Actions)

### `.github/workflows/test.yml`
- Triggers on: push to main/PRs
- Runs: `ruff format --check`, `ruff check`, `pytest`
- Publishes: Coverage reports

### `.github/workflows/deploy.yml`
- Triggers on: merge to main (after tests pass)
- Deploys: Infrastructure via CDK, Lambdas via S3, Frontend to CloudFront

### `.github/workflows/build-frontend.yml`
- Triggers on: frontend/ changes
- Builds: Vite bundle
- Uploads: To S3 bucket for CloudFront distribution

---

## Key Design Decisions

### 1. **Lambdas for Scalability**
- Stateless, auto-scaling
- Pay-per-invocation
- Cold start acceptable for chat latency (agent calls are ~2-5s anyway)

### 2. **PostgreSQL over DynamoDB**
- Relational queries (orders → line items → inventory)
- Consistent transactions (inventory reservations)
- Easier schema evolution

### 3. **MCP Server Pattern**
- Agent calls tools via MCP
- Clear abstraction between agent logic and backend services
- Testable: can mock tools for unit tests

### 4. **Pydantic Models**
- Validation at API boundaries
- Type hints enable IDE support
- Self-documenting schemas

### 5. **Dependency Injection**
- All services receive dependencies in `__init__`
- Enables easy mocking for tests
- Makes service dependencies explicit

### 6. **Vite + React**
- Fast build and HMR during development
- Minimal bundle size
- Strong TypeScript support

---

## Constitution Compliance

This architecture adheres to `.claude/constitution.md`:

✅ **Radical Simplicity**: No over-engineered patterns; direct service calls, no event buses or complex flows
✅ **Fail Fast**: Services raise exceptions on missing data; agent clearly states limitations
✅ **Type Safety**: All Python code uses type hints; frontend uses TypeScript
✅ **Structured Data**: Pydantic models for all business objects
✅ **Dependency Injection**: Services receive all dependencies; no singletons
✅ **Unit Testing**: Mocks for DB, agent, external APIs
✅ **SOLID Principles**: Each service has one responsibility; extensions via new policies, not modifications

---

## Next Steps for Implementation

1. **Database Setup**: Define schema in `docs/DATABASE.md`, create migration scripts
2. **Models & Repositories**: Implement Pydantic models and DAL layer
3. **Services**: Build business logic (OrderService, InventoryService, PolicyService)
4. **Agent**: Define tools, system prompt, test with simple scenarios
5. **Lambda Handlers**: Wire services into Lambda entry points
6. **Frontend**: Build React components, connect to APIs
7. **Infrastructure**: Deploy CDK stacks to AWS
8. **Testing**: Unit tests, integration tests, end-to-end agent scenarios
9. **Documentation**: API docs, deployment guide, agent behavior guide

---

**Last Updated**: 2025-12-16
**Architecture Version**: 1.0
**Constitution Version**: 3.2.0
