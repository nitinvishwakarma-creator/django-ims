from apps.core.services.api_serialization_service import (
    APISerializationService,
)


class CustomerAPISerializer:

    @staticmethod
    def serialize_summary(
        customer,
    ):
        if not customer:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    customer.id
                )
            ),
            "code":
                customer.code,
            "name":
                customer.name,
            "email":
                (
                    customer.email
                    or
                    None
                ),
            "phone":
                (
                    customer.phone
                    or
                    None
                ),
            "gstin":
                (
                    customer.gstin
                    or
                    None
                ),
            "city":
                (
                    customer.city
                    or
                    None
                ),
            "state":
                (
                    customer.state
                    or
                    None
                ),
            "country":
                (
                    customer.country
                    or
                    None
                ),
            "is_active":
                bool(
                    customer.is_active
                ),
        }

    @staticmethod
    def serialize_detail(
        customer,
    ):
        if not customer:
            return None

        summary = (
            CustomerAPISerializer
            .serialize_summary(
                customer
            )
        )

        return {
            **summary,
            "billing_address":
                (
                    customer.billing_address
                    or
                    None
                ),
            "shipping_address":
                (
                    customer.shipping_address
                    or
                    None
                ),
            "pincode":
                (
                    customer.pincode
                    or
                    None
                ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    customer.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    customer.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_many(
        customers,
    ):
        return [
            (
                CustomerAPISerializer
                .serialize_summary(
                    customer
                )
            )
            for customer
            in customers
        ]