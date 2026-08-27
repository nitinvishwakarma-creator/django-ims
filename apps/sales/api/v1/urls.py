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
]