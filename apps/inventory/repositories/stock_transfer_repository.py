from apps.inventory.models import StockTransfer


class StockTransferRepository:

    @staticmethod
    def create_transfer(
        *,
        organization,
        transfer_number,
        product,
        source_warehouse,
        destination_warehouse,
        source_inventory,
        destination_inventory,
        quantity,
        status,
        notes,
        created_by,
        completed_at=None,
    ):
        """
        Create a stock transfer record.
        """

        transfer = StockTransfer(
            organization=organization,
            transfer_number=transfer_number,
            product=product,
            source_warehouse=source_warehouse,
            destination_warehouse=destination_warehouse,
            source_inventory=source_inventory,
            destination_inventory=destination_inventory,
            quantity=quantity,
            status=status,
            notes=notes,
            created_by=created_by,
            completed_at=completed_at,
        )

        transfer.save()

        return transfer

    @staticmethod
    def get_by_id(
        *,
        organization,
        transfer_id,
    ):
        return StockTransfer.objects(
            organization=organization,
            id=transfer_id,
        ).first()

    @staticmethod
    def get_by_transfer_number(
        *,
        organization,
        transfer_number,
    ):
        return StockTransfer.objects(
            organization=organization,
            transfer_number=transfer_number,
        ).first()

    @staticmethod
    def list_by_organization(
        *,
        organization,
    ):
        return StockTransfer.objects(
            organization=organization,
        ).order_by("-created_at")

    @staticmethod
    def list_by_product(
        *,
        organization,
        product,
    ):
        return StockTransfer.objects(
            organization=organization,
            product=product,
        ).order_by("-created_at")

    @staticmethod
    def list_by_source_warehouse(
        *,
        organization,
        warehouse,
    ):
        return StockTransfer.objects(
            organization=organization,
            source_warehouse=warehouse,
        ).order_by("-created_at")

    @staticmethod
    def list_by_destination_warehouse(
        *,
        organization,
        warehouse,
    ):
        return StockTransfer.objects(
            organization=organization,
            destination_warehouse=warehouse,
        ).order_by("-created_at")

    @staticmethod
    def list_by_status(
        *,
        organization,
        status,
    ):
        return StockTransfer.objects(
            organization=organization,
            status=status,
        ).order_by("-created_at")

    @staticmethod
    def update_status(
        *,
        transfer,
        status,
        completed_at=None,
    ):
        transfer.status = status
        transfer.completed_at = completed_at
        transfer.save()

        return transfer