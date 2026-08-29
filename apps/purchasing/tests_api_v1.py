import json

from datetime import (
    date,
    datetime,
)
from decimal import (
    Decimal,
)
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
    PurchaseOrderAPISerializer,
    SupplierAPISerializer,
)
from apps.purchasing.repositories.supplier_repository import (
    SupplierRepository,
)
from apps.products.repositories.product_repository import (
    ProductRepository,
)
from apps.purchasing.repositories.purchase_order_repository import (
    PurchaseOrderRepository,
)
from apps.purchasing.services.supplier_api_service import (
    SupplierAPIService,
    SupplierAPIStateError,
    SupplierAPIValidationError,
)
from apps.purchasing.services.purchase_order_api_service import (
    PurchaseOrderAPIService,
    PurchaseOrderAPIStateError,
    PurchaseOrderAPIValidationError,
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


class PurchaseOrderAPIV1RegressionTestCase(
    SimpleTestCase
):

    PURCHASE_ORDERS_URL = (
        "/api/v1/purchase-orders/"
    )

    def setUp(self):
        now = datetime.utcnow()

        self.organization = SimpleNamespace(
            id=ObjectId(),
            name="Purchase Order Organization",
            email="purchasing@example.com",
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

        self.supplier = SimpleNamespace(
            id=ObjectId(),
            organization=self.organization,
            code="SUPP-PO-001",
            name="Purchase Order Supplier",
            email="supplier@example.com",
            phone="9999999999",
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

        self.product = SimpleNamespace(
            id=ObjectId(),
            organization=self.organization,
            sku="RAW-PO-001",
            name="Purchase Material",
            unit="piece",
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.purchase_order_item = (
            SimpleNamespace(
                product=self.product,
                quantity=Decimal("10.00"),
                received_quantity=(
                    Decimal("0.00")
                ),
                unit_price=Decimal("100.00"),
                tax_rate=Decimal("18.00"),
                discount=Decimal("50.00"),
                subtotal=Decimal("950.00"),
                tax_amount=Decimal("171.00"),
                total=Decimal("1121.00"),
            )
        )

        self.purchase_order = (
            SimpleNamespace(
                id=ObjectId(),
                organization=self.organization,
                po_number="PO-TEST000001",
                supplier=self.supplier,
                status="DRAFT",
                order_date=date(
                    2026,
                    8,
                    29,
                ),
                expected_delivery_date=(
                    date(
                        2026,
                        9,
                        5,
                    )
                ),
                items=[
                    self.purchase_order_item,
                ],
                subtotal=Decimal("950.00"),
                tax_amount=Decimal("171.00"),
                discount_amount=(
                    Decimal("50.00")
                ),
                total_amount=(
                    Decimal("1121.00")
                ),
                notes=(
                    "Regression purchase order."
                ),
                created_by=self.user,
                confirmed_at=None,
                cancelled_at=None,
                created_at=now,
                updated_at=now,
            )
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
        purchase_order=None,
    ):
        purchase_order = (
            purchase_order
            or
            self.purchase_order
        )

        return (
            f"{self.PURCHASE_ORDERS_URL}"
            f"{purchase_order.id}/"
        )

    def confirm_url(
        self,
        purchase_order=None,
    ):
        purchase_order = (
            purchase_order
            or
            self.purchase_order
        )

        return (
            f"{self.PURCHASE_ORDERS_URL}"
            f"{purchase_order.id}/confirm/"
        )

    def cancel_url(
        self,
        purchase_order=None,
    ):
        purchase_order = (
            purchase_order
            or
            self.purchase_order
        )

        return (
            f"{self.PURCHASE_ORDERS_URL}"
            f"{purchase_order.id}/cancel/"
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

    def test_anonymous_purchase_order_list_is_rejected(
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
                self.PURCHASE_ORDERS_URL
            )

        self.assert_error_contract(
            response,
            401,
            "UNAUTHORIZED",
        )

    # ==================================================
    # LIST
    # ==================================================

    def test_purchase_order_list_uses_query_pipeline(
        self,
    ):
        pipeline_result = {
            "items": [
                self.purchase_order,
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
                PurchaseOrderRepository,
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
                    f"{self.PURCHASE_ORDERS_URL}"
                    "?supplier_id="
                    f"{self.supplier.id}"
                    "&status=DRAFT"
                    "&sort=-created_at"
                )
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"][
                "purchase_orders"
            ][0]["po_number"],
            self.purchase_order.po_number,
        )

        pipeline_mock.assert_called_once()

    def test_purchase_order_list_without_permission_is_forbidden(
        self,
    ):
        with patch.object(
            AuthorizationService,
            "has_permission",
            return_value=False,
        ):
            response = self.client.get(
                self.PURCHASE_ORDERS_URL
            )

        self.assert_error_contract(
            response,
            403,
            "FORBIDDEN",
        )

    def test_purchase_order_query_error_uses_contract(
        self,
    ):
        pipeline_error = (
            APIQueryPipelineError(
                component="filtering",
                message=(
                    "Unsupported filter value."
                ),
                details={
                    "supplier_id": [
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
                PurchaseOrderRepository,
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
                    f"{self.PURCHASE_ORDERS_URL}"
                    "?supplier_id=invalid-id"
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

    def test_create_purchase_order(
        self,
    ):
        payload = {
            "supplier_id":
                str(
                    self.supplier.id
                ),
            "order_date":
                "2026-08-29",
            "expected_delivery_date":
                "2026-09-05",
            "items": [
                {
                    "product_id":
                        str(
                            self.product.id
                        ),
                    "quantity":
                        "10.00",
                    "unit_price":
                        "100.00",
                    "tax_rate":
                        "18.00",
                    "discount":
                        "50.00",
                },
            ],
            "notes":
                "Regression purchase order.",
        }

        with patch.object(
            PurchaseOrderAPIService,
            "create_purchase_order",
            return_value=self.purchase_order,
        ) as create_mock:
            response = self.client.post(
                self.PURCHASE_ORDERS_URL,
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
            body["data"][
                "purchase_order"
            ]["po_number"],
            self.purchase_order.po_number,
        )

        create_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            payload=payload,
        )

    def test_create_purchase_order_validation_error(
        self,
    ):
        with patch.object(
            PurchaseOrderAPIService,
            "create_purchase_order",
            side_effect=(
                PurchaseOrderAPIValidationError(
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
                self.PURCHASE_ORDERS_URL,
                data=json.dumps({
                    "supplier_id":
                        str(
                            self.supplier.id
                        ),
                    "order_date":
                        "2026-08-29",
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
    # DETAIL
    # ==================================================

    def test_purchase_order_detail(
        self,
    ):
        with patch.object(
            PurchaseOrderAPIService,
            "get_purchase_order",
            return_value=self.purchase_order,
        ) as get_mock:
            response = self.client.get(
                self.detail_url()
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"][
                "purchase_order"
            ]["id"],
            str(
                self.purchase_order.id
            ),
        )

        self.assertEqual(
            body["data"][
                "purchase_order"
            ]["items"][0][
                "remaining_quantity"
            ],
            "10.00",
        )

        get_mock.assert_called_once_with(
            organization=self.organization,
            purchase_order_id=str(
                self.purchase_order.id
            ),
        )

    def test_missing_purchase_order_returns_not_found(
        self,
    ):
        with patch.object(
            PurchaseOrderAPIService,
            "get_purchase_order",
            side_effect=LookupError(
                "Purchase order not found."
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

    def test_malformed_purchase_order_id_is_validation_error(
        self,
    ):
        response = self.client.get(
            (
                f"{self.PURCHASE_ORDERS_URL}"
                "invalid-id/"
            )
        )

        self.assert_error_contract(
            response,
            400,
            "VALIDATION_ERROR",
        )

    # ==================================================
    # UPDATE
    # ==================================================

    def test_update_purchase_order(
        self,
    ):
        payload = {
            "notes":
                "Updated purchase order.",
        }

        updated_purchase_order = (
            SimpleNamespace(
                **{
                    **vars(
                        self.purchase_order
                    ),
                    "notes":
                        (
                            "Updated purchase "
                            "order."
                        ),
                }
            )
        )

        with patch.object(
            PurchaseOrderAPIService,
            "update_purchase_order",
            return_value=(
                updated_purchase_order
            ),
        ) as update_mock:
            response = self.client.patch(
                self.detail_url(),
                data=json.dumps(
                    payload
                ),
                content_type="application/json",
            )

        body = self.assert_success_contract(
            response
        )

        self.assertEqual(
            body["data"][
                "purchase_order"
            ]["notes"],
            "Updated purchase order.",
        )

        update_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            purchase_order_id=str(
                self.purchase_order.id
            ),
            payload=payload,
        )

    def test_non_draft_update_is_unprocessable(
        self,
    ):
        with patch.object(
            PurchaseOrderAPIService,
            "update_purchase_order",
            side_effect=(
                PurchaseOrderAPIStateError(
                    message=(
                        "Only draft purchase "
                        "orders can be updated."
                    ),
                    details={
                        "status": [
                            "CONFIRMED",
                        ],
                    },
                )
            ),
        ):
            response = self.client.patch(
                self.detail_url(),
                data=json.dumps({
                    "notes":
                        "Cannot update.",
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

    def test_confirm_purchase_order(
        self,
    ):
        confirmed_purchase_order = (
            SimpleNamespace(
                **{
                    **vars(
                        self.purchase_order
                    ),
                    "status":
                        "CONFIRMED",
                    "confirmed_at":
                        datetime.utcnow(),
                }
            )
        )

        with patch.object(
            PurchaseOrderAPIService,
            "confirm_purchase_order",
            return_value=(
                confirmed_purchase_order
            ),
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
            body["data"][
                "purchase_order"
            ]["status"],
            "CONFIRMED",
        )

        confirm_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            purchase_order_id=str(
                self.purchase_order.id
            ),
        )

    def test_confirm_non_draft_order_is_unprocessable(
        self,
    ):
        with patch.object(
            PurchaseOrderAPIService,
            "confirm_purchase_order",
            side_effect=(
                PurchaseOrderAPIStateError(
                    message=(
                        "Only draft purchase "
                        "orders can be confirmed."
                    ),
                    details={
                        "status": [
                            "CONFIRMED",
                        ],
                    },
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

    # ==================================================
    # CANCEL
    # ==================================================

    def test_cancel_purchase_order(
        self,
    ):
        cancelled_purchase_order = (
            SimpleNamespace(
                **{
                    **vars(
                        self.purchase_order
                    ),
                    "status":
                        "CANCELLED",
                    "cancelled_at":
                        datetime.utcnow(),
                }
            )
        )

        with patch.object(
            PurchaseOrderAPIService,
            "cancel_purchase_order",
            return_value=(
                cancelled_purchase_order
            ),
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
            body["data"][
                "purchase_order"
            ]["status"],
            "CANCELLED",
        )

        cancel_mock.assert_called_once_with(
            user=self.user,
            organization=self.organization,
            purchase_order_id=str(
                self.purchase_order.id
            ),
        )

    def test_received_purchase_order_cannot_be_cancelled(
        self,
    ):
        with patch.object(
            PurchaseOrderAPIService,
            "cancel_purchase_order",
            side_effect=(
                PurchaseOrderAPIStateError(
                    message=(
                        "Received purchase orders "
                        "cannot be cancelled."
                    ),
                    details={
                        "status": [
                            "RECEIVED",
                        ],
                    },
                )
            ),
        ):
            response = self.client.post(
                self.cancel_url(),
                data=json.dumps({}),
                content_type="application/json",
            )

        self.assert_error_contract(
            response,
            422,
            "UNPROCESSABLE_ENTITY",
        )

    # ==================================================
    # SERIALIZATION
    # ==================================================

    def test_purchase_order_serializer_has_safe_fields(
        self,
    ):
        serialized = (
            PurchaseOrderAPISerializer
            .serialize_detail(
                self.purchase_order
            )
        )

        self.assertEqual(
            serialized["id"],
            str(
                self.purchase_order.id
            ),
        )

        self.assertEqual(
            serialized["order_date"],
            "2026-08-29",
        )

        self.assertEqual(
            serialized["supplier"]["id"],
            str(
                self.supplier.id
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
            "1121.00",
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
            "supplier_id":
                str(
                    self.supplier.id
                ),
            "order_date":
                "2026-08-29",
            "expected_delivery_date":
                "2026-09-05",
            "items": [
                {
                    "product_id":
                        str(
                            self.product.id
                        ),
                    "quantity":
                        "10.00",
                    "unit_price":
                        "100.00",
                    "tax_rate":
                        "18.00",
                    "discount":
                        "50.00",
                },
            ],
            "notes":
                " Test purchase order ",
        }

        with (
            patch.object(
                SupplierRepository,
                "get_by_id",
                return_value=self.supplier,
            ),
            patch.object(
                ProductRepository,
                "get_by_id",
                return_value=self.product,
            ),
        ):
            values = (
                PurchaseOrderAPIService
                .validate_create_payload(
                    organization=(
                        self.organization
                    ),
                    payload=payload,
                )
            )

        self.assertEqual(
            values["supplier"],
            self.supplier,
        )

        self.assertEqual(
            values["order_date"],
            date(
                2026,
                8,
                29,
            ),
        )

        self.assertEqual(
            values[
                "expected_delivery_date"
            ],
            date(
                2026,
                9,
                5,
            ),
        )

        self.assertEqual(
            values["raw_items"][0][
                "quantity"
            ],
            Decimal("10.00"),
        )

        self.assertEqual(
            values["raw_items"][0][
                "product"
            ],
            self.product,
        )

        self.assertEqual(
            values["notes"],
            "Test purchase order",
        )

    def test_service_rejects_cross_tenant_supplier(
        self,
    ):
        with patch.object(
            SupplierRepository,
            "get_by_id",
            return_value=None,
        ):
            with self.assertRaises(
                PurchaseOrderAPIValidationError
            ) as context:
                (
                    PurchaseOrderAPIService
                    .validate_create_payload(
                        organization=(
                            self.organization
                        ),
                        payload={
                            "supplier_id":
                                str(
                                    ObjectId()
                                ),
                            "order_date":
                                "2026-08-29",
                            "items": [
                                {
                                    "product_id":
                                        str(
                                            self.product.id
                                        ),
                                    "quantity":
                                        "1.00",
                                    "unit_price":
                                        "10.00",
                                },
                            ],
                        },
                    )
                )

        self.assertIn(
            "supplier_id",
            context.exception.details,
        )

    def test_service_rejects_cross_tenant_product(
        self,
    ):
        with (
            patch.object(
                SupplierRepository,
                "get_by_id",
                return_value=self.supplier,
            ),
            patch.object(
                ProductRepository,
                "get_by_id",
                return_value=None,
            ),
        ):
            with self.assertRaises(
                PurchaseOrderAPIValidationError
            ) as context:
                (
                    PurchaseOrderAPIService
                    .validate_create_payload(
                        organization=(
                            self.organization
                        ),
                        payload={
                            "supplier_id":
                                str(
                                    self.supplier.id
                                ),
                            "order_date":
                                "2026-08-29",
                            "items": [
                                {
                                    "product_id":
                                        str(
                                            ObjectId()
                                        ),
                                    "quantity":
                                        "1.00",
                                    "unit_price":
                                        "10.00",
                                },
                            ],
                        },
                    )
                )

        self.assertIn(
            "items.0.product_id",
            context.exception.details,
        )

    def test_service_rejects_protected_fields(
        self,
    ):
        with self.assertRaises(
            PurchaseOrderAPIValidationError
        ) as context:
            (
                PurchaseOrderAPIService
                .validate_update_payload(
                    organization=(
                        self.organization
                    ),
                    purchase_order=(
                        self.purchase_order
                    ),
                    payload={
                        "organization_id":
                            str(
                                self.other_organization.id
                            ),
                        "status":
                            "CONFIRMED",
                        "po_number":
                            "CHANGED-PO",
                    },
                )
            )

        self.assertIn(
            "organization_id",
            context.exception.details,
        )

        self.assertIn(
            "status",
            context.exception.details,
        )

        self.assertIn(
            "po_number",
            context.exception.details,
        )

    def test_service_rejects_delivery_before_order_date(
        self,
    ):
        with (
            patch.object(
                SupplierRepository,
                "get_by_id",
                return_value=self.supplier,
            ),
            patch.object(
                ProductRepository,
                "get_by_id",
                return_value=self.product,
            ),
        ):
            with self.assertRaises(
                PurchaseOrderAPIValidationError
            ) as context:
                (
                    PurchaseOrderAPIService
                    .validate_create_payload(
                        organization=(
                            self.organization
                        ),
                        payload={
                            "supplier_id":
                                str(
                                    self.supplier.id
                                ),
                            "order_date":
                                "2026-08-29",
                            "expected_delivery_date":
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
                                        "10.00",
                                },
                            ],
                        },
                    )
                )

        self.assertIn(
            "expected_delivery_date",
            context.exception.details,
        )

    # ==================================================
    # METHOD RESTRICTIONS
    # ==================================================

    def test_purchase_order_collection_rejects_delete(
        self,
    ):
        response = self.client.delete(
            self.PURCHASE_ORDERS_URL
        )

        self.assert_error_contract(
            response,
            405,
            "METHOD_NOT_ALLOWED",
        )

    def test_purchase_order_detail_rejects_post(
        self,
    ):
        response = self.client.post(
            self.detail_url(),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assert_error_contract(
            response,
            405,
            "METHOD_NOT_ALLOWED",
        )