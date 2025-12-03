"""Tests for LienOS FastAPI endpoints."""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

from api.main import app


# Create test client
client = TestClient(app)

# Test tenant ID for all requests
TEST_TENANT_ID = "api-test-tenant-001"


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "LienOS API"

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "LienOS API"
        assert "docs" in data


class TestLienEndpoints:
    """Tests for lien CRUD endpoints."""

    def test_create_lien(self):
        """Test creating a lien via API."""
        lien_data = {
            "certificate_number": "API-2024-001",
            "purchase_amount": 7500.00,
            "interest_rate": 15.0,
            "sale_date": (date.today() - timedelta(days=60)).isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=305)).isoformat(),
            "county": "API Test County",
            "property_address": "789 API Street",
            "parcel_id": "API-123-456"
        }

        response = client.post(
            "/api/liens",
            json=lien_data,
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["created"] is True
        assert "lien_id" in data["data"]

    def test_create_lien_missing_tenant_id(self):
        """Test that missing tenant ID returns 422."""
        lien_data = {
            "certificate_number": "API-2024-002",
            "purchase_amount": 5000.00,
            "interest_rate": 12.0,
            "sale_date": date.today().isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=365)).isoformat(),
            "county": "Test County",
            "property_address": "Test Address",
            "parcel_id": "TEST-001"
        }

        response = client.post("/api/liens", json=lien_data)

        assert response.status_code == 422  # Validation error

    def test_list_liens(self):
        """Test listing liens via API."""
        # First create a lien
        lien_data = {
            "certificate_number": "API-2024-003",
            "purchase_amount": 3000.00,
            "interest_rate": 10.0,
            "sale_date": date.today().isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=365)).isoformat(),
            "county": "List Test County",
            "property_address": "List Test Address",
            "parcel_id": "LIST-001"
        }

        client.post(
            "/api/liens",
            json=lien_data,
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        # List liens
        response = client.get(
            "/api/liens",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] >= 1

    def test_list_liens_with_filter(self):
        """Test listing liens with status filter."""
        response = client.get(
            "/api/liens",
            params={"status": "ACTIVE"},
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_lien_not_found(self):
        """Test getting a non-existent lien."""
        response = client.get(
            "/api/liens/non-existent-lien-id",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 404


class TestInterestEndpoints:
    """Tests for interest calculation endpoints."""

    def test_calculate_interest(self):
        """Test calculating interest via API."""
        # First create a lien
        lien_data = {
            "certificate_number": "API-INT-001",
            "purchase_amount": 10000.00,
            "interest_rate": 18.0,
            "sale_date": (date.today() - timedelta(days=100)).isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=265)).isoformat(),
            "county": "Interest Test County",
            "property_address": "Interest Test Address",
            "parcel_id": "INT-001"
        }

        create_response = client.post(
            "/api/liens",
            json=lien_data,
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )
        lien_id = create_response.json()["data"]["lien_id"]

        # Calculate interest
        response = client.post(
            "/api/interest/calculate",
            json={"lien_id": lien_id},
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["lien_id"] == lien_id
        assert data["principal"] == 10000.00
        assert data["interest_accrued"] >= 0
        assert data["total_owed"] >= data["principal"]


class TestPaymentEndpoints:
    """Tests for payment endpoints."""

    def test_record_payment(self):
        """Test recording a payment via API."""
        # First create a lien
        lien_data = {
            "certificate_number": "API-PAY-001",
            "purchase_amount": 5000.00,
            "interest_rate": 12.0,
            "sale_date": date.today().isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=365)).isoformat(),
            "county": "Payment Test County",
            "property_address": "Payment Test Address",
            "parcel_id": "PAY-001"
        }

        create_response = client.post(
            "/api/liens",
            json=lien_data,
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )
        lien_id = create_response.json()["data"]["lien_id"]

        # Record payment
        response = client.post(
            "/api/payments/record",
            json={
                "lien_id": lien_id,
                "amount": 1000.00
            },
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["lien_id"] == lien_id
        assert data["amount"] == 1000.00
        assert "payment_id" in data


class TestDeadlineEndpoints:
    """Tests for deadline endpoints."""

    def test_check_deadlines(self):
        """Test checking deadlines via API."""
        response = client.post(
            "/api/deadlines/check",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert "deadlines_checked" in data
        assert "alerts_sent" in data


class TestPortfolioEndpoints:
    """Tests for portfolio dashboard endpoints."""

    def test_calculate_portfolio_summary(self):
        """Test calculating portfolio summary via API."""
        # First create a lien
        lien_data = {
            "certificate_number": "API-PORT-001",
            "purchase_amount": 8000.00,
            "interest_rate": 14.0,
            "sale_date": (date.today() - timedelta(days=30)).isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=335)).isoformat(),
            "county": "Portfolio Test County",
            "property_address": "Portfolio Test Address",
            "parcel_id": "PORT-001"
        }

        client.post(
            "/api/liens",
            json=lien_data,
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        # Calculate summary
        response = client.post(
            "/api/portfolio/summary",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_liens"] >= 1
        assert "total_invested" in data["data"]

    def test_get_portfolio_stats(self):
        """Test getting portfolio stats via API."""
        # First calculate summary to have cached stats
        client.post(
            "/api/portfolio/summary",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        # Get stats
        response = client.get(
            "/api/portfolio/stats",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_generate_performance_report(self):
        """Test generating performance report via API."""
        response = client.get(
            "/api/portfolio/report",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "summary" in data["data"]


class TestNotificationEndpoints:
    """Tests for notification endpoints."""

    def test_send_notification(self):
        """Test sending a notification via API."""
        response = client.post(
            "/api/notifications",
            json={
                "notification_type": "PAYMENT_RECEIVED",
                "title": "API Test Notification",
                "message": "This is a test notification from the API."
            },
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["created"] is True

    def test_get_notifications(self):
        """Test getting notifications via API."""
        # First create a notification
        client.post(
            "/api/notifications",
            json={
                "notification_type": "DEADLINE_APPROACHING",
                "title": "Test",
                "message": "Test message"
            },
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        # Get notifications
        response = client.get(
            "/api/notifications",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] >= 1


class TestDocumentEndpoints:
    """Tests for document generation endpoints."""

    def test_generate_redemption_notice(self):
        """Test generating redemption notice via API."""
        # First create a lien
        lien_data = {
            "certificate_number": "API-DOC-001",
            "purchase_amount": 6000.00,
            "interest_rate": 16.0,
            "sale_date": (date.today() - timedelta(days=45)).isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=320)).isoformat(),
            "county": "Document Test County",
            "property_address": "Document Test Address",
            "parcel_id": "DOC-001"
        }

        create_response = client.post(
            "/api/liens",
            json=lien_data,
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )
        lien_id = create_response.json()["data"]["lien_id"]

        # Generate notice
        response = client.post(
            "/api/documents/redemption-notice",
            json={"lien_id": lien_id},
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["document_type"] == "REDEMPTION_NOTICE"

    def test_generate_portfolio_report_document(self):
        """Test generating portfolio report document via API."""
        response = client.post(
            "/api/documents/portfolio-report",
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["document_type"] == "PORTFOLIO_REPORT"

    def test_generate_tax_form(self):
        """Test generating tax form via API."""
        response = client.post(
            "/api/documents/tax-form",
            json={"tax_year": 2024},
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["document_type"] == "TAX_FORM"
        assert data["data"]["tax_year"] == 2024


class TestEmailSmsEndpoints:
    """Tests for email and SMS endpoints."""

    def test_send_email(self):
        """Test queueing an email via API."""
        response = client.post(
            "/api/email/send",
            json={
                "to_email": "api-test@example.com",
                "subject": "API Test Email",
                "body": "This is a test email from the API."
            },
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "queued"

    def test_send_sms(self):
        """Test queueing an SMS via API."""
        response = client.post(
            "/api/sms/send",
            json={
                "to_phone": "+15559876543",
                "message": "API test SMS message"
            },
            headers={"X-Tenant-ID": TEST_TENANT_ID}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "queued"
