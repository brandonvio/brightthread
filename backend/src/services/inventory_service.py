"""Inventory service with reservation logic."""

import uuid

from repositories.inventory_repository import InventoryRepository
from services.inventory_models import (
    EnrichedInventory,
    Inventory,
    InventoryAvailability,
)


class InsufficientInventoryError(Exception):
    """Raised when inventory availability check fails."""

    pass


class InventoryService:
    """Business logic for inventory management and reservations."""

    def __init__(self, inventory_repo: InventoryRepository) -> None:
        """Initialize inventory service with required dependencies.

        Args:
            inventory_repo: Repository for inventory data access.
        """
        self._inventory_repo = inventory_repo

    def check_availability(
        self,
        product_id: uuid.UUID,
        color_id: uuid.UUID,
        size_id: uuid.UUID,
        quantity: int,
    ) -> InventoryAvailability:
        """Check if requested quantity is available.

        Args:
            product_id: UUID of the product.
            color_id: UUID of the color.
            size_id: UUID of the size.
            quantity: Requested quantity.

        Returns:
            Availability status with quantities.
        """
        inventory = self._inventory_repo.get_by_product_color_size(
            product_id, color_id, size_id
        )

        available = inventory.available_qty >= quantity

        return InventoryAvailability(
            available=available,
            available_qty=inventory.available_qty,
            reserved_qty=inventory.reserved_qty,
        )

    def reserve_inventory(
        self,
        inventory_id: uuid.UUID,
        quantity: int,
    ) -> Inventory:
        """Reserve inventory for an order.

        Args:
            inventory_id: UUID of the inventory item.
            quantity: Quantity to reserve.

        Returns:
            Updated inventory model.

        Raises:
            InsufficientInventoryError: If insufficient inventory available.
        """
        inventory = self._inventory_repo.get_by_id(inventory_id)

        if inventory.available_qty < quantity:
            raise InsufficientInventoryError(
                f"Insufficient inventory. Available: {inventory.available_qty}, Requested: {quantity}"
            )

        inventory.available_qty -= quantity
        inventory.reserved_qty += quantity

        updated_inventory = self._inventory_repo.update(inventory)
        return Inventory.model_validate(updated_inventory)

    def release_reservation(
        self,
        inventory_id: uuid.UUID,
        quantity: int,
    ) -> Inventory:
        """Release inventory reservation.

        Args:
            inventory_id: UUID of the inventory item.
            quantity: Quantity to release.

        Returns:
            Updated inventory model.
        """
        inventory = self._inventory_repo.get_by_id(inventory_id)

        inventory.available_qty += quantity
        inventory.reserved_qty -= quantity

        updated_inventory = self._inventory_repo.update(inventory)
        return Inventory.model_validate(updated_inventory)

    def get_inventory_by_product(self, product_id: uuid.UUID) -> list[Inventory]:
        """Retrieve all inventory records for a product.

        Args:
            product_id: UUID of the product.

        Returns:
            List of inventory models.
        """
        items = self._inventory_repo.get_by_product_id(product_id)
        return [Inventory.model_validate(item) for item in items]

    def get_inventory_by_id(self, inventory_id: uuid.UUID) -> Inventory:
        """Retrieve inventory record by ID.

        Args:
            inventory_id: UUID of the inventory item.

        Returns:
            Inventory model.
        """
        inventory = self._inventory_repo.get_by_id(inventory_id)
        return Inventory.model_validate(inventory)

    def get_enriched_inventory_by_id(
        self, inventory_id: uuid.UUID
    ) -> EnrichedInventory:
        """Retrieve enriched inventory record by ID with product/color/size details.

        Args:
            inventory_id: UUID of the inventory item.

        Returns:
            Enriched inventory model.
        """
        inventory = self._inventory_repo.get_by_id(inventory_id)
        return EnrichedInventory(
            id=inventory.id,
            product_id=inventory.product_id,
            color_id=inventory.color_id,
            size_id=inventory.size_id,
            available_qty=inventory.available_qty,
            reserved_qty=inventory.reserved_qty,
            updated_at=inventory.updated_at,
            product_name=inventory.product.name,
            product_sku=inventory.product.sku,
            color_name=inventory.color.name,
            color_hex=inventory.color.hex_code,
            size_name=inventory.size.name,
            size_code=inventory.size.code,
        )

    def get_all_inventory(self) -> list[Inventory]:
        """Retrieve all inventory records.

        Returns:
            List of all inventory models.
        """
        items = self._inventory_repo.get_all()
        return [Inventory.model_validate(item) for item in items]

    def get_all_enriched_inventory(self) -> list[EnrichedInventory]:
        """Retrieve all enriched inventory records with product/color/size details.

        Returns:
            List of all enriched inventory models.
        """
        items = self._inventory_repo.get_all()
        return [
            EnrichedInventory(
                id=item.id,
                product_id=item.product_id,
                color_id=item.color_id,
                size_id=item.size_id,
                available_qty=item.available_qty,
                reserved_qty=item.reserved_qty,
                updated_at=item.updated_at,
                product_name=item.product.name,
                product_sku=item.product.sku,
                color_name=item.color.name,
                color_hex=item.color.hex_code,
                size_name=item.size.name,
                size_code=item.size.code,
            )
            for item in items
        ]
