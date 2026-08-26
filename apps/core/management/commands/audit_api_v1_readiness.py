from django.conf import settings
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.test import Client
from django.urls import (
    Resolver404,
    resolve,
)


class Command(
    BaseCommand
):

    help = (
        "Run the final Django IMS API v1 "
        "readiness audit."
    )

    def handle(
        self,
        *args,
        **options,
    ):
        passed = 0
        failed = 0

        def check(
            name,
            condition,
            detail=None,
        ):
            nonlocal passed
            nonlocal failed

            if condition:

                passed += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[PASS] {name}"
                    )
                )

            else:

                failed += 1

                message = (
                    f"[FAIL] {name}"
                )

                if detail:

                    message += (
                        f" — {detail}"
                    )

                self.stdout.write(
                    self.style.ERROR(
                        message
                    )
                )

        # ==================================================
        # SETTINGS
        # ==================================================

        check(
            "Session engine uses MongoDB",
            settings.SESSION_ENGINE
            ==
            (
                "apps.accounts."
                "session_backend"
            ),
        )

        check(
            "Session cookie has expected name",
            settings.SESSION_COOKIE_NAME
            ==
            "ims_sessionid",
        )

        check(
            "Session cookie is HttpOnly",
            settings.SESSION_COOKIE_HTTPONLY
            is True,
        )

        check(
            "CSRF cookie remains frontend-readable",
            settings.CSRF_COOKIE_HTTPONLY
            is False,
        )

        check(
            "Session and CSRF SameSite match",
            settings.SESSION_COOKIE_SAMESITE
            ==
            settings.CSRF_COOKIE_SAMESITE,
        )

        check(
            "Credentialed CORS enabled",
            settings.CORS_ALLOW_CREDENTIALS
            is True,
        )

        check(
            "Wildcard CORS disabled",
            settings.CORS_ALLOW_ALL_ORIGINS
            is False,
        )

        check(
            "Internal API test routes disabled",
            settings
            .ENABLE_INTERNAL_API_TEST_ENDPOINTS
            is False,
        )

        if settings.IS_PRODUCTION:

            check(
                "Production DEBUG disabled",
                settings.DEBUG
                is False,
            )

            check(
                "Production session cookie secure",
                settings.SESSION_COOKIE_SECURE
                is True,
            )

            check(
                "Production CSRF cookie secure",
                settings.CSRF_COOKIE_SECURE
                is True,
            )

            check(
                "Production wildcard hosts rejected",
                "*"
                not in settings.ALLOWED_HOSTS,
            )

        # ==================================================
        # MIDDLEWARE ORDER
        # ==================================================

        middleware = list(
            settings.MIDDLEWARE
        )

        required_middleware = [
            (
                "django.contrib.sessions."
                "middleware.SessionMiddleware"
            ),
            (
                "django.middleware.csrf."
                "CsrfViewMiddleware"
            ),
            (
                "django.contrib.auth."
                "middleware.AuthenticationMiddleware"
            ),
            (
                "apps.accounts.middleware."
                "MongoAuthenticationMiddleware"
            ),
            (
                "apps.core.middleware."
                "request_id_middleware."
                "RequestIDMiddleware"
            ),
            (
                "apps.core.middleware."
                "exception_logging_middleware."
                "ExceptionLoggingMiddleware"
            ),
            (
                "apps.core.middleware."
                "request_logging_middleware."
                "RequestLoggingMiddleware"
            ),
        ]

        all_middleware_present = all(
            middleware_name
            in middleware
            for middleware_name
            in required_middleware
        )

        check(
            "Required middleware present",
            all_middleware_present,
        )

        if all_middleware_present:

            indexes = {
                middleware_name:
                    middleware.index(
                        middleware_name
                    )
                for middleware_name
                in required_middleware
            }

            check(
                "Session runs before CSRF",
                indexes[
                    required_middleware[
                        0
                    ]
                ]
                <
                indexes[
                    required_middleware[
                        1
                    ]
                ],
            )

            check(
                "Django auth runs before Mongo auth",
                indexes[
                    required_middleware[
                        2
                    ]
                ]
                <
                indexes[
                    required_middleware[
                        3
                    ]
                ],
            )

            check(
                (
                    "Request ID runs before "
                    "exception/request logging"
                ),
                (
                    indexes[
                        required_middleware[
                            4
                        ]
                    ]
                    <
                    indexes[
                        required_middleware[
                            5
                        ]
                    ]
                    <
                    indexes[
                        required_middleware[
                            6
                        ]
                    ]
                ),
            )

        # ==================================================
        # ROUTE EXPOSURE
        # ==================================================

        def route_exists(
            path,
        ):
            try:

                resolve(
                    path
                )

                return True

            except Resolver404:

                return False

        check(
            "API root route available",
            route_exists(
                "/api/v1/"
            ),
        )

        check(
            "Authentication root available",
            route_exists(
                "/api/v1/auth/"
            ),
        )

        check(
            "CSRF route available",
            route_exists(
                "/api/v1/auth/csrf/"
            ),
        )

        check(
            "Login route available",
            route_exists(
                "/api/v1/auth/login/"
            ),
        )

        check(
            "Logout route available",
            route_exists(
                "/api/v1/auth/logout/"
            ),
        )

        check(
            "Current-user route available",
            route_exists(
                "/api/v1/auth/me/"
            ),
        )
        check(
            "Logout-all route available",
            route_exists(
                "/api/v1/auth/logout-all/"
            ),
        )

        check(
            "Organization route available",
            route_exists(
                "/api/v1/organization/"
            ),
        )

        check(
            "Users collection route available",
            route_exists(
                "/api/v1/users/"
            ),
        )

        check(
            "User detail route available",
            route_exists(
                "/api/v1/users/audit-user-id/"
            ),
        )

        check(
            "User activation route available",
            route_exists(
                (
                    "/api/v1/users/"
                    "audit-user-id/activate/"
                )
            ),
        )

        check(
            "User deactivation route available",
            route_exists(
                (
                    "/api/v1/users/"
                    "audit-user-id/deactivate/"
                )
            ),
        )

        check(
            "Category-list route available",
            route_exists(
                "/api/v1/categories/"
            ),
        )

        check(
            "Product collection route available",
            route_exists(
                "/api/v1/products/"
            ),
        )

        check(
            "Product detail route available",
            route_exists(
                (
                    "/api/v1/products/"
                    "audit-product-id/"
                )
            ),
        )

        check(
            "Product activation route available",
            route_exists(
                (
                    "/api/v1/products/"
                    "audit-product-id/activate/"
                )
            ),
        )

        check(
            "Product deactivation route available",
            route_exists(
                (
                    "/api/v1/products/"
                    "audit-product-id/deactivate/"
                )
            ),
        )

        check(
            "Warehouse collection route available",
            route_exists(
                "/api/v1/warehouses/"
            ),
        )

        check(
            "Warehouse detail route available",
            route_exists(
                (
                    "/api/v1/warehouses/"
                    "audit-warehouse-id/"
                )
            ),
        )

        check(
            "Warehouse activation route available",
            route_exists(
                (
                    "/api/v1/warehouses/"
                    "audit-warehouse-id/activate/"
                )
            ),
        )

        check(
            "Warehouse deactivation route available",
            route_exists(
                (
                    "/api/v1/warehouses/"
                    "audit-warehouse-id/deactivate/"
                )
            ),
        )

        check(
            "Inventory collection route available",
            route_exists(
                "/api/v1/inventory/"
            ),
        )

        check(
            "Inventory detail route available",
            route_exists(
                (
                    "/api/v1/inventory/"
                    "audit-inventory-id/"
                )
            ),
        )

        check(
            "Inventory adjustment route available",
            route_exists(
                (
                    "/api/v1/inventory/"
                    "audit-inventory-id/adjust/"
                )
            ),
        )

        check(
            "Stock movement collection route available",
            route_exists(
                "/api/v1/stock-movements/"
            ),
        )

        check(
            "Stock movement detail route available",
            route_exists(
                (
                    "/api/v1/stock-movements/"
                    "audit-movement-id/"
                )
            ),
        )

        check(
            "Stock transfer collection route available",
            route_exists(
                "/api/v1/stock-transfers/"
            ),
        )

        check(
            "Stock transfer detail route available",
            route_exists(
                (
                    "/api/v1/stock-transfers/"
                    "audit-transfer-id/"
                )
            ),
        )

        check(
            "Permission-list route available",
            route_exists(
                "/api/v1/permissions/"
            ),
        )

        check(
            "Role collection route available",
            route_exists(
                "/api/v1/roles/"
            ),
        )

        check(
            "Role detail route available",
            route_exists(
                "/api/v1/roles/audit-role-id/"
            ),
        )

        check(
            (
                "Role permission-assignment "
                "route available"
            ),
            route_exists(
                (
                    "/api/v1/roles/"
                    "audit-role-id/permissions/"
                )
            ),
        )

        check(
            "Role activation route available",
            route_exists(
                (
                    "/api/v1/roles/"
                    "audit-role-id/activate/"
                )
            ),
        )

        check(
            "Role deactivation route available",
            route_exists(
                (
                    "/api/v1/roles/"
                    "audit-role-id/deactivate/"
                )
            ),
        )

        check(
            "Internal contract routes hidden",
            not route_exists(
                (
                    "/api/v1/_tests/"
                    "contract/success/"
                )
            ),
        )

        check(
            "Authorization probe hidden",
            not route_exists(
                (
                    "/api/v1/auth/"
                    "authorization-probe/"
                )
            ),
        )

        # ==================================================
        # HTTP CONTRACT
        # ==================================================

        host = (
            settings.ALLOWED_HOSTS[
                0
            ]
            if settings.ALLOWED_HOSTS
            else "testserver"
        )

        if host.startswith(
            "."
        ):

            host = host[
                1:
            ]

        client = Client(
            raise_request_exception=False,
        )

        request_options = {
            "HTTP_HOST":
                host,
        }

        if settings.IS_PRODUCTION:

            request_options[
                "secure"
            ] = True

        api_response = client.get(
            "/api/v1/",
            **request_options,
        )

        check(
            "API root returns 200",
            api_response.status_code
            ==
            200,
            detail=(
                f"status="
                f"{api_response.status_code}"
            ),
        )

        if (
            api_response.status_code
            ==
            200
        ):

            api_body = (
                api_response.json()
            )

            header_request_id = (
                api_response.headers.get(
                    "X-Request-ID"
                )
            )

            check(
                "API response contract succeeds",
                api_body.get(
                    "success"
                )
                is True,
            )

            check(
                "Request ID header/body match",
                bool(
                    header_request_id
                )
                and
                header_request_id
                ==
                api_body.get(
                    "request_id"
                ),
            )

            check(
                "API metadata version is v1",
                api_body.get(
                    "meta",
                    {},
                ).get(
                    "api_version"
                )
                ==
                "v1",
            )

            check(
                "API responses disable caching",
                api_response.headers.get(
                    "Cache-Control"
                )
                ==
                "no-store",
            )

            serialized_manifest = str(
                api_body.get(
                    "data",
                    {}
                )
            )

            check(
                "Discovery hides internal routes",
                "_tests"
                not in serialized_manifest,
            )

            check(
                "Discovery hides authorization probe",
                "authorization-probe"
                not in serialized_manifest,
            )

            manifest_endpoints = (
                api_body.get(
                    "data",
                    {},
                )
                .get(
                    "endpoints",
                    {},
                )
            )

            organization_endpoints = (
                manifest_endpoints.get(
                    "organization",
                    {},
                )
            )

            user_endpoints = (
                manifest_endpoints.get(
                    "users",
                    {},
                )
            )

            category_endpoints = (
                manifest_endpoints.get(
                    "categories",
                    {},
                )
            )

            product_endpoints = (
                manifest_endpoints.get(
                    "products",
                    {},
                )
            )

            warehouse_endpoints = (
                manifest_endpoints.get(
                    "warehouses",
                    {},
                )
            )

            inventory_endpoints = (
                manifest_endpoints.get(
                    "inventory",
                    {},
                )
            )

            movement_endpoints = (
                manifest_endpoints.get(
                    "stock_movements",
                    {},
                )
            )

            transfer_endpoints = (
                manifest_endpoints.get(
                    "stock_transfers",
                    {},
                )
            )
            check(
                (
                    "Discovery exposes current "
                    "organization endpoint"
                ),
                (
                    organization_endpoints
                    .get(
                        "current",
                        {},
                    )
                    .get(
                        "path"
                    )
                    ==
                    "/api/v1/organization/"
                    and
                    organization_endpoints
                    .get(
                        "current",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                ),
            )

            check(
                (
                    "Discovery exposes user "
                    "management endpoints"
                ),


                (
                    user_endpoints
                    .get(
                        "list",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    user_endpoints
                    .get(
                        "detail",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    user_endpoints
                    .get(
                        "activate",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    user_endpoints
                    .get(
                        "deactivate",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                ),
            )

            check(
                (
                    "Discovery exposes product "
                    "category endpoint"
                ),
                (
                    category_endpoints
                    .get(
                        "list",
                        {},
                    )
                    .get(
                        "path"
                    )
                    ==
                    "/api/v1/categories/"
                    and
                    category_endpoints
                    .get(
                        "list",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                ),
            )

            check(
                (
                    "Discovery exposes product "
                    "management endpoints"
                ),
                (
                    product_endpoints
                    .get(
                        "collection",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    product_endpoints
                    .get(
                        "detail",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    product_endpoints
                    .get(
                        "activate",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    product_endpoints
                    .get(
                        "deactivate",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    product_endpoints
                    .get(
                        "collection",
                        {},
                    )
                    .get(
                        "path"
                    )
                    ==
                    "/api/v1/products/"
                ),
            )
            check(
                (
                    "Discovery exposes warehouse "
                    "management endpoints"
                ),
                (
                    warehouse_endpoints
                    .get(
                        "collection",
                        {},
                    )
                    .get(
                        "path"
                    )
                    ==
                    "/api/v1/warehouses/"
                    and
                    warehouse_endpoints
                    .get(
                        "detail",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    warehouse_endpoints
                    .get(
                        "activate",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    warehouse_endpoints
                    .get(
                        "deactivate",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                ),
            )

            check(
                (
                    "Discovery exposes inventory "
                    "balance endpoints"
                ),
                (
                    inventory_endpoints
                    .get(
                        "collection",
                        {},
                    )
                    .get(
                        "path"
                    )
                    ==
                    "/api/v1/inventory/"
                    and
                    inventory_endpoints
                    .get(
                        "detail",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                    and
                    inventory_endpoints
                    .get(
                        "adjust",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                ),
            )

            check(
                (
                    "Discovery exposes immutable "
                    "stock movement endpoints"
                ),
                (
                    movement_endpoints
                    .get(
                        "collection",
                        {},
                    )
                    .get(
                        "path"
                    )
                    ==
                    "/api/v1/stock-movements/"
                    and
                    movement_endpoints
                    .get(
                        "collection",
                        {},
                    )
                    .get(
                        "immutable"
                    )
                    is True
                    and
                    movement_endpoints
                    .get(
                        "detail",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                ),
            )

            check(
                (
                    "Discovery exposes stock "
                    "transfer endpoints"
                ),
                (
                    transfer_endpoints
                    .get(
                        "collection",
                        {},
                    )
                    .get(
                        "path"
                    )
                    ==
                    "/api/v1/stock-transfers/"
                    and
                    transfer_endpoints
                    .get(
                        "detail",
                        {},
                    )
                    .get(
                        "status"
                    )
                    ==
                    "available"
                ),
            )
            check(
                "Users remain inside endpoints",
                (
                    "users"
                    in manifest_endpoints
                    and
                    "users"
                    not in api_body.get(
                        "data",
                        {},
                    )
                ),
            )

            authorization_endpoints = (
                manifest_endpoints.get(
                    "authorization",
                    {},
                )
            )

            required_authorization_endpoints = {
                "permissions",
                "roles",
                "role_detail",
                "role_permissions",
                "role_activate",
                "role_deactivate",
            }

            check(
                (
                    "Discovery exposes authorization "
                    "management endpoints"
                ),
                (
                    required_authorization_endpoints
                    <=
                    set(
                        authorization_endpoints
                    )
                    and
                    all(
                        authorization_endpoints[
                            endpoint_name
                        ].get(
                            "status"
                        )
                        ==
                        "available"

                        for endpoint_name
                        in (
                            required_authorization_endpoints
                        )
                    )
                ),
            )

            check(
                (
                    "Discovery documents protected "
                    "system-role operations"
                ),
                (
                    authorization_endpoints
                    .get(
                        "role_permissions",
                        {},
                    )
                    .get(
                        "system_roles_protected"
                    )
                    is True
                    and
                    authorization_endpoints
                    .get(
                        "role_deactivate",
                        {},
                    )
                    .get(
                        "system_roles_protected"
                    )
                    is True
                    and
                    authorization_endpoints
                    .get(
                        "role_deactivate",
                        {},
                    )
                    .get(
                        "assigned_user_protection"
                    )
                    is True
                ),
            )

        auth_response = client.get(
            "/api/v1/auth/",
            **request_options,
        )

        check(
            "Authentication discovery returns 200",
            auth_response.status_code
            ==
            200,
        )

        csrf_client = Client(
            enforce_csrf_checks=True,
            raise_request_exception=False,
        )

        csrf_response = csrf_client.get(
            "/api/v1/auth/csrf/",
            **request_options,
        )

        check(
            "CSRF bootstrap returns 200",
            csrf_response.status_code
            ==
            200,
        )

        check(
            "CSRF cookie issued",
            settings.CSRF_COOKIE_NAME
            in csrf_client.cookies,
        )

        csrf_failure_response = (
            csrf_client.post(
                "/api/v1/auth/login/",
                data=(
                    '{"email":"audit@example.com",'
                    '"password":"not-sent"}'
                ),
                content_type=(
                    "application/json"
                ),
                **request_options,
            )
        )

        check(
            "Unsafe request without token rejected",
            csrf_failure_response.status_code
            ==
            403,
        )

        try:

            csrf_failure_code = (
                csrf_failure_response.json()
                [
                    "error"
                ][
                    "code"
                ]
            )

        except Exception:

            csrf_failure_code = None

        check(
            "CSRF failure uses API contract",
            csrf_failure_code
            ==
            "CSRF_FAILED",
        )

        anonymous_me = client.get(
            "/api/v1/auth/me/",
            **request_options,
        )

        check(
            "Anonymous current-user request rejected",
            anonymous_me.status_code
            ==
            401,
        )

        try:

            anonymous_code = (
                anonymous_me.json()
                [
                    "error"
                ][
                    "code"
                ]
            )

        except Exception:

            anonymous_code = None

        check(
            "Anonymous error uses API contract",
            anonymous_code
            ==
            "UNAUTHORIZED",
        )

        anonymous_organization = client.get(
            "/api/v1/organization/",
            **request_options,
        )

        check(
            (
                "Anonymous organization request "
                "rejected"
            ),
            anonymous_organization.status_code
            ==
            401,
        )

        try:

            anonymous_organization_code = (
                anonymous_organization.json()
                [
                    "error"
                ][
                    "code"
                ]
            )

        except Exception:

            anonymous_organization_code = None

        check(
            (
                "Anonymous organization error "
                "uses API contract"
            ),
            anonymous_organization_code
            ==
            "UNAUTHORIZED",
        )

        anonymous_users = client.get(
            "/api/v1/users/",
            **request_options,
        )

        check(
            "Anonymous users request rejected",
            anonymous_users.status_code
            ==
            401,
        )

        try:

            anonymous_users_code = (
                anonymous_users.json()
                [
                    "error"
                ][
                    "code"
                ]
            )

        except Exception:

            anonymous_users_code = None

        check(
            (
                "Anonymous users error uses "
                "API contract"
            ),
            anonymous_users_code
            ==
            "UNAUTHORIZED",
        )

        anonymous_permissions = client.get(
            "/api/v1/permissions/",
            **request_options,
        )

        check(
            (
                "Anonymous permission request "
                "rejected"
            ),
            anonymous_permissions.status_code
            ==
            401,
        )

        try:
            anonymous_permissions_code = (
                anonymous_permissions.json()
                [
                    "error"
                ][
                    "code"
                ]
            )

        except Exception:
            anonymous_permissions_code = None

        check(
            (
                "Anonymous permission error "
                "uses API contract"
            ),
            anonymous_permissions_code
            ==
            "UNAUTHORIZED",
        )

        anonymous_roles = client.get(
            "/api/v1/roles/",
            **request_options,
        )

        check(
            "Anonymous role request rejected",
            anonymous_roles.status_code
            ==
            401,
        )

        try:
            anonymous_roles_code = (
                anonymous_roles.json()
                [
                    "error"
                ][
                    "code"
                ]
            )

        except Exception:
            anonymous_roles_code = None

        check(
            (
                "Anonymous role error uses "
                "API contract"
            ),
            anonymous_roles_code
            ==
            "UNAUTHORIZED",
        )
        # ==================================================
        # SUMMARY
        # ==================================================

        total = (
            passed
            +
            failed
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            (
                "API v1 readiness summary: "
                f"{passed}/{total} passed, "
                f"{failed} failed."
            )
        )

        if failed:

            raise CommandError(
                (
                    "API v1 readiness audit "
                    "failed."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "API v1 readiness audit "
                    "passed."
                )
            )
        )