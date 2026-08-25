import json

from django.contrib.auth import authenticate

from apps.accounts.login_rate_limit_service import (
    LoginRateLimitService,
)
from apps.accounts.services import (
    AuthenticationService,
)

from apps.core.services.api_response_service import (
    APIResponseService,
)

from apps.organizations.api_context_service import (
    APIOrganizationContextService,
)
from apps.authorization.api_context_service import (
    APIPermissionContextService,
)
from apps.core.api.decorators import (
    api_login_required,

)
from apps.accounts.api.v1.serializers import (
    AccountAPISerializer,
)

from apps.core.services.api_discovery_service import (
    APIDiscoveryService,
)
from django.middleware.csrf import (
    get_token,
)
from django.views.decorators.csrf import (
    ensure_csrf_cookie,
)

def auth_root(
    request,
):
    # ==================================================
    # METHOD
    # ==================================================

    if request.method != "GET":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use GET to retrieve "
                    "authentication metadata."
                ),
                request=request,
            )
        )

    # ==================================================
    # RESPONSE
    # ==================================================

    return (
        APIResponseService
        .success(
            data={
                "namespace":
                    "auth",

                "version":
                    "v1",

                "authentication":
                    "session",

                "endpoints": (
                    APIDiscoveryService
                    .get_authentication_endpoints()
                ),

                "capabilities": {
                    "csrf_required_for_unsafe_methods":
                        True,

                    "session_cookie_name":
                        (
                            APIDiscoveryService
                            .get_capabilities()
                            [
                                "authentication"
                            ]
                            [
                                "cookie_name"
                            ]
                        ),

                    "server_request_header":
                        "X-Request-ID",

                    "client_correlation_header":
                        "X-Correlation-ID",
                },
            },
            message=(
                "Authentication API metadata "
                "retrieved successfully."
            ),
            request=request,
        )
    )


@ensure_csrf_cookie
def csrf_api(
    request,
):
    # ==================================================
    # METHOD
    # ==================================================

    if request.method != "GET":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use GET to retrieve "
                    "a CSRF token."
                ),
                request=request,
            )
        )

    # ==================================================
    # TOKEN
    # ==================================================

    csrf_token = get_token(
        request
    )

    # ==================================================
    # RESPONSE
    # ==================================================

    return (
        APIResponseService
        .success(
            data={
                "csrf": {
                    "token":
                        csrf_token,

                    "header_name":
                        "X-CSRFToken",

                    "cookie_name":
                        "csrftoken",
                },
            },
            message=(
                "CSRF token issued "
                "successfully."
            ),
            request=request,
        )
    )


