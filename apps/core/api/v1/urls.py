from django.conf import settings
from django.urls import (
    include,
    path,
)

from apps.core.api.v1 import views


app_name = "api_v1"


urlpatterns = [
    path(
        "",
        views.api_root,
        name="root",
    ),

    path(
        "auth/",
        include(
            "apps.accounts.api.v1.urls"
        ),
    ),

    path(
        "organization/",
        include(
            "apps.organizations.api.v1.urls"
        ),
    ),

    path(
        "",
        include(
            "apps.authorization.api.v1.urls"
        ),
    ),
    
    path(
        "users/",
        include(
            "apps.accounts.api.v1.user_urls"
        ),
    ),

    path(
        "",
        include(
            "apps.products.api.v1.urls"
        ),
    ),
]

# ==================================================
# INTERNAL AUTOMATED-TEST ROUTES
#
# These routes are:
# - automatically enabled by manage.py test
# - disabled during normal development by default
# - always disabled in production
# ==================================================

if (
    settings
    .ENABLE_INTERNAL_API_TEST_ENDPOINTS
):

    from apps.core.api.v1 import (
        test_views,
    )

    urlpatterns += [
        # ==============================================
        # RESPONSE CONTRACT
        # ==============================================

        path(
            "_tests/contract/success/",
            (
                test_views
                .test_contract_success
            ),
            name="test_contract_success",
        ),

        path(
            "_tests/contract/validation/",
            (
                test_views
                .test_contract_validation
            ),
            name="test_contract_validation",
        ),

        path(
            "_tests/contract/conflict/",
            (
                test_views
                .test_contract_conflict
            ),
            name="test_contract_conflict",
        ),

        path(
            "_tests/contract/unprocessable/",
            (
                test_views
                .test_contract_unprocessable
            ),
            name="test_contract_unprocessable",
        ),

        # ==============================================
        # EXCEPTION NORMALIZATION
        # ==============================================

        path(
            "_tests/exceptions/validation/",
            (
                test_views
                .test_exception_validation
            ),
            name="test_exception_validation",
        ),

        path(
            "_tests/exceptions/not-found/",
            (
                test_views
                .test_exception_not_found
            ),
            name="test_exception_not_found",
        ),

        path(
            "_tests/exceptions/conflict/",
            (
                test_views
                .test_exception_conflict
            ),
            name="test_exception_conflict",
        ),

        path(
            "_tests/exceptions/business-rule/",
            (
                test_views
                .test_exception_business_rule
            ),
            name="test_exception_business_rule",
        ),

        path(
            "_tests/exceptions/mongodb/",
            (
                test_views
                .test_exception_mongodb
            ),
            name="test_exception_mongodb",
        ),

        path(
            "_tests/exceptions/unexpected/",
            (
                test_views
                .test_exception_unexpected
            ),
            name="test_exception_unexpected",
        ),
    ]