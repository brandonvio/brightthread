"""Integration tests for BrightThread Order Support Agent API.

These tests verify the deployed FastAPI application running on AWS Lambda
via API Gateway. They test the actual HTTP endpoints rather than unit
testing the services.

Environment:
    API_ENDPOINT: The deployed API endpoint (e.g., https://...execute-api.../)
                 If not set, tests will be skipped.

Usage:
    export API_ENDPOINT=https://25wmfybuka.execute-api.us-west-2.amazonaws.com/prod/
    pytest backend/tests_integration -v
"""
