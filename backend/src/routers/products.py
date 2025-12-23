"""Product management endpoints for BrightThread."""

import uuid

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import CreateProductRequest
from auth import AuthenticatedUser
from db.session import get_db_session
from repositories.product_repository import ProductRepository
from repositories.supplier_repository import SupplierRepository
from services.product_models import Product
from services.product_service import ProductService

router = APIRouter(prefix="/v1/products", tags=["BrightThread Products"])


# =============================================================================
# Response Models (thin wrappers for list responses with counts)
# =============================================================================


class ProductListResponse(BaseModel):
    """Response for list of products."""

    products: list[Product]
    total: int


# =============================================================================
# Dependency Injection
# =============================================================================


def get_product_service(session: Session = Depends(get_db_session)) -> ProductService:
    """Create ProductService with injected dependencies."""
    product_repo = ProductRepository(session)
    supplier_repo = SupplierRepository(session)
    return ProductService(product_repo, supplier_repo)


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=ProductListResponse)
def list_products(
    auth: AuthenticatedUser,
    product_service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    """List all products."""
    logger.info("GET /v1/products")

    products = product_service.list_products()
    return ProductListResponse(products=products, total=len(products))


@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: str,
    auth: AuthenticatedUser,
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    """Get product by ID."""
    logger.info(f"GET /v1/products/{product_id}")

    product_uuid = uuid.UUID(product_id)
    return product_service.get_product(product_uuid)


@router.post("", response_model=Product, status_code=201)
def create_product(
    request: CreateProductRequest,
    auth: AuthenticatedUser,
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    """Create a new product."""
    logger.info("POST /v1/products")

    return product_service.create_product(
        supplier_id=request.supplier_id,
        sku=request.sku,
        name=request.name,
        base_price=request.base_price,
        description=request.description,
    )
