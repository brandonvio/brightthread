# Integration Tests

Integration tests for the BrightThread Order Support Agent API. These tests validate the deployed Lambda function running on AWS Lambda via API Gateway.

## What's Tested

- **Health Endpoints**: System status and readiness
- **Order Management**: Order status, quantity adjustments, shipping, delivery dates
- **Inventory Management**: Availability checks, production timelines
- **Policy Evaluation**: Policy rules and change approval
- **Agent Endpoints**: Chat, customer request processing
- **Operations**: Dashboard, alerts
- **Error Handling**: Invalid inputs, validation errors
- **Concurrency**: Multiple concurrent requests

## Prerequisites

1. **Deployed API**: Backend must be deployed to AWS Lambda
   ```bash
   make deploy-backend
   ```

2. **API Endpoint**: The API is available at the custom domain (HTTPS)
   ```
   https://api.brightthread.design
   ```
   - This custom domain is configured in Route53 pointing to the API Gateway
   - SSL/TLS certificate is managed by ACM (AWS Certificate Manager)
   - Both `api.brightthread.design` and `*.brightthread.design` are covered

3. **httpx**: HTTP client library (add to dev dependencies if needed)
   ```bash
   cd backend && uv add --dev httpx
   ```

## Running Integration Tests

### Set the API Endpoint (Optional)

By default, tests use `https://api.brightthread.design`. To override:

```bash
# Use default custom domain (recommended)
pytest backend/tests_integration -v

# Or override with API Gateway endpoint if needed
export API_ENDPOINT=https://api.brightthread.design
pytest backend/tests_integration -v

# Or use raw API Gateway endpoint for troubleshooting
export API_ENDPOINT=https://25wmfybuka.execute-api.us-west-2.amazonaws.com/prod/
pytest backend/tests_integration -v
```

### Run All Integration Tests

```bash
pytest backend/tests_integration -v
```

### Run Specific Test Classes

```bash
# Test only health endpoints
pytest backend/tests_integration/test_api_endpoints.py::TestHealthEndpoints -v

# Test only order endpoints
pytest backend/tests_integration/test_api_endpoints.py::TestOrderEndpoints -v

# Test only agent endpoints
pytest backend/tests_integration/test_api_endpoints.py::TestAgentEndpoints -v
```

### Run Specific Tests

```bash
# Test health check only
pytest backend/tests_integration/test_api_endpoints.py::TestHealthEndpoints::test_health_check -v

# Test with verbose output and print statements
pytest backend/tests_integration -v -s
```

### Run with Different Options

```bash
# Run with detailed output
pytest backend/tests_integration -vv

# Stop on first failure
pytest backend/tests_integration -x

# Run only failed tests from last run
pytest backend/tests_integration --lf

# Run tests matching a pattern
pytest backend/tests_integration -k "health" -v

# Run with coverage
pytest backend/tests_integration --cov=src --cov-report=html
```

## Test Structure

Each test is organized by endpoint category:

```
TestHealthEndpoints/
  - test_health_check
  - test_root_endpoint

TestOrderEndpoints/
  - test_get_order_status
  - test_update_order_status
  - test_quantity_adjustment
  - test_update_shipping_address
  - test_update_delivery_date

TestInventoryEndpoints/
  - test_get_inventory
  - test_check_availability
  - test_production_timeline

TestPolicyEndpoints/
  - test_get_policies
  - test_evaluate_change

TestAgentEndpoints/
  - test_chat_message
  - test_process_customer_request

TestOperationsEndpoints/
  - test_operations_dashboard
  - test_create_alert

TestErrorHandling/
  - test_invalid_order_id
  - test_missing_required_fields
  - test_api_latency

TestConcurrentRequests/
  - test_concurrent_health_checks
  - test_concurrent_order_requests
```

## What Gets Tested

### Deployment Validation
- Lambda function is reachable
- API Gateway is properly configured
- Cold start handling

### API Functionality
- All endpoints return proper HTTP status codes
- Response data structures are valid
- Payload validation works correctly

### Error Handling
- Invalid inputs are handled gracefully
- Missing required fields are caught
- Proper error responses are returned

### Performance
- API responds within reasonable timeframe
- Concurrent requests are handled

## Example CI/CD Integration

```bash
#!/bin/bash
# Deploy backend
make deploy-backend

# Extract API endpoint from CloudFormation output
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name BackendServiceStack \
  --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
  --output text)

# Run integration tests
export API_ENDPOINT=$API_ENDPOINT
pytest backend/tests_integration -v --tb=short

# Exit with test result code
exit $?
```

## Continuous Monitoring

After deployment, you can monitor the API:

```bash
# Watch logs
aws logs tail /aws/lambda/brightthread-order-support-agent --follow

# Get CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=brightthread-order-support-agent \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Test API directly
curl https://25wmfybuka.execute-api.us-west-2.amazonaws.com/prod/health
```

## Notes

- **Default Endpoint**: Tests default to `https://api.brightthread.design` (custom domain with HTTPS)
- **Override**: Set `API_ENDPOINT` environment variable to use a different endpoint
- **Cold start**: First Lambda invocation may take longer (up to 30 seconds)
- **Timeout**: HTTP timeout is set to 30 seconds to account for cold starts
- **Concurrent tests**: Use `@pytest.mark.parametrize` to test multiple scenarios
- **SSL/TLS**: All requests use HTTPS with ACM certificate validation

## Troubleshooting

### Tests Fail with SSL Certificate Error
```bash
# This usually means the API Gateway custom domain isn't fully configured yet
# Verify the Route53 DNS records are pointing to API Gateway:
nslookup api.brightthread.design

# Or test directly:
curl https://api.brightthread.design/health

# If it fails, use the raw API Gateway endpoint instead:
export API_ENDPOINT=https://25wmfybuka.execute-api.us-west-2.amazonaws.com/prod/
pytest backend/tests_integration -v
```

### Tests Skip or Connection Refused
```bash
# Verify the infrastructure is deployed:
aws cloudformation list-stacks --profile brightthread --region us-west-2 | grep -i "CDN\|Backend\|Route53"

# Verify API is deployed:
make deploy-backend

# Verify endpoint is accessible:
curl -v https://api.brightthread.design/health

# Or check the CloudFormation stack outputs:
aws cloudformation describe-stacks \
  --stack-name BackendServiceStack \
  --profile brightthread \
  --query 'Stacks[0].Outputs' \
  --output table
```

### Timeout Errors
```
Cold start may take longer. Increase timeout:
# In conftest.py, change:
timeout=30.0  # or higher
```

### Invalid JSON
```
Check Lambda logs:
aws logs tail /aws/lambda/brightthread-order-support-agent --follow
```
