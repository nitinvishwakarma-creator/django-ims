from apps.inventory.models import Warehouse
from datetime import datetime

class WarehouseRepository:

    @staticmethod
    def get_by_id(*, organization, warehouse_id):
        """
        Retrieve a warehouse by ID within an organization.
        """

        return Warehouse.objects(
            organization=organization,
            id=warehouse_id,
        ).first()

    @staticmethod
    def get_by_code(*, organization, code):
        """
        Retrieve a warehouse by code within an organization.
        """

        return Warehouse.objects(
            organization=organization,
            code=code,
        ).first()

    @staticmethod
    def get_by_name(*, organization, name):
        """
        Retrieve a warehouse by name within an organization.
        """

        return Warehouse.objects(
            organization=organization,
            name=name,
        ).first()

    @staticmethod
    def list_by_organization(*, organization):
        """
        Return all warehouses belonging to an organization.
        """

        return Warehouse.objects(
            organization=organization,
        ).order_by("-created_at")

    @staticmethod
    def list_active(*, organization):
        """
        Return active warehouses belonging to an organization.
        """

        return Warehouse.objects(
            organization=organization,
            is_active=True,
        ).order_by("-created_at")

    @staticmethod
    def update_warehouse(
        *,
        warehouse,
        name,
        code,
        address="",
        city="",
        state="",
        country="India",
        pincode="",
        is_active=True,
    ):
        """
        Update an existing warehouse.
        """

        warehouse.name = name
        warehouse.code = code
        warehouse.address = address
        warehouse.city = city
        warehouse.state = state
        warehouse.country = country
        warehouse.pincode = pincode
        warehouse.is_active = is_active

        warehouse.save()

        return warehouse

    @staticmethod
    def deactivate(*, organization, warehouse_id):
        """
        Deactivate a warehouse belonging to an organization.
        """

        warehouse = Warehouse.objects(
            organization=organization,
            id=warehouse_id,
        ).first()

        if not warehouse:
            return None

        warehouse.is_active = False
        warehouse.updated_at = datetime.utcnow()
        warehouse.save()

        return warehouse


    @staticmethod
    def activate(*, organization, warehouse_id):
        """
        Activate a warehouse belonging to an organization.
        """

        warehouse = Warehouse.objects(
            organization=organization,
            id=warehouse_id,
        ).first()

        if not warehouse:
            return None

        warehouse.is_active = True
        warehouse.updated_at = datetime.utcnow()
        warehouse.save()

        return warehouse