def login_api(
    request,
):
    # ==================================================
    # METHOD
    # ==================================================

    if request.method != "POST":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use POST to authenticate."
                ),
                request=request,
            )
        )

    # ==================================================
    # CONTENT TYPE
    # ==================================================

    content_type = (
        request.content_type
        or
        ""
    ).lower()

    if (
        "application/json"
        not in content_type
    ):

        return (
            APIResponseService
            .bad_request(
                message=(
                    "Content-Type must be "
                    "application/json."
                ),
                request=request,
            )
        )

    # ==================================================
    # JSON BODY
    # ==================================================

    try:

        payload = json.loads(
            request.body.decode(
                "utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return (
            APIResponseService
            .bad_request(
                message="Invalid JSON body.",
                request=request,
            )
        )

    if not isinstance(
        payload,
        dict,
    ):

        return (
            APIResponseService
            .validation_error(
                message="Validation failed.",
                details={
                    "body": [
                        (
                            "JSON body must "
                            "be an object."
                        )
                    ],
                },
                request=request,
            )
        )

    # ==================================================
    # INPUT
    # ==================================================

    email = (
        LoginRateLimitService
        .normalize_email(
            payload.get(
                "email"
            )
        )
    )

    password = payload.get(
        "password"
    )

    validation_errors = {}

    if not email:

        validation_errors[
            "email"
        ] = [
            "Email is required."
        ]

    if (
        not isinstance(
            password,
            str,
        )
        or
        not password
    ):

        validation_errors[
            "password"
        ] = [
            "Password is required."
        ]

    if validation_errors:

        return (
            APIResponseService
            .validation_error(
                message="Validation failed.",
                details=validation_errors,
                request=request,
            )
        )

    # ==================================================
    # AUTHENTICATE
    #
    # MongoEngineBackend performs:
    # - login rate-limit checking
    # - user lookup
    # - user active validation
    # - organization validation
    # - password verification
    # - authentication audit logging
    # - operational logging
    # ==================================================

    user = authenticate(
        request=request,
        email=email,
        password=password,
    )

    # ==================================================
    # AUTHENTICATION FAILED
    # ==================================================

    if user is None:

        ip_address = (
            LoginRateLimitService
            .get_client_ip(
                request
            )
        )

        rate_limit_identifier = (
            LoginRateLimitService
            .build_identifier(
                email=email,
                ip_address=ip_address,
            )
        )

        rate_limit_status = (
            LoginRateLimitService
            .get_status(
                rate_limit_identifier
            )
        )

        if rate_limit_status[
            "blocked"
        ]:

            return (
                APIResponseService
                .rate_limited(
                    message=(
                        "Too many failed login "
                        "attempts. Try again later."
                    ),
                    request=request,
                )
            )

        return (
            APIResponseService
            .unauthorized(
                message=(
                    "Invalid email or password."
                ),
                request=request,
            )
        )

    # ==================================================
    # ORGANIZATION
    # ==================================================

    organization = getattr(
        user,
        "organization",
        None,
    )

    if not organization:

        return (
            APIResponseService
            .forbidden(
                message=(
                    "Organization context "
                    "is unavailable."
                ),
                request=request,
            )
        )

    # ==================================================
    # ORGANIZATION CONTEXT
    #
    # This context is derived from the authenticated
    # backend user, never from request JSON.
    # ==================================================

    organization_context = {
        "user":
            user,

        "organization":
            organization,

        "organization_id":
            str(
                organization.id
            ),
    }

    # ==================================================
    # PERMISSION CONTEXT
    #
    # Resolve this before creating the session. If the
    # role belongs to another tenant, no authenticated
    # session should be issued.
    # ==================================================

    try:

        permission_context = (
            APIPermissionContextService
            .resolve(
                request,
                organization_context=(
                    organization_context
                ),
            )
        )

    except PermissionError:

        return (
            APIResponseService
            .forbidden(
                message=(
                    "Invalid authorization "
                    "context."
                ),
                request=request,
            )
        )

    role = permission_context[
        "role"
    ]

    permissions = permission_context[
        "permission_codes"
    ]

    permissions_by_module = (
        permission_context[
            "permissions_by_module"
        ]
    )

    # ==================================================
    # CREATE SESSION
    # ==================================================

    try:

        AuthenticationService.login(
            request,
            user,
        )

    except Exception:

        return (
            APIResponseService
            .internal_error(
                message=(
                    "Unable to create "
                    "authentication session."
                ),
                request=request,
            )
        )

    # ==================================================
    # SERIALIZED RESPONSE
    # ==================================================

    response_data = (
        AccountAPISerializer
        .serialize_authentication_context(
            user=user,
            organization=organization,
            role=role,
            permission_codes=(
                permissions
            ),
            permissions_by_module=(
                permissions_by_module
            ),
            authenticated=True,
        )
    )

    return (
        APIResponseService
        .success(
            data=response_data,
            message="Login successful.",
            status=200,
            request=request,
        )
    )
def logout_api(
    request,
):
    # ==================================================
    # METHOD
    # ==================================================

    if request.method != "POST":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use POST to log out."
                ),
                request=request,
            )
        )

    # ==================================================
    # AUTHENTICATION
    # ==================================================

    user = (
        AuthenticationService
        .get_user(
            request
        )
    )

    if not user:

        return (
            APIResponseService
            .unauthorized(
                message="Not authenticated.",
                request=request,
            )
        )

    user_id = str(
        user.id
    )

    email = user.email

    # ==================================================
    # LOGOUT
    #
    # AuthenticationService.logout():
    # - records LOGOUT audit
    # - records operational log
    # - flushes the current session
    # ==================================================

    try:

        AuthenticationService.logout(
            request
        )

    except Exception:

        return (
            APIResponseService
            .internal_error(
                message=(
                    "Unable to terminate "
                    "authentication session."
                ),
                request=request,
            )
        )

    # ==================================================
    # RESPONSE
    # ==================================================

    return (
        APIResponseService
        .success(
            data={
                "authentication": {
                    "type":
                        "session",

                    "authenticated":
                        False,
                },

                "logged_out_user": {
                    "id":
                        user_id,

                    "email":
                        email,
                },
            },
            message="Logout successful.",
            status=200,
            request=request,
        )
    )

