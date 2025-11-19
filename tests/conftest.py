"""Pytest fixtures for LienOS tests."""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal

from core.storage import FirestoreClient


@pytest.fixture
def test_tenant_id():
    """Provide a test tenant ID."""
    return "test-tenant-001"


@pytest.fixture
def storage():
    """Provide a local storage client for testing."""
    # Uses local in-memory storage, no Google Cloud needed
    return FirestoreClient(project_id="local-dev")


@pytest.fixture
def sample_lien_data(test_tenant_id):
    """Provide sample lien data for testing."""
    return {
        "certificate_number": "2024-TEST-001",
        "purchase_amount": 5000.00,
        "interest_rate": 18.0,
        "sale_date": (date.today() - timedelta(days=180)).isoformat(),
        "redemption_deadline": (date.today() + timedelta(days=185)).isoformat(),
        "county": "Test County",
        "property_address": "123 Test Street, Test City, TS 12345",
        "parcel_id": "12-34-56-789-000"
    }


@pytest.fixture
def sample_lien_data_2(test_tenant_id):
    """Provide second sample lien data for testing."""
    return {
        "certificate_number": "2024-TEST-002",
        "purchase_amount": 10000.00,
        "interest_rate": 12.0,
        "sale_date": (date.today() - timedelta(days=90)).isoformat(),
        "redemption_deadline": (date.today() + timedelta(days=275)).isoformat(),
        "county": "Another County",
        "property_address": "456 Another Ave, Other City, OC 67890",
        "parcel_id": "98-76-54-321-000"
    }


@pytest.fixture
def sample_payment_data():
    """Provide sample payment data for testing."""
    return {
        "amount": 1000.00,
        "payment_date": date.today().isoformat()
    }


@pytest.fixture
def sample_notification_data():
    """Provide sample notification data for testing."""
    return {
        "notification_type": "PAYMENT_RECEIVED",
        "title": "Test Notification",
        "message": "This is a test notification message.",
        "priority": "normal",
        "channels": ["email", "in_app"],
        "action_required": False
    }


@pytest.fixture
async def created_lien(storage, test_tenant_id, sample_lien_data):
    """Create and return a lien for testing."""
    from agents.lien_tracker.agent import LienTrackerAgent

    agent = LienTrackerAgent(storage=storage)
    result = await agent.run(
        tenant_id=test_tenant_id,
        task="create_lien",
        parameters=sample_lien_data
    )
    return result
