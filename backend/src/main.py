"""BrightThread Order Support Agent - FastAPI Backend."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from routers import (
    agent_router,
    artworks_router,
    auth_router,
    catalog_router,
    companies_router,
    conversations_router,
    inventory_router,
    orders_router,
    products_router,
    shipping_router,
    system_router,
    users_router,
)

app = FastAPI(
    title="BrightThread Order Support Agent",
    description="API for managing orders and customer support requests",
    version="0.1.0",
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://brightthread.design",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with method, path, and body."""
    body = None
    if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()
        logger.info(
            f"REQUEST: {request.method} {request.url.path} | "
            f"Query: {dict(request.query_params)} | "
            f"Body: {body.decode('utf-8') if body else 'None'}"
        )
    else:
        logger.info(
            f"REQUEST: {request.method} {request.url.path} | "
            f"Query: {dict(request.query_params)}"
        )

    response = await call_next(request)
    logger.info(
        f"RESPONSE: {request.method} {request.url.path} -> {response.status_code}"
    )
    return response


# Register routers
app.include_router(system_router)
app.include_router(agent_router)
app.include_router(conversations_router)

# BrightThread API routers (database-backed)
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(inventory_router)
app.include_router(products_router)
app.include_router(users_router)
app.include_router(companies_router)
app.include_router(artworks_router)
app.include_router(shipping_router)
app.include_router(catalog_router)


def lambda_handler(event: dict, context: object) -> dict:
    """AWS Lambda handler for the API."""
    logger.info(f"Lambda invoked: {event}")

    from mangum import Mangum

    handler = Mangum(app)
    return handler(event, context)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting BrightThread Order Support Agent API")
    uvicorn.run(app, host="0.0.0.0", port=8000)
