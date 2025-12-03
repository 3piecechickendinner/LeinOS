"""

Quick test script for InterestCalculatorAgent.

Run with: python test_interest_calculator.py

"""



import asyncio

from datetime import date, timedelta

from decimal import Decimal

import uuid



from core.storage import FirestoreClient

from core.data_models import Lien, LienStatus

from agents.interest_calculator.agent import InterestCalculatorAgent





async def test_interest_calculator():

    """Test the interest calculator with a sample lien"""

    

    # Initialize storage (will use actual Firestore if credentials set, otherwise will fail gracefully)

    try:

        storage = FirestoreClient(project_id="test-project")

        print("✓ Storage client initialized")

    except Exception as e:

        print(f"✗ Storage initialization failed: {e}")

        print("  (This is expected if you haven't set up Google Cloud credentials yet)")

        return

    

    # Create a test lien

    tenant_id = "test_tenant_123"

    lien_id = str(uuid.uuid4())

    

    test_lien = Lien(

        lien_id=lien_id,

        tenant_id=tenant_id,

        certificate_number="CERT-2024-001",

        purchase_amount=Decimal("5000.00"),

        interest_rate=Decimal("18.0"),  # 18% annual interest

        sale_date=date.today() - timedelta(days=365),  # Purchased 1 year ago

        redemption_deadline=date.today() + timedelta(days=730),  # 2 years to redeem

        status=LienStatus.ACTIVE,

        county="San Diego",

        property_address="123 Main St, San Diego, CA 92101",

        parcel_id="123-456-789"

    )

    

    print(f"\n📋 Test Lien Created:")

    print(f"   ID: {lien_id}")

    print(f"   Principal: ${test_lien.purchase_amount}")

    print(f"   Interest Rate: {test_lien.interest_rate}%")

    print(f"   Days Held: 365")

    print(f"   Expected Interest: ~${float(test_lien.purchase_amount) * 0.18:.2f}")

    

    # Save to Firestore

    try:

        lien_dict = test_lien.model_dump()

        await storage.create("liens", lien_dict, tenant_id)

        print("✓ Test lien saved to Firestore")

    except Exception as e:

        print(f"✗ Failed to save lien: {e}")

        return

    

    # Initialize Interest Calculator Agent

    agent = InterestCalculatorAgent(storage=storage)

    print(f"\n🤖 Agent initialized: {agent.agent_name}")

    print(f"   Capabilities: {agent.capabilities}")

    

    # Run the agent

    try:

        result = await agent.run(

            tenant_id=tenant_id,

            task="calculate_interest",

            lien_ids=[lien_id]

        )

        

        print(f"\n✓ Interest Calculation Complete:")

        print(f"   Principal: ${result['principal']:.2f}")

        print(f"   Interest Rate: {result['interest_rate']}%")

        print(f"   Days Elapsed: {result['days_elapsed']}")

        print(f"   Interest Accrued: ${result['interest_accrued']:.2f}")

        print(f"   Total Owed: ${result['total_owed']:.2f}")

        

    except Exception as e:

        print(f"\n✗ Agent execution failed: {e}")

        import traceback

        traceback.print_exc()





if __name__ == "__main__":

    print("🧪 Testing InterestCalculatorAgent...\n")

    asyncio.run(test_interest_calculator())

    print("\n✅ Test complete!")

