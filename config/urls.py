from django.contrib import admin
from django.urls import include, path
from apps.products.views import product_list, product_search, product_detail, product_create, product_deactivate, product_activate
from apps.core import error_handlers
from apps.accounts.views import (
    test_login,
    test_current_user,
    test_logout,
    test_protected,
    test_product_create_permission,
    test_tenant_access,
    test_logout_all_devices,
    authentication_audit_logs,
    test_unhandled_exception,
    test_mongodb_exception,
    test_slow_request
)
from apps.inventory.views import (
    warehouse_detail,
    warehouse_list,
    warehouse_create,
    warehouse_activate,
    warehouse_deactivate,
)

handler400 = (
    error_handlers.handler400
)

handler403 = (
    error_handlers.handler403
)

handler404 = (
    error_handlers.handler404
)

handler500 = (
    error_handlers.handler500
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("test-login/", test_login),
    path("test-logout/", test_logout),
    path("test-protected/", test_protected),
    path("test-current-user/",test_current_user),
    path("test-product-create/",test_product_create_permission),
    path("test-tenant/",test_tenant_access),
    path("products/",product_list,),
    path("products/search/",product_search),
    path("products/<str:product_id>/",product_detail),
    path("products/",product_create),
    path("products/<str:product_id>/deactivate/",product_deactivate),
    path("products/<str:product_id>/activate/",product_activate),
    path("warehouses/", warehouse_list),
    path("warehouses/create/", warehouse_create),
    path("warehouses/<str:warehouse_id>/", warehouse_detail),

    path(
        "warehouses/<str:warehouse_id>/deactivate/",
        warehouse_deactivate,
    ),
    path(
        "warehouses/<str:warehouse_id>/activate/",
        warehouse_activate,
    ),
    path(
        "inventory/",
        include("apps.inventory.urls"),
    ),
    path(
        "purchasing/",
        include("apps.purchasing.urls"),
    ),

    path(
        "sales/",
        include("apps.sales.urls"),
    ),
    path(
        "finance/",
        include(
            "apps.finance.urls"
        ),
    ),
    path(
        "test-logout-all/",test_logout_all_devices,name="test_logout_all_devices",
    ),
    path("accounts/authentication-audit-logs/",authentication_audit_logs,name="authentication_audit_logs",),
    path("test-unhandled-exception/",test_unhandled_exception,name="test_unhandled_exception",),
    path("test-mongodb-exception/",test_mongodb_exception,name="test_mongodb_exception",),
    path(
        "",
        include(
            "apps.core.urls"
        ),
    ),
    path(
        "test-slow-request/",test_slow_request,name="test_slow_request",
    ),
    path(
        "api/v1/",
        include(
            "apps.core.api.v1.urls"
        ),
    ),
]


