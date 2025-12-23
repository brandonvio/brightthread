"""Product repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import Product


class ProductRepository:
    """Data access layer for products."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[Product]:
        """Retrieve all products from database.

        Returns:
            List of all Product entities.
        """
        return list(self._session.query(Product).order_by(Product.name).all())

    def get_by_id(self, product_id: uuid.UUID) -> Product:
        """Retrieve a product by its ID.

        Args:
            product_id: UUID of the product.

        Returns:
            Product entity.

        Raises:
            NoResultFound: If product does not exist.
        """
        return self._session.query(Product).filter(Product.id == product_id).one()

    def get_by_sku(self, sku: str) -> Product:
        """Retrieve a product by SKU.

        Args:
            sku: SKU of the product.

        Returns:
            Product entity.

        Raises:
            NoResultFound: If product does not exist.
        """
        return self._session.query(Product).filter(Product.sku == sku).one()

    def get_by_supplier_id(self, supplier_id: uuid.UUID) -> list[Product]:
        """Retrieve all products from a supplier.

        Args:
            supplier_id: UUID of the supplier.

        Returns:
            List of Product entities.
        """
        return list(
            self._session.query(Product)
            .filter(Product.supplier_id == supplier_id)
            .order_by(Product.name)
            .all()
        )

    def create(self, product: Product) -> Product:
        """Create a new product in the database.

        Args:
            product: Product entity to create.

        Returns:
            Created Product entity.
        """
        self._session.add(product)
        self._session.flush()
        return product

    def count(self) -> int:
        """Count total products in database.

        Returns:
            Number of products.
        """
        return self._session.query(Product).count()
