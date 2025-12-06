import sys
import os
import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock
import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Google packages if missing (Copied from load_universal_data.py for stability)
# Handle Google Cloud imports
try:
    import google.auth
    import google.cloud
    import google.cloud.firestore
except ImportError:
    print("CRITICAL ERROR: google.cloud and google.auth modules are required.")
    print("Please install them with: pip install google-cloud-firestore google-auth")
    sys.exit(1)

# Handle ADK imports (Mock if missing, as we only need Agents logic)
try:
    import google.adk
except ImportError:
    # Check if google.adk is already in sys.modules (partial install)
    if "google.adk" not in sys.modules:
        adk = MagicMock()
        sys.modules["google.adk"] = adk
        if hasattr(google, 'adk'):
             google.adk = adk
        
        sys.modules["google.adk.agents"] = MagicMock()
        sys.modules["google.adk.types"] = MagicMock()
        sys.modules["google.adk.apps"] = MagicMock()
        sys.modules["google.adk.apps.app"] = MagicMock()
        
        # Mock Agent class specifically if needed by base classes
        class MockAgent:
            def __init__(self, *args, **kwargs): pass
        sys.modules["google.adk.agents"].Agent = MockAgent

# Import your agents (The "Engines")
from core.storage import FirestoreClient
try:
    from agents.lien_tracker.agent import LienTrackerAgent
    from agents.judgment_tracker.agent import JudgmentTrackerAgent
    from agents.mineral_tracker.agent import MineralTrackerAgent
    from agents.probate_tracker.agent import ProbateTrackerAgent
    from agents.surplus_tracker.agent import SurplusTrackerAgent
except ImportError as e:
    print(f"Error importing agents: {e}")
    sys.exit(1)

# Constants for "Big Data"
TENANT_ID = "demo-user"
COUNTIES = ["Miami-Dade", "Cook", "Harris", "Maricopa", "San Bernardino", "Clark", "Fulton", "Bexar"]
NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
COMPANIES = ["Energy Inc", "Permian Resources", "Eagle Ford Ops", "Bakken Drillers", "GeoWest"]

class SimpleContext:
    def __init__(self, parameters):
        self.parameters = parameters
        self.tenant_id = parameters.get("tenant_id")

async def generate_bulk_data():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID") or os.getenv("GOOGLE_PROJECT_ID")
    if not project_id:
        print("⚠️  WARNING: No GOOGLE_CLOUD_PROJECT_ID found in .env. Defaulting to 'local-dev'.")
        project_id = "local-dev"
        
    print(f"🚀 Initializing Big Data Loader for tenant: {TENANT_ID}")
    print(f"🔌 Connecting to Firestore Project: {project_id}")
    
    # Initialize Storage with real Project ID
    storage = FirestoreClient(project_id=project_id) 
    
    agents = {
        "tax_lien": LienTrackerAgent(storage),
        "civil_judgment": JudgmentTrackerAgent(storage),
        "mineral_rights": MineralTrackerAgent(storage),
        "probate": ProbateTrackerAgent(storage),
        "surplus_funds": SurplusTrackerAgent(storage)
    }

    # 1. Generate 50 Tax Liens
    print("   ... Generating 50 Tax Liens")
    for i in range(50):
        await agents["tax_lien"]._create_lien(SimpleContext({
            "tenant_id": TENANT_ID,
            "certificate_number": f"TL-{2024000 + i}",
            "purchase_amount": random.randint(1000, 25000),
            "interest_rate": random.choice([8, 12, 18, 24]),
            "sale_date": (datetime.now() - timedelta(days=random.randint(30, 700))).date().isoformat(),
            "redemption_deadline": (datetime.now() + timedelta(days=random.randint(10, 365))).date().isoformat(),
            "county": random.choice(COUNTIES),
            "property_address": f"{random.randint(100, 9999)} {random.choice(NAMES)} St",
            "parcel_id": f"P-{random.randint(10000, 99999)}",
            "status": "ACTIVE"
        }))

    # 2. Generate 50 Civil Judgments
    print("   ... Generating 50 Civil Judgments")
    for i in range(50):
        await agents["civil_judgment"]._create_judgment(SimpleContext({
            "tenant_id": TENANT_ID,
            "case_number": f"CV-{2023}-{random.randint(1000, 9999)}",
            "defendant_name": f"{random.choice(NAMES)} Construction LLC",
            "judgment_amount": random.randint(5000, 150000),
            "judgment_date": (datetime.now() - timedelta(days=random.randint(100, 1500))).date().isoformat(),
            "interest_rate": 10.0,
            "court_name": f"{random.choice(COUNTIES)} Superior Court",
            "county": random.choice(COUNTIES),
            "status": random.choice(["ACTIVE", "GARNISHING", "SETTLED"])
        }))

    # 3. Generate 30 Mineral Rights
    print("   ... Generating 30 Mineral Rights")
    for i in range(30):
        await agents["mineral_rights"]._create_mineral(SimpleContext({
            "tenant_id": TENANT_ID,
            "legal_description": f"Section {random.randint(1, 36)}, Block {random.randint(1, 100)}",
            "net_mineral_acres": random.uniform(5.0, 640.0),
            "royalty_decimal": random.choice([0.125, 0.1875, 0.20, 0.25]),
            "operator_name": random.choice(COMPANIES),
            "county": random.choice(COUNTIES),
            "status": random.choice(["LEASED", "PRODUCING", "OPEN"])
        }))

    # 4. Generate 20 Probate Cases
    print("   ... Generating 20 Probate Leads")
    for i in range(20):
        await agents["probate"]._create_probate(SimpleContext({
            "tenant_id": TENANT_ID,
            "deceased_name": f"{random.choice(['John', 'Jane', 'Robert', 'Mary'])} {random.choice(NAMES)}",
            "date_of_death": (datetime.now() - timedelta(days=random.randint(30, 180))).date().isoformat(),
            "case_status": "OPEN",
            "county": random.choice(COUNTIES),
            "attorney_contact": f"Law Offices of {random.choice(NAMES)}"
        }))

    # 5. Generate 20 Surplus Funds
    print("   ... Generating 20 Surplus Claims")
    for i in range(20):
        bid = random.randint(200000, 500000)
        debt = bid - random.randint(20000, 100000)
        await agents["surplus_funds"]._create_surplus(SimpleContext({
            "tenant_id": TENANT_ID,
            "foreclosure_date": (datetime.now() - timedelta(days=random.randint(30, 90))).date().isoformat(),
            "winning_bid_amount": bid,
            "total_debt_owed": debt,
            "surplus_amount": bid - debt,
            "claim_deadline": (datetime.now() + timedelta(days=120)).date().isoformat(),
            "county": random.choice(COUNTIES)
        }))

    print("🎉 DONE! 170 Assets Loaded.")

if __name__ == "__main__":
    asyncio.run(generate_bulk_data())
