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

from agents.surplus_tracker.agent import SurplusTrackerAgent
from core.data_models import AssetType

@pytest.mark.asyncio
async def test_create_surplus_fund():
    # Setup
    storage = MagicMock()
    storage.create = AsyncMock(return_value=None)
    
    agent = SurplusTrackerAgent(storage=storage)
    tenant_id = "test-tenant"
    
    params = {
        "foreclosure_date": date(2023, 1, 1),
        "winning_bid_amount": 100000.00,
        "total_debt_owed": 50000.00,
        "surplus_amount": 50000.00,
        "claim_deadline": date(2023, 6, 1),
        "county": "Surplus County"
    }
    
    # Execute
    result = await agent.run(
        tenant_id=tenant_id,
        task="create_surplus",
        parameters=params
    )
    
    # Verify return structure
    assert result["status"] == "created"
    assert result["data"]["county"] == "Surplus County"
    
    # Verify storage call
    assert storage.create.called
    call_args = storage.create.call_args
    assert call_args[0][0] == "surplus_funds"
    saved_data = call_args[0][1]
    assert saved_data["asset_type"] == AssetType.SURPLUS_FUND
    # Decimal conversion check (serialized to float)
    assert isinstance(saved_data["surplus_amount"], float)
    assert saved_data["surplus_amount"] == 50000.00
    # Date conversion check (serialized to ISO string)
    assert isinstance(saved_data["foreclosure_date"], str)
    assert saved_data["foreclosure_date"] == "2023-01-01"

@pytest.mark.asyncio
async def test_list_surplus_funds():
    # Setup
    storage = MagicMock()
    mock_surplus = [
        {"id": "s1", "surplus_amount": 1000.0, "county": "C1"},
        {"id": "s2", "surplus_amount": 2000.0, "county": "C2"}
    ]
    storage.query = AsyncMock(return_value=mock_surplus)
    
    agent = SurplusTrackerAgent(storage=storage)
    tenant_id = "test-tenant"
    
    # Execute
    result = await agent.run(
        tenant_id=tenant_id,
        task="list_surplus",
        parameters={"limit": 10}
    )
    
    # Verify
    assert result["count"] == 2
    assert len(result["surplus_funds"]) == 2
    assert result["surplus_funds"][0]["id"] == "s1"
