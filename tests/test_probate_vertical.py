import pytest
import sys
from unittest.mock import MagicMock, AsyncMock
from datetime import date, datetime

# Mock google.adk dependencies
if "google.adk" not in sys.modules:
    sys.modules["google.adk"] = MagicMock()
    sys.modules["google.adk.agents"] = MagicMock()
    sys.modules["google.adk.types"] = MagicMock()
    sys.modules["google.adk.apps"] = MagicMock()
    sys.modules["google.adk.apps.app"] = MagicMock()

from agents.probate_tracker.agent import ProbateTrackerAgent
from core.verticals.probate import ProbateEstate
from core.data_models import AgentContext

@pytest.mark.asyncio
async def test_create_probate_estate():
    # Setup
    storage = MagicMock()
    storage.create = AsyncMock(return_value=None)
    
    agent = ProbateTrackerAgent(storage=storage)
    tenant_id = "test-tenant"
    
    params = {
        "deceased_name": "John Doe",
        "date_of_death": "2023-01-01",
        "case_status": "OPEN",
        "county": "Miami-Dade",
        "attorney_contact": "Jane Lawyer"
    }
    
    # Execute
    result = await agent.run(
        tenant_id=tenant_id,
        task="create_probate",
        parameters=params
    )
    
    # Verify
    assert result["status"] == "created"
    assert result["data"]["deceased_name"] == "John Doe"
    assert result["data"]["case_status"] == "OPEN"
    
    # Verify proper type conversion in model
    assert storage.create.called
    call_args = storage.create.call_args
    assert call_args[0][0] == "probates"
    saved_data = call_args[0][1]
    assert saved_data["deceased_name"] == "John Doe"
    assert saved_data["asset_type"] == "PROBATE"

@pytest.mark.asyncio
async def test_list_probate_estates():
    # Setup
    storage = MagicMock()
    mock_probates = [
        {"id": "p1", "deceased_name": "A", "created_at": "2023-01-01"},
        {"id": "p2", "deceased_name": "B", "created_at": "2023-01-02"}
    ]
    storage.query = AsyncMock(return_value=mock_probates)
    
    agent = ProbateTrackerAgent(storage=storage)
    tenant_id = "test-tenant"
    
    # Execute
    result = await agent.run(
        tenant_id=tenant_id,
        task="list_probate",
        parameters={"limit": 10}
    )
    
    # Verify
    assert result["count"] == 2
    assert len(result["probates"]) == 2
