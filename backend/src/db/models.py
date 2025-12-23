"""SQLAlchemy database models for BrightThread."""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class Company(Base):
    """Company model representing B2B customers."""

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    users: Mapped[list["User"]] = relationship(back_populates="company")

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name!r})>"


class Supplier(Base):
    """Supplier model representing vendors who supply products."""

    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    contact_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )
    address: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    products: Mapped[list["Product"]] = relationship(back_populates="supplier")

    def __repr__(self) -> str:
        return f"<Supplier(id={self.id}, name={self.name!r})>"


class Product(Base):
    """Product model representing apparel items available for order."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id"),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    base_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    supplier: Mapped["Supplier"] = relationship(back_populates="products")
    inventory_items: Mapped[list["Inventory"]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku={self.sku!r}, name={self.name!r})>"


class Color(Base):
    """Color model representing available color options for products."""

    __tablename__ = "colors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    hex_code: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
    )

    # Relationships
    inventory_items: Mapped[list["Inventory"]] = relationship(back_populates="color")

    def __repr__(self) -> str:
        return f"<Color(id={self.id}, name={self.name!r}, hex_code={self.hex_code!r})>"


class Size(Base):
    """Size model representing available size options for products."""

    __tablename__ = "sizes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Relationships
    inventory_items: Mapped[list["Inventory"]] = relationship(back_populates="size")

    def __repr__(self) -> str:
        return f"<Size(id={self.id}, name={self.name!r}, code={self.code!r})>"


class Inventory(Base):
    """Inventory model representing stock by product/color/size combination."""

    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "color_id", "size_id", name="uq_inventory_product_color_size"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
    )
    color_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colors.id"),
        nullable=False,
    )
    size_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sizes.id"),
        nullable=False,
    )
    available_qty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    reserved_qty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="inventory_items")
    color: Mapped["Color"] = relationship(back_populates="inventory_items")
    size: Mapped["Size"] = relationship(back_populates="inventory_items")
    order_line_items: Mapped[list["OrderLineItem"]] = relationship(
        back_populates="inventory"
    )

    def __repr__(self) -> str:
        return f"<Inventory(id={self.id}, product_id={self.product_id}, available={self.available_qty})>"


class User(Base):
    """User model representing individual users belonging to a company."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="users")
    artworks: Mapped[list["Artwork"]] = relationship(back_populates="uploaded_by_user")
    shipping_addresses: Mapped[list["ShippingAddress"]] = relationship(
        back_populates="created_by_user"
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email!r})>"


class Artwork(Base):
    """Artwork model representing logo and artwork assets uploaded by users."""

    __tablename__ = "artworks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    width_px: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    height_px: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    uploaded_by_user: Mapped["User"] = relationship(back_populates="artworks")
    orders: Mapped[list["Order"]] = relationship(back_populates="artwork")

    def __repr__(self) -> str:
        return f"<Artwork(id={self.id}, name={self.name!r})>"


class ShippingAddress(Base):
    """ShippingAddress model representing saved delivery addresses for companies."""

    __tablename__ = "shipping_addresses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    street_address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    postal_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    created_by_user: Mapped["User"] = relationship(back_populates="shipping_addresses")
    orders: Mapped[list["Order"]] = relationship(back_populates="shipping_address")

    def __repr__(self) -> str:
        return f"<ShippingAddress(id={self.id}, label={self.label!r})>"


class Order(Base):
    """Order model representing bulk orders placed by users."""

    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    shipping_address_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shipping_addresses.id"),
        nullable=False,
    )
    artwork_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artworks.id"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="CREATED",
    )
    delivery_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    shipping_address: Mapped["ShippingAddress"] = relationship(back_populates="orders")
    artwork: Mapped["Artwork | None"] = relationship(back_populates="orders")
    line_items: Mapped[list["OrderLineItem"]] = relationship(back_populates="order")
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        back_populates="order", order_by="OrderStatusHistory.transitioned_at"
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, status={self.status!r})>"


class OrderLineItem(Base):
    """OrderLineItem model representing individual product lines within an order."""

    __tablename__ = "order_line_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
    )
    inventory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="line_items")
    inventory: Mapped["Inventory"] = relationship(back_populates="order_line_items")

    def __repr__(self) -> str:
        return f"<OrderLineItem(id={self.id}, order_id={self.order_id}, quantity={self.quantity})>"


class OrderStatusHistory(Base):
    """OrderStatusHistory model tracking order state transitions over time."""

    __tablename__ = "order_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    transitioned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="status_history")

    def __repr__(self) -> str:
        return f"<OrderStatusHistory(id={self.id}, order_id={self.order_id}, status={self.status!r})>"
