"""Product service for product management."""

import uuid

from repositories.product_repository import ProductRepository
from repositories.supplier_repository import SupplierRepository
from services.product_models import Product


class ProductService:
    """Business logic for product management."""

    def __init__(
        self,
        product_repo: ProductRepository,
        supplier_repo: SupplierRepository,
    ) -> None:
        """Initialize product service with required dependencies.

        Args:
            product_repo: Repository for product data access.
            supplier_repo: Repository for supplier data access.
        """
        self._product_repo = product_repo
        self._supplier_repo = supplier_repo

    def get_product(self, product_id: uuid.UUID) -> Product:
        """Retrieve a product by ID.

        Args:
            product_id: UUID of the product.

        Returns:
            Product model.
        """
        product = self._product_repo.get_by_id(product_id)
        return Product(
            id=product.id,
            supplier_id=product.supplier_id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            base_price=float(product.base_price),
            created_at=product.created_at,
        )

    def list_products(self) -> list[Product]:
        """List all products.

        Returns:
            List of all products.
        """
        products = self._product_repo.get_all()
        return [
            Product(
                id=p.id,
                supplier_id=p.supplier_id,
                sku=p.sku,
                name=p.name,
                description=p.description,
                base_price=float(p.base_price),
                created_at=p.created_at,
            )
            for p in products
        ]

    def get_by_sku(self, sku: str) -> Product:
        """Retrieve a product by SKU.

        Args:
            sku: SKU of the product.

        Returns:
            Product model.
        """
        product = self._product_repo.get_by_sku(sku)
        return Product(
            id=product.id,
            supplier_id=product.supplier_id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            base_price=float(product.base_price),
            created_at=product.created_at,
        )

    def get_products_by_supplier(self, supplier_id: uuid.UUID) -> list[Product]:
        """List all products from a supplier.

        Args:
            supplier_id: UUID of the supplier.

        Returns:
            List of products.
        """
        products = self._product_repo.get_by_supplier_id(supplier_id)
        return [
            Product(
                id=p.id,
                supplier_id=p.supplier_id,
                sku=p.sku,
                name=p.name,
                description=p.description,
                base_price=float(p.base_price),
                created_at=p.created_at,
            )
            for p in products
        ]

    def create_product(
        self,
        supplier_id: uuid.UUID,
        sku: str,
        name: str,
        base_price: float,
        description: str | None = None,
    ) -> Product:
        """Create a new product.

        Args:
            supplier_id: UUID of the supplier.
            sku: Product SKU.
            name: Product name.
            base_price: Base price.
            description: Product description.

        Returns:
            Created product model.
        """
        from db.models import Product as ProductDB

        product = ProductDB(
            id=uuid.uuid4(),
            supplier_id=supplier_id,
            sku=sku,
            name=name,
            description=description,
            base_price=base_price,
        )

        created_product = self._product_repo.create(product)
        return Product(
            id=created_product.id,
            supplier_id=created_product.supplier_id,
            sku=created_product.sku,
            name=created_product.name,
            description=created_product.description,
            base_price=float(created_product.base_price),
            created_at=created_product.created_at,
        )
