from typing import Dict, Any, List, Optional
from datetime import datetime, date
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext, Lien, LienStatus
from core.storage import FirestoreClient
from agents.deadline_alert.agent import DeadlineAlertAgent


class LienTrackerAgent(LienOSBaseAgent):
    """
    CRUD agent for tax lien management.
    Handles all basic lien operations: create, read, update, delete, list.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="LienTracker",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return ["create_lien", "update_lien", "get_lien", "list_liens", "delete_lien"]

    def _register_tools(self) -> None:
        """No external tools needed for lien tracking"""
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Main agent logic.

        Handles tasks:
        - create_lien: Create a new lien record
        - update_lien: Update existing lien fields
        - get_lien: Retrieve lien by ID
        - list_liens: Query liens with filters
        - delete_lien: Delete a lien (soft or hard)

        Returns:
            Dict with operation results
        """
        if context.task == "create_lien":
            return await self._create_lien(context)
        elif context.task == "update_lien":
            return await self._update_lien(context)
        elif context.task == "get_lien":
            return await self._get_lien(context)
        elif context.task == "list_liens":
            return await self._list_liens(context)
        elif context.task == "delete_lien":
            return await self._delete_lien(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _create_lien(self, context: AgentContext) -> Dict[str, Any]:
        """
        Create a new lien record.

        Required parameters:
        - certificate_number: str
        - purchase_amount: Decimal/float
        - interest_rate: Decimal/float (percentage)
        - sale_date: date or ISO string
        - redemption_deadline: date or ISO string
        - county: str
        - property_address: str
        - parcel_id: str

        Optional parameters:
        - lien_id: str (auto-generated if not provided)
        - status: LienStatus (defaults to ACTIVE)

        Returns:
            Dict with created lien details
        """
        params = context.parameters

        # Validate required fields
        required_fields = [
            "certificate_number", "purchase_amount", "interest_rate",
            "sale_date", "redemption_deadline", "county",
            "property_address", "parcel_id"
        ]

        missing = [f for f in required_fields if f not in params]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        # Parse dates
        sale_date = params["sale_date"]
        if isinstance(sale_date, str):
            sale_date = date.fromisoformat(sale_date)

        redemption_deadline = params["redemption_deadline"]
        if isinstance(redemption_deadline, str):
            redemption_deadline = date.fromisoformat(redemption_deadline)

        # Generate lien_id if not provided
        lien_id = params.get("lien_id")
        if not lien_id:
            lien_id = f"lien_{params['certificate_number']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Create lien object
        lien = Lien(
            asset_id=lien_id,
            tenant_id=context.tenant_id,
            certificate_number=params["certificate_number"],
            purchase_amount=Decimal(str(params["purchase_amount"])),
            interest_rate=Decimal(str(params["interest_rate"])),
            sale_date=sale_date,
            redemption_deadline=redemption_deadline,
            status=LienStatus(params.get("status", LienStatus.ACTIVE.value)),
            county=params["county"],
            property_address=params["property_address"],
            parcel_id=params["parcel_id"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to storage
        lien_dict = lien.model_dump()
        lien_dict["id"] = lien_id  # Ensure document ID matches asset_id
        await self.storage.create("liens", lien_dict, context.tenant_id)

        self.log_info(f"Created lien {lien_id} for {params['property_address']}")

        # Automatically create redemption deadline using DeadlineAlertAgent
        deadline_agent = DeadlineAlertAgent(storage=self.storage)
        deadline_result = await deadline_agent.run(
            tenant_id=context.tenant_id,
            task="create_deadline",
            lien_ids=[lien_id]
        )

        self.log_info(f"Created deadline for lien {lien_id}")

        return {
            "lien_id": lien_id,
            "certificate_number": lien.certificate_number,
            "purchase_amount": float(lien.purchase_amount),
            "interest_rate": float(lien.interest_rate),
            "sale_date": lien.sale_date.isoformat(),
            "redemption_deadline": lien.redemption_deadline.isoformat(),
            "status": lien.status.value,
            "county": lien.county,
            "property_address": lien.property_address,
            "parcel_id": lien.parcel_id,
            "created": True,
            "deadline_id": deadline_result.get("deadline_id")
        }

    async def _update_lien(self, context: AgentContext) -> Dict[str, Any]:
        """
        Update existing lien fields.

        Required:
        - lien_ids[0]: The lien ID to update
        - parameters: Dict of fields to update

        Returns:
            Dict with updated lien details
        """
        if not context.lien_ids or len(context.lien_ids) == 0:
            raise ValueError("lien_id required in context.lien_ids")

        lien_id = context.lien_ids[0]

        # Verify lien exists
        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)
        if not lien_data:
            raise ValueError(f"Lien {lien_id} not found")

        # Prepare updates
        updates = {}
        allowed_fields = [
            "certificate_number", "purchase_amount", "interest_rate",
            "sale_date", "redemption_deadline", "status", "county",
            "property_address", "parcel_id"
        ]

        for field in allowed_fields:
            if field in context.parameters:
                value = context.parameters[field]

                # Convert types as needed
                if field in ["purchase_amount", "interest_rate"]:
                    value = float(Decimal(str(value)))
                elif field in ["sale_date", "redemption_deadline"]:
                    if isinstance(value, str):
                        value = date.fromisoformat(value).isoformat()
                    elif isinstance(value, date):
                        value = value.isoformat()
                elif field == "status":
                    value = LienStatus(value).value

                updates[field] = value

        if not updates:
            raise ValueError("No valid fields to update")

        # Perform update
        success = await self.storage.update("liens", lien_id, updates, context.tenant_id)

        if not success:
            raise ValueError(f"Failed to update lien {lien_id}")

        self.log_info(f"Updated lien {lien_id}: {list(updates.keys())}")

        # Get updated lien data
        updated_lien = await self.storage.get("liens", lien_id, context.tenant_id)

        return {
            "lien_id": lien_id,
            "updated_fields": list(updates.keys()),
            "updated": True,
            "current_status": updated_lien.get("status"),
            "property_address": updated_lien.get("property_address")
        }

    async def _get_lien(self, context: AgentContext) -> Dict[str, Any]:
        """
        Retrieve a lien by ID.

        Required:
        - lien_ids[0]: The lien ID to retrieve

        Returns:
            Dict with full lien details
        """
        if not context.lien_ids or len(context.lien_ids) == 0:
            raise ValueError("lien_id required in context.lien_ids")

        lien_id = context.lien_ids[0]

        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)
        if not lien_data:
            return {
                "lien_id": lien_id,
                "found": False,
                "error": "Lien not found"
            }

        return {
            "lien_id": lien_data.get("asset_id") or lien_data.get("lien_id"),
            "asset_id": lien_data.get("asset_id"),
            "found": True,
            "certificate_number": lien_data.get("certificate_number"),
            "purchase_amount": lien_data.get("purchase_amount"),
            "interest_rate": lien_data.get("interest_rate"),
            "sale_date": lien_data.get("sale_date"),
            "redemption_deadline": lien_data.get("redemption_deadline"),
            "status": lien_data.get("status"),
            "county": lien_data.get("county"),
            "property_address": lien_data.get("property_address"),
            "parcel_id": lien_data.get("parcel_id"),
            "created_at": lien_data.get("created_at"),
            "updated_at": lien_data.get("updated_at")
        }

    async def _list_liens(self, context: AgentContext) -> Dict[str, Any]:
        """
        Query liens with optional filters.

        Optional parameters:
        - status: Filter by LienStatus
        - county: Filter by county
        - limit: Max results (default 100)
        - order_by: Field to sort by (default "created_at")

        Returns:
            Dict with list of liens and count
        """
        filters = []

        # Build filters from parameters
        if "status" in context.parameters:
            status = context.parameters["status"]
            if isinstance(status, LienStatus):
                status = status.value
            filters.append(("status", "==", status))

        if "county" in context.parameters:
            filters.append(("county", "==", context.parameters["county"]))

        # Query parameters
        limit = context.parameters.get("limit", 100)
        order_by = context.parameters.get("order_by", "created_at")

        # Execute query
        liens = await self.storage.query(
            "liens",
            context.tenant_id,
            filters=filters if filters else None,
            order_by=order_by,
            limit=limit
        )

        # Format results
        results = []
        for lien in liens:
            results.append({
                "lien_id": lien.get("asset_id") or lien.get("lien_id"),
                "asset_id": lien.get("asset_id"),
                "certificate_number": lien.get("certificate_number"),
                "purchase_amount": lien.get("purchase_amount"),
                "interest_rate": lien.get("interest_rate"),
                "sale_date": lien.get("sale_date"),
                "redemption_deadline": lien.get("redemption_deadline"),
                "status": lien.get("status"),
                "county": lien.get("county"),
                "property_address": lien.get("property_address"),
                "parcel_id": lien.get("parcel_id")
            })

        return {
            "liens": results,
            "count": len(results),
            "filters_applied": {k: v for k, _, v in filters} if filters else {},
            "limit": limit
        }

    async def _delete_lien(self, context: AgentContext) -> Dict[str, Any]:
        """
        Delete a lien (soft delete by default).

        Required:
        - lien_ids[0]: The lien ID to delete

        Optional parameters:
        - hard_delete: bool (default False) - if True, permanently delete

        Returns:
            Dict with deletion status
        """
        if not context.lien_ids or len(context.lien_ids) == 0:
            raise ValueError("lien_id required in context.lien_ids")

        lien_id = context.lien_ids[0]

        # Verify lien exists
        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)
        if not lien_data:
            raise ValueError(f"Lien {lien_id} not found")

        hard_delete = context.parameters.get("hard_delete", False)

        if hard_delete:
            # Permanent deletion
            success = await self.storage.delete("liens", lien_id, context.tenant_id)
            if success:
                self.log_info(f"Hard deleted lien {lien_id}")
                return {
                    "lien_id": lien_id,
                    "deleted": True,
                    "delete_type": "hard",
                    "property_address": lien_data.get("property_address")
                }
            else:
                raise ValueError(f"Failed to delete lien {lien_id}")
        else:
            # Soft delete - mark as expired/deleted
            success = await self.storage.update(
                "liens",
                lien_id,
                {"status": LienStatus.EXPIRED.value},
                context.tenant_id
            )

            if success:
                self.log_info(f"Soft deleted lien {lien_id} (marked as EXPIRED)")
                return {
                    "lien_id": lien_id,
                    "deleted": True,
                    "delete_type": "soft",
                    "new_status": LienStatus.EXPIRED.value,
                    "property_address": lien_data.get("property_address")
                }
            else:
                raise ValueError(f"Failed to soft delete lien {lien_id}")
