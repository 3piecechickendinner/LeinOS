from typing import Dict, Any, List
from datetime import datetime, date
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext
from core.verticals.probate import ProbateEstate
from core.storage import FirestoreClient


class ProbateTrackerAgent(LienOSBaseAgent):
    """
    Agent responsible for managing Probate Estates.
    Handles creation, retrieval, updates, and listing of probate cases.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="ProbateTracker",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return [
            "create_probate",
            "get_probate",
            "update_probate",
            "list_probate"
        ]

    def _register_tools(self) -> None:
        """No external tools needed for basic CRUD"""
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """Execute the requested task"""
        if context.task == "create_probate":
            return await self._create_probate(context)
        elif context.task == "get_probate":
            return await self._get_probate(context)
        elif context.task == "update_probate":
            return await self._update_probate(context)
        elif context.task == "list_probate":
            return await self._list_probate(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _create_probate(self, context: AgentContext) -> Dict[str, Any]:
        """Create a new probate estate"""
        params = context.parameters
        
        # Validate required fields
        required_fields = [
            "deceased_name", "date_of_death", "case_status", "county"
        ]
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")

        # Generate ID if not provided
        probate_id = params.get("asset_id")
        if not probate_id:
            probate_id = f"probate_{params['deceased_name'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Parse dates
        date_of_death = params["date_of_death"]
        if isinstance(date_of_death, str):
            date_of_death = date.fromisoformat(date_of_death)

        # Create probate object
        probate = ProbateEstate(
            asset_id=probate_id,
            tenant_id=context.tenant_id,
            deceased_name=params["deceased_name"],
            date_of_death=date_of_death,
            case_status=params["case_status"],
            attorney_contact=params.get("attorney_contact"),
            purchase_amount=Decimal(str(params.get("purchase_amount", "0"))),
            interest_rate=Decimal(str(params.get("interest_rate", "0"))),
            status=params.get("status", "ACTIVE"),
            county=params["county"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to storage
        probate_dict = probate.model_dump()
        probate_dict["id"] = probate_id
        await self.storage.create("probates", probate_dict, context.tenant_id)

        self.log_info(f"Created probate {probate_id} for {params['deceased_name']}")

        return {
            "asset_id": probate_id,
            "status": "created",
            "data": probate_dict
        }

    async def _get_probate(self, context: AgentContext) -> Dict[str, Any]:
        """Get a probate by ID"""
        if not context.asset_ids or len(context.asset_ids) == 0:
            raise ValueError("asset_id required in context.asset_ids")

        probate_id = context.asset_ids[0]
        probate_data = await self.storage.get("probates", probate_id, context.tenant_id)

        if not probate_data:
            return {"found": False, "asset_id": probate_id}

        return {
            "found": True,
            "asset_id": probate_id,
            **probate_data
        }

    async def _update_probate(self, context: AgentContext) -> Dict[str, Any]:
        """Update a probate case"""
        if not context.asset_ids or len(context.asset_ids) == 0:
            raise ValueError("asset_id required in context.asset_ids")

        probate_id = context.asset_ids[0]
        updates = context.parameters
        
        # Add timestamp
        updates["updated_at"] = datetime.now()

        await self.storage.update("probates", probate_id, updates, context.tenant_id)
        
        self.log_info(f"Updated probate {probate_id}")

        return {
            "asset_id": probate_id,
            "status": "updated",
            "updates": updates
        }

    async def _list_probate(self, context: AgentContext) -> Dict[str, Any]:
        """List probates with optional filtering"""
        params = context.parameters
        filters = []
        
        if "case_status" in params:
            filters.append(("case_status", "==", params["case_status"]))
        if "county" in params:
            filters.append(("county", "==", params["county"]))

        probates = await self.storage.query(
            "probates",
            context.tenant_id,
            filters=filters,
            limit=params.get("limit", 50),
            order_by=params.get("order_by", "created_at")
        )

        return {
            "count": len(probates),
            "probates": probates
        }
