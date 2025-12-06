import sys
from unittest.mock import MagicMock

# Mock google.adk if not installed
if "google.adk" not in sys.modules:
    sys.modules["google.adk"] = MagicMock()
    sys.modules["google.adk.agents"] = MagicMock()
    sys.modules["google.adk.types"] = MagicMock()
    sys.modules["google.adk.apps"] = MagicMock()
    sys.modules["google.adk.apps.app"] = MagicMock()
    sys.modules["google.adk.agents.context_cache_config"] = MagicMock()
    sys.modules["google.adk.apps.events_compaction_config"] = MagicMock()
    sys.modules["google.adk.apps.resumability_config"] = MagicMock()

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal

from agents.interest_calculator.agent import InterestCalculatorAgent
from agents.lien_tracker.agent import LienTrackerAgent
from agents.judgment_tracker.agent import JudgmentTrackerAgent
from core.data_models import CivilJudgment


@pytest.mark.asyncio
async def test_calculate_interest_tax_lien(storage, test_tenant_id, sample_lien_data):
    """Test interest calculation for a Tax Lien (legacy support)."""
    # Create a lien
    lien_agent = LienTrackerAgent(storage=storage)
    create_result = await lien_agent.run(
        tenant_id=test_tenant_id,
        task="create_lien",
        parameters=sample_lien_data
    )
    lien_id = create_result["lien_id"]

    # Calculate interest
    agent = InterestCalculatorAgent(storage=storage)
    result = await agent.run(
        tenant_id=test_tenant_id,
        task="calculate_interest",
        lien_ids=[lien_id]
    )

    assert result["lien_id"] == lien_id
    assert result["principal"] == sample_lien_data["purchase_amount"]
    assert result["interest_rate"] == sample_lien_data["interest_rate"]
    assert result["days_elapsed"] >= 0
    assert result["interest_accrued"] >= 0


@pytest.mark.asyncio
async def test_calculate_interest_civil_judgment(storage, test_tenant_id):
    """Test interest calculation for a Civil Judgment."""
    # Create a judgment
    judgment_data = {
        "case_number": "CASE-2024-001",
        "court_name": "Superior Court",
        "judgment_date": (date.today() - timedelta(days=100)).isoformat(),
        "defendant_name": "John Doe",
        "judgment_amount": 10000.00,
        "interest_rate": 10.0,
        "status": "ACTIVE",
        "county": "Test County",
        "statute_limitations_date": (date.today() + timedelta(days=3650)).isoformat()
    }

    judgment_agent = JudgmentTrackerAgent(storage=storage)
    create_result = await judgment_agent.run(
        tenant_id=test_tenant_id,
        task="create_judgment",
        parameters=judgment_data
    )
    asset_id = create_result["asset_id"]

    # Calculate interest using asset_ids
    # Note: InterestCalculatorAgent should handle context.asset_ids
    agent = InterestCalculatorAgent(storage=storage)
    result = await agent.run(
        tenant_id=test_tenant_id,
        task="calculate_interest",
        asset_ids=[asset_id]
        # logic also supports lien_ids fallback if we passed asset_id as lien_id,
        # but technically we should use asset_ids context field if available or just lien_ids for backward compat.
        # The agent update handled checking both.
    )

    assert result["lien_id"] == asset_id
    assert result["principal"] == 10000.00
    assert result["interest_rate"] == 10.0
    assert result["days_elapsed"] == 100
    
    # 10000 * 0.10 * (100/365) = 1000 * 0.2739... = 273.97
    expected_interest = 10000.0 * 0.10 * (100 / 365.0)
    assert abs(result["interest_accrued"] - expected_interest) < 0.1
    assert result["total_owed"] > 10000.0
