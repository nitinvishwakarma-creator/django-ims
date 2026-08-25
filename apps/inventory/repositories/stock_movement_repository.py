from apps.inventory.models import StockMovement


class StockMovementRepository:

    @staticmethod
    def create_movement(
        *,
        organization,
        inventory,
        product,
        warehouse,
        movement_type,
        quantity,
        quantity_before,
        quantity_after,
        reserved_before,
        reserved_after,
        created_by,
        reference_type="",
        reference_id="",
        notes="",
    ):
        """
        Create an immutable stock movement record.
        """

        movement = StockMovement(
            organization=organization,
            inventory=inventory,
            product=product,
            warehouse=warehouse,
            movement_type=movement_type,
            quantity=quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reserved_before=reserved_before,
            reserved_after=reserved_after,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by,
        )

        movement.save()

        return movement

    @staticmethod
    def get_by_id(
        *,
        organization,
        movement_id,
    ):
        return StockMovement.objects(
            organization=organization,
            id=movement_id,
        ).first()

    @staticmethod
    def list_by_organization(
        *,
        organization,
    ):
        return StockMovement.objects(
            organization=organization,
        ).order_by("-created_at")

    @staticmethod
    def list_by_inventory(
        *,
        organization,
        inventory,
    ):
        return StockMovement.objects(
            organization=organization,
            inventory=inventory,
        ).order_by("-created_at")

    @staticmethod
    def list_by_product(
        *,
        organization,
        product,
    ):
        return StockMovement.objects(
            organization=organization,
            product=product,
        ).order_by("-created_at")

    @staticmethod
    def list_by_warehouse(
        *,
        organization,
        warehouse,
    ):
        return StockMovement.objects(
            organization=organization,
            warehouse=warehouse,
        ).order_by("-created_at")

    @staticmethod
    def list_by_type(
        *,
        organization,
        movement_type,
    ):
        return StockMovement.objects(
            organization=organization,
            movement_type=movement_type,
        ).order_by("-created_at")