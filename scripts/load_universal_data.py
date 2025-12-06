import sys
import os
import asyncio
import argparse
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Google packages if missing
import types
try:
    import google.auth
    import google.cloud
    import google.adk
except ImportError:
    # Create module hierarchy
    google = types.ModuleType("google")
    sys.modules["google"] = google
    
    auth = MagicMock()
    sys.modules["google.auth"] = auth
    google.auth = auth
    
    cloud = MagicMock()
    sys.modules["google.cloud"] = cloud
    google.cloud = cloud
    
    firestore = MagicMock()
    sys.modules["google.cloud.firestore"] = firestore
    cloud.firestore = firestore
    
    genai = MagicMock()
    sys.modules["google.genai"] = genai
    google.genai = genai
    sys.modules["google.genai.types"] = MagicMock()
    
    adk = MagicMock()
    sys.modules["google.adk"] = adk
    google.adk = adk
    
    sys.modules["google.adk.agents"] = MagicMock()
    sys.modules["google.adk.types"] = MagicMock()
    sys.modules["google.adk.apps"] = MagicMock()
    sys.modules["google.adk.apps.app"] = MagicMock()
    
    # Mock Agent class specifically if needed by base classes
    class MockAgent:
        def __init__(self, *args, **kwargs): pass
    sys.modules["google.adk.agents"].Agent = MockAgent

from core.storage import FirestoreClient
# Import Agents
try:
    from agents.lien_tracker.agent import LienTrackerAgent
    from agents.judgment_tracker.agent import JudgmentTrackerAgent
    from agents.probate_tracker.agent import ProbateTrackerAgent
    from agents.mineral_tracker.agent import MineralTrackerAgent
    from agents.surplus_tracker.agent import SurplusTrackerAgent
except ImportError as e:
    print(f"Error importing agents: {e}")
    sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="Load mock data for all verticals")
    parser.add_argument("--tenant_id", default="demo-user", help="Tenant ID")
    args = parser.parse_args()
    
    tenant_id = args.tenant_id
    print(f"Loading data for tenant: {tenant_id}")
    
    storage = FirestoreClient(project_id="local-dev")
    
    # 1. Tax Liens
    print("Generating Tax Liens...")
    lien_agent = LienTrackerAgent(storage=storage)
    for i in range(1, 6):
        data = {
            "certificate_number": f"TL-{2024}-{i:03d}",
            "property_address": f"{100+i} Main St",
            "county": "Tax County",
            "purchase_amount": 1000 + (i * 100),
            "interest_rate": 18.0,
            "payment_status": "PENDING",
            "sale_date": (date.today() - timedelta(days=i*30)).isoformat(),
            "parcel_id": f"P-{123456+i}",
            "purchase_date": (date.today() - timedelta(days=i*30)).isoformat(),
            "redemption_deadline": (date.today() + timedelta(days=365 - i*30)).isoformat(),
            "status": "ACTIVE"
        }
        await lien_agent.run(tenant_id=tenant_id, task="create_lien", parameters=data)
        
    # 2. Civil Judgments
    print("Generating Civil Judgments...")
    judgment_agent = JudgmentTrackerAgent(storage=storage)
    for i in range(1, 6):
        data = {
            "case_number": f"CJ-{2024}-{i:03d}",
            "court_name": "Superior Court",
            "plaintiff_name": "Lender LLC",
            "defendant_name": f"Debtor {i}",
            "judgment_amount": 5000 + (i * 500),
            "judgment_date": (date.today() - timedelta(days=i*60)).isoformat(),
            "statute_limitations_date": (date.today() + timedelta(days=3650)).isoformat(), # 10 years
            "status": "ACTIVE",
            "county": "Judgment County"
        }
        await judgment_agent.run(tenant_id=tenant_id, task="create_judgment", parameters=data)
        
    # 3. Probate Estates
    print("Generating Probate Estates...")
    probate_agent = ProbateTrackerAgent(storage=storage)
    for i in range(1, 6):
        data = {
            "deceased_name": f"John Doe {i}",
            "date_of_death": (date.today() - timedelta(days=i*100)).isoformat(),
            "case_status": "Open",
            "county": "Probate County",
            "attorney_contact": f"attorney{i}@law.com",
            "probate_filing_date": (date.today() - timedelta(days=i*80)).isoformat(),
            "estimated_value": 200000 + (i * 10000),
            "mortgages_amount": 100000,
            "liens_amount": 5000
        }
        await probate_agent.run(tenant_id=tenant_id, task="create_probate", parameters=data)

    # 4. Mineral Rights
    print("Generating Mineral Rights...")
    mineral_agent = MineralTrackerAgent(storage=storage)
    for i in range(1, 6):
        data = {
            "legal_description": f"Section {i}, Township 5N, Range 3W",
            "net_mineral_acres": 10 + i,
            "royalty_decimal": 0.125,
            "operator_name": f"Operator {i}",
            "county": "Mineral County",
            "lease_expiration_date": (date.today() + timedelta(days=365*i)).isoformat()
        }
        await mineral_agent.run(tenant_id=tenant_id, task="create_mineral", parameters=data)

    # 5. Surplus Funds
    print("Generating Surplus Funds...")
    surplus_agent = SurplusTrackerAgent(storage=storage)
    for i in range(1, 6):
        data = {
            "foreclosure_date": (date.today() - timedelta(days=i*40)).isoformat(),
            "winning_bid_amount": 150000 + (i*1000),
            "total_debt_owed": 100000,
            "surplus_amount": 50000 + (i*1000),
            "claim_deadline": (date.today() + timedelta(days=120)).isoformat(),
            "county": "Surplus County"
        }
        await surplus_agent.run(tenant_id=tenant_id, task="create_surplus", parameters=data)

    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
