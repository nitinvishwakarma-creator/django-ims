from django.urls import (
    path,
)

from apps.sales.api.v1 import (
    views,
)


app_name = "sales_api_v1"


urlpatterns = [
    path(
        "customers/",
        views.customer_collection_api,
        name="customer_collection",
    ),

    path(
        (
            "customers/"
            "<str:customer_id>/activate/"
        ),
        views.customer_activate_api,
        name="customer_activate",
    ),

    path(
        (
            "customers/"
            "<str:customer_id>/deactivate/"
        ),
        views.customer_deactivate_api,
        name="customer_deactivate",
    ),

    path(
        "customers/<str:customer_id>/",
        views.customer_detail_api,
        name="customer_detail",
    ),
    path(
        "sales-orders/",
        views.sales_order_collection_api,
        name="sales_order_collection",
    ),

    path(
        (
            "sales-orders/"
            "<str:sales_order_id>/confirm/"
        ),
        views.sales_order_confirm_api,
        name="sales_order_confirm",
    ),

    path(
        (
            "sales-orders/"
            "<str:sales_order_id>/cancel/"
        ),
        views.sales_order_cancel_api,
        name="sales_order_cancel",
    ),

    path(
        (
            "sales-orders/"
            "<str:sales_order_id>/fulfill/"
        ),
        views.sales_order_fulfill_api,
        name="sales_order_fulfill",
    ),

    path(
        (
            "sales-orders/"
            "<str:sales_order_id>/"
        ),
        views.sales_order_detail_api,
        name="sales_order_detail",
    ),
]