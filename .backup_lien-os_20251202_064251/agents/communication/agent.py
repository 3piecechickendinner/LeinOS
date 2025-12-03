from typing import Dict, Any, List, Optional
from datetime import datetime, date

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext, Notification, NotificationType
from core.storage import FirestoreClient


class CommunicationAgent(LienOSBaseAgent):
    """
    Agent that manages notifications and communication channels.
    Handles notification queue, email, and SMS (placeholders for future integrations).
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="Communication",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return [
            "send_notification",
            "get_notifications",
            "mark_notification_read",
            "send_email",
            "send_sms"
        ]

    def _register_tools(self) -> None:
        """
        No external tools yet.
        Future: Register MCP tools for SendGrid, Twilio, etc.
        """
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Main agent logic.

        Handles tasks:
        - send_notification: Create and queue a notification
        - get_notifications: Retrieve notifications for tenant
        - mark_notification_read: Mark notification as read
        - send_email: Placeholder for email sending
        - send_sms: Placeholder for SMS sending

        Returns:
            Dict with operation results
        """
        if context.task == "send_notification":
            return await self._send_notification(context)
        elif context.task == "get_notifications":
            return await self._get_notifications(context)
        elif context.task == "mark_notification_read":
            return await self._mark_notification_read(context)
        elif context.task == "send_email":
            return await self._send_email(context)
        elif context.task == "send_sms":
            return await self._send_sms(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _send_notification(self, context: AgentContext) -> Dict[str, Any]:
        """
        Create and queue a notification.

        Required parameters:
        - notification_type: NotificationType value
        - title: str
        - message: str

        Optional parameters:
        - lien_id: str (link to specific lien)
        - priority: str ("low", "normal", "high") - default "normal"
        - channels: List[str] - default ["in_app"]
        - action_required: bool - default False
        - action_url: str

        Returns:
            Dict with notification details
        """
        params = context.parameters

        # Validate required fields
        if "notification_type" not in params:
            raise ValueError("notification_type required")
        if "title" not in params:
            raise ValueError("title required")
        if "message" not in params:
            raise ValueError("message required")

        # Parse notification type
        notif_type = params["notification_type"]
        if isinstance(notif_type, str):
            notif_type = NotificationType(notif_type)

        # Generate notification ID
        notification_id = f"notif_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        # Get lien_id from parameters or context
        lien_id = params.get("lien_id")
        if not lien_id and context.lien_ids and len(context.lien_ids) > 0:
            lien_id = context.lien_ids[0]

        # Create notification
        notification = Notification(
            notification_id=notification_id,
            tenant_id=context.tenant_id,
            lien_id=lien_id,
            notification_type=notif_type,
            title=params["title"],
            message=params["message"],
            priority=params.get("priority", "normal"),
            channels=params.get("channels", ["in_app"]),
            action_required=params.get("action_required", False),
            action_url=params.get("action_url")
        )

        # Save to storage
        notif_dict = notification.model_dump()
        await self.storage.create("notifications", notif_dict, context.tenant_id)

        self.log_info(f"Notification created: {notification_id} - {params['title']}")

        # If channels include email or sms, queue those for sending
        channels_queued = []
        if "email" in notification.channels:
            channels_queued.append("email")
            self.log_info(f"Email queued for notification {notification_id}")
        if "sms" in notification.channels:
            channels_queued.append("sms")
            self.log_info(f"SMS queued for notification {notification_id}")

        return {
            "notification_id": notification_id,
            "notification_type": notif_type.value,
            "title": notification.title,
            "message": notification.message,
            "priority": notification.priority,
            "channels": notification.channels,
            "channels_queued": channels_queued,
            "lien_id": lien_id,
            "created": True
        }

    async def _get_notifications(self, context: AgentContext) -> Dict[str, Any]:
        """
        Retrieve notifications for a tenant.

        Optional parameters:
        - unread_only: bool - only return unread notifications
        - lien_id: str - filter by specific lien
        - notification_type: str - filter by type
        - priority: str - filter by priority
        - limit: int - max results (default 50)

        Returns:
            Dict with list of notifications
        """
        filters = []

        # Build filters
        if context.parameters.get("unread_only", False):
            filters.append(("read_at", "==", None))

        if "lien_id" in context.parameters:
            filters.append(("lien_id", "==", context.parameters["lien_id"]))

        if "notification_type" in context.parameters:
            notif_type = context.parameters["notification_type"]
            if isinstance(notif_type, NotificationType):
                notif_type = notif_type.value
            filters.append(("notification_type", "==", notif_type))

        if "priority" in context.parameters:
            filters.append(("priority", "==", context.parameters["priority"]))

        limit = context.parameters.get("limit", 50)

        # Query notifications
        notifications = await self.storage.query(
            "notifications",
            context.tenant_id,
            filters=filters if filters else None,
            order_by="created_at",
            limit=limit
        )

        # Format results
        results = []
        unread_count = 0
        for notif in notifications:
            is_read = notif.get("read_at") is not None
            if not is_read:
                unread_count += 1

            results.append({
                "notification_id": notif.get("notification_id"),
                "notification_type": notif.get("notification_type"),
                "title": notif.get("title"),
                "message": notif.get("message"),
                "priority": notif.get("priority"),
                "lien_id": notif.get("lien_id"),
                "channels": notif.get("channels"),
                "action_required": notif.get("action_required"),
                "action_url": notif.get("action_url"),
                "is_read": is_read,
                "read_at": notif.get("read_at"),
                "created_at": notif.get("created_at")
            })

        return {
            "notifications": results,
            "count": len(results),
            "unread_count": unread_count,
            "limit": limit
        }

    async def _mark_notification_read(self, context: AgentContext) -> Dict[str, Any]:
        """
        Mark a notification as read.

        Required parameters:
        - notification_id: str

        Returns:
            Dict with update status
        """
        notification_id = context.parameters.get("notification_id")
        if not notification_id:
            raise ValueError("notification_id required in parameters")

        # Verify notification exists
        notif_data = await self.storage.get("notifications", notification_id, context.tenant_id)
        if not notif_data:
            return {
                "notification_id": notification_id,
                "marked_read": False,
                "error": "Notification not found"
            }

        # Check if already read
        if notif_data.get("read_at"):
            return {
                "notification_id": notification_id,
                "marked_read": True,
                "already_read": True,
                "read_at": notif_data.get("read_at")
            }

        # Update read_at timestamp
        read_at = datetime.utcnow().isoformat()
        success = await self.storage.update(
            "notifications",
            notification_id,
            {"read_at": read_at},
            context.tenant_id
        )

        if success:
            self.log_info(f"Notification {notification_id} marked as read")
            return {
                "notification_id": notification_id,
                "marked_read": True,
                "read_at": read_at
            }
        else:
            return {
                "notification_id": notification_id,
                "marked_read": False,
                "error": "Failed to update notification"
            }

    async def _send_email(self, context: AgentContext) -> Dict[str, Any]:
        """
        Placeholder for sending email.
        Logs email details for now - will integrate SendGrid/Gmail later via MCP.

        Required parameters:
        - to_email: str
        - subject: str
        - body: str

        Optional parameters:
        - from_email: str
        - html_body: str
        - notification_id: str (to link back to notification)

        Returns:
            Dict with email status (queued for now)
        """
        params = context.parameters

        # Validate required fields
        if "to_email" not in params:
            raise ValueError("to_email required")
        if "subject" not in params:
            raise ValueError("subject required")
        if "body" not in params:
            raise ValueError("body required")

        # Log email details (placeholder for actual sending)
        email_id = f"email_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        self.log_info(
            f"Email queued [{email_id}]: "
            f"To: {params['to_email']}, "
            f"Subject: {params['subject']}"
        )

        # Save to email queue for future processing
        email_record = {
            "email_id": email_id,
            "tenant_id": context.tenant_id,
            "to_email": params["to_email"],
            "from_email": params.get("from_email", "noreply@lienos.app"),
            "subject": params["subject"],
            "body": params["body"],
            "html_body": params.get("html_body"),
            "notification_id": params.get("notification_id"),
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        }

        await self.storage.create("email_queue", email_record, context.tenant_id)

        return {
            "email_id": email_id,
            "to_email": params["to_email"],
            "subject": params["subject"],
            "status": "queued",
            "message": "Email queued for sending. Integration pending."
        }

    async def _send_sms(self, context: AgentContext) -> Dict[str, Any]:
        """
        Placeholder for sending SMS.
        Logs SMS details for now - will integrate Twilio later via MCP.

        Required parameters:
        - to_phone: str
        - message: str

        Optional parameters:
        - from_phone: str
        - notification_id: str (to link back to notification)

        Returns:
            Dict with SMS status (queued for now)
        """
        params = context.parameters

        # Validate required fields
        if "to_phone" not in params:
            raise ValueError("to_phone required")
        if "message" not in params:
            raise ValueError("message required")

        # Log SMS details (placeholder for actual sending)
        sms_id = f"sms_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        self.log_info(
            f"SMS queued [{sms_id}]: "
            f"To: {params['to_phone']}, "
            f"Message: {params['message'][:50]}..."
        )

        # Save to SMS queue for future processing
        sms_record = {
            "sms_id": sms_id,
            "tenant_id": context.tenant_id,
            "to_phone": params["to_phone"],
            "from_phone": params.get("from_phone"),
            "message": params["message"],
            "notification_id": params.get("notification_id"),
            "status": "queued",
            "created_at": datetime.utcnow().isoformat()
        }

        await self.storage.create("sms_queue", sms_record, context.tenant_id)

        return {
            "sms_id": sms_id,
            "to_phone": params["to_phone"],
            "message_preview": params["message"][:50] + "..." if len(params["message"]) > 50 else params["message"],
            "status": "queued",
            "message": "SMS queued for sending. Integration pending."
        }
