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

class PurchaseOrderAPISerializer:

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
            item.received_quantity
        )

        if remaining_quantity < 0:
            remaining_quantity = 0

        return {
            "product": (
                PurchaseOrderAPISerializer
                ._serialize_product(
                    item.product
                )
            ),
            "quantity":
                str(
                    item.quantity
                ),
            "received_quantity":
                str(
                    item.received_quantity
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
            "subtotal":
                str(
                    item.subtotal
                ),
            "tax_amount":
                str(
                    item.tax_amount
                ),
            "total":
                str(
                    item.total
                ),
        }

    @staticmethod
    def serialize_summary(
        purchase_order,
    ):
        if not purchase_order:
            return None

        return {
            "id": (
                APISerializationService
                .serialize_identifier(
                    purchase_order.id
                )
            ),
            "po_number":
                purchase_order.po_number,
            "supplier": (
                SupplierAPISerializer
                .serialize_summary(
                    purchase_order.supplier
                )
            ),
            "status":
                purchase_order.status,
            "order_date": (
                APISerializationService
                .serialize_date(
                    purchase_order.order_date
                )
            ),
            "expected_delivery_date": (
                APISerializationService
                .serialize_date(
                    (
                        purchase_order
                        .expected_delivery_date
                    )
                )
            ),
            "subtotal":
                str(
                    purchase_order.subtotal
                ),
            "tax_amount":
                str(
                    purchase_order.tax_amount
                ),
            "discount_amount":
                str(
                    purchase_order
                    .discount_amount
                ),
            "total_amount":
                str(
                    purchase_order.total_amount
                ),
            "item_count":
                len(
                    purchase_order.items
                    or
                    []
                ),
            "created_at": (
                APISerializationService
                .serialize_datetime(
                    purchase_order.created_at
                )
            ),
            "updated_at": (
                APISerializationService
                .serialize_datetime(
                    purchase_order.updated_at
                )
            ),
        }

    @staticmethod
    def serialize_detail(
        purchase_order,
    ):
        if not purchase_order:
            return None

        summary = (
            PurchaseOrderAPISerializer
            .serialize_summary(
                purchase_order
            )
        )

        return {
            **summary,
            "items": [
                (
                    PurchaseOrderAPISerializer
                    .serialize_item(
                        item
                    )
                )
                for item
                in (
                    purchase_order.items
                    or
                    []
                )
            ],
            "notes":
                (
                    purchase_order.notes
                    or
                    None
                ),
            "created_by": (
                PurchaseOrderAPISerializer
                ._serialize_created_by(
                    purchase_order.created_by
                )
            ),
            "confirmed_at": (
                APISerializationService
                .serialize_datetime(
                    purchase_order.confirmed_at
                )
            ),
            "cancelled_at": (
                APISerializationService
                .serialize_datetime(
                    purchase_order.cancelled_at
                )
            ),
        }

    @staticmethod
    def serialize_many(
        purchase_orders,
    ):
        return [
            (
                PurchaseOrderAPISerializer
                .serialize_summary(
                    purchase_order
                )
            )
            for purchase_order
            in purchase_orders
        ]