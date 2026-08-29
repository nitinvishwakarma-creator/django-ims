from django.urls import (
    path,
)

from apps.purchasing.api.v1 import (
    views,
)


app_name = "purchasing_api_v1"


urlpatterns = [
    path(
        "suppliers/",
        views.supplier_collection_api,
        name="supplier_collection",
    ),

    path(
        (
            "suppliers/"
            "<str:supplier_id>/activate/"
        ),
        views.supplier_activate_api,
        name="supplier_activate",
    ),

    path(
        (
            "suppliers/"
            "<str:supplier_id>/deactivate/"
        ),
        views.supplier_deactivate_api,
        name="supplier_deactivate",
    ),

    path(
        "suppliers/<str:supplier_id>/",
        views.supplier_detail_api,
        name="supplier_detail",
    ),
    path(
        "purchase-orders/",
        views.purchase_order_collection_api,
        name="purchase_order_collection",
    ),

    path(
        (
            "purchase-orders/"
            "<str:purchase_order_id>/"
            "confirm/"
        ),
        views.purchase_order_confirm_api,
        name="purchase_order_confirm",
    ),

    path(
        (
            "purchase-orders/"
            "<str:purchase_order_id>/"
            "cancel/"
        ),
        views.purchase_order_cancel_api,
        name="purchase_order_cancel",
    ),

    path(
        (
            "purchase-orders/"
            "<str:purchase_order_id>/"
        ),
        views.purchase_order_detail_api,
        name="purchase_order_detail",
    ),
]