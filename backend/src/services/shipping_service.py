"""Shipping address service for address management."""

import uuid

from repositories.shipping_address_repository import ShippingAddressRepository
from services.shipping_models import ShippingAddress


class ShippingService:
    """Business logic for shipping address management."""

    def __init__(self, shipping_repo: ShippingAddressRepository) -> None:
        """Initialize shipping service with required dependencies.

        Args:
            shipping_repo: Repository for shipping address data access.
        """
        self._shipping_repo = shipping_repo

    def get_address(self, address_id: uuid.UUID) -> ShippingAddress:
        """Retrieve a shipping address by ID.

        Args:
            address_id: UUID of the shipping address.

        Returns:
            Shipping address model.
        """
        address = self._shipping_repo.get_by_id(address_id)
        return ShippingAddress.model_validate(address)

    def create_address(
        self,
        user_id: uuid.UUID,
        label: str,
        street_address: str,
        city: str,
        state: str,
        postal_code: str,
        country: str,
        is_default: bool = False,
    ) -> ShippingAddress:
        """Create a new shipping address.

        Args:
            user_id: UUID of the user.
            label: Address label.
            street_address: Street address.
            city: City.
            state: State.
            postal_code: Postal code.
            country: Country.
            is_default: Whether this is the default address.

        Returns:
            Created shipping address model.
        """
        from db.models import ShippingAddress as ShippingAddressDB

        address = ShippingAddressDB(
            id=uuid.uuid4(),
            created_by_user_id=user_id,
            label=label,
            street_address=street_address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default,
        )

        created_address = self._shipping_repo.create(address)
        return ShippingAddress.model_validate(created_address)

    def list_user_addresses(self, user_id: uuid.UUID) -> list[ShippingAddress]:
        """List all shipping addresses for a user.

        Args:
            user_id: UUID of the user.

        Returns:
            List of shipping addresses.
        """
        addresses = self._shipping_repo.get_by_user_id(user_id)
        return [ShippingAddress.model_validate(a) for a in addresses]

    def get_default_address(self, user_id: uuid.UUID) -> ShippingAddress:
        """Get the default shipping address for a user.

        Args:
            user_id: UUID of the user.

        Returns:
            Default shipping address.
        """
        address = self._shipping_repo.get_default_by_user_id(user_id)
        return ShippingAddress.model_validate(address)

    def set_default(self, address_id: uuid.UUID, user_id: uuid.UUID) -> ShippingAddress:
        """Set an address as the default for a user.

        Args:
            address_id: UUID of the address to set as default.
            user_id: UUID of the user.

        Returns:
            Updated shipping address.
        """
        addresses = self._shipping_repo.get_by_user_id(user_id)

        for addr in addresses:
            addr.is_default = addr.id == address_id
            self._shipping_repo.update(addr)

        address = self._shipping_repo.get_by_id(address_id)
        return ShippingAddress.model_validate(address)
