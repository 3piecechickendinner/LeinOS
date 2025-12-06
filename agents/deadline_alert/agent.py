from typing import Dict, Any, List
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext, Deadline, Notification, NotificationType, TaxLien, CivilJudgment
from core.storage import FirestoreClient


class DeadlineAlertAgent(LienOSBaseAgent):
    """
    Agent that monitors deadlines and sends proactive alerts.
    Checks for approaching deadlines and creates notifications.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="DeadlineAlert",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """This agent monitors deadlines and sends alerts"""
        return ["check_deadlines", "send_alert", "create_deadline"]

    def _register_tools(self) -> None:
        """No external tools needed for deadline monitoring"""
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Check for upcoming deadlines and send alerts.

        Two modes:
        1. If context.task == "check_deadlines": Scan all deadlines for tenant
        2. If context.task == "create_deadline": Create new deadline for a lien

        Returns:
            Dict with alerts_sent count and deadline details
        """
        if context.task == "create_deadline":
            return await self._create_deadline(context)
        elif context.task == "check_deadlines":
            return await self._check_all_deadlines(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _create_deadline(self, context: AgentContext) -> Dict[str, Any]:
        """Create a new deadline for a lien or judgment"""
        if not context.lien_ids and not context.asset_ids:
            if (not context.lien_ids or len(context.lien_ids) == 0) and \
               (not context.asset_ids or len(context.asset_ids) == 0):
                raise ValueError("lien_id or asset_id required in context")

        # Prefer asset_id if available, else lien_id
        asset_id = context.asset_ids[0] if context.asset_ids else context.lien_ids[0]

        # Try getting as Tax Lien
        asset_data = await self.storage.get("liens", asset_id, context.tenant_id)
        asset_type = "TAX_LIEN"
        
        if not asset_data:
            # Check other verticals
            collections = {
                "judgments": "CIVIL_JUDGMENT",
                "probate_estates": "PROBATE",
                "minerals": "MINERAL_RIGHT",
                "surplus_funds": "SURPLUS_FUND"
            }
            found = False
            for coll, type_name in collections.items():
                asset_data = await self.storage.get(coll, asset_id, context.tenant_id)
                if asset_data:
                    asset_type = type_name
                    found = True
                    break
            
            if not found:
                 raise ValueError(f"Asset {asset_id} not found")

        # Determine deadline details based on asset type
        if asset_type == "CIVIL_JUDGMENT":
            deadline_date = asset_data.get("statute_limitations_date")
            if not deadline_date:
                # Fallback or error
                # For this logic, we'll error if critical date missing
                raise ValueError(f"statute_limitations_date missing for judgment {asset_id}")
            description = "Judgment Expiration / Renewal Deadline"
            deadline_suffix = "expiration"
            
        elif asset_type == "PROBATE":
            # Logic: Filing Date + 6 Months
            filing_date_str = asset_data.get("probate_filing_date")
            if not filing_date_str:
                raise ValueError(f"probate_filing_date missing for probate {asset_id}")
            filing_date = date.fromisoformat(filing_date_str)
            deadline_date = (filing_date + timedelta(days=180)).isoformat()
            description = "Creditor Claim Period Ends"
            deadline_suffix = "claim_period"
            
        elif asset_type == "MINERAL_RIGHT":
            deadline_date = asset_data.get("lease_expiration_date")
            if not deadline_date:
                raise ValueError(f"lease_expiration_date missing for mineral {asset_id}")
            description = "Primary Term Expiration"
            deadline_suffix = "lease_expiration"
            
        elif asset_type == "SURPLUS_FUND":
            deadline_date = asset_data.get("claim_deadline")
            if not deadline_date:
                raise ValueError(f"claim_deadline missing for surplus {asset_id}")
            description = "Escheatment Deadline"
            deadline_suffix = "escheatment"
            
        else: # TAX_LIEN
            deadline_date = asset_data.get("redemption_deadline")
            if not deadline_date:
                 raise ValueError(f"redemption_deadline missing for lien {asset_id}")
            description = f"Redemption deadline for {asset_data.get('property_address', 'Unknown Property')}"
            deadline_suffix = "redemption"

        # Create deadline
        deadline = Deadline(
            deadline_id=f"{asset_id}_{deadline_suffix}",
            lien_id=asset_id,
            tenant_id=context.tenant_id,
            deadline_type=deadline_suffix,
            deadline_date=deadline_date,
            description=description,
            alert_days_before=[90, 60, 30, 14, 7, 3, 1],
            alerts_sent=[],
            is_completed=False
        )

        deadline_dict = deadline.model_dump()
        await self.storage.create("deadlines", deadline_dict, context.tenant_id)

        self.log_info(f"Created deadline for asset {asset_id}")

        return {
            "deadline_id": deadline.deadline_id,
            "asset_id": asset_id,
            "deadline_date": deadline.deadline_date.isoformat(),
            "created": True
        }

    async def _check_all_deadlines(self, context: AgentContext) -> Dict[str, Any]:
        """Check all deadlines and send alerts if needed"""

        # Get all incomplete deadlines for this tenant
        deadlines = await self.storage.query(
            "deadlines",
            context.tenant_id,
            filters=[("is_completed", "==", False)]
        )

        today = date.today()
        alerts_sent = 0
        deadlines_checked = 0

        for deadline_data in deadlines:
            deadlines_checked += 1

            deadline_date = deadline_data["deadline_date"]
            if isinstance(deadline_date, str):
                deadline_date = date.fromisoformat(deadline_date)

            days_until = (deadline_date - today).days

            # Check if we need to send an alert
            alert_days = deadline_data.get("alert_days_before", [90, 60, 30, 14, 7, 3, 1])
            alerts_already_sent = deadline_data.get("alerts_sent", [])

            # Convert alerts_sent dates from strings if needed
            sent_dates = []
            for sent in alerts_already_sent:
                if isinstance(sent, str):
                    sent_dates.append(date.fromisoformat(sent))
                else:
                    sent_dates.append(sent)

            # Should we send an alert today?
            should_alert = False
            for alert_day in alert_days:
                if days_until == alert_day and today not in sent_dates:
                    should_alert = True
                    break

            if should_alert:
                # Create notification
                notification = Notification(
                    notification_id=f"alert_{deadline_data['deadline_id']}_{today.isoformat()}",
                    tenant_id=context.tenant_id,
                    lien_id=deadline_data.get("lien_id"),
                    notification_type=NotificationType.DEADLINE_APPROACHING,
                    title=f"Deadline Alert: {days_until} days remaining",
                    message=f"{deadline_data['description']} - Due on {deadline_date.isoformat()}",
                    priority="high" if days_until <= 7 else "normal",
                    channels=["email"],
                    action_required=True
                )

                notif_dict = notification.model_dump()
                await self.storage.create("notifications", notif_dict, context.tenant_id)

                # Update deadline with alert sent
                sent_dates.append(today)
                await self.storage.update(
                    "deadlines",
                    deadline_data["deadline_id"],
                    {"alerts_sent": [d.isoformat() for d in sent_dates]},
                    context.tenant_id
                )

                alerts_sent += 1
                self.log_info(f"Alert sent for deadline {deadline_data['deadline_id']} ({days_until} days)")

        return {
            "deadlines_checked": deadlines_checked,
            "alerts_sent": alerts_sent,
            "check_date": today.isoformat()
        }
