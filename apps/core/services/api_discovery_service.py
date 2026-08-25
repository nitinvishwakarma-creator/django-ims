from django.conf import settings

from apps.core.services.api_filtering_service import (
    APIFilteringService,
)
from apps.core.services.api_pagination_service import (
    APIPaginationService,
)
from apps.core.services.api_search_service import (
    APISearchService,
)
from apps.core.services.api_sorting_service import (
    APISortingService,
)
from apps.core.services.build_info_service import (
    BuildInfoService,
)


class APIDiscoveryService:

    API_NAME = "django-ims"
    API_VERSION = "v1"
    API_PREFIX = "/api/v1/"

    @staticmethod
    def get_authentication_endpoints():
        return {
            "csrf": {
                "method":
                    "GET",

                "path":
                    "/api/v1/auth/csrf/",

                "authentication_required":
                    False,

                "status":
                    "available",
            },
            "root": {
                "method":
                    "GET",

                "path":
                    "/api/v1/auth/",

                "authentication_required":
                    False,

                "status":
                    "available",
            },

            "login": {
                "method":
                    "POST",

                "path":
                    "/api/v1/auth/login/",

                "authentication_required":
                    False,

                "status":
                    "available",
            },

            "logout": {
                "method":
                    "POST",

                "path":
                    "/api/v1/auth/logout/",

                "authentication_required":
                    True,

                "status":
                    "available",
            },

            "current_user": {
                "method":
                    "GET",

                "path":
                    "/api/v1/auth/me/",

                "authentication_required":
                    True,

                "status":
                    "available",
            },

            "logout_all": {
                "method":
                    "POST",

                "path":
                    "/api/v1/auth/logout-all/",

                "authentication_required":
                    True,

                "status":
                    "available",
            },
        }

    @staticmethod
    def get_organization_endpoints():
        return {
            "current": {
                "methods": [
                    "GET",
                    "PATCH",
                ],

                "path":
                    "/api/v1/organization/",

                "authentication_required":
                    True,

                "tenant_scoped":
                    True,

                "update_permission":
                    "organizations.update",

                "status":
                    "available",
            },
        }
    
    @staticmethod
    def get_capabilities():
        return {
            "authentication": {
                "type":
                    "session",

                "cookie_name":
                    settings
                    .SESSION_COOKIE_NAME,

                "csrf_required_for_unsafe_methods":
                    True,

                "csrf_endpoint":
                    "/api/v1/auth/csrf/",

                "csrf_cookie_name":
                    settings
                    .CSRF_COOKIE_NAME,

                "csrf_header_name":
                    "X-CSRFToken",

                "unsafe_methods": [
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE",
                ],
            },

            "tenant_isolation": {
                "enabled":
                    True,

                "source":
                    "authenticated_session",

                "client_organization_id_trusted":
                    False,
            },

            "authorization": {
                "enabled":
                    True,

                "model":
                    "role_permissions",

                "default_policy":
                    "deny",
            },

            "pagination": {
                "enabled":
                    True,

                "page_parameter":
                    "page",

                "page_size_parameter":
                    "page_size",

                "default_page":
                    (
                        APIPaginationService
                        .DEFAULT_PAGE
                    ),

                "default_page_size":
                    (
                        APIPaginationService
                        .DEFAULT_PAGE_SIZE
                    ),

                "maximum_page_size":
                    (
                        APIPaginationService
                        .MAX_PAGE_SIZE
                    ),
            },

            "filtering": {
                "enabled":
                    True,

                "policy":
                    "endpoint_whitelist",

                "supported_lookups":
                    sorted(
                        APIFilteringService
                        .ALLOWED_LOOKUPS
                    ),
            },

            "search": {
                "enabled":
                    True,

                "parameter":
                    (
                        APISearchService
                        .DEFAULT_PARAMETER
                    ),

                "minimum_length":
                    (
                        APISearchService
                        .MIN_LENGTH
                    ),

                "maximum_length":
                    (
                        APISearchService
                        .MAX_LENGTH
                    ),

                "regex_input_escaped":
                    True,
            },

            "sorting": {
                "enabled":
                    True,

                "parameter":
                    "sort",

                "descending_prefix":
                    "-",

                "multiple_fields":
                    True,

                "maximum_fields":
                    (
                        APISortingService
                        .MAX_SORT_FIELDS
                    ),

                "stable_tiebreaker":
                    True,
            },

            "rate_limiting": {
                "enabled":
                    True,

                "response_status":
                    429,

                "headers": {
                    "limit":
                        "X-RateLimit-Limit",

                    "remaining":
                        "X-RateLimit-Remaining",

                    "reset":
                        "X-RateLimit-Reset",

                    "retry_after":
                        "Retry-After",
                },
            },

            "correlation": {
                "server_request_header":
                    "X-Request-ID",

                "client_request_header":
                    "X-Correlation-ID",

                "client_correlation_optional":
                    True,

                "client_request_id_trusted":
                    False,
            },

            "response_contract": {
                "success_field":
                    "success",

                "data_field":
                    "data",

                "error_field":
                    "error",

                "request_id_field":
                    "request_id",

                "metadata_field":
                    "meta",
            },
        }

    @staticmethod
    def get_manifest():
        build_info = (
            BuildInfoService
            .get_info()
        )

        return {
            "api": {
                "name":
                    (
                        APIDiscoveryService
                        .API_NAME
                    ),

                "version":
                    (
                        APIDiscoveryService
                        .API_VERSION
                    ),

                "prefix":
                    (
                        APIDiscoveryService
                        .API_PREFIX
                    ),

                "status":
                    "available",

                "application_version":
                    build_info.get(
                        "version"
                    ),
            },

            "endpoints": {
                "authentication":
                    (
                        APIDiscoveryService
                        .get_authentication_endpoints()
                    ),

                "organization":
                    (
                        APIDiscoveryService
                        .get_organization_endpoints()
                    ),

                "users":
                    (
                        APIDiscoveryService
                        .get_user_endpoints()
                    ),
            },

            "capabilities":
                (
                    APIDiscoveryService
                    .get_capabilities()
                ),
        }


    @staticmethod
    def get_user_endpoints():
        return {
            # ==================================================
            # USER COLLECTION
            # ==================================================

            "list": {
                "methods": [
                    "GET",
                    "POST",
                ],

                "path":
                    "/api/v1/users/",

                "authentication_required":
                    True,

                "tenant_scoped":
                    True,

                "permissions": {
                    "GET":
                        "users.read",

                    "POST":
                        "users.create",
                },

                "query_capabilities": [
                    "filtering",
                    "search",
                    "sorting",
                    "pagination",
                ],

                "status":
                    "available",
            },

            # ==================================================
            # USER DETAIL
            # ==================================================

            "detail": {
                "methods": [
                    "GET",
                    "PATCH",
                ],

                "path":
                    "/api/v1/users/{user_id}/",

                "authentication_required":
                    True,

                "tenant_scoped":
                    True,

                "permissions": {
                    "GET":
                        "users.read",

                    "PATCH":
                        "users.update",
                },

                "editable_fields": [
                    "email",
                    "first_name",
                    "last_name",
                    "role_id",
                ],

                "cross_tenant_behavior":
                    "not_found",

                "status":
                    "available",
            },

            "activate": {
                "method":
                    "POST",

                "path":
                    (
                        "/api/v1/users/"
                        "{user_id}/activate/"
                    ),

                "authentication_required":
                    True,

                "tenant_scoped":
                    True,

                "permission":
                    "users.activate",

                "idempotent":
                    True,

                "cross_tenant_behavior":
                    "not_found",

                "status":
                    "available",
            },
            
            "deactivate": {
                "method":
                    "POST",

                "path":
                    (
                        "/api/v1/users/"
                        "{user_id}/deactivate/"
                    ),

                "authentication_required":
                    True,

                "tenant_scoped":
                    True,

                "permission":
                    "users.deactivate",

                "idempotent":
                    True,

                "self_operation_allowed":
                    False,

                "revokes_sessions":
                    True,

                "last_active_admin_protected":
                    True,

                "cross_tenant_behavior":
                    "not_found",

                "status":
                    "available",
            },
        }