@api_login_required
def logout_all_api(
    request,
):
    # ==================================================
    # METHOD
    # ==================================================

    if request.method != "POST":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use POST to log out "
                    "from all devices."
                ),
                request=request,
            )
        )

    # ==================================================
    # TRUSTED AUTHENTICATION CONTEXT
    # ==================================================

    user = request.api_user

    user_id = str(
        user.id
    )

    email = user.email

    # ==================================================
    # LOGOUT ALL DEVICES
    #
    # The service:
    # - finds every MongoDB session for the user
    # - deletes those sessions
    # - records LOGOUT_ALL audit
    # - records the operational log
    # - flushes the current session
    # ==================================================

    try:

        deleted_count = (
            AuthenticationService
            .logout_all_devices(
                request,
                user,
            )
        )

    except Exception:

        return (
            APIResponseService
            .internal_error(
                message=(
                    "Unable to terminate "
                    "authentication sessions."
                ),
                request=request,
            )
        )

    # ==================================================
    # RESPONSE
    # ==================================================

    return (
        APIResponseService
        .success(
            data={
                "authentication": {
                    "type":
                        "session",

                    "authenticated":
                        False,
                },

                "logged_out_user": {
                    "id":
                        user_id,

                    "email":
                        email,
                },

                "sessions_deleted":
                    deleted_count,
            },
            message=(
                "Logged out from all "
                "devices successfully."
            ),
            status=200,
            request=request,
        )
    )


@api_login_required
def me_api(
    request,
):
    # ==================================================
    # METHOD
    # ==================================================

    if request.method != "GET":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use GET to retrieve "
                    "the current user."
                ),
                request=request,
            )
        )

    # ==================================================
    # ORGANIZATION CONTEXT
    # ==================================================

    organization_context = (
        request.api_organization_context
    )

    user = request.api_user

    organization = (
        request.api_organization
    )

    # ==================================================
    # PERMISSION CONTEXT
    # ==================================================

    try:

        permission_context = (
            APIPermissionContextService
            .resolve(
                request,
                organization_context=(
                    organization_context
                ),
            )
        )

    except PermissionError as exc:

        return (
            APIResponseService
            .forbidden(
                message=str(
                    exc
                ),
                request=request,
            )
        )

    role = permission_context[
        "role"
    ]

    permissions = permission_context[
        "permission_codes"
    ]

    permissions_by_module = (
        permission_context[
            "permissions_by_module"
        ]
    )

    # ==================================================
    # RESPONSE
    # ==================================================

    return (
        APIResponseService
        .success(
            data=(
                AccountAPISerializer
                .serialize_authentication_context(
                    user=user,
                    organization=organization,
                    role=role,
                    permission_codes=(
                        permissions
                    ),
                    permissions_by_module=(
                        permissions_by_module
                    ),
                    authenticated=True,
                )
            ),
            message=(
                "Current user retrieved "
                "successfully."
            ),
            status=200,
            request=request,
        )
    )

