import pytest
from datetime import date, datetime
from decimal import Decimal
from agents.judgment_tracker.agent import JudgmentTrackerAgent
from core.storage import FirestoreClient

@pytest.fixture
def storage():
    return FirestoreClient(project_id="local-dev")

@pytest.fixture
def agent(storage):
    return JudgmentTrackerAgent(storage=storage)

@pytest.fixture
def tenant_id():
    return "test-tenant-judgment"

@pytest.mark.asyncio
async def test_create_judgment(agent, tenant_id):
    params = {
        "case_number": "CASE-2024-001",
        "court_name": "Circuit Court",
        "judgment_date": date.today().isoformat(),
        "defendant_name": "John Doe",
        "judgment_amount": 5000.00,
        "county": "Test County",
        "status": "ACTIVE"
    }
    
    result = await agent.run(
        tenant_id=tenant_id,
        task="create_judgment",
        parameters=params
    )
    
    assert result["status"] == "created"
    assert result["data"]["case_number"] == "CASE-2024-001"
    assert result["data"]["judgment_amount"] == 5000.00

@pytest.mark.asyncio
async def test_get_judgment(agent, tenant_id):
    # Create first
    create_params = {
        "case_number": "CASE-2024-002",
        "court_name": "Circuit Court",
        "judgment_date": date.today().isoformat(),
        "defendant_name": "Jane Doe",
        "judgment_amount": 7500.00,
        "county": "Test County"
    }
    create_result = await agent.run(
        tenant_id=tenant_id,
        task="create_judgment",
        parameters=create_params
    )
    judgment_id = create_result["asset_id"]
    
    # Get
    result = await agent.run(
        tenant_id=tenant_id,
        task="get_judgment",
        asset_ids=[judgment_id]
    )
    
    assert result["found"] is True
    assert result["asset_id"] == judgment_id
    assert result["case_number"] == "CASE-2024-002"

@pytest.mark.asyncio
async def test_update_judgment(agent, tenant_id):
    # Create first
    create_params = {
        "case_number": "CASE-2024-003",
        "court_name": "Circuit Court",
        "judgment_date": date.today().isoformat(),
        "defendant_name": "Bob Smith",
        "judgment_amount": 1000.00,
        "county": "Test County"
    }
    create_result = await agent.run(
        tenant_id=tenant_id,
        task="create_judgment",
        parameters=create_params
    )
    judgment_id = create_result["asset_id"]
    
    # Update
    update_params = {"status": "SATISFIED"}
    result = await agent.run(
        tenant_id=tenant_id,
        task="update_judgment",
        asset_ids=[judgment_id],
        parameters=update_params
    )
    
    assert result["status"] == "updated"
    
    # Verify update
    get_result = await agent.run(
        tenant_id=tenant_id,
        task="get_judgment",
        asset_ids=[judgment_id]
    )
    assert get_result["status"] == "SATISFIED"

@pytest.mark.asyncio
async def test_list_judgments(agent, tenant_id):
    # Create a few judgments
    for i in range(3):
        await agent.run(
            tenant_id=tenant_id,
            task="create_judgment",
            parameters={
                "case_number": f"LIST-CASE-{i}",
                "court_name": "Circuit Court",
                "judgment_date": date.today().isoformat(),
                "defendant_name": f"Defendant {i}",
                "judgment_amount": 1000.00 + (i * 100),
                "county": "List County",
                "status": "ACTIVE" if i < 2 else "SATISFIED"
            }
        )
    
    # List all
    result = await agent.run(
        tenant_id=tenant_id,
        task="list_judgments",
        parameters={"limit": 10}
    )
    assert result["count"] >= 3
    
    # Filter by status
    active_result = await agent.run(
        tenant_id=tenant_id,
        task="list_judgments",
        parameters={"status": "ACTIVE"}
    )
    # Note: count might be higher if other tests run first, but at least 2 we just created
    assert active_result["count"] >= 2
    for j in active_result["judgments"]:
        assert j["status"] == "ACTIVE"
