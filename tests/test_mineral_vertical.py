import pytest
import sys
from unittest.mock import MagicMock, AsyncMock
from datetime import date, datetime
from decimal import Decimal

# Mock google.adk dependencies
if "google.adk" not in sys.modules:
    sys.modules["google.adk"] = MagicMock()
    sys.modules["google.adk.agents"] = MagicMock()
    sys.modules["google.adk.types"] = MagicMock()
    sys.modules["google.adk.apps"] = MagicMock()
    sys.modules["google.adk.apps.app"] = MagicMock()

from agents.mineral_tracker.agent import MineralTrackerAgent
from core.data_models import AssetType

@pytest.mark.asyncio
async def test_create_mineral_right():
    # Setup
    storage = MagicMock()
    storage.create = AsyncMock(return_value=None)
    
    agent = MineralTrackerAgent(storage=storage)
    tenant_id = "test-tenant"
    
    params = {
        "legal_description": "Section 10, Township 5N, Range 3W",
        "net_mineral_acres": 12.5,
        "royalty_decimal": 0.125,
        "operator_name": "Big Oil Corp",
        "county": "Midland"
    }
    
    # Execute
    result = await agent.run(
        tenant_id=tenant_id,
        task="create_mineral",
        parameters=params
    )
    
    # Verify return structure
    assert result["status"] == "created"
    assert result["data"]["legal_description"] == "Section 10, Township 5N, Range 3W"
    assert result["data"]["operator_name"] == "Big Oil Corp"
    
    # Verify storage call
    assert storage.create.called
    call_args = storage.create.call_args
    assert call_args[0][0] == "minerals"
    saved_data = call_args[0][1]
    assert saved_data["legal_description"] == params["legal_description"]
    assert saved_data["asset_type"] == AssetType.MINERAL_RIGHT
    # Decimal conversion check (serialized to float)
    assert isinstance(saved_data["net_mineral_acres"], float)
    assert saved_data["net_mineral_acres"] == 12.5

@pytest.mark.asyncio
async def test_list_mineral_rights():
    # Setup
    storage = MagicMock()
    mock_minerals = [
        {"id": "m1", "legal_description": "Desc 1", "operator_name": "Op 1"},
        {"id": "m2", "legal_description": "Desc 2", "operator_name": "Op 2"}
    ]
    storage.query = AsyncMock(return_value=mock_minerals)
    
    agent = MineralTrackerAgent(storage=storage)
    tenant_id = "test-tenant"
    
    # Execute
    result = await agent.run(
        tenant_id=tenant_id,
        task="list_mineral",
        parameters={"limit": 10}
    )
    
    # Verify
    assert result["count"] == 2
    assert len(result["minerals"]) == 2
    assert result["minerals"][0]["id"] == "m1"
