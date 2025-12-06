from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext
from core.verticals.mineral import MineralRight
from core.storage import FirestoreClient


class MineralTrackerAgent(LienOSBaseAgent):
    """
    Agent responsible for managing Mineral Rights.
    Handles creation, retrieval, updates, and listing of mineral rights.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="MineralTracker",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return [
            "create_mineral",
            "get_mineral",
            "update_mineral",
            "list_mineral"
        ]

    def _register_tools(self) -> None:
        """No external tools needed for basic CRUD"""
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """Execute the requested task"""
        if context.task == "create_mineral":
            return await self._create_mineral(context)
        elif context.task == "get_mineral":
            return await self._get_mineral(context)
        elif context.task == "update_mineral":
            return await self._update_mineral(context)
        elif context.task == "list_mineral":
            return await self._list_mineral(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _create_mineral(self, context: AgentContext) -> Dict[str, Any]:
        """Create a new mineral right"""
        params = context.parameters
        
        # Validate required fields
        required_fields = [
            "legal_description", "net_mineral_acres", "royalty_decimal", "operator_name", "county"
        ]
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")

        # Generate ID if not provided
        mineral_id = params.get("asset_id")
        if not mineral_id:
            # Simple ID generation
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            mineral_id = f"mineral_{timestamp}"

        # Create mineral object
        mineral = MineralRight(
            asset_id=mineral_id,
            tenant_id=context.tenant_id,
            legal_description=params["legal_description"],
            net_mineral_acres=Decimal(str(params["net_mineral_acres"])),
            royalty_decimal=Decimal(str(params["royalty_decimal"])),
            operator_name=params["operator_name"],
            purchase_amount=Decimal(str(params.get("purchase_amount", "0"))),
            interest_rate=Decimal(str(params.get("interest_rate", "0"))),
            status=params.get("status", "ACTIVE"),
            county=params["county"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to storage
        mineral_dict = mineral.model_dump()
        mineral_dict["id"] = mineral_id
        await self.storage.create("minerals", mineral_dict, context.tenant_id)

        self.log_info(f"Created mineral right {mineral_id}")

        return {
            "asset_id": mineral_id,
            "status": "created",
            "data": mineral_dict
        }

    async def _get_mineral(self, context: AgentContext) -> Dict[str, Any]:
        """Get a mineral right by ID"""
        if not context.asset_ids or len(context.asset_ids) == 0:
            raise ValueError("asset_id required in context.asset_ids")

        mineral_id = context.asset_ids[0]
        mineral_data = await self.storage.get("minerals", mineral_id, context.tenant_id)

        if not mineral_data:
            return {"found": False, "asset_id": mineral_id}

        return {
            "found": True,
            "asset_id": mineral_id,
            **mineral_data
        }

    async def _update_mineral(self, context: AgentContext) -> Dict[str, Any]:
        """Update a mineral right"""
        if not context.asset_ids or len(context.asset_ids) == 0:
            raise ValueError("asset_id required in context.asset_ids")

        mineral_id = context.asset_ids[0]
        updates = context.parameters
        
        # Add timestamp
        updates["updated_at"] = datetime.now()

        await self.storage.update("minerals", mineral_id, updates, context.tenant_id)
        
        self.log_info(f"Updated mineral {mineral_id}")

        return {
            "asset_id": mineral_id,
            "status": "updated",
            "updates": updates
        }

    async def _list_mineral(self, context: AgentContext) -> Dict[str, Any]:
        """List minerals with optional filtering"""
        params = context.parameters
        filters = []
        
        if "operator_name" in params:
            filters.append(("operator_name", "==", params["operator_name"]))
        if "county" in params:
            filters.append(("county", "==", params["county"]))

        minerals = await self.storage.query(
            "minerals",
            context.tenant_id,
            filters=filters,
            limit=params.get("limit", 50),
            order_by=params.get("order_by", "created_at")
        )

        return {
            "count": len(minerals),
            "minerals": minerals
        }
