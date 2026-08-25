from apps.inventory.models import Inventory


class InventoryRepository:

    @staticmethod
    def get_by_id(
        *,
        organization,
        inventory_id,
    ):
        """
        Retrieve inventory by ID within an organization.
        """

        return Inventory.objects(
            organization=organization,
            id=inventory_id,
        ).first()

    @staticmethod
    def get_by_product_and_warehouse(
        *,
        organization,
        product,
        warehouse,
    ):
        """
        Retrieve inventory for a specific
        product and warehouse.
        """

        return Inventory.objects(
            organization=organization,
            product=product,
            warehouse=warehouse,
        ).first()

    @staticmethod
    def list_by_organization(
        *,
        organization,
    ):
        """
        Return all inventory belonging
        to an organization.
        """

        return Inventory.objects(
            organization=organization,
        ).order_by(
            "-updated_at"
        )

    @staticmethod
    def list_by_warehouse(
        *,
        organization,
        warehouse,
    ):
        """
        Return inventory belonging
        to a specific warehouse.
        """

        return Inventory.objects(
            organization=organization,
            warehouse=warehouse,
        ).order_by(
            "-updated_at"
        )

    @staticmethod
    def list_by_product(
        *,
        organization,
        product,
    ):
        """
        Return inventory belonging
        to a specific product.
        """

        return Inventory.objects(
            organization=organization,
            product=product,
        ).order_by(
            "-updated_at"
        )

    @staticmethod
    def create_inventory(
        *,
        organization,
        product,
        warehouse,
        quantity=0,
        reserved_quantity=0,
    ):
        """
        Create a new inventory record.
        """

        inventory = Inventory(
            organization=organization,
            product=product,
            warehouse=warehouse,
            quantity=quantity,
            reserved_quantity=reserved_quantity,
        )

        inventory.save()

        return inventory

    @staticmethod
    def update_quantity(
        *,
        inventory,
        quantity,
    ):
        """
        Update inventory quantity.
        """

        inventory.quantity = quantity
        inventory.save()

        return inventory

    @staticmethod
    def update_reserved_quantity(
        *,
        inventory,
        reserved_quantity,
    ):
        """
        Update reserved quantity.
        """

        inventory.reserved_quantity = (
            reserved_quantity
        )

        inventory.save()

        return inventory