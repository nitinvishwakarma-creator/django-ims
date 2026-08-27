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
from apps.purchasing.api.v1.serializers import (
    SupplierAPISerializer,
)
from apps.purchasing.repositories.supplier_repository import (
    SupplierRepository,
)
from apps.purchasing.services.supplier_api_service import (
    SupplierAPIService,
    SupplierAPIStateError,
    SupplierAPIValidationError,
)


@api_login_required
@api_rate_limit(
    scope="suppliers.collection",
    limit=120,
    window_seconds=60,
)
def supplier_collection_api(
    request,
):
    # ==================================================
    # GET: LIST SUPPLIERS
    # ==================================================

    if request.method == "GET":

        if not (
            AuthorizationService
            .has_permission(
                request.api_user,
                "suppliers.read",
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
            SupplierRepository
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

        serialized_suppliers = (
            SupplierAPISerializer
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
                    "suppliers":
                        serialized_suppliers,
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
                    "Suppliers retrieved "
                    "successfully."
                ),
                request=request,
            )
        )

    # ==================================================
    # POST: CREATE SUPPLIER
    # ==================================================

    if request.method == "POST":

        if not (
            AuthorizationService
            .has_permission(
                request.api_user,
                "suppliers.create",
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

            supplier = (
                SupplierAPIService
                .create_supplier(
                    organization=(
                        request.api_organization
                    ),
                    payload=payload,
                )
            )

        except SupplierAPIValidationError as exc:

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
                    "supplier": (
                        SupplierAPISerializer
                        .serialize_detail(
                            supplier
                        )
                    ),
                },
                message=(
                    "Supplier created "
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
                "the supplier collection."
            ),
            request=request,
        )
    )

@api_login_required
@api_rate_limit(
    scope="suppliers.detail",
    limit=120,
    window_seconds=60,
)
def supplier_detail_api(
    request,
    supplier_id,
):
    # ==================================================
    # GET: SUPPLIER DETAIL
    # ==================================================

    if request.method == "GET":

        if not (
            AuthorizationService
            .has_permission(
                request.api_user,
                "suppliers.read",
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

            supplier = (
                SupplierAPIService
                .get_supplier(
                    organization=(
                        request.api_organization
                    ),
                    supplier_id=supplier_id,
                )
            )

        except SupplierAPIValidationError as exc:

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
                    message="Supplier not found.",
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
                    "supplier": (
                        SupplierAPISerializer
                        .serialize_detail(
                            supplier
                        )
                    ),
                },
                message=(
                    "Supplier retrieved "
                    "successfully."
                ),
                request=request,
            )
        )

    # ==================================================
    # PATCH: UPDATE SUPPLIER
    # ==================================================

    if request.method == "PATCH":

        if not (
            AuthorizationService
            .has_permission(
                request.api_user,
                "suppliers.update",
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

            supplier = (
                SupplierAPIService
                .update_supplier(
                    organization=(
                        request.api_organization
                    ),
                    supplier_id=supplier_id,
                    payload=payload,
                )
            )

        except SupplierAPIValidationError as exc:

            return (
                APIResponseService
                .validation_error(
                    message=exc.message,
                    details=exc.details,
                    request=request,
                )
            )

        except SupplierAPIStateError as exc:

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
                    message="Supplier not found.",
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
                    "supplier": (
                        SupplierAPISerializer
                        .serialize_detail(
                            supplier
                        )
                    ),
                },
                message=(
                    "Supplier updated "
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
                "supplier detail."
            ),
            request=request,
        )
    )


@api_login_required
@api_rate_limit(
    scope="suppliers.activate",
    limit=60,
    window_seconds=60,
)
def supplier_activate_api(
    request,
    supplier_id,
):
    if request.method != "POST":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use POST to activate "
                    "a supplier."
                ),
                request=request,
            )
        )

    if not (
        AuthorizationService
        .has_permission(
            request.api_user,
            "suppliers.update",
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

        supplier = (
            SupplierAPIService
            .activate_supplier(
                organization=(
                    request.api_organization
                ),
                supplier_id=supplier_id,
            )
        )

    except SupplierAPIValidationError as exc:

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
                message="Supplier not found.",
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
                "supplier": (
                    SupplierAPISerializer
                    .serialize_detail(
                        supplier
                    )
                ),
            },
            message=(
                "Supplier activated "
                "successfully."
            ),
            request=request,
        )
    )


@api_login_required
@api_rate_limit(
    scope="suppliers.deactivate",
    limit=60,
    window_seconds=60,
)
def supplier_deactivate_api(
    request,
    supplier_id,
):
    if request.method != "POST":

        return (
            APIResponseService
            .method_not_allowed(
                message=(
                    "Use POST to deactivate "
                    "a supplier."
                ),
                request=request,
            )
        )

    if not (
        AuthorizationService
        .has_permission(
            request.api_user,
            "suppliers.update",
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

        supplier = (
            SupplierAPIService
            .deactivate_supplier(
                organization=(
                    request.api_organization
                ),
                supplier_id=supplier_id,
            )
        )

    except SupplierAPIValidationError as exc:

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
                message="Supplier not found.",
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
                "supplier": (
                    SupplierAPISerializer
                    .serialize_detail(
                        supplier
                    )
                ),
            },
            message=(
                "Supplier deactivated "
                "successfully."
            ),
            request=request,
        )
    )