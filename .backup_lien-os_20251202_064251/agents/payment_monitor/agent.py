from typing import Dict, Any, List, Optional
from datetime import datetime, date
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import (
    AgentContext,
    Payment,
    PaymentStatus,
    LienStatus,
    Notification,
    NotificationType
)
from core.storage import FirestoreClient
from agents.interest_calculator.agent import InterestCalculatorAgent


class PaymentMonitorAgent(LienOSBaseAgent):
    """
    Agent that monitors and processes payments for tax liens.
    Records payments, checks for full redemption, and sends notifications.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="PaymentMonitor",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return ["record_payment", "verify_payment", "reconcile_lien"]

    def _register_tools(self) -> None:
        """No external tools needed for payment monitoring"""
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Main agent logic.

        Handles tasks:
        - record_payment: Record a payment and check for full redemption
        - verify_payment: Verify a payment was properly recorded
        - reconcile_lien: Reconcile all payments for a lien

        Returns:
            Dict with payment details and redemption status
        """
        if context.task == "record_payment":
            return await self._record_payment(context)
        elif context.task == "verify_payment":
            return await self._verify_payment(context)
        elif context.task == "reconcile_lien":
            return await self._reconcile_lien(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _record_payment(self, context: AgentContext) -> Dict[str, Any]:
        """
        Record a payment for a lien.

        Required parameters:
        - lien_ids[0]: The lien ID
        - parameters.amount: Payment amount
        - parameters.payment_date: Optional, defaults to today

        Returns:
            Dict with payment_id, redemption status, and notification details
        """
        if not context.lien_ids or len(context.lien_ids) == 0:
            raise ValueError("lien_id required in context.lien_ids")

        lien_id = context.lien_ids[0]
        amount = context.parameters.get("amount")

        if amount is None:
            raise ValueError("amount required in parameters")

        payment_date = context.parameters.get("payment_date", date.today())
        if isinstance(payment_date, str):
            payment_date = date.fromisoformat(payment_date)

        # Validate lien exists and is active
        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)
        if not lien_data:
            raise ValueError(f"Lien {lien_id} not found")

        if lien_data.get("status") == LienStatus.REDEEMED.value:
            raise ValueError(f"Lien {lien_id} is already redeemed")

        # Create payment record
        payment = Payment(
            payment_id=f"pmt_{lien_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            lien_id=lien_id,
            tenant_id=context.tenant_id,
            amount=Decimal(str(amount)),
            payment_date=payment_date,
            status=PaymentStatus.COMPLETED,
            created_at=datetime.utcnow()
        )

        payment_dict = payment.model_dump()
        await self.storage.create("payments", payment_dict, context.tenant_id)

        self.log_info(f"Payment recorded for lien {lien_id}: ${amount}")

        # Calculate total owed using InterestCalculatorAgent
        interest_agent = InterestCalculatorAgent(storage=self.storage)
        interest_result = await interest_agent.run(
            tenant_id=context.tenant_id,
            task="calculate_interest",
            lien_ids=[lien_id]
        )

        total_owed = Decimal(str(interest_result.get("total_owed", 0)))

        # Get all completed payments for this lien
        all_payments = await self.storage.query(
            "payments",
            context.tenant_id,
            filters=[
                ("lien_id", "==", lien_id),
                ("status", "==", PaymentStatus.COMPLETED.value)
            ]
        )

        # Calculate total paid
        total_paid = Decimal("0")
        for pmt in all_payments:
            pmt_amount = pmt.get("amount", 0)
            if isinstance(pmt_amount, (int, float)):
                total_paid += Decimal(str(pmt_amount))
            else:
                total_paid += Decimal(str(pmt_amount))

        # Check if lien is fully redeemed
        is_fully_paid = total_paid >= total_owed
        remaining_balance = max(Decimal("0"), total_owed - total_paid)

        # If fully paid, update lien status to REDEEMED
        if is_fully_paid:
            await self.storage.update(
                "liens",
                lien_id,
                {"status": LienStatus.REDEEMED.value},
                context.tenant_id
            )
            self.log_info(f"Lien {lien_id} fully redeemed")

        # Create notification for payment received
        notification = Notification(
            notification_id=f"notif_{payment.payment_id}",
            tenant_id=context.tenant_id,
            lien_id=lien_id,
            notification_type=NotificationType.PAYMENT_RECEIVED,
            title="Payment Received" if not is_fully_paid else "Lien Fully Redeemed",
            message=self._build_payment_message(
                amount=float(amount),
                total_paid=float(total_paid),
                total_owed=float(total_owed),
                is_fully_paid=is_fully_paid,
                property_address=lien_data.get("property_address", "Unknown")
            ),
            priority="high" if is_fully_paid else "normal",
            channels=["email"],
            action_required=False
        )

        notif_dict = notification.model_dump()
        await self.storage.create("notifications", notif_dict, context.tenant_id)

        return {
            "payment_id": payment.payment_id,
            "lien_id": lien_id,
            "amount": float(amount),
            "payment_date": payment_date.isoformat(),
            "total_paid": float(total_paid),
            "total_owed": float(total_owed),
            "remaining_balance": float(remaining_balance),
            "is_fully_redeemed": is_fully_paid,
            "lien_status": LienStatus.REDEEMED.value if is_fully_paid else lien_data.get("status"),
            "notification_id": notification.notification_id
        }

    def _build_payment_message(
        self,
        amount: float,
        total_paid: float,
        total_owed: float,
        is_fully_paid: bool,
        property_address: str
    ) -> str:
        """Build notification message for payment"""
        if is_fully_paid:
            return (
                f"Payment of ${amount:,.2f} received for {property_address}. "
                f"Total paid: ${total_paid:,.2f}. "
                f"Lien has been fully redeemed."
            )
        else:
            remaining = total_owed - total_paid
            return (
                f"Payment of ${amount:,.2f} received for {property_address}. "
                f"Total paid: ${total_paid:,.2f} of ${total_owed:,.2f}. "
                f"Remaining balance: ${remaining:,.2f}."
            )

    async def _verify_payment(self, context: AgentContext) -> Dict[str, Any]:
        """
        Verify a payment was properly recorded.

        Required parameters:
        - parameters.payment_id: The payment ID to verify

        Returns:
            Dict with payment details and verification status
        """
        payment_id = context.parameters.get("payment_id")
        if not payment_id:
            raise ValueError("payment_id required in parameters")

        payment_data = await self.storage.get("payments", payment_id, context.tenant_id)
        if not payment_data:
            return {
                "payment_id": payment_id,
                "verified": False,
                "error": "Payment not found"
            }

        return {
            "payment_id": payment_id,
            "verified": True,
            "lien_id": payment_data.get("lien_id"),
            "amount": payment_data.get("amount"),
            "payment_date": payment_data.get("payment_date"),
            "status": payment_data.get("status")
        }

    async def _reconcile_lien(self, context: AgentContext) -> Dict[str, Any]:
        """
        Reconcile all payments for a lien.

        Required:
        - lien_ids[0]: The lien ID to reconcile

        Returns:
            Dict with all payments and current balance
        """
        if not context.lien_ids or len(context.lien_ids) == 0:
            raise ValueError("lien_id required in context.lien_ids")

        lien_id = context.lien_ids[0]

        # Get lien data
        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)
        if not lien_data:
            raise ValueError(f"Lien {lien_id} not found")

        # Get all payments for this lien
        payments = await self.storage.query(
            "payments",
            context.tenant_id,
            filters=[("lien_id", "==", lien_id)],
            order_by="payment_date"
        )

        # Calculate totals
        total_paid = Decimal("0")
        completed_payments = []
        pending_payments = []

        for pmt in payments:
            pmt_amount = Decimal(str(pmt.get("amount", 0)))
            if pmt.get("status") == PaymentStatus.COMPLETED.value:
                total_paid += pmt_amount
                completed_payments.append({
                    "payment_id": pmt.get("payment_id"),
                    "amount": float(pmt_amount),
                    "payment_date": pmt.get("payment_date"),
                    "status": pmt.get("status")
                })
            else:
                pending_payments.append({
                    "payment_id": pmt.get("payment_id"),
                    "amount": float(pmt_amount),
                    "payment_date": pmt.get("payment_date"),
                    "status": pmt.get("status")
                })

        # Get current total owed
        interest_agent = InterestCalculatorAgent(storage=self.storage)
        interest_result = await interest_agent.run(
            tenant_id=context.tenant_id,
            task="calculate_interest",
            lien_ids=[lien_id]
        )

        total_owed = Decimal(str(interest_result.get("total_owed", 0)))
        remaining_balance = max(Decimal("0"), total_owed - total_paid)

        return {
            "lien_id": lien_id,
            "property_address": lien_data.get("property_address"),
            "lien_status": lien_data.get("status"),
            "total_owed": float(total_owed),
            "total_paid": float(total_paid),
            "remaining_balance": float(remaining_balance),
            "is_fully_redeemed": total_paid >= total_owed,
            "completed_payments": completed_payments,
            "pending_payments": pending_payments,
            "payment_count": len(payments)
        }
