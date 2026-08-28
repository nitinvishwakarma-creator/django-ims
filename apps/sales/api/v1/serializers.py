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

class SalesOrderAPISerializer:

    @staticmethod
    def _serialize_warehouse(
        warehouse,
    ):
        if not warehouse:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    warehouse.id
                )
            ),
            "code":
                warehouse.code,
            "name":
                warehouse.name,
            "city":
                (
                    warehouse.city
                    or
                    None
                ),
            "is_active":
                bool(
                    warehouse.is_active
                ),
        }

    @staticmethod
    def _serialize_product(
        product,
    ):
        if not product:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    product.id
                )
            ),
            "sku":
                product.sku,
            "name":
                product.name,
            "unit":
                product.unit,
            "is_active":
                bool(
                    product.is_active
                ),
        }

    @staticmethod
    def _serialize_created_by(
        user,
    ):
        if not user:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    user.id
                )
            ),
            "email":
                user.email,
            "first_name":
                user.first_name,
            "last_name":
                user.last_name,
        }

    @staticmethod
    def serialize_item(
        item,
    ):
        if not item:
            return None

        remaining_quantity = (
            item.quantity
            -
            item.fulfilled_quantity
        )

        return {
            "product": (
                SalesOrderAPISerializer
                ._serialize_product(
                    item.product
                )
            ),
            "quantity":
                str(
                    item.quantity
                ),
            "fulfilled_quantity":
                str(
                    item.fulfilled_quantity
                ),
            "remaining_quantity":
                str(
                    remaining_quantity
                ),
            "unit_price":
                str(
                    item.unit_price
                ),
            "tax_rate":
                str(
                    item.tax_rate
                ),
            "discount":
                str(
                    item.discount
                ),
            "line_subtotal":
                str(
                    item.line_subtotal
                ),
            "line_tax":
                str(
                    item.line_tax
                ),
            "line_total":
                str(
                    item.line_total
                ),
        }

    @staticmethod
    def serialize_summary(
        sales_order,
    ):
        if not sales_order:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    sales_order.id
                )
            ),
            "so_number":
                sales_order.so_number,
            "customer": (
                CustomerAPISerializer
                .serialize_summary(
                    sales_order.customer
                )
            ),
            "warehouse": (
                SalesOrderAPISerializer
                ._serialize_warehouse(
                    sales_order.warehouse
                )
            ),
            "status":
                sales_order.status,
            "order_date": (
                APISerializationService
                .serialize_datetime(
                    sales_order.order_date
                )
            ),
            "expected_delivery_date": (
                APISerializationService
                .serialize_datetime(
                    sales_order
                    .expected_delivery_date
                )
            ),
            "subtotal":
                str(
                    sales_order.subtotal
                ),
            "tax_amount":
                str(
                    sales_order.tax_amount
                ),
            "discount_amount":
                str(
                    sales_order
                    .discount_amount
                ),
            "total_amount":
                str(
                    sales_order.total_amount
                ),
            "item_count":
                len(
                    sales_order.items
                    or
                    []
                ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    sales_order.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    sales_order.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_detail(
        sales_order,
    ):
        if not sales_order:
            return None

        summary = (
            SalesOrderAPISerializer
            .serialize_summary(
                sales_order
            )
        )

        return {
            **summary,
            "items": [
                (
                    SalesOrderAPISerializer
                    .serialize_item(
                        item
                    )
                )
                for item
                in (
                    sales_order.items
                    or
                    []
                )
            ],
            "notes":
                (
                    sales_order.notes
                    or
                    None
                ),
            "created_by": (
                SalesOrderAPISerializer
                ._serialize_created_by(
                    sales_order.created_by
                )
            ),
            "confirmed_at": (
                APISerializationService
                .serialize_datetime(
                    sales_order.confirmed_at
                )
            ),
            "fulfilled_at": (
                APISerializationService
                .serialize_datetime(
                    sales_order.fulfilled_at
                )
            ),
            "cancelled_at": (
                APISerializationService
                .serialize_datetime(
                    sales_order.cancelled_at
                )
            ),
        }

    @staticmethod
    def serialize_many(
        sales_orders,
    ):
        return [
            (
                SalesOrderAPISerializer
                .serialize_summary(
                    sales_order
                )
            )
            for sales_order
            in sales_orders
        ]