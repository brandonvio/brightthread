# BrightThread Order Support Agent - Backend API

A FastAPI-based order support agent for BrightThread's B2B apparel platform. This API provides endpoints for customer service requests, order management, inventory tracking, and policy evaluation.

## Overview

The backend implements a conversational order support system that helps customers make changes to their orders through natural language requests. The system:

- **Understands customer requests** in free-form text
- **Checks order policies** to determine what changes are allowed
- **Validates inventory** and production constraints
- **Generates options** with costs, delays, and approval status
- **Applies approved changes** to orders
- **Provides operations dashboards** for the support team

## API Documentation

📖 **Interactive API Docs**: [brandonvio.github.io/brightthread/api](https://brandonvio.github.io/brightthread/api/)

## Architecture

### Services

- **OrderService**: Manages order retrieval and updates
- **InventoryService**: Handles inventory checking and production timelines
- **PolicyService**: Evaluates change policies based on order status
- **AgentService**: Processes customer requests and generates response options

### API Endpoints

**18 total endpoints** organized into 6 categories:

#### System & Health (2)
- `GET /` - API information
- `GET /health` - Health check

#### Orders (3)
- `GET /orders/{order_id}` - Retrieve order details
- `GET /orders/{order_id}/status` - Get current status
- `PUT /orders/{order_id}/status` - Update status

#### Agent / Chat (2)
- `POST /orders/{order_id}/chat` - Process customer request
- `POST /orders/{order_id}/apply-change` - Apply approved change

#### Inventory (3)
- `GET /inventory/{product_id}` - Get inventory levels
- `GET /inventory/{product_id}/check` - Check availability
- `GET /orders/{order_id}/production-timeline` - Get production schedule

#### Policies (2)
- `GET /policies/order-changes` - Get all policies
- `POST /policies/evaluate-change` - Evaluate specific change

#### Operations (2)
- `POST /operations/alert` - Create operations alert
- `GET /operations/dashboard` - Get ops dashboard

## Installation

### Requirements
- Python 3.13+
- UV package manager (https://astral.sh/uv/)

### Setup

```bash
# Install dependencies
uv sync

# Run locally
uv run python main.py
```

API will be available at `http://localhost:8000`

## Usage Examples

### 1. Get an Order

```bash
curl http://localhost:8000/orders/order-001
```

Response:
```json
{
  "order_id": "order-001",
  "company_id": "company-001",
  "status": "APPROVED",
  "line_items": [...],
  "total_amount": 1297.10
}
```

### 2. Submit Customer Request (Chat)

```bash
curl -X POST http://localhost:8000/orders/order-001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order-001",
    "message": "Can you change 20 of the medium shirts to large?",
    "conversation_history": []
  }'
```

Response:
```json
{
  "agent_message": "Great! I can help with that. We can process this change with no additional cost or delay. Please confirm if you'd like to proceed with this change.",
  "options": [
    {
      "option_id": "uuid-here",
      "description": "Change size adjustment - We can process this change with no additional cost or delay.",
      "proposed_changes": [...],
      "approval_status": "ALLOWED",
      "cost_adjustment": 0,
      "estimated_delay_days": 0,
      "confidence_score": 0.8
    }
  ],
  "requires_manual_review": false,
  "confidence_score": 0.85
}
```

### 3. Apply a Change

```bash
curl -X POST "http://localhost:8000/orders/order-001/apply-change?option_id=uuid-here&applied_by=customer"
```

Response:
```json
{
  "change_id": "change-uuid",
  "option_id": "option-uuid",
  "applied_by": "customer",
  "applied_at": "2025-12-16T12:00:00"
}
```

### 4. Check Inventory

```bash
curl "http://localhost:8000/inventory/prod-001?color=Navy%20Blue&size=M"
```

Response:
```json
{
  "product_id": "prod-001",
  "color": "Navy Blue",
  "size": "M",
  "available_quantity": 150,
  "in_production_quantity": 75,
  "total_quantity": 225
}
```

### 5. Get Policies

```bash
curl http://localhost:8000/policies/order-changes
```

Response: Array of policy rules organized by stage and change type.

## Data Models

### Order Statuses
- `CREATED` - Order created but not yet approved
- `APPROVED` - Order approved and ready for production
- `IN_PRODUCTION` - Currently being manufactured
- `READY_TO_SHIP` - Completed, awaiting shipment
- `SHIPPED` - Order delivered

### Change Types
- `SIZE_ADJUSTMENT` - Change product size
- `QUANTITY_ADJUSTMENT` - Change quantity
- `ARTWORK_CHANGE` - Switch artwork/logo
- `SHIPPING_ADDRESS_CHANGE` - Update delivery address
- `DELIVERY_DATE_CHANGE` - Request expedited/delayed delivery
- `COLOR_CHANGE` - Change product color

### Approval Status
- `ALLOWED` - Change approved with no cost or delay
- `ALLOWED_WITH_COST` - Approved but customer pays surcharge
- `ALLOWED_WITH_DELAY` - Approved but will delay delivery
- `ALLOWED_WITH_COST_AND_DELAY` - Approved with both cost and delay
- `REQUIRES_MANUAL_REVIEW` - Needs human agent review
- `NOT_ALLOWED` - Policy prohibits this change at this stage

## Logging

All operations are logged using Loguru. By default, logs are output to stdout:

```
2025-12-16 12:00:00 INFO | Processing customer request for order order-001: Can you change sizes?
2025-12-16 12:00:00 INFO | Order status: APPROVED
2025-12-16 12:00:00 INFO | Detected 1 potential changes
2025-12-16 12:00:00 INFO | Generated 1 options for customer
```

## Lambda Deployment

The API includes a Lambda handler for AWS deployment:

```python
def lambda_handler(event: dict, context) -> dict:
    """AWS Lambda handler for the API."""
    from mangum import Mangum
    handler = Mangum(app)
    return handler(event, context)
```

Use with API Gateway by:
1. Setting Lambda handler to `main.lambda_handler`
2. Configure API Gateway to trigger the Lambda function
3. The `mangum` middleware automatically adapts FastAPI to Lambda's event format

## Code Quality

All code follows the BrightThread constitution:

✓ **Radical Simplicity**: Clear, straightforward implementations
✓ **Type Safety**: Full type hints throughout
✓ **Structured Data**: Pydantic models for all data
✓ **Dependency Injection**: All services use constructor injection
✓ **Zero Ruff Violations**: Code passes all linting checks

## Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov
```

## Next Steps

1. **Database Integration**: Connect to real orders/inventory database
2. **Authentication**: Add user authentication and authorization
3. **AI Integration**: Replace placeholder change detection with LLM-based agent
4. **Webhook Notifications**: Add customer/ops notifications on changes
5. **CloudFormation/CDK**: Deploy infrastructure using Python CDK

## Configuration

Currently uses placeholder data. To integrate with real systems:

1. Replace `OrderService.get_order()` with database queries
2. Replace `InventoryService` with real inventory system
3. Replace `PolicyService.get_policies()` with policy database
4. Add database connection details in environment variables

## Dependencies

- **fastapi**: Web framework
- **pydantic**: Data validation and serialization
- **loguru**: Structured logging
- **mangum**: ASGI adapter for Lambda
- **uvicorn**: ASGI server (local development)

## File Structure

```
backend/
├── main.py                 # FastAPI application and endpoints
├── models.py               # Pydantic data models
├── order_service.py        # Order, inventory, and policy services
├── agent_service.py        # Conversational agent service
├── pyproject.toml          # Project configuration and dependencies
└── README.md               # This file
```

## License

All code retains rights per BrightThread interview assignment terms.
