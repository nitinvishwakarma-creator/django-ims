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
]