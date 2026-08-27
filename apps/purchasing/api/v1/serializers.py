from apps.core.services.api_serialization_service import (
    APISerializationService,
)


class SupplierAPISerializer:

    @staticmethod
    def serialize_summary(
        supplier,
    ):
        if not supplier:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    supplier.id
                )
            ),
            "code":
                supplier.code,
            "name":
                supplier.name,
            "email":
                (
                    supplier.email
                    or
                    None
                ),
            "phone":
                (
                    supplier.phone
                    or
                    None
                ),
            "gstin":
                (
                    supplier.gstin
                    or
                    None
                ),
            "city":
                (
                    supplier.city
                    or
                    None
                ),
            "state":
                (
                    supplier.state
                    or
                    None
                ),
            "country":
                (
                    supplier.country
                    or
                    None
                ),
            "is_active":
                bool(
                    supplier.is_active
                ),
        }

    @staticmethod
    def serialize_detail(
        supplier,
    ):
        if not supplier:
            return None

        summary = (
            SupplierAPISerializer
            .serialize_summary(
                supplier
            )
        )

        return {
            **summary,
            "address":
                (
                    supplier.address
                    or
                    None
                ),
            "pincode":
                (
                    supplier.pincode
                    or
                    None
                ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    supplier.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    supplier.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_many(
        suppliers,
    ):
        return [
            (
                SupplierAPISerializer
                .serialize_summary(
                    supplier
                )
            )
            for supplier
            in suppliers
        ]