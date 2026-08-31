import json
import tempfile

from pathlib import Path

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
from apps.finance.api.v1.serializers import (
    BankStatementAPISerializer,
    BankTransactionAPISerializer,
)
from apps.finance.importers.bank_statement_parser import (
    BankStatementParser,
)
from apps.finance.repositories.bank_statement_repository import (
    BankStatementRepository,
)
from apps.finance.services.bank_statement_api_service import (
    BankStatementAPIService,
    BankStatementAPIStateError,
    BankStatementAPIValidationError,
)


MAX_UPLOAD_SIZE = 5 * 1024 * 1024


def _json_body(
    request,
):
    content_type = (
        request.content_type
        or
        ""
    ).lower()

    if "application/json" not in content_type:
        return (
            None,
            APIResponseService
            .validation_error(
                message=(
                    "Content-Type must be "
                    "application/json."
                ),
                details={
                    "content_type": [
                        "Send the request body as JSON.",
                    ],
                },
                request=request,
            ),
        )

    try:
        return (
            json.loads(
                request.body
                or
                b"{}"
            ),
            None,
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return (
            None,
            APIResponseService
            .validation_error(
                message="Malformed JSON body.",
                details={
                    "body": [
                        "Request body must contain valid JSON.",
                    ],
                },
                request=request,
            ),
        )


def _parse_uploaded_statement(
    uploaded_file,
):
    if not uploaded_file:
        raise BankStatementAPIValidationError(
            details={
                "file": [
                    "A CSV or XLSX file is required.",
                ],
            },
        )

    if uploaded_file.size > MAX_UPLOAD_SIZE:
        raise BankStatementAPIValidationError(
            details={
                "file": [
                    "File size must not exceed 5 MB.",
                ],
            },
        )

    filename = Path(
        uploaded_file.name
        or
        "statement"
    ).name

    suffix = Path(filename).suffix.lower()

    if suffix not in {
        ".csv",
        ".xlsx",
    }:
        raise BankStatementAPIValidationError(
            details={
                "file": [
                    "Upload a CSV or XLSX file.",
                ],
            },
        )

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(
                temporary_file.name
            )

            for chunk in uploaded_file.chunks():
                temporary_file.write(
                    chunk
                )

        if suffix == ".csv":
            rows = (
                BankStatementParser
                .parse_csv(
                    str(
                        temporary_path
                    )
                )
            )
            source_type = "CSV"

        else:
            rows = (
                BankStatementParser
                .parse_xlsx(
                    str(
                        temporary_path
                    )
                )
            )
            source_type = "XLSX"

        return (
            rows,
            source_type,
            filename,
        )

    except BankStatementAPIValidationError:
        raise

    except ValueError as exc:
        raise BankStatementAPIValidationError(
            message="Unable to parse bank statement.",
            details={
                "file": [
                    str(exc),
                ],
            },
        ) from exc

    finally:
        if (
            temporary_path
            and
            temporary_path.exists()
        ):
            temporary_path.unlink(
                missing_ok=True
            )


@api_login_required
@api_rate_limit(
    scope="bank_statements.collection",
    limit=60,
    window_seconds=60,
)
def bank_statement_collection_api(
    request,
):
    if request.method == "GET":
        if not AuthorizationService.has_permission(
            request.api_user,
            "bank_statements.read",
        ):
            return APIResponseService.forbidden(
                message="Permission denied.",
                request=request,
            )

        queryset = (
            BankStatementRepository
            .queryset_for_organization(
                organization=request.api_organization,
            )
        )

        try:
            pipeline_result = (
                APIQueryPipelineService
                .execute(
                    queryset,
                    request,
                    allowed_filters={
                        "bank_account_id": {
                            "field": "bank_account",
                            "parser": "object_id",
                        },
                        "status": {
                            "field": "status",
                            "parser": "string",
                        },
                        "source_type": {
                            "field": "source_type",
                            "parser": "string",
                        },
                    },
                    search_fields=[
                        "statement_number",
                        "source_filename",
                    ],
                    allowed_sort_fields={
                        "statement_number": "statement_number",
                        "statement_start_date": "statement_start_date",
                        "statement_end_date": "statement_end_date",
                        "opening_balance": "opening_balance",
                        "closing_balance": "closing_balance",
                        "status": "status",
                        "source_type": "source_type",
                        "created_at": "created_at",
                        "updated_at": "updated_at",
                    },
                    default_sort=[
                        "-statement_start_date",
                    ],
                    stable_sort_field="id",
                    default_page_size=25,
                    maximum_page_size=100,
                )
            )

        except APIQueryPipelineError as exc:
            return APIResponseService.validation_error(
                message=exc.message,
                details={
                    "component": exc.component,
                    "fields": exc.details,
                },
                request=request,
            )

        return APIResponseService.success(
            data={
                "bank_statements": (
                    BankStatementAPISerializer
                    .serialize_many(
                        pipeline_result["items"]
                    )
                ),
                "pagination": pipeline_result["pagination"],
                "query": pipeline_result["query"],
            },
            request=request,
        )

    if request.method == "POST":
        if not AuthorizationService.has_permission(
            request.api_user,
            "bank_statements.create",
        ):
            return APIResponseService.forbidden(
                message="Permission denied.",
                request=request,
            )

        content_type = (
            request.content_type
            or
            ""
        ).lower()

        if "multipart/form-data" not in content_type:
            return APIResponseService.validation_error(
                message=(
                    "Content-Type must be multipart/form-data."
                ),
                details={
                    "content_type": [
                        "Upload the statement as form data.",
                    ],
                },
                request=request,
            )

        try:
            (
                raw_lines,
                source_type,
                source_filename,
            ) = _parse_uploaded_statement(
                request.FILES.get("file")
            )

            statement = (
                BankStatementAPIService
                .create_statement(
                    user=request.api_user,
                    organization=request.api_organization,
                    bank_account_id=request.POST.get(
                        "bank_account_id"
                    ),
                    statement_start_date=request.POST.get(
                        "statement_start_date"
                    ),
                    statement_end_date=request.POST.get(
                        "statement_end_date"
                    ),
                    opening_balance=request.POST.get(
                        "opening_balance"
                    ),
                    closing_balance=request.POST.get(
                        "closing_balance"
                    ),
                    raw_lines=raw_lines,
                    source_type=source_type,
                    source_filename=source_filename,
                )
            )

        except BankStatementAPIValidationError as exc:
            return APIResponseService.validation_error(
                message=exc.message,
                details=exc.details,
                request=request,
            )

        except BankStatementAPIStateError as exc:
            return APIResponseService.unprocessable_entity(
                message=exc.message,
                details=exc.details,
                request=request,
            )

        except PermissionError:
            return APIResponseService.forbidden(
                message="Permission denied.",
                request=request,
            )

        return APIResponseService.success(
            data={
                "bank_statement": (
                    BankStatementAPISerializer
                    .serialize_detail(
                        statement
                    )
                ),
            },
            message="Bank statement imported successfully.",
            status=201,
            request=request,
        )

    return APIResponseService.method_not_allowed(
        message=(
            "Use GET to list bank statements or "
            "POST to import one."
        ),
        request=request,
    )


@api_login_required
@api_rate_limit(
    scope="bank_statements.detail",
    limit=120,
    window_seconds=60,
)
def bank_statement_detail_api(
    request,
    statement_id,
):
    if request.method != "GET":
        return APIResponseService.method_not_allowed(
            message="Use GET to retrieve a bank statement.",
            request=request,
        )

    if not AuthorizationService.has_permission(
        request.api_user,
        "bank_statements.read",
    ):
        return APIResponseService.forbidden(
            message="Permission denied.",
            request=request,
        )

    try:
        statement = (
            BankStatementAPIService
            .get_statement(
                organization=request.api_organization,
                statement_id=statement_id,
            )
        )

    except BankStatementAPIValidationError as exc:
        return APIResponseService.validation_error(
            message=exc.message,
            details=exc.details,
            request=request,
        )

    except LookupError:
        return APIResponseService.not_found(
            message="Bank statement not found.",
            request=request,
        )

    return APIResponseService.success(
        data={
            "bank_statement": (
                BankStatementAPISerializer
                .serialize_detail(
                    statement
                )
            ),
        },
        request=request,
    )


@api_login_required
@api_rate_limit(
    scope="bank_statements.cancel",
    limit=60,
    window_seconds=60,
)
def bank_statement_cancel_api(
    request,
    statement_id,
):
    if request.method != "POST":
        return APIResponseService.method_not_allowed(
            message="Use POST to cancel a bank statement.",
            request=request,
        )

    if not AuthorizationService.has_permission(
        request.api_user,
        "bank_statements.cancel",
    ):
        return APIResponseService.forbidden(
            message="Permission denied.",
            request=request,
        )

    try:
        statement = (
            BankStatementAPIService
            .cancel_statement(
                user=request.api_user,
                organization=request.api_organization,
                statement_id=statement_id,
            )
        )

    except BankStatementAPIValidationError as exc:
        return APIResponseService.validation_error(
            message=exc.message,
            details=exc.details,
            request=request,
        )

    except LookupError:
        return APIResponseService.not_found(
            message="Bank statement not found.",
            request=request,
        )

    except BankStatementAPIStateError as exc:
        return APIResponseService.unprocessable_entity(
            message=exc.message,
            details=exc.details,
            request=request,
        )

    except PermissionError:
        return APIResponseService.forbidden(
            message="Permission denied.",
            request=request,
        )

    return APIResponseService.success(
        data={
            "bank_statement": (
                BankStatementAPISerializer
                .serialize_detail(
                    statement
                )
            ),
        },
        message="Bank statement cancelled successfully.",
        request=request,
    )


def _line_action_error_response(
    request,
    exc,
):
    if isinstance(
        exc,
        BankStatementAPIValidationError,
    ):
        return APIResponseService.validation_error(
            message=exc.message,
            details=exc.details,
            request=request,
        )

    if isinstance(
        exc,
        LookupError,
    ):
        return APIResponseService.not_found(
            message="Bank statement not found.",
            request=request,
        )

    if isinstance(
        exc,
        BankStatementAPIStateError,
    ):
        return APIResponseService.unprocessable_entity(
            message=exc.message,
            details=exc.details,
            request=request,
        )

    return APIResponseService.forbidden(
        message="Permission denied.",
        request=request,
    )


@api_login_required
@api_rate_limit(
    scope="bank_statements.auto_match",
    limit=120,
    window_seconds=60,
)
def bank_statement_line_auto_match_api(
    request,
    statement_id,
    line_number,
):
    if request.method != "POST":
        return APIResponseService.method_not_allowed(
            message="Use POST to auto-match a statement line.",
            request=request,
        )

    if not AuthorizationService.has_permission(
        request.api_user,
        "bank_statements.reconcile",
    ):
        return APIResponseService.forbidden(
            message="Permission denied.",
            request=request,
        )

    payload = {}

    if (
        "application/json"
        in (
            request.content_type
            or
            ""
        ).lower()
    ):
        payload, error_response = _json_body(
            request
        )

        if error_response:
            return error_response

        if not isinstance(payload, dict):
            return APIResponseService.validation_error(
                message="JSON body must be an object.",
                details={
                    "body": [
                        "JSON body must be an object.",
                    ],
                },
                request=request,
            )

    try:
        result = (
            BankStatementAPIService
            .auto_match_line(
                user=request.api_user,
                organization=request.api_organization,
                statement_id=statement_id,
                line_number=line_number,
                date_tolerance_days=payload.get(
                    "date_tolerance_days",
                    2,
                ),
            )
        )

    except (
        BankStatementAPIValidationError,
        BankStatementAPIStateError,
        LookupError,
        PermissionError,
    ) as exc:
        return _line_action_error_response(
            request,
            exc,
        )

    transaction = result.get(
        "transaction"
    )

    return APIResponseService.success(
        data={
            "statement": (
                BankStatementAPISerializer
                .serialize_summary(
                    result["statement"]
                )
            ),
            "line": (
                BankStatementAPISerializer
                .serialize_line(
                    result["line"]
                )
            ),
            "match_type": result.get("match_type"),
            "matched": bool(result.get("matched", False)),
            "candidate_count": result.get("candidate_count"),
            "transaction": (
                BankTransactionAPISerializer
                .serialize_detail(
                    transaction
                )
                if transaction
                else None
            ),
        },
        request=request,
    )


@api_login_required
@api_rate_limit(
    scope="bank_statements.manual_match",
    limit=120,
    window_seconds=60,
)
def bank_statement_line_match_api(
    request,
    statement_id,
    line_number,
):
    if request.method != "POST":
        return APIResponseService.method_not_allowed(
            message="Use POST to match a statement line.",
            request=request,
        )

    if not AuthorizationService.has_permission(
        request.api_user,
        "bank_statements.reconcile",
    ):
        return APIResponseService.forbidden(
            message="Permission denied.",
            request=request,
        )

    payload, error_response = _json_body(
        request
    )

    if error_response:
        return error_response

    if not isinstance(payload, dict):
        return APIResponseService.validation_error(
            message="JSON body must be an object.",
            details={
                "body": [
                    "JSON body must be an object.",
                ],
            },
            request=request,
        )

    try:
        result = (
            BankStatementAPIService
            .match_line(
                user=request.api_user,
                organization=request.api_organization,
                statement_id=statement_id,
                line_number=line_number,
                transaction_id=payload.get(
                    "transaction_id"
                ),
            )
        )

    except (
        BankStatementAPIValidationError,
        BankStatementAPIStateError,
        LookupError,
        PermissionError,
    ) as exc:
        return _line_action_error_response(
            request,
            exc,
        )

    return APIResponseService.success(
        data={
            "statement": (
                BankStatementAPISerializer
                .serialize_summary(
                    result["statement"]
                )
            ),
            "line": (
                BankStatementAPISerializer
                .serialize_line(
                    result["line"]
                )
            ),
            "transaction": (
                BankTransactionAPISerializer
                .serialize_detail(
                    result["transaction"]
                )
            ),
        },
        message="Statement line matched successfully.",
        request=request,
    )


@api_login_required
@api_rate_limit(
    scope="bank_statements.ignore_line",
    limit=120,
    window_seconds=60,
)
def bank_statement_line_ignore_api(
    request,
    statement_id,
    line_number,
):
    if request.method != "POST":
        return APIResponseService.method_not_allowed(
            message="Use POST to ignore a statement line.",
            request=request,
        )

    if not AuthorizationService.has_permission(
        request.api_user,
        "bank_statements.reconcile",
    ):
        return APIResponseService.forbidden(
            message="Permission denied.",
            request=request,
        )

    try:
        result = (
            BankStatementAPIService
            .ignore_line(
                user=request.api_user,
                organization=request.api_organization,
                statement_id=statement_id,
                line_number=line_number,
            )
        )

    except (
        BankStatementAPIValidationError,
        BankStatementAPIStateError,
        LookupError,
        PermissionError,
    ) as exc:
        return _line_action_error_response(
            request,
            exc,
        )

    return APIResponseService.success(
        data={
            "statement": (
                BankStatementAPISerializer
                .serialize_summary(
                    result["statement"]
                )
            ),
            "line": (
                BankStatementAPISerializer
                .serialize_line(
                    result["line"]
                )
            ),
        },
        message="Statement line ignored successfully.",
        request=request,
    )
