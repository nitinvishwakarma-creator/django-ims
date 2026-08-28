import json

from datetime import datetime
from decimal import Decimal
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
    SalesOrderAPISerializer,
)
from apps.sales.repositories.customer_repository import (
    CustomerRepository,
)
from apps.sales.repositories.sales_order_repository import (
    SalesOrderRepository,
)
from apps.sales.services.customer_api_service import (
    CustomerAPIService,
    CustomerAPIStateError,
    CustomerAPIValidationError,
)
from apps.sales.services.sales_order_api_service import (
    SalesOrderAPIService,
    SalesOrderAPIStateError,
    SalesOrderAPIValidationError,
)
from apps.sales.services.sales_order_service import (
    SalesOrderService,
)
from apps.inventory.repositories.warehouse_repository import (
    WarehouseRepository,
)
from apps.products.repositories.product_repository import (
    ProductRepository,
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

class SalesOrderAPIV1RegressionTestCase(
    SimpleTestCase
):

    SALES_ORDERS_URL = (
        "/api/v1/sales-orders/"
    )

    def setUp(self):
        now = datetime.utcnow()

        self.organization = SimpleNamespace(
            id=ObjectId(),
            name="Sales Order Organization",
            email="sales-orders@example.com",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.other_organization = (
            SimpleNamespace(
                id=ObjectId(),
                name="Other Organization",
                email="other@example.com",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
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
            name="Sales Order Customer",
            email="customer@example.com",
            phone="9999999999",
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

        self.warehouse = SimpleNamespace(
            id=ObjectId(),
            organization=self.organization,
            code="MAIN-001",
            name="Main Warehouse",
            address="Warehouse Road",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            pincode="400001",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.product = SimpleNamespace(
            id=ObjectId(),
            organization=self.organization,
            sku="PHONE-001",
            name="Smart Phone",
            unit="piece",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.sales_order_item = (
            SimpleNamespace(
                product=self.product,
                quantity=Decimal("2.00"),
                fulfilled_quantity=(
                    Decimal("0.00")
                ),
                unit_price=Decimal("100.00"),
                tax_rate=Decimal("18.00"),
                discount=Decimal("10.00"),
                line_subtotal=(
                    Decimal("200.00")
                ),
                line_tax=Decimal("34.20"),
                line_total=Decimal("224.20"),
            )
        )

        self.sales_order = SimpleNamespace(
            id=ObjectId(),
            organization=self.organization,
            so_number="SO-TEST000001",
            customer=self.customer,
            warehouse=self.warehouse,
            status="DRAFT",
            order_date=now,
            expected_delivery_date=now,
            items=[
                self.sales_order_item,
            ],
            subtotal=Decimal("200.00"),
            tax_amount=Decimal("34.20"),
            discount_amount=Decimal("10.00"),
            total_amount=Decimal("224.20"),
            notes="Regression sales order.",
            created_by=self.user,
            confirmed_at=None,
            fulfilled_at=None,
            cancelled_at=None,
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
        sales_order=None,
    ):
        sales_order = (
            sales_order
            or
            self.sales_order
        )

        return (
            f"{self.SALES_ORDERS_URL}"
            f"{sales_order.id}/"
        )

    def confirm_url(
        self,
        sales_order=None,
    ):
        sales_order = (
            sales_order
            or
            self.sales_order
        )

        return (
            f"{self.SALES_ORDERS_URL}"
            f"{sales_order.id}/confirm/"
        )

    def cancel_url(
        self,
        sales_order=None,
    ):
        sales_order = (
            sales_order
            or
            self.sales_order
        )

        return (
            f"{self.SALES_ORDERS_URL}"
            f"{sales_order.id}/cancel/"
        )

    def fulfill_url(
        self,
        sales_order=None,
    ):
        sales_order = (
            sales_order
            or
            self.sales_order
        )

        return (
            f"{self.SALES_ORDERS_URL}"
            f"{sales_order.id}/fulfill/"
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
    # AUTHENTICATION AND COLLECTION
    # ==================================================

    def test_anonymous_sales_order_list_is_rejected(
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
                self.SALES_ORDERS_URL
            )

        self.assert_error_contract(
            response,
            401,
            "UNAUTHORIZED",
        )

    def test_sales_order_list_without_permission_is_forbidden(
        self,
    ):
        with patch.object(
            AuthorizationService,
            "has_permission",
            return_value=False,
        ):
            response = self.client.get(
                self.SALES_ORDERS_URL
            )

        self.assert_error_contract(
            response,
            403,
            "FORBIDDEN",
        )

    def test_sales_order_list_uses_query_pipeline(
        self,
    ):
        pipeline_result = {
            "items": [
                self.sales_order,
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
                    "-created_at",
                    "id",
                ],
            },
        }

        with (
            patch.object(
                SalesOrderRepository,
                "queryset_for_organization",
                return_value=object(),
            ),
            patch.object(
                APIQueryPipelineService,
                "execute",
                return_value=pipeline_result,
            ) as pipeline_mock,
        ):
            response = self.client.get(
                (
                    f"{self.SALES_ORDERS_URL}"
                    "?status=DRAFT"
                )
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            len(
                body["data"][
                    "sales_orders"
                ]
            ),
            1,
        )

        self.assertEqual(
            body["data"]["sales_orders"][0][
                "so_number"
            ],
            self.sales_order.so_number,
        )

        pipeline_mock.assert_called_once()

    def test_sales_order_list_query_error_uses_contract(
        self,
    ):
        pipeline_error = (
            APIQueryPipelineError(
                component="filtering",
                message=(
                    "Invalid filter value."
                ),
                details={
                    "customer_id": [
                        (
                            "Enter a valid "
                            "identifier."
                        ),
                    ],
                },
            )
        )

        with (
            patch.object(
                SalesOrderRepository,
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
                    f"{self.SALES_ORDERS_URL}"
                    "?customer_id=invalid-id"
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
            "filtering",
        )

    # ==================================================
    # CREATE
    # ==================================================

    def test_create_sales_order(
        self,
    ):
        payload = {
            "customer_id":
                str(
                    self.customer.id
                ),
            "warehouse_id":
                str(
                    self.warehouse.id
                ),
            "order_date":
                "2026-08-28T10:00:00",
            "expected_delivery_date":
                "2026-08-30T10:00:00",
            "items": [
                {
                    "product_id":
                        str(
                            self.product.id
                        ),
                    "quantity":
                        "2.00",
                    "unit_price":
                        "100.00",
                    "tax_rate":
                        "18.00",
                    "discount":
                        "10.00",
                },
            ],
            "notes":
                "Regression sales order.",
        }

        with patch.object(
            SalesOrderAPIService,
            "create_sales_order",
            return_value=self.sales_order,
        ) as create_mock:
            response = self.client.post(
                self.SALES_ORDERS_URL,
                data=json.dumps(
                    payload
                ),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response,
            201,
        )

        self.assertEqual(
            body["data"]["sales_order"][
                "total_amount"
            ],
            "224.20",
        )

        create_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            payload=payload,
        )

    def test_create_sales_order_validation_error(
        self,
    ):
        with patch.object(
            SalesOrderAPIService,
            "create_sales_order",
            side_effect=(
                SalesOrderAPIValidationError(
                    details={
                        "items": [
                            (
                                "At least one item "
                                "is required."
                            ),
                        ],
                    },
                )
            ),
        ):
            response = self.client.post(
                self.SALES_ORDERS_URL,
                data=json.dumps({
                    "items": [],
                }),
                content_type="application/json",
            )

        body = self.assert_error_contract(
            response,
            400,
            "VALIDATION_ERROR",
        )

        self.assertIn(
            "items",
            body["error"]["details"],
        )

    # ==================================================
    # DETAIL AND UPDATE
    # ==================================================

    def test_sales_order_detail(
        self,
    ):
        with patch.object(
            SalesOrderAPIService,
            "get_sales_order",
            return_value=self.sales_order,
        ):
            response = self.client.get(
                self.detail_url()
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["sales_order"][
                "so_number"
            ],
            self.sales_order.so_number,
        )

        self.assertEqual(
            len(
                body["data"]["sales_order"][
                    "items"
                ]
            ),
            1,
        )

    def test_missing_sales_order_returns_not_found(
        self,
    ):
        with patch.object(
            SalesOrderAPIService,
            "get_sales_order",
            side_effect=LookupError(
                "Sales order not found."
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

    def test_malformed_sales_order_id_is_validation_error(
        self,
    ):
        response = self.client.get(
            (
                f"{self.SALES_ORDERS_URL}"
                "invalid-id/"
            )
        )

        self.assert_error_contract(
            response,
            400,
            "VALIDATION_ERROR",
        )

    def test_update_sales_order(
        self,
    ):
        payload = {
            "notes":
                "Updated notes.",
        }

        with patch.object(
            SalesOrderAPIService,
            "update_sales_order",
            return_value=self.sales_order,
        ) as update_mock:
            response = self.client.put(
                self.detail_url(),
                data=json.dumps(
                    payload
                ),
                content_type="application/json",
            )

        self.assert_success_contract(
            response
        )

        update_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            sales_order_id=str(
                self.sales_order.id
            ),
            payload=payload,
        )

    def test_confirmed_sales_order_update_is_unprocessable(
        self,
    ):
        with patch.object(
            SalesOrderAPIService,
            "update_sales_order",
            side_effect=(
                SalesOrderAPIStateError(
                    message=(
                        "Only draft sales orders "
                        "can be edited."
                    ),
                    details={
                        "status": [
                            (
                                "Editing is not "
                                "allowed."
                            ),
                        ],
                    },
                )
            ),
        ):
            response = self.client.put(
                self.detail_url(),
                data=json.dumps({
                    "notes":
                        "Invalid update.",
                }),
                content_type="application/json",
            )

        self.assert_error_contract(
            response,
            422,
            "UNPROCESSABLE_ENTITY",
        )

    # ==================================================
    # CONFIRM
    # ==================================================

    def test_confirm_sales_order(
        self,
    ):
        confirmed_order = SimpleNamespace(
            **{
                **vars(
                    self.sales_order
                ),
                "status":
                    "CONFIRMED",
                "confirmed_at":
                    datetime.utcnow(),
            }
        )

        with patch.object(
            SalesOrderAPIService,
            "confirm_sales_order",
            return_value=confirmed_order,
        ) as confirm_mock:
            response = self.client.post(
                self.confirm_url(),
                data=json.dumps({}),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["sales_order"][
                "status"
            ],
            "CONFIRMED",
        )

        confirm_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            sales_order_id=str(
                self.sales_order.id
            ),
        )

    def test_confirm_sales_order_state_error(
        self,
    ):
        with patch.object(
            SalesOrderAPIService,
            "confirm_sales_order",
            side_effect=(
                SalesOrderAPIStateError(
                    message=(
                        "Only draft sales orders "
                        "can be confirmed."
                    ),
                )
            ),
        ):
            response = self.client.post(
                self.confirm_url(),
                data=json.dumps({}),
                content_type="application/json",
            )

        self.assert_error_contract(
            response,
            422,
            "UNPROCESSABLE_ENTITY",
        )

    def test_confirm_sales_order_rejects_get(
        self,
    ):
        response = self.client.get(
            self.confirm_url()
        )

        self.assert_error_contract(
            response,
            405,
            "METHOD_NOT_ALLOWED",
        )

    # ==================================================
    # CANCEL
    # ==================================================

    def test_cancel_sales_order(
        self,
    ):
        cancelled_order = SimpleNamespace(
            **{
                **vars(
                    self.sales_order
                ),
                "status":
                    "CANCELLED",
                "cancelled_at":
                    datetime.utcnow(),
            }
        )

        with patch.object(
            SalesOrderAPIService,
            "cancel_sales_order",
            return_value=cancelled_order,
        ) as cancel_mock:
            response = self.client.post(
                self.cancel_url(),
                data=json.dumps({}),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["sales_order"][
                "status"
            ],
            "CANCELLED",
        )

        cancel_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            sales_order_id=str(
                self.sales_order.id
            ),
        )

    def test_cancel_without_permission_is_forbidden(
        self,
    ):
        with patch.object(
            AuthorizationService,
            "has_permission",
            return_value=False,
        ):
            response = self.client.post(
                self.cancel_url(),
                data=json.dumps({}),
                content_type="application/json",
            )

        self.assert_error_contract(
            response,
            403,
            "FORBIDDEN",
        )

    # ==================================================
    # FULFILMENT
    # ==================================================

    def test_fulfill_sales_order(
        self,
    ):
        fulfilled_item = SimpleNamespace(
            **{
                **vars(
                    self.sales_order_item
                ),
                "fulfilled_quantity":
                    Decimal("2.00"),
            }
        )

        fulfilled_order = SimpleNamespace(
            **{
                **vars(
                    self.sales_order
                ),
                "status":
                    "FULFILLED",
                "items": [
                    fulfilled_item,
                ],
                "fulfilled_at":
                    datetime.utcnow(),
            }
        )

        payload = {
            "items": [
                {
                    "product_id":
                        str(
                            self.product.id
                        ),
                    "quantity":
                        "2.00",
                },
            ],
            "notes":
                "Dispatched.",
        }

        with patch.object(
            SalesOrderAPIService,
            "fulfill_sales_order",
            return_value=fulfilled_order,
        ) as fulfill_mock:
            response = self.client.post(
                self.fulfill_url(),
                data=json.dumps(
                    payload
                ),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"]["sales_order"][
                "status"
            ],
            "FULFILLED",
        )

        self.assertEqual(
            body["data"]["sales_order"][
                "items"
            ][0]["remaining_quantity"],
            "0.00",
        )

        fulfill_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            sales_order_id=str(
                self.sales_order.id
            ),
            payload=payload,
        )

    def test_fulfill_sales_order_validation_error(
        self,
    ):
        with patch.object(
            SalesOrderAPIService,
            "fulfill_sales_order",
            side_effect=(
                SalesOrderAPIValidationError(
                    details={
                        "items": [
                            (
                                "At least one item "
                                "is required."
                            ),
                        ],
                    },
                )
            ),
        ):
            response = self.client.post(
                self.fulfill_url(),
                data=json.dumps({
                    "items": [],
                }),
                content_type="application/json",
            )

        self.assert_error_contract(
            response,
            400,
            "VALIDATION_ERROR",
        )

    # ==================================================
    # SERIALIZATION
    # ==================================================

    def test_sales_order_serializer_has_safe_fields(
        self,
    ):
        serialized = (
            SalesOrderAPISerializer
            .serialize_detail(
                self.sales_order
            )
        )

        self.assertEqual(
            serialized["id"],
            str(
                self.sales_order.id
            ),
        )

        self.assertEqual(
            serialized["customer"]["id"],
            str(
                self.customer.id
            ),
        )

        self.assertEqual(
            serialized["warehouse"]["id"],
            str(
                self.warehouse.id
            ),
        )

        self.assertEqual(
            serialized["items"][0][
                "product"
            ]["id"],
            str(
                self.product.id
            ),
        )

        self.assertEqual(
            serialized["total_amount"],
            "224.20",
        )

        self.assertNotIn(
            "organization",
            serialized,
        )

        self.assertNotIn(
            "_data",
            serialized,
        )

    # ==================================================
    # SERVICE VALIDATION
    # ==================================================

    def test_service_normalizes_create_payload(
        self,
    ):
        payload = {
            "customer_id":
                str(
                    self.customer.id
                ),
            "warehouse_id":
                str(
                    self.warehouse.id
                ),
            "order_date":
                "2026-08-28T10:00:00",
            "expected_delivery_date":
                "2026-08-30T10:00:00",
            "items": [
                {
                    "product_id":
                        str(
                            self.product.id
                        ),
                    "quantity":
                        "2.00",
                    "unit_price":
                        100,
                    "tax_rate":
                        "18.00",
                    "discount":
                        "10.00",
                },
            ],
            "notes":
                " Test order ",
        }

        with (
            patch.object(
                CustomerRepository,
                "get_by_id",
                return_value=self.customer,
            ),
            patch.object(
                WarehouseRepository,
                "get_by_id",
                return_value=self.warehouse,
            ),
            patch.object(
                ProductRepository,
                "get_by_id",
                return_value=self.product,
            ),
        ):
            values = (
                SalesOrderAPIService
                .validate_create_payload(
                    organization=(
                        self.organization
                    ),
                    payload=payload,
                )
            )

        self.assertEqual(
            values["customer"],
            self.customer,
        )

        self.assertEqual(
            values["warehouse"],
            self.warehouse,
        )

        self.assertEqual(
            values["raw_items"][0][
                "quantity"
            ],
            Decimal("2.00"),
        )

        self.assertEqual(
            values["raw_items"][0][
                "unit_price"
            ],
            Decimal("100"),
        )

        self.assertEqual(
            values["notes"],
            "Test order",
        )

    def test_service_rejects_cross_tenant_customer(
        self,
    ):
        with patch.object(
            CustomerRepository,
            "get_by_id",
            return_value=None,
        ):
            with self.assertRaises(
                SalesOrderAPIValidationError
            ) as context:
                (
                    SalesOrderAPIService
                    .validate_create_payload(
                        organization=(
                            self.organization
                        ),
                        payload={
                            "customer_id":
                                str(
                                    ObjectId()
                                ),
                            "warehouse_id":
                                str(
                                    self.warehouse.id
                                ),
                            "order_date":
                                "2026-08-28",
                            "items": [
                                {
                                    "product_id":
                                        str(
                                            self.product.id
                                        ),
                                    "quantity":
                                        "1.00",
                                    "unit_price":
                                        "100.00",
                                },
                            ],
                        },
                    )
                )

        self.assertIn(
            "customer_id",
            context.exception.details,
        )

    def test_service_rejects_protected_fields(
        self,
    ):
        with self.assertRaises(
            SalesOrderAPIValidationError
        ) as context:
            (
                SalesOrderAPIService
                .validate_update_payload(
                    organization=(
                        self.organization
                    ),
                    sales_order=(
                        self.sales_order
                    ),
                    payload={
                        "status":
                            "CONFIRMED",
                        "total_amount":
                            "1.00",
                    },
                )
            )

        self.assertIn(
            "status",
            context.exception.details,
        )

        self.assertIn(
            "total_amount",
            context.exception.details,
        )

    # ==================================================
    # METHOD RESTRICTION
    # ==================================================

    def test_sales_order_collection_rejects_delete(
        self,
    ):
        response = self.client.delete(
            self.SALES_ORDERS_URL
        )

        self.assert_error_contract(
            response,
            405,
            "METHOD_NOT_ALLOWED",
        )