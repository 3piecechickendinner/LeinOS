import pytest
import sys
from unittest.mock import MagicMock, AsyncMock
from datetime import date, datetime, timedelta
from decimal import Decimal

# Mock google.adk dependencies if needed (already done in conftest or here)
if "google.adk" not in sys.modules:
    sys.modules["google.adk"] = MagicMock()
    sys.modules["google.adk.agents"] = MagicMock()
    sys.modules["google.adk.types"] = MagicMock()
    sys.modules["google.adk.apps"] = MagicMock()
    sys.modules["google.adk.apps.app"] = MagicMock()

from agents.interest_calculator.agent import InterestCalculatorAgent
from agents.deadline_alert.agent import DeadlineAlertAgent

@pytest.mark.asyncio
async def test_all_verticals_interest_calculation():
    storage = MagicMock()
    
    # Mock data for all 5 types
    mock_data = {
        "liens": {"l1": {"purchase_amount": 1000, "interest_rate": 10, "purchase_date": "2023-01-01"}},
        "judgments": {"j1": {"judgment_amount": 5000, "interest_rate": 5, "judgment_date": "2023-01-01"}},
        "probate_estates": {"p1": {"estimated_value": 100000, "mortgages_amount": 50000, "liens_amount": 10000}},
        "minerals": {"m1": {"net_mineral_acres": 10, "royalty_decimal": 0.125}},
        "surplus_funds": {"s1": {"surplus_amount": 10000}}
    }
    
    async def mock_get(collection, doc_id, tenant_id):
        return mock_data.get(collection, {}).get(doc_id)
        
    storage.get = AsyncMock(side_effect=mock_get)
    
    agent = InterestCalculatorAgent(storage=storage)
    tenant_id = "test-tenant"

    # 1. Tax Lien
    res = await agent.run(tenant_id=tenant_id, task="calculate_interest", asset_ids=["l1"])
    assert res["label"] == "Total Owed"
    assert res["principal"] == 1000.0
    
    # 2. Civil Judgment
    res = await agent.run(tenant_id=tenant_id, task="calculate_interest", asset_ids=["j1"])
    assert res["label"] == "Total Owed"
    assert res["principal"] == 5000.0

    # 3. Probate
    res = await agent.run(tenant_id=tenant_id, task="calculate_interest", asset_ids=["p1"])
    assert res["label"] == "Estimated Equity"
    # 100k - (50k + 10k) = 40k
    assert res["value"] == 40000.0

    # 4. Mineral Rights
    res = await agent.run(tenant_id=tenant_id, task="calculate_interest", asset_ids=["m1"])
    assert res["label"] == "Monthly Revenue Estimate"
    # 10 * 0.125 * 80 * 30 = 3000
    assert res["value"] == 3000.0

    # 5. Surplus Funds
    res = await agent.run(tenant_id=tenant_id, task="calculate_interest", asset_ids=["s1"])
    assert res["label"] == "Potential Fee"
    # 10000 * 0.30 = 3000
    assert res["value"] == 3000.0

@pytest.mark.asyncio
async def test_all_verticals_deadline_creation():
    storage = MagicMock()
    
    # Mock data for all 5 types
    mock_data = {
        "liens": {"l1": {"redemption_deadline": "2023-12-31", "property_address": "123 Main"}},
        "judgments": {"j1": {"statute_limitations_date": "2030-01-01"}},
        "probate_estates": {"p1": {"probate_filing_date": "2023-01-01"}},
        "minerals": {"m1": {"lease_expiration_date": "2025-06-01"}},
        "surplus_funds": {"s1": {"claim_deadline": "2024-01-01"}}
    }
    
    async def mock_get(collection, doc_id, tenant_id):
        return mock_data.get(collection, {}).get(doc_id)
        
    storage.get = AsyncMock(side_effect=mock_get)
    storage.create = AsyncMock(return_value=None)
    
    agent = DeadlineAlertAgent(storage=storage)
    tenant_id = "test-tenant"

    # 1. Tax Lien
    await agent.run(tenant_id=tenant_id, task="create_deadline", asset_ids=["l1"])
    call_args = storage.create.call_args
    assert call_args[0][0] == "deadlines"
    assert call_args[0][1]["deadline_type"] == "redemption"
    assert call_args[0][1]["deadline_date"] == "2023-12-31"

    # 2. Civil Judgment
    await agent.run(tenant_id=tenant_id, task="create_deadline", asset_ids=["j1"])
    call_args = storage.create.call_args
    assert call_args[0][1]["deadline_type"] == "expiration"
    assert call_args[0][1]["deadline_date"] == "2030-01-01"

    # 3. Probate
    await agent.run(tenant_id=tenant_id, task="create_deadline", asset_ids=["p1"])
    call_args = storage.create.call_args
    assert call_args[0][1]["deadline_type"] == "claim_period"
    # 2023-01-01 + 180 days approx 2023-06-30
    assert call_args[0][1]["deadline_date"] == "2023-06-30"

    # 4. Mineral Rights
    await agent.run(tenant_id=tenant_id, task="create_deadline", asset_ids=["m1"])
    call_args = storage.create.call_args
    assert call_args[0][1]["deadline_type"] == "lease_expiration"
    assert call_args[0][1]["deadline_date"] == "2025-06-01"

    # 5. Surplus Funds
    await agent.run(tenant_id=tenant_id, task="create_deadline", asset_ids=["s1"])
    call_args = storage.create.call_args
    assert call_args[0][1]["deadline_type"] == "escheatment"
    assert call_args[0][1]["deadline_date"] == "2024-01-01"
