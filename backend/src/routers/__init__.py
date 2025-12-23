"""API routers for BrightThread."""

from routers.agent import router as agent_router
from routers.artworks import router as artworks_router
from routers.auth import router as auth_router
from routers.catalog import router as catalog_router
from routers.companies import router as companies_router
from routers.conversations import router as conversations_router
from routers.inventory import router as inventory_router
from routers.orders import router as orders_router
from routers.products import router as products_router
from routers.shipping import router as shipping_router
from routers.system import router as system_router
from routers.users import router as users_router

__all__ = [
    "system_router",
    "agent_router",
    "conversations_router",
    "orders_router",
    "inventory_router",
    "products_router",
    "users_router",
    "companies_router",
    "artworks_router",
    "shipping_router",
    "catalog_router",
    "auth_router",
]
