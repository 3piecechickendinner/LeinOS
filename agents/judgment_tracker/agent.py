from typing import Dict, Any, List, Optional
from datetime import datetime, date
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext, CivilJudgment, AssetType
from core.storage import FirestoreClient


class JudgmentTrackerAgent(LienOSBaseAgent):
    """
    Agent responsible for managing Civil Judgments.
    Handles creation, retrieval, updates, and listing of judgments.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="JudgmentTracker",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return [
            "create_judgment",
            "get_judgment",
            "update_judgment",
            "list_judgments"
        ]

    def _register_tools(self) -> None:
        """No external tools needed for basic CRUD"""
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """Execute the requested task"""
        if context.task == "create_judgment":
            return await self._create_judgment(context)
        elif context.task == "get_judgment":
            return await self._get_judgment(context)
        elif context.task == "update_judgment":
            return await self._update_judgment(context)
        elif context.task == "list_judgments":
            return await self._list_judgments(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _create_judgment(self, context: AgentContext) -> Dict[str, Any]:
        """Create a new civil judgment"""
        params = context.parameters
        
        # Validate required fields
        required_fields = [
            "case_number", "court_name", "judgment_date", 
            "defendant_name", "judgment_amount", "county"
        ]
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")

        # Generate ID if not provided
        judgment_id = params.get("asset_id")
        if not judgment_id:
            judgment_id = f"judgment_{params['case_number']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Parse dates
        judgment_date = params["judgment_date"]
        if isinstance(judgment_date, str):
            judgment_date = date.fromisoformat(judgment_date)

        statute_limitations_date = params.get("statute_limitations_date")
        if isinstance(statute_limitations_date, str):
            statute_limitations_date = date.fromisoformat(statute_limitations_date)

        # Create judgment object
        judgment = CivilJudgment(
            asset_id=judgment_id,
            tenant_id=context.tenant_id,
            case_number=params["case_number"],
            court_name=params["court_name"],
            judgment_date=judgment_date,
            defendant_name=params["defendant_name"],
            judgment_amount=Decimal(str(params["judgment_amount"])),
            purchase_amount=Decimal(str(params.get("purchase_amount", "0"))),
            interest_rate=Decimal(str(params.get("interest_rate", "0"))),
            status=params.get("status", "ACTIVE"),
            county=params["county"],
            statute_limitations_date=statute_limitations_date,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to storage
        judgment_dict = judgment.model_dump()
        judgment_dict["id"] = judgment_id
        await self.storage.create("judgments", judgment_dict, context.tenant_id)

        self.log_info(f"Created judgment {judgment_id} for case {params['case_number']}")

        return {
            "asset_id": judgment_id,
            "status": "created",
            "data": judgment_dict
        }

    async def _get_judgment(self, context: AgentContext) -> Dict[str, Any]:
        """Get a judgment by ID"""
        if not context.asset_ids or len(context.asset_ids) == 0:
            raise ValueError("asset_id required in context.asset_ids")

        judgment_id = context.asset_ids[0]
        judgment_data = await self.storage.get("judgments", judgment_id, context.tenant_id)

        if not judgment_data:
            return {"found": False, "asset_id": judgment_id}

        return {
            "found": True,
            "asset_id": judgment_id,
            **judgment_data
        }

    async def _update_judgment(self, context: AgentContext) -> Dict[str, Any]:
        """Update a judgment"""
        if not context.asset_ids or len(context.asset_ids) == 0:
            raise ValueError("asset_id required in context.asset_ids")

        judgment_id = context.asset_ids[0]
        updates = context.parameters
        
        # Add timestamp
        updates["updated_at"] = datetime.now()

        await self.storage.update("judgments", judgment_id, updates, context.tenant_id)
        
        self.log_info(f"Updated judgment {judgment_id}")

        return {
            "asset_id": judgment_id,
            "status": "updated",
            "updates": updates
        }

    async def _list_judgments(self, context: AgentContext) -> Dict[str, Any]:
        """List judgments with optional filtering"""
        params = context.parameters
        filters = []
        
        if "status" in params:
            filters.append(("status", "==", params["status"]))
        if "county" in params:
            filters.append(("county", "==", params["county"]))

        judgments = await self.storage.query(
            "judgments",
            context.tenant_id,
            filters=filters,
            limit=params.get("limit", 50),
            order_by=params.get("order_by", "created_at")
        )

        return {
            "count": len(judgments),
            "judgments": judgments
        }
