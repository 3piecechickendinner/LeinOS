from typing import Dict, Any, List
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext, Deadline, Notification, NotificationType
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
        """Create a new deadline for a lien"""
        if not context.lien_ids or len(context.lien_ids) == 0:
            raise ValueError("lien_id required in context.lien_ids")

        lien_id = context.lien_ids[0]

        # Get lien to extract deadline info
        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)
        if not lien_data:
            raise ValueError(f"Lien {lien_id} not found")

        # Create deadline for redemption period
        deadline = Deadline(
            deadline_id=f"{lien_id}_redemption",
            lien_id=lien_id,
            tenant_id=context.tenant_id,
            deadline_type="redemption",
            deadline_date=lien_data["redemption_deadline"],
            description=f"Redemption deadline for {lien_data['property_address']}",
            alert_days_before=[90, 60, 30, 14, 7, 3, 1],
            alerts_sent=[],
            is_completed=False
        )

        deadline_dict = deadline.model_dump()
        await self.storage.create("deadlines", deadline_dict, context.tenant_id)

        self.log_info(f"Created deadline for lien {lien_id}")

        return {
            "deadline_id": deadline.deadline_id,
            "lien_id": lien_id,
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
