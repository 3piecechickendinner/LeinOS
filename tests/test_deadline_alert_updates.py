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

from agents.deadline_alert.agent import DeadlineAlertAgent
from agents.judgment_tracker.agent import JudgmentTrackerAgent
from agents.lien_tracker.agent import LienTrackerAgent
from core.data_models import Deadline

@pytest.mark.asyncio
async def test_create_deadline_tax_lien(storage, test_tenant_id, sample_lien_data):
    """Test creating a deadline for a Tax Lien."""
    # Create lien
    lien_agent = LienTrackerAgent(storage=storage)
    create_result = await lien_agent.run(
        tenant_id=test_tenant_id,
        task="create_lien",
        parameters=sample_lien_data
    )
    lien_id = create_result["lien_id"]

    agent = DeadlineAlertAgent(storage=storage)
    # Manually trigger checking creation directly to verify the specific logic used
    # But usually 'create_lien' triggers are implicit. here we manually call create_deadline task if agent supports it
    result = await agent.run(
        tenant_id=test_tenant_id,
        task="create_deadline",
        lien_ids=[lien_id]
    )

    assert result["created"] is True
    assert "redemption" in result["deadline_id"]


@pytest.mark.asyncio
async def test_create_deadline_civil_judgment(storage, test_tenant_id):
    """Test creating a deadline for a Civil Judgment."""
    # Create judgment
    judgment_data = {
        "case_number": "CASE-2024-DEADLINE",
        "court_name": "Superior Court",
        "judgment_date": date.today().isoformat(),
        "defendant_name": "Jane Doe",
        "judgment_amount": 5000.00,
        "county": "Test County",
        "statute_limitations_date": (date.today() + timedelta(days=3650)).isoformat() # 10 years
    }

    judgment_agent = JudgmentTrackerAgent(storage=storage)
    create_result = await judgment_agent.run(
        tenant_id=test_tenant_id,
        task="create_judgment",
        parameters=judgment_data
    )
    asset_id = create_result["asset_id"]

    agent = DeadlineAlertAgent(storage=storage)
    result = await agent.run(
        tenant_id=test_tenant_id,
        task="create_deadline",
        asset_ids=[asset_id]
    )

    assert result["created"] is True
    assert result["asset_id"] == asset_id
    # Verify description or type
    
    # We can check storage to be sure
    deadlines = await storage.query("deadlines", test_tenant_id)
    judgment_deadline = next((d for d in deadlines if d["lien_id"] == asset_id), None)
    
    assert judgment_deadline is not None
    assert judgment_deadline["description"] == 'Judgment Expiration / Renewal Deadline'
    assert judgment_deadline["deadline_date"] == judgment_data["statute_limitations_date"]
