from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext
from core.verticals.surplus import SurplusFund
from core.storage import FirestoreClient


class SurplusTrackerAgent(LienOSBaseAgent):
    """
    Agent responsible for managing Surplus Funds.
    Handles creation, retrieval, updates, and listing of surplus funds.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="SurplusTracker",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return [
            "create_surplus",
            "get_surplus",
            "update_surplus",
            "list_surplus"
        ]

    def _register_tools(self) -> None:
        """No external tools needed for basic CRUD"""
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """Execute the requested task"""
        if context.task == "create_surplus":
            return await self._create_surplus(context)
        elif context.task == "get_surplus":
            return await self._get_surplus(context)
        elif context.task == "update_surplus":
            return await self._update_surplus(context)
        elif context.task == "list_surplus":
            return await self._list_surplus(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _create_surplus(self, context: AgentContext) -> Dict[str, Any]:
        """Create a new surplus fund"""
        params = context.parameters
        
        # Validate required fields
        required_fields = [
            "foreclosure_date", "winning_bid_amount", "total_debt_owed", "surplus_amount", "claim_deadline", "county"
        ]
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")

        # Generate ID if not provided
        surplus_id = params.get("asset_id")
        if not surplus_id:
            # Simple ID generation
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            surplus_id = f"surplus_{timestamp}"

        # Create surplus object
        surplus = SurplusFund(
            asset_id=surplus_id,
            tenant_id=context.tenant_id,
            foreclosure_date=params["foreclosure_date"],
            winning_bid_amount=Decimal(str(params["winning_bid_amount"])),
            total_debt_owed=Decimal(str(params["total_debt_owed"])),
            surplus_amount=Decimal(str(params["surplus_amount"])),
            claim_deadline=params["claim_deadline"],
            purchase_amount=Decimal(str(params.get("purchase_amount", "0"))),
            interest_rate=Decimal(str(params.get("interest_rate", "0"))),
            status=params.get("status", "ACTIVE"),
            county=params["county"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to storage
        surplus_dict = surplus.model_dump()
        surplus_dict["id"] = surplus_id
        await self.storage.create("surplus_funds", surplus_dict, context.tenant_id)

        self.log_info(f"Created surplus fund {surplus_id}")

        return {
            "asset_id": surplus_id,
            "status": "created",
            "data": surplus_dict
        }

    async def _get_surplus(self, context: AgentContext) -> Dict[str, Any]:
        """Get a surplus fund by ID"""
        if not context.asset_ids or len(context.asset_ids) == 0:
            raise ValueError("asset_id required in context.asset_ids")

        surplus_id = context.asset_ids[0]
        surplus_data = await self.storage.get("surplus_funds", surplus_id, context.tenant_id)

        if not surplus_data:
            return {"found": False, "asset_id": surplus_id}

        return {
            "found": True,
            "asset_id": surplus_id,
            **surplus_data
        }

    async def _update_surplus(self, context: AgentContext) -> Dict[str, Any]:
        """Update a surplus fund"""
        if not context.asset_ids or len(context.asset_ids) == 0:
            raise ValueError("asset_id required in context.asset_ids")

        surplus_id = context.asset_ids[0]
        updates = context.parameters
        
        # Add timestamp
        updates["updated_at"] = datetime.now()

        await self.storage.update("surplus_funds", surplus_id, updates, context.tenant_id)
        
        self.log_info(f"Updated surplus {surplus_id}")

        return {
            "asset_id": surplus_id,
            "status": "updated",
            "updates": updates
        }

    async def _list_surplus(self, context: AgentContext) -> Dict[str, Any]:
        """List surplus funds with optional filtering"""
        params = context.parameters
        filters = []
        
        if "county" in params:
            filters.append(("county", "==", params["county"]))

        surplus_funds = await self.storage.query(
            "surplus_funds",
            context.tenant_id,
            filters=filters,
            limit=params.get("limit", 50),
            order_by=params.get("order_by", "created_at")
        )

        return {
            "count": len(surplus_funds),
            "surplus_funds": surplus_funds
        }
