import json

from apps.authorization.services import (
    AuthorizationService,
)
from apps.core.api.decorators import (
    api_login_required,
    api_rate_limit,
)
from apps.core.services.api_query_pipeline_service import (
    APIQueryPipelineError,
    APIQueryPipelineService,
)
from apps.core.services.api_response_service import (
    APIResponseService,
)
from apps.sales.api.v1.serializers import (
    CustomerAPISerializer,
)
from apps.sales.repositories.customer_repository import (
    CustomerRepository,
)
from apps.sales.services.customer_api_service import (
    CustomerAPIService,
    CustomerAPIStateError,
    CustomerAPIValidationError,
)


@api_login_required
@api_rate_limit(
    scope="customers.collection",
    limit=120,
    window_seconds=60,
)
def customer_collection_api(
    request,
):
    # ==================================================
    # GET: LIST CUSTOMERS
    # ==================================================

    if request.method == "GET":

        if not (
            AuthorizationService
            .has_permission(
                request.api_user,
                "customers.read",
            )
        ):

            return (
                APIResponseService
                .forbidden(
                    message="Permission denied.",
                    request=request,
                )
            )

        queryset = (
            CustomerRepository
            .queryset_for_organization(
                organization=(
                    request.api_organization
                ),
            )
        )

        try:

            pipeline_result = (
                APIQueryPipelineService
                .execute(
                    queryset,
                    request,
                    allowed_filters={
                        "is_active": {
                            "field":
                                "is_active",
                            "parser":
                                "boolean",
                        },
                    },
                    search_fields=[
                        "code",
                        "name",
                        "email",
                        "phone",
                        "gstin",
                        "city",
                        "state",
                    ],
                    allowed_sort_fields={
                        "code":
                            "code",
                        "name":
                            "name",
                        "email":
                            "email",
                        "city":
                            "city",
                        "state":
                            "state",
                        "country":
                            "country",
                        "created_at":
                            "created_at",
                        "updated_at":
                            "updated_at",
                    },
                    default_sort=[
                        "name",
                    ],
                    stable_sort_field="id",
                    default_page_size=25,
                    maximum_page_size=100,
                )
            )

        except APIQueryPipelineError as exc:

            return (
                APIResponseService
                .validation_error(
                    message=exc.message,
                    details={
                        "component":
                            exc.component,
                        "fields":
                            exc.details,
                    },
                    request=request,
                )
            )

        serialized_customers = (
            CustomerAPISerializer
            .serialize_many(
                pipeline_result[
                    "items"
                ]
            )
        )

        return (
            APIResponseService
            .success(
                data={
                    "customers":
                        serialized_customers,
                    "pagination":
                        pipeline_result[
                            "pagination"
                        ],
                    "query":
                        pipeline_result[
                            "query"
                        ],
                },
                message=(
                    "Customers retrieved "
                    "successfully."
                ),
                request=request,
            )
        )

    # ==================================================
    # POST: CREATE CUSTOMER
    # ==================================================

    if request.method == "POST":

        if not (
            AuthorizationService
            .has_permission(
                request.api_user,
                "customers.create",
            )
        ):

            return (
                APIResponseService
                .forbidden(
                    message="Permission denied.",
                    request=request,
                )
            )

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

        try:

            customer = (
                CustomerAPIService
                .create_customer(
                    organization=(
                        request.api_organization
                    ),
                    payload=payload,
                )
            )

        except CustomerAPIValidationError as exc:

            return (
                APIResponseService
                .validation_error(
                    message=exc.message,
                    details=exc.details,
                    request=request,
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

        return (
            APIResponseService
            .success(
                data={
                    "customer": (
                        CustomerAPISerializer
                        .serialize_detail(
                            customer
                        )
                    ),
                },
                message=(
                    "Customer created "
                    "successfully."
                ),
                status=201,
                request=request,
            )
        )

    return (
        APIResponseService
        .method_not_allowed(
            message=(
                "Use GET or POST for "
                "the customer collection."
            ),
            request=request,
        )
    )

@api_login_required
@api_rate_limit(
    scope="customers.detail",
    limit=120,
    window_seconds=60,
)
def customer_detail_api(
    request,
    customer_id,
):
    # ==================================================
    # GET: CUSTOMER DETAIL
    # ==================================================

    if request.method == "GET":

        if not (
            AuthorizationService
            .has_permission(
                request.api_user,
                "customers.read",
            )
        ):

            return (
                APIResponseService
                .forbidden(
                    message="Permission denied.",
                    request=request,
                )
            )

        try:

            customer = (
                CustomerAPIService
                .get_customer(
                    organization=(
                        request.api_organization
                    ),
                    customer_id=customer_id,
                )
            )

        except CustomerAPIValidationError as exc:

            return (
                APIResponseService
                .validation_error(
                    message=exc.message,
                    details=exc.details,
                    request=request,
                )
            )

        except LookupError:

            return (
                APIResponseService
                .not_found(
                    message="Customer not found.",
                    request=request,
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

        return (
            APIResponseService
            .success(
                data={
                    "customer": (
                        CustomerAPISerializer
                        .serialize_detail(
                            customer
                        )
                    ),
                },
                message=(
                    "Customer retrieved "
                    "successfully."
                ),
                request=request,
            )
        )

    # ==================================================
    # PATCH: UPDATE CUSTOMER
    # ==================================================

    if request.method == "PATCH":

        if not (
            AuthorizationService
            .has_permission(
                request.api_user,
                "customers.update",
            )
        ):

            return (
                APIResponseService
                .forbidden(
                    message="Permission denied.",
                    request=request,
                )
            )

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

        try:

            customer = (
                CustomerAPIService
                .update_customer(
                    organization=(
                        request.api_organization
                    ),
                    customer_id=customer_id,
                    payload=payload,
                )
            )

        except CustomerAPIValidationError as exc:

            return (
                APIResponseService
                .validation_error(
                    message=exc.message,
                    details=exc.details,
                    request=request,
                )
            )

        except CustomerAPIStateError as exc:

            return (
                APIResponseService
                .unprocessable_entity(
                    message=exc.message,
                    details=exc.details,
                    request=request,
                )
            )

        except LookupError:

            return (
                APIResponseService
                .not_found(
                    message="Customer not found.",
                    request=request,
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

        return (
            APIResponseService
            .success(
                data={
                    "customer": (
                        CustomerAPISerializer
                        .serialize_detail(
                            customer
                        )
                    ),
                },
                message=(
                    "Customer updated "
                    "successfully."
                ),
                request=request,
            )
        )

    return (
        APIResponseService
        .method_not_allowed(
            message=(
                "Use GET or PATCH for "
                "customer detail."
            ),
            request=request,
        )
    )


@api_login_required
@api_rate_limit(
    scope="customers.activate",
    limit=60,
    window_seconds=60,
)
def customer_activate_api(
    request,
    customer_id,
):
    if request.method != "POST":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use POST to activate "
                    "a customer."
                ),
                request=request,
            )
        )

    if not (
        AuthorizationService
        .has_permission(
            request.api_user,
            "customers.update",
        )
    ):

        return (
            APIResponseService
            .forbidden(
                message="Permission denied.",
                request=request,
            )
        )

    try:

        customer = (
            CustomerAPIService
            .activate_customer(
                organization=(
                    request.api_organization
                ),
                customer_id=customer_id,
            )
        )

    except CustomerAPIValidationError as exc:

        return (
            APIResponseService
            .validation_error(
                message=exc.message,
                details=exc.details,
                request=request,
            )
        )

    except LookupError:

        return (
            APIResponseService
            .not_found(
                message="Customer not found.",
                request=request,
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

    return (
        APIResponseService
        .success(
            data={
                "customer": (
                    CustomerAPISerializer
                    .serialize_detail(
                        customer
                    )
                ),
            },
            message=(
                "Customer activated "
                "successfully."
            ),
            request=request,
        )
    )


@api_login_required
@api_rate_limit(
    scope="customers.deactivate",
    limit=60,
    window_seconds=60,
)
def customer_deactivate_api(
    request,
    customer_id,
):
    if request.method != "POST":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use POST to deactivate "
                    "a customer."
                ),
                request=request,
            )
        )

    if not (
        AuthorizationService
        .has_permission(
            request.api_user,
            "customers.update",
        )
    ):

        return (
            APIResponseService
            .forbidden(
                message="Permission denied.",
                request=request,
            )
        )

    try:

        customer = (
            CustomerAPIService
            .deactivate_customer(
                organization=(
                    request.api_organization
                ),
                customer_id=customer_id,
            )
        )

    except CustomerAPIValidationError as exc:

        return (
            APIResponseService
            .validation_error(
                message=exc.message,
                details=exc.details,
                request=request,
            )
        )

    except LookupError:

        return (
            APIResponseService
            .not_found(
                message="Customer not found.",
                request=request,
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

    return (
        APIResponseService
        .success(
            data={
                "customer": (
                    CustomerAPISerializer
                    .serialize_detail(
                        customer
                    )
                ),
            },
            message=(
                "Customer deactivated "
                "successfully."
            ),
            request=request,
        )
    )