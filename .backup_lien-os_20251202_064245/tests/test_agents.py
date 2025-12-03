"""Tests for all LienOS agents."""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal

from agents.interest_calculator.agent import InterestCalculatorAgent
from agents.deadline_alert.agent import DeadlineAlertAgent
from agents.payment_monitor.agent import PaymentMonitorAgent
from agents.lien_tracker.agent import LienTrackerAgent
from agents.communication.agent import CommunicationAgent
from agents.portfolio_dashboard.agent import PortfolioDashboardAgent
from agents.document_generator.agent import DocumentGeneratorAgent


# =============================================================================
# LienTrackerAgent Tests
# =============================================================================

class TestLienTrackerAgent:
    """Tests for LienTrackerAgent CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_lien(self, storage, test_tenant_id, sample_lien_data):
        """Test creating a new lien."""
        agent = LienTrackerAgent(storage=storage)

        result = await agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )

        assert result["created"] is True
        assert result["certificate_number"] == sample_lien_data["certificate_number"]
        assert result["purchase_amount"] == sample_lien_data["purchase_amount"]
        assert result["status"] == "ACTIVE"
        assert "lien_id" in result
        assert "deadline_id" in result

    @pytest.mark.asyncio
    async def test_get_lien(self, storage, test_tenant_id, sample_lien_data):
        """Test retrieving a lien by ID."""
        agent = LienTrackerAgent(storage=storage)

        # Create lien first
        create_result = await agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Get lien
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="get_lien",
            lien_ids=[lien_id]
        )

        assert result["found"] is True
        assert result["lien_id"] == lien_id
        assert result["certificate_number"] == sample_lien_data["certificate_number"]

    @pytest.mark.asyncio
    async def test_list_liens(self, storage, test_tenant_id, sample_lien_data, sample_lien_data_2):
        """Test listing liens with filters."""
        agent = LienTrackerAgent(storage=storage)

        # Create two liens
        await agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        await agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data_2
        )

        # List all liens
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="list_liens",
            parameters={"limit": 100}
        )

        assert result["count"] >= 2
        assert len(result["liens"]) >= 2

    @pytest.mark.asyncio
    async def test_update_lien(self, storage, test_tenant_id, sample_lien_data):
        """Test updating a lien."""
        agent = LienTrackerAgent(storage=storage)

        # Create lien
        create_result = await agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Update lien
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="update_lien",
            lien_ids=[lien_id],
            parameters={"county": "Updated County"}
        )

        assert result["updated"] is True
        assert "county" in result["updated_fields"]

    @pytest.mark.asyncio
    async def test_delete_lien_soft(self, storage, test_tenant_id, sample_lien_data):
        """Test soft deleting a lien."""
        agent = LienTrackerAgent(storage=storage)

        # Create lien
        create_result = await agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Soft delete
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="delete_lien",
            lien_ids=[lien_id],
            parameters={"hard_delete": False}
        )

        assert result["deleted"] is True
        assert result["delete_type"] == "soft"
        assert result["new_status"] == "EXPIRED"


# =============================================================================
# InterestCalculatorAgent Tests
# =============================================================================

class TestInterestCalculatorAgent:
    """Tests for InterestCalculatorAgent."""

    @pytest.mark.asyncio
    async def test_calculate_interest(self, storage, test_tenant_id, sample_lien_data):
        """Test interest calculation for a lien."""
        # First create a lien
        lien_agent = LienTrackerAgent(storage=storage)
        create_result = await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Calculate interest
        agent = InterestCalculatorAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="calculate_interest",
            lien_ids=[lien_id]
        )

        assert result["lien_id"] == lien_id
        assert result["principal"] == sample_lien_data["purchase_amount"]
        assert result["interest_rate"] == sample_lien_data["interest_rate"]
        assert result["days_elapsed"] >= 0
        assert result["interest_accrued"] >= 0
        assert result["total_owed"] >= result["principal"]

    @pytest.mark.asyncio
    async def test_interest_increases_with_time(self, storage, test_tenant_id):
        """Test that interest increases with more days elapsed."""
        # Create lien with older sale date
        old_lien_data = {
            "certificate_number": "2024-OLD-001",
            "purchase_amount": 5000.00,
            "interest_rate": 18.0,
            "sale_date": (date.today() - timedelta(days=365)).isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=365)).isoformat(),
            "county": "Test County",
            "property_address": "999 Old Street",
            "parcel_id": "99-99-99-999"
        }

        lien_agent = LienTrackerAgent(storage=storage)
        create_result = await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=old_lien_data
        )
        lien_id = create_result["lien_id"]

        agent = InterestCalculatorAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="calculate_interest",
            lien_ids=[lien_id]
        )

        # With 365 days at 18% on $5000, interest should be significant
        assert result["days_elapsed"] >= 365
        assert result["interest_accrued"] > 0
        # Approximate: 5000 * 0.18 = 900 for one year
        assert result["interest_accrued"] >= 800  # Allow some variance


# =============================================================================
# DeadlineAlertAgent Tests
# =============================================================================

class TestDeadlineAlertAgent:
    """Tests for DeadlineAlertAgent."""

    @pytest.mark.asyncio
    async def test_create_deadline(self, storage, test_tenant_id, sample_lien_data):
        """Test creating a deadline for a lien."""
        # Create lien first
        lien_agent = LienTrackerAgent(storage=storage)
        create_result = await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Note: Deadline is already created by LienTrackerAgent
        # But we can verify it exists
        assert "deadline_id" in create_result

    @pytest.mark.asyncio
    async def test_check_deadlines(self, storage, test_tenant_id, sample_lien_data):
        """Test checking all deadlines."""
        # Create lien (which creates deadline)
        lien_agent = LienTrackerAgent(storage=storage)
        await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )

        # Check deadlines
        agent = DeadlineAlertAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="check_deadlines"
        )

        assert "deadlines_checked" in result
        assert "alerts_sent" in result
        assert "check_date" in result
        assert result["deadlines_checked"] >= 1


# =============================================================================
# PaymentMonitorAgent Tests
# =============================================================================

class TestPaymentMonitorAgent:
    """Tests for PaymentMonitorAgent."""

    @pytest.mark.asyncio
    async def test_record_payment(self, storage, test_tenant_id, sample_lien_data, sample_payment_data):
        """Test recording a payment for a lien."""
        # Create lien
        lien_agent = LienTrackerAgent(storage=storage)
        create_result = await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Record payment
        agent = PaymentMonitorAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="record_payment",
            lien_ids=[lien_id],
            parameters=sample_payment_data
        )

        assert result["lien_id"] == lien_id
        assert result["amount"] == sample_payment_data["amount"]
        assert "payment_id" in result
        assert "total_paid" in result
        assert "total_owed" in result
        assert "notification_id" in result

    @pytest.mark.asyncio
    async def test_full_redemption(self, storage, test_tenant_id):
        """Test that paying full amount redeems the lien."""
        # Create lien with small amount
        small_lien_data = {
            "certificate_number": "2024-SMALL-001",
            "purchase_amount": 100.00,
            "interest_rate": 10.0,
            "sale_date": date.today().isoformat(),  # Today, no interest accrued
            "redemption_deadline": (date.today() + timedelta(days=365)).isoformat(),
            "county": "Test County",
            "property_address": "Small Street",
            "parcel_id": "00-00-00-001"
        }

        lien_agent = LienTrackerAgent(storage=storage)
        create_result = await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=small_lien_data
        )
        lien_id = create_result["lien_id"]

        # Pay more than enough to redeem
        agent = PaymentMonitorAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="record_payment",
            lien_ids=[lien_id],
            parameters={"amount": 150.00}
        )

        assert result["is_fully_redeemed"] is True
        assert result["lien_status"] == "REDEEMED"

    @pytest.mark.asyncio
    async def test_reconcile_lien(self, storage, test_tenant_id, sample_lien_data):
        """Test reconciling payments for a lien."""
        # Create lien
        lien_agent = LienTrackerAgent(storage=storage)
        create_result = await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Record a payment
        agent = PaymentMonitorAgent(storage=storage)
        await agent.run(
            tenant_id=test_tenant_id,
            task="record_payment",
            lien_ids=[lien_id],
            parameters={"amount": 500.00}
        )

        # Reconcile
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="reconcile_lien",
            lien_ids=[lien_id]
        )

        assert result["lien_id"] == lien_id
        assert result["total_paid"] == 500.00
        assert result["payment_count"] == 1
        assert len(result["completed_payments"]) == 1


# =============================================================================
# CommunicationAgent Tests
# =============================================================================

class TestCommunicationAgent:
    """Tests for CommunicationAgent."""

    @pytest.mark.asyncio
    async def test_send_notification(self, storage, test_tenant_id, sample_notification_data):
        """Test sending a notification."""
        agent = CommunicationAgent(storage=storage)

        result = await agent.run(
            tenant_id=test_tenant_id,
            task="send_notification",
            parameters=sample_notification_data
        )

        assert result["created"] is True
        assert result["title"] == sample_notification_data["title"]
        assert "notification_id" in result

    @pytest.mark.asyncio
    async def test_get_notifications(self, storage, test_tenant_id, sample_notification_data):
        """Test retrieving notifications."""
        agent = CommunicationAgent(storage=storage)

        # Create notification
        await agent.run(
            tenant_id=test_tenant_id,
            task="send_notification",
            parameters=sample_notification_data
        )

        # Get notifications
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="get_notifications",
            parameters={"limit": 50}
        )

        assert result["count"] >= 1
        assert len(result["notifications"]) >= 1

    @pytest.mark.asyncio
    async def test_mark_notification_read(self, storage, test_tenant_id, sample_notification_data):
        """Test marking a notification as read."""
        agent = CommunicationAgent(storage=storage)

        # Create notification
        create_result = await agent.run(
            tenant_id=test_tenant_id,
            task="send_notification",
            parameters=sample_notification_data
        )
        notification_id = create_result["notification_id"]

        # Mark as read
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="mark_notification_read",
            parameters={"notification_id": notification_id}
        )

        assert result["marked_read"] is True
        assert "read_at" in result

    @pytest.mark.asyncio
    async def test_send_email(self, storage, test_tenant_id):
        """Test queueing an email."""
        agent = CommunicationAgent(storage=storage)

        result = await agent.run(
            tenant_id=test_tenant_id,
            task="send_email",
            parameters={
                "to_email": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email body."
            }
        )

        assert result["status"] == "queued"
        assert "email_id" in result

    @pytest.mark.asyncio
    async def test_send_sms(self, storage, test_tenant_id):
        """Test queueing an SMS."""
        agent = CommunicationAgent(storage=storage)

        result = await agent.run(
            tenant_id=test_tenant_id,
            task="send_sms",
            parameters={
                "to_phone": "+15551234567",
                "message": "This is a test SMS message."
            }
        )

        assert result["status"] == "queued"
        assert "sms_id" in result


# =============================================================================
# PortfolioDashboardAgent Tests
# =============================================================================

class TestPortfolioDashboardAgent:
    """Tests for PortfolioDashboardAgent."""

    @pytest.mark.asyncio
    async def test_calculate_portfolio_summary(self, storage, test_tenant_id, sample_lien_data, sample_lien_data_2):
        """Test calculating portfolio summary."""
        # Create some liens
        lien_agent = LienTrackerAgent(storage=storage)
        await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data_2
        )

        # Calculate summary
        agent = PortfolioDashboardAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="calculate_portfolio_summary"
        )

        assert result["total_liens"] >= 2
        assert result["active_liens"] >= 2
        assert result["total_invested"] >= 15000  # 5000 + 10000
        assert "liens_by_status" in result
        assert "liens_by_county" in result
        assert "portfolio_id" in result

    @pytest.mark.asyncio
    async def test_get_portfolio_stats(self, storage, test_tenant_id, sample_lien_data):
        """Test getting cached portfolio stats."""
        # Create lien and calculate summary first
        lien_agent = LienTrackerAgent(storage=storage)
        await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )

        agent = PortfolioDashboardAgent(storage=storage)
        await agent.run(
            tenant_id=test_tenant_id,
            task="calculate_portfolio_summary"
        )

        # Get stats
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="get_portfolio_stats"
        )

        assert result["found"] is True
        assert "total_liens" in result

    @pytest.mark.asyncio
    async def test_generate_performance_report(self, storage, test_tenant_id, sample_lien_data):
        """Test generating performance report."""
        # Create lien
        lien_agent = LienTrackerAgent(storage=storage)
        await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )

        # Generate report
        agent = PortfolioDashboardAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="generate_performance_report"
        )

        assert "summary" in result
        assert "detailed_liens" in result
        assert "portfolio_health_score" in result
        assert "recommendations" in result


# =============================================================================
# DocumentGeneratorAgent Tests
# =============================================================================

class TestDocumentGeneratorAgent:
    """Tests for DocumentGeneratorAgent."""

    @pytest.mark.asyncio
    async def test_generate_redemption_notice(self, storage, test_tenant_id, sample_lien_data):
        """Test generating a redemption notice."""
        # Create lien
        lien_agent = LienTrackerAgent(storage=storage)
        create_result = await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Generate notice
        agent = DocumentGeneratorAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="generate_redemption_notice",
            lien_ids=[lien_id]
        )

        assert result["lien_id"] == lien_id
        assert result["document_type"] == "REDEMPTION_NOTICE"
        assert result["format"] == "html"
        assert "content" in result
        assert "<html>" in result["content"]
        assert sample_lien_data["property_address"] in result["content"]

    @pytest.mark.asyncio
    async def test_generate_portfolio_report(self, storage, test_tenant_id, sample_lien_data):
        """Test generating a portfolio report document."""
        # Create lien
        lien_agent = LienTrackerAgent(storage=storage)
        await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )

        # Generate report
        agent = DocumentGeneratorAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="generate_portfolio_report"
        )

        assert result["document_type"] == "PORTFOLIO_REPORT"
        assert result["format"] == "html"
        assert "content" in result

    @pytest.mark.asyncio
    async def test_generate_payment_receipt(self, storage, test_tenant_id, sample_lien_data):
        """Test generating a payment receipt."""
        # Create lien
        lien_agent = LienTrackerAgent(storage=storage)
        create_result = await lien_agent.run(
            tenant_id=test_tenant_id,
            task="create_lien",
            parameters=sample_lien_data
        )
        lien_id = create_result["lien_id"]

        # Record payment
        payment_agent = PaymentMonitorAgent(storage=storage)
        payment_result = await payment_agent.run(
            tenant_id=test_tenant_id,
            task="record_payment",
            lien_ids=[lien_id],
            parameters={"amount": 1000.00}
        )
        payment_id = payment_result["payment_id"]

        # Generate receipt
        agent = DocumentGeneratorAgent(storage=storage)
        result = await agent.run(
            tenant_id=test_tenant_id,
            task="generate_payment_receipt",
            parameters={"payment_id": payment_id}
        )

        assert result["document_type"] == "PAYMENT_RECEIPT"
        assert result["payment_id"] == payment_id
        assert "content" in result

    @pytest.mark.asyncio
    async def test_generate_tax_form(self, storage, test_tenant_id):
        """Test generating a tax form."""
        agent = DocumentGeneratorAgent(storage=storage)

        result = await agent.run(
            tenant_id=test_tenant_id,
            task="generate_tax_form",
            parameters={"tax_year": 2024}
        )

        assert result["document_type"] == "TAX_FORM"
        assert result["tax_year"] == 2024
        assert "content" in result
        assert "1099" in result["content"] or "Interest Income" in result["content"]
