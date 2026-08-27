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


class CustomerAPIV1RegressionTestCase(
    SimpleTestCase
):

    CUSTOMERS_URL = (
        "/api/v1/customers/"
    )

    def setUp(self):
        now = datetime.utcnow()

        self.organization = SimpleNamespace(
            id=ObjectId(),
            name="Customer Regression Organization",
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

        self.customer = SimpleNamespace(
            id=ObjectId(),
            organization=self.organization,
            code="CUST-001",
            name="Regression Customer",
            email="customer@example.com",
            phone="9999999998",
            gstin="27ABCDE1234F1Z5",
            billing_address="Billing Address",
            shipping_address="Shipping Address",
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
        customer=None,
    ):
        customer = (
            customer
            or
            self.customer
        )

        return (
            f"{self.CUSTOMERS_URL}"
            f"{customer.id}/"
        )

    def activate_url(
        self,
        customer=None,
    ):
        customer = (
            customer
            or
            self.customer
        )

        return (
            f"{self.CUSTOMERS_URL}"
            f"{customer.id}/activate/"
        )

    def deactivate_url(
        self,
        customer=None,
    ):
        customer = (
            customer
            or
            self.customer
        )

        return (
            f"{self.CUSTOMERS_URL}"
            f"{customer.id}/deactivate/"
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

    def test_anonymous_customer_list_is_rejected(
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
                self.CUSTOMERS_URL
            )

        self.assert_error_contract(
            response,
            401,
            "UNAUTHORIZED",
        )

    # ==================================================
    # LIST
    # ==================================================

    def test_customer_list_uses_query_pipeline(
        self,
    ):
        with (
            patch.object(
                CustomerRepository,
                "queryset_for_organization",
                return_value=object(),
            ),
            patch.object(
                APIQueryPipelineService,
                "execute",
                return_value={
                    "items": [
                        self.customer,
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
                    f"{self.CUSTOMERS_URL}"
                    "?search=Regression"
                    "&is_active=true"
                    "&sort=name"
                )
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["customers"][0][
                "code"
            ],
            "CUST-001",
        )

        pipeline_mock.assert_called_once()

    def test_customer_list_query_error_uses_contract(
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
                CustomerRepository,
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
                    f"{self.CUSTOMERS_URL}"
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

    def test_customer_list_without_permission_is_forbidden(
        self,
    ):
        with patch.object(
            AuthorizationService,
            "has_permission",
            return_value=False,
        ):
            response = self.client.get(
                self.CUSTOMERS_URL
            )

        self.assert_error_contract(
            response,
            403,
            "FORBIDDEN",
        )

    # ==================================================
    # CREATE
    # ==================================================

    def test_create_customer(
        self,
    ):
        with patch.object(
            CustomerAPIService,
            "create_customer",
            return_value=self.customer,
        ) as create_mock:
            response = self.client.post(
                self.CUSTOMERS_URL,
                data=json.dumps({
                    "code":
                        "CUST-001",
                    "name":
                        "Regression Customer",
                    "email":
                        "customer@example.com",
                }),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response,
            201,
        )

        self.assertEqual(
            body["data"]["customer"][
                "code"
            ],
            "CUST-001",
        )

        create_mock.assert_called_once_with(
            organization=self.organization,
            payload={
                "code":
                    "CUST-001",
                "name":
                    "Regression Customer",
                "email":
                    "customer@example.com",
            },
        )

    def test_create_customer_validation_error(
        self,
    ):
        with patch.object(
            CustomerAPIService,
            "create_customer",
            side_effect=(
                CustomerAPIValidationError(
                    details={
                        "code": [
                            (
                                "Customer code is "
                                "required."
                            ),
                        ],
                    },
                )
            ),
        ):
            response = self.client.post(
                self.CUSTOMERS_URL,
                data=json.dumps({
                    "name":
                        "Regression Customer",
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

    def test_customer_collection_rejects_delete(
        self,
    ):
        response = self.client.delete(
            self.CUSTOMERS_URL
        )

        self.assert_error_contract(
            response,
            405,
            "METHOD_NOT_ALLOWED",
        )

    # ==================================================
    # DETAIL
    # ==================================================

    def test_customer_detail(
        self,
    ):
        with patch.object(
            CustomerAPIService,
            "get_customer",
            return_value=self.customer,
        ):
            response = self.client.get(
                self.detail_url()
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["customer"][
                "billing_address"
            ],
            "Billing Address",
        )

    def test_missing_customer_returns_not_found(
        self,
    ):
        with patch.object(
            CustomerAPIService,
            "get_customer",
            side_effect=LookupError(
                "Customer not found."
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

    def test_malformed_customer_id_is_validation_error(
        self,
    ):
        response = self.client.get(
            (
                f"{self.CUSTOMERS_URL}"
                "invalid-id/"
            )
        )

        body = self.assert_error_contract(
            response,
            400,
            "VALIDATION_ERROR",
        )

        self.assertIn(
            "customer_id",
            body["error"]["details"],
        )

    # ==================================================
    # UPDATE
    # ==================================================

    def test_update_customer(
        self,
    ):
        updated_customer = SimpleNamespace(
            **{
                **vars(
                    self.customer
                ),
                "name":
                    "Updated Customer",
            }
        )

        with patch.object(
            CustomerAPIService,
            "update_customer",
            return_value=updated_customer,
        ) as update_mock:
            response = self.client.patch(
                self.detail_url(),
                data=json.dumps({
                    "name":
                        "Updated Customer",
                }),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["customer"]["name"],
            "Updated Customer",
        )

        update_mock.assert_called_once_with(
            organization=self.organization,
            customer_id=str(
                self.customer.id
            ),
            payload={
                "name":
                    "Updated Customer",
            },
        )

    def test_inactive_customer_update_is_unprocessable(
        self,
    ):
        with patch.object(
            CustomerAPIService,
            "update_customer",
            side_effect=(
                CustomerAPIStateError(
                    message=(
                        "Inactive customers cannot "
                        "be updated."
                    ),
                    details={
                        "is_active": [
                            (
                                "Activate the customer "
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
                        "Updated Customer",
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

    def test_activate_customer(
        self,
    ):
        with patch.object(
            CustomerAPIService,
            "activate_customer",
            return_value=self.customer,
        ):
            response = self.client.post(
                self.activate_url(),
                data=json.dumps({}),
                content_type="application/json",
            )

        self.assert_success_contract(
            response
        )

    def test_deactivate_customer(
        self,
    ):
        deactivated_customer = (
            SimpleNamespace(
                **{
                    **vars(
                        self.customer
                    ),
                    "is_active":
                        False,
                }
            )
        )

        with patch.object(
            CustomerAPIService,
            "deactivate_customer",
            return_value=(
                deactivated_customer
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
            body["data"]["customer"][
                "is_active"
            ]
        )


    # ==================================================
    # SERIALIZATION SAFETY
    # ==================================================

    def test_customer_serializer_has_safe_fields(
        self,
    ):
        serialized = (
            CustomerAPISerializer
            .serialize_detail(
                self.customer
            )
        )

        self.assertEqual(
            serialized["id"],
            str(
                self.customer.id
            ),
        )

        self.assertEqual(
            serialized["code"],
            "CUST-001",
        )

        self.assertEqual(
            serialized["billing_address"],
            "Billing Address",
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
            CustomerRepository,
            "code_exists",
            return_value=False,
        ):
            values = (
                CustomerAPIService
                .validate_create_payload(
                    organization=(
                        self.organization
                    ),
                    payload={
                        "code":
                            " cust-002 ",
                        "name":
                            " Test Customer ",
                        "email":
                            " CUSTOMER@EXAMPLE.COM ",
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
            "CUST-002",
        )

        self.assertEqual(
            values["name"],
            "Test Customer",
        )

        self.assertEqual(
            values["email"],
            "customer@example.com",
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
            CustomerRepository,
            "code_exists",
            return_value=True,
        ):
            with self.assertRaises(
                CustomerAPIValidationError
            ) as context:
                (
                    CustomerAPIService
                    .validate_create_payload(
                        organization=(
                            self.organization
                        ),
                        payload={
                            "code":
                                "CUST-001",
                            "name":
                                "Duplicate Customer",
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
            CustomerAPIValidationError
        ) as context:
            (
                CustomerAPIService
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
            CustomerRepository,
            "code_exists",
            return_value=False,
        ):
            with self.assertRaises(
                CustomerAPIValidationError
            ) as context:
                (
                    CustomerAPIService
                    .validate_create_payload(
                        organization=(
                            self.organization
                        ),
                        payload={
                            "code":
                                "CUST-003",
                            "name":
                                "Invalid Email Customer",
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
            CustomerAPIValidationError
        ) as context:
            (
                CustomerAPIService
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