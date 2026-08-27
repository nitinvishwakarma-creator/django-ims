import json

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from bson import ObjectId

from django.test import (
    Client,
    SimpleTestCase,
)

from apps.authorization.services import (
    AuthorizationService,
)
from apps.core.services.api_query_pipeline_service import (
    APIQueryPipelineError,
    APIQueryPipelineService,
)
from apps.core.services.api_rate_limit_service import (
    APIRateLimitService,
)
from apps.core.services.application_logging_service import (
    ApplicationLoggingService,
)
from apps.core.services.mongodb_error_logging_service import (
    MongoDBErrorLoggingService,
)
from apps.organizations.api_context_service import (
    APIOrganizationContextService,
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


class SupplierAPIV1RegressionTestCase(
    SimpleTestCase
):

    SUPPLIERS_URL = (
        "/api/v1/suppliers/"
    )

    def setUp(self):
        now = datetime.utcnow()

        self.organization = SimpleNamespace(
            id=ObjectId(),
            name="Supplier Regression Organization",
            email="organization@example.com",
            phone="9999999999",
            address="Regression Test Address",
            country="India",
            currency="INR",
            timezone="Asia/Kolkata",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.user = SimpleNamespace(
            id=ObjectId(),
            organization=self.organization,
            email="admin@example.com",
            first_name="System",
            last_name="Administrator",
            is_active=True,
            is_authenticated=True,
            is_anonymous=False,
        )

        self.supplier = SimpleNamespace(
            id=ObjectId(),
            organization=self.organization,
            code="SUPP-001",
            name="Regression Supplier",
            email="supplier@example.com",
            phone="9999999998",
            gstin="27ABCDE1234F1Z5",
            address="Supplier Address",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            pincode="400001",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.organization_context = {
            "user":
                self.user,
            "organization":
                self.organization,
        }

        self.patchers = [
            patch.object(
                ApplicationLoggingService,
                "log",
                return_value=None,
            ),
            patch.object(
                MongoDBErrorLoggingService,
                "log_exception",
                return_value=None,
            ),
            patch.object(
                APIOrganizationContextService,
                "resolve",
                return_value=(
                    self.organization_context
                ),
            ),
            patch.object(
                AuthorizationService,
                "has_permission",
                return_value=True,
            ),
            patch.object(
                APIRateLimitService,
                "check",
                return_value={
                    "allowed": True,
                },
            ),
            patch.object(
                APIRateLimitService,
                "add_headers",
                side_effect=(
                    lambda response, result:
                    response
                ),
            ),
        ]

        for patcher in self.patchers:
            patcher.start()

        self.client = Client(
            raise_request_exception=False
        )

    def tearDown(self):
        for patcher in reversed(
            self.patchers
        ):
            patcher.stop()

    def detail_url(
        self,
        supplier=None,
    ):
        supplier = (
            supplier
            or
            self.supplier
        )

        return (
            f"{self.SUPPLIERS_URL}"
            f"{supplier.id}/"
        )

    def activate_url(
        self,
        supplier=None,
    ):
        supplier = (
            supplier
            or
            self.supplier
        )

        return (
            f"{self.SUPPLIERS_URL}"
            f"{supplier.id}/activate/"
        )

    def deactivate_url(
        self,
        supplier=None,
    ):
        supplier = (
            supplier
            or
            self.supplier
        )

        return (
            f"{self.SUPPLIERS_URL}"
            f"{supplier.id}/deactivate/"
        )

    def assert_success_contract(
        self,
        response,
        expected_status=200,
    ):
        body = response.json()

        self.assertEqual(
            response.status_code,
            expected_status,
        )

        self.assertTrue(
            body["success"]
        )

        self.assertIn(
            "data",
            body,
        )

        self.assertTrue(
            body.get(
                "request_id"
            )
        )

        self.assertEqual(
            response.headers.get(
                "X-Request-ID"
            ),
            body["request_id"],
        )

        self.assertEqual(
            response.headers.get(
                "Cache-Control"
            ),
            "no-store",
        )

        return body

    def assert_error_contract(
        self,
        response,
        expected_status,
        expected_code,
    ):
        body = response.json()

        self.assertEqual(
            response.status_code,
            expected_status,
        )

        self.assertFalse(
            body["success"]
        )

        self.assertEqual(
            body["error"]["code"],
            expected_code,
        )

        self.assertTrue(
            body.get(
                "request_id"
            )
        )

        return body

    # ==================================================
    # AUTHENTICATION
    # ==================================================

    def test_anonymous_supplier_list_is_rejected(
        self,
    ):
        with patch.object(
            APIOrganizationContextService,
            "resolve",
            side_effect=PermissionError(
                "Not authenticated."
            ),
        ):
            response = self.client.get(
                self.SUPPLIERS_URL
            )

        self.assert_error_contract(
            response,
            401,
            "UNAUTHORIZED",
        )

    # ==================================================
    # LIST
    # ==================================================

    def test_supplier_list_uses_query_pipeline(
        self,
    ):
        with (
            patch.object(
                SupplierRepository,
                "queryset_for_organization",
                return_value=object(),
            ),
            patch.object(
                APIQueryPipelineService,
                "execute",
                return_value={
                    "items": [
                        self.supplier,
                    ],
                    "pagination": {
                        "page": 1,
                        "page_size": 25,
                        "total_items": 1,
                        "total_pages": 1,
                        "has_next": False,
                        "has_previous": False,
                    },
                    "query": {
                        "search": None,
                        "filters": {},
                        "sort": [
                            "name",
                            "id",
                        ],
                    },
                },
            ) as pipeline_mock,
        ):
            response = self.client.get(
                (
                    f"{self.SUPPLIERS_URL}"
                    "?search=Regression"
                    "&is_active=true"
                    "&sort=name"
                )
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["suppliers"][0][
                "code"
            ],
            "SUPP-001",
        )

        pipeline_mock.assert_called_once()

    def test_supplier_list_query_error_uses_contract(
        self,
    ):
        pipeline_error = (
            APIQueryPipelineError(
                component="sorting",
                message=(
                    "Unsupported sorting field."
                ),
                details={
                    "sort": [
                        (
                            "The requested sorting "
                            "field is not supported."
                        ),
                    ],
                },
            )
        )

        with (
            patch.object(
                SupplierRepository,
                "queryset_for_organization",
                return_value=object(),
            ),
            patch.object(
                APIQueryPipelineService,
                "execute",
                side_effect=pipeline_error,
            ),
        ):
            response = self.client.get(
                (
                    f"{self.SUPPLIERS_URL}"
                    "?sort=$where"
                )
            )

        body = self.assert_error_contract(
            response,
            400,
            "VALIDATION_ERROR",
        )

        self.assertEqual(
            body["error"]["details"][
                "component"
            ],
            "sorting",
        )

    def test_supplier_list_without_permission_is_forbidden(
        self,
    ):
        with patch.object(
            AuthorizationService,
            "has_permission",
            return_value=False,
        ):
            response = self.client.get(
                self.SUPPLIERS_URL
            )

        self.assert_error_contract(
            response,
            403,
            "FORBIDDEN",
        )

    # ==================================================
    # CREATE
    # ==================================================

    def test_create_supplier(
        self,
    ):
        with patch.object(
            SupplierAPIService,
            "create_supplier",
            return_value=self.supplier,
        ) as create_mock:
            response = self.client.post(
                self.SUPPLIERS_URL,
                data=json.dumps({
                    "code":
                        "SUPP-001",
                    "name":
                        "Regression Supplier",
                    "email":
                        "supplier@example.com",
                }),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response,
            201,
        )

        self.assertEqual(
            body["data"]["supplier"][
                "code"
            ],
            "SUPP-001",
        )

        create_mock.assert_called_once_with(
            organization=self.organization,
            payload={
                "code":
                    "SUPP-001",
                "name":
                    "Regression Supplier",
                "email":
                    "supplier@example.com",
            },
        )

    def test_create_supplier_validation_error(
        self,
    ):
        with patch.object(
            SupplierAPIService,
            "create_supplier",
            side_effect=(
                SupplierAPIValidationError(
                    details={
                        "code": [
                            (
                                "Supplier code is "
                                "required."
                            ),
                        ],
                    },
                )
            ),
        ):
            response = self.client.post(
                self.SUPPLIERS_URL,
                data=json.dumps({
                    "name":
                        "Regression Supplier",
                }),
                content_type="application/json",
            )

        body = self.assert_error_contract(
            response,
            400,
            "VALIDATION_ERROR",
        )

        self.assertIn(
            "code",
            body["error"]["details"],
        )

    def test_supplier_collection_rejects_delete(
        self,
    ):
        response = self.client.delete(
            self.SUPPLIERS_URL
        )

        self.assert_error_contract(
            response,
            405,
            "METHOD_NOT_ALLOWED",
        )

    # ==================================================
    # DETAIL
    # ==================================================

    def test_supplier_detail(
        self,
    ):
        with patch.object(
            SupplierAPIService,
            "get_supplier",
            return_value=self.supplier,
        ):
            response = self.client.get(
                self.detail_url()
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["supplier"][
                "address"
            ],
            "Supplier Address",
        )

    def test_missing_supplier_returns_not_found(
        self,
    ):
        with patch.object(
            SupplierAPIService,
            "get_supplier",
            side_effect=LookupError(
                "Supplier not found."
            ),
        ):
            response = self.client.get(
                self.detail_url()
            )

        self.assert_error_contract(
            response,
            404,
            "NOT_FOUND",
        )

    def test_malformed_supplier_id_is_validation_error(
        self,
    ):
        response = self.client.get(
            (
                f"{self.SUPPLIERS_URL}"
                "invalid-id/"
            )
        )

        body = self.assert_error_contract(
            response,
            400,
            "VALIDATION_ERROR",
        )

        self.assertIn(
            "supplier_id",
            body["error"]["details"],
        )

    # ==================================================
    # UPDATE
    # ==================================================

    def test_update_supplier(
        self,
    ):
        updated_supplier = SimpleNamespace(
            **{
                **vars(
                    self.supplier
                ),
                "name":
                    "Updated Supplier",
            }
        )

        with patch.object(
            SupplierAPIService,
            "update_supplier",
            return_value=updated_supplier,
        ) as update_mock:
            response = self.client.patch(
                self.detail_url(),
                data=json.dumps({
                    "name":
                        "Updated Supplier",
                }),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["supplier"]["name"],
            "Updated Supplier",
        )

        update_mock.assert_called_once_with(
            organization=self.organization,
            supplier_id=str(
                self.supplier.id
            ),
            payload={
                "name":
                    "Updated Supplier",
            },
        )

    def test_inactive_supplier_update_is_unprocessable(
        self,
    ):
        with patch.object(
            SupplierAPIService,
            "update_supplier",
            side_effect=(
                SupplierAPIStateError(
                    message=(
                        "Inactive suppliers cannot "
                        "be updated."
                    ),
                    details={
                        "is_active": [
                            (
                                "Activate the supplier "
                                "before updating it."
                            ),
                        ],
                    },
                )
            ),
        ):
            response = self.client.patch(
                self.detail_url(),
                data=json.dumps({
                    "name":
                        "Updated Supplier",
                }),
                content_type="application/json",
            )

        self.assert_error_contract(
            response,
            422,
            "UNPROCESSABLE_ENTITY",
        )

    # ==================================================
    # LIFECYCLE
    # ==================================================

    def test_activate_supplier(
        self,
    ):
        with patch.object(
            SupplierAPIService,
            "activate_supplier",
            return_value=self.supplier,
        ):
            response = self.client.post(
                self.activate_url(),
                data=json.dumps({}),
                content_type="application/json",
            )

        self.assert_success_contract(
            response
        )

    def test_deactivate_supplier(
        self,
    ):
        deactivated_supplier = (
            SimpleNamespace(
                **{
                    **vars(
                        self.supplier
                    ),
                    "is_active":
                        False,
                }
            )
        )

        with patch.object(
            SupplierAPIService,
            "deactivate_supplier",
            return_value=(
                deactivated_supplier
            ),
        ):
            response = self.client.post(
                self.deactivate_url(),
                data=json.dumps({}),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response
        )

        self.assertFalse(
            body["data"]["supplier"][
                "is_active"
            ]
        )


    # ==================================================
    # SERIALIZATION SAFETY
    # ==================================================

    def test_supplier_serializer_has_safe_fields(
        self,
    ):
        serialized = (
            SupplierAPISerializer
            .serialize_detail(
                self.supplier
            )
        )

        self.assertEqual(
            serialized["id"],
            str(
                self.supplier.id
            ),
        )

        self.assertEqual(
            serialized["code"],
            "SUPP-001",
        )

        self.assertEqual(
            serialized["address"],
            "Supplier Address",
        )

        self.assertNotIn(
            "organization",
            serialized,
        )

        self.assertNotIn(
            "_data",
            serialized,
        )

        self.assertNotIn(
            "_cls",
            serialized,
        )

    # ==================================================
    # SERVICE VALIDATION
    # ==================================================

    def test_service_normalizes_create_payload(
        self,
    ):
        with patch.object(
            SupplierRepository,
            "code_exists",
            return_value=False,
        ):
            values = (
                SupplierAPIService
                .validate_create_payload(
                    organization=(
                        self.organization
                    ),
                    payload={
                        "code":
                            " supp-002 ",
                        "name":
                            " Test Supplier ",
                        "email":
                            " SUPPLIER@EXAMPLE.COM ",
                        "phone":
                            " 9999999997 ",
                        "gstin":
                            " 27abcde1234f1z5 ",
                        "country":
                            " India ",
                    },
                )
            )

        self.assertEqual(
            values["code"],
            "SUPP-002",
        )

        self.assertEqual(
            values["name"],
            "Test Supplier",
        )

        self.assertEqual(
            values["email"],
            "supplier@example.com",
        )

        self.assertEqual(
            values["gstin"],
            "27ABCDE1234F1Z5",
        )

        self.assertEqual(
            values["country"],
            "India",
        )

    def test_service_rejects_duplicate_code(
        self,
    ):
        with patch.object(
            SupplierRepository,
            "code_exists",
            return_value=True,
        ):
            with self.assertRaises(
                SupplierAPIValidationError
            ) as context:
                (
                    SupplierAPIService
                    .validate_create_payload(
                        organization=(
                            self.organization
                        ),
                        payload={
                            "code":
                                "SUPP-001",
                            "name":
                                "Duplicate Supplier",
                        },
                    )
                )

        self.assertIn(
            "code",
            context.exception.details,
        )

    def test_service_rejects_code_update(
        self,
    ):
        with self.assertRaises(
            SupplierAPIValidationError
        ) as context:
            (
                SupplierAPIService
                .validate_update_payload(
                    payload={
                        "code":
                            "CHANGED-CODE",
                    },
                )
            )

        self.assertIn(
            "code",
            context.exception.details,
        )

    def test_service_rejects_invalid_email(
        self,
    ):
        with patch.object(
            SupplierRepository,
            "code_exists",
            return_value=False,
        ):
            with self.assertRaises(
                SupplierAPIValidationError
            ) as context:
                (
                    SupplierAPIService
                    .validate_create_payload(
                        organization=(
                            self.organization
                        ),
                        payload={
                            "code":
                                "SUPP-003",
                            "name":
                                "Invalid Email Supplier",
                            "email":
                                "not-an-email",
                        },
                    )
                )

        self.assertIn(
            "email",
            context.exception.details,
        )

    def test_service_rejects_protected_fields(
        self,
    ):
        with self.assertRaises(
            SupplierAPIValidationError
        ) as context:
            (
                SupplierAPIService
                .validate_update_payload(
                    payload={
                        "organization_id":
                            str(
                                ObjectId()
                            ),
                        "is_active":
                            False,
                    },
                )
            )

        self.assertIn(
            "organization_id",
            context.exception.details,
        )

        self.assertIn(
            "is_active",
            context.exception.details,
        )
