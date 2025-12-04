#!/usr/bin/env python3
"""
Load mock tax lien data into Firestore for testing and demo purposes.

This script creates realistic sample data including:
- Tax liens with varied statuses, amounts, and dates
- Redemption deadlines
- Payment records for redeemed liens

Usage:
    python scripts/load_mock_data.py
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Add parent directory to path to import from core and agents
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from core.storage import FirestoreClient
from core.data_models import LienStatus, PaymentStatus, NotificationType

# Load environment variables
load_dotenv()


def generate_lien_id(certificate_number: str, sale_date: date) -> str:
    """Generate a lien ID from certificate number and sale date."""
    timestamp = sale_date.strftime("%Y%m%d%H%M%S")
    # Use the base certificate without state prefix for consistency
    cert_base = certificate_number.split('-')[-1]
    return f"lien_{cert_base}_{timestamp}"


def create_mock_liens() -> list:
    """Create 12 realistic mock tax liens."""

    # Base data for generating realistic liens
    florida_counties = [
        "Miami-Dade", "Broward", "Palm Beach", "Hillsborough",
        "Orange", "Pinellas", "Duval", "Lee"
    ]

    addresses = [
        ("123 Ocean Drive", "Miami", "33139"),
        ("456 Las Olas Blvd", "Fort Lauderdale", "33301"),
        ("789 Worth Ave", "Palm Beach", "33480"),
        ("321 Bay Shore Dr", "Tampa", "33602"),
        ("654 Park Ave", "Miami Beach", "33140"),
        ("987 Collins Ave", "Miami Beach", "33139"),
        ("147 Brickell Ave", "Miami", "33131"),
        ("258 Atlantic Blvd", "Pompano Beach", "33062"),
        ("369 Clematis St", "West Palm Beach", "33401"),
        ("741 Flagler Dr", "West Palm Beach", "33401"),
        ("852 Beach Blvd", "Jacksonville Beach", "32250"),
        ("963 Fifth Ave", "Naples", "34102"),
    ]

    # Generate liens with realistic variation
    liens = []
    current_date = date.today()

    for i in range(12):
        county = random.choice(florida_counties[:3])  # Focus on main 3 counties
        street, city, zipcode = addresses[i]

        # Generate dates
        months_ago = random.randint(6, 18)
        sale_date = current_date - timedelta(days=months_ago * 30)
        redemption_deadline = sale_date + timedelta(days=730)  # 2 years

        # Most liens are active, a few are redeemed
        status = "ACTIVE" if i < 10 else "REDEEMED"

        # Generate amounts
        purchase_amount = Decimal(random.randrange(2500, 15000, 500))
        interest_rate = Decimal(random.choice([12, 15, 18, 18, 18, 24]))  # 18% most common

        # Generate IDs
        cert_number = f"{county[:2].upper()}-{sale_date.year}-{1000 + i:04d}"
        parcel_id = f"{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(10, 99)}-{random.randint(100, 999)}"

        lien = {
            "certificate_number": cert_number,
            "purchase_amount": purchase_amount,
            "interest_rate": interest_rate,
            "sale_date": sale_date,
            "redemption_deadline": redemption_deadline,
            "status": status,
            "county": county,
            "property_address": f"{street}, {city}, FL {zipcode}",
            "parcel_id": parcel_id,
        }

        liens.append(lien)

    return liens


def create_mock_deadlines(lien_ids: list) -> list:
    """Create 4 mock deadlines for various liens."""
    current_date = date.today()

    deadlines = []

    # Create deadlines at various intervals
    deadline_days = [30, 60, 90, 120]
    deadline_types = ["redemption", "notice_required", "interest_calculation", "annual_review"]

    for i in range(min(4, len(lien_ids))):
        lien_id = lien_ids[i]
        days_out = deadline_days[i]
        deadline_type = deadline_types[i]

        deadline = {
            "lien_id": lien_id,
            "deadline_type": deadline_type,
            "due_date": current_date + timedelta(days=days_out),
            "description": f"{deadline_type.replace('_', ' ').title()} for {lien_id}",
            "status": "pending",
            "created_at": datetime.now(),
        }

        deadlines.append(deadline)

    return deadlines


def create_mock_payments(redeemed_liens: list) -> list:
    """Create payment records for redeemed liens."""
    payments = []

    for lien_data in redeemed_liens:
        lien_id = lien_data["lien_id"]

        # Calculate redemption amount (principal + interest)
        sale_date = lien_data["sale_date"]
        payment_date = date.today() - timedelta(days=random.randint(30, 90))
        days_held = (payment_date - sale_date).days

        # Use float arithmetic since we already converted to float
        principal = lien_data["purchase_amount"]
        interest_rate = lien_data["interest_rate"]
        daily_rate = interest_rate / 100 / 365
        interest = principal * daily_rate * days_held
        total_amount = principal + interest

        payment = {
            "lien_id": lien_id,
            "amount": total_amount,
            "payment_date": payment_date,
            "status": "COMPLETED",
            "payment_type": "redemption",
            "created_at": datetime.now(),
        }

        payments.append(payment)

    return payments


async def load_data_async(tenant_id: str = "demo-user"):
    """Load all mock data into Firestore."""
    print("=" * 60)
    print("LienOS Mock Data Loader")
    print("=" * 60)

    # Get project ID from environment
    project_id = os.getenv("GOOGLE_PROJECT_ID", "valid-perigee-480016-f3")
    print(f"\nProject ID: {project_id}")
    print(f"Tenant ID: {tenant_id}")

    # Initialize storage
    print("\n📦 Initializing Firestore connection...")
    storage = FirestoreClient(project_id=project_id)

    if storage._use_local:
        print("⚠️  Warning: Using LocalStorageClient (in-memory). Set GOOGLE_PROJECT_ID in .env for production Firestore.")
        return

    print("✓ Connected to Firestore\n")

    # Generate mock liens
    print("🏠 Generating mock lien data...")
    mock_liens = create_mock_liens()

    # Create liens in Firestore
    print(f"📝 Creating {len(mock_liens)} liens...")
    created_liens = []

    for i, lien_data in enumerate(mock_liens, 1):
        # Generate lien ID
        lien_id = generate_lien_id(lien_data["certificate_number"], lien_data["sale_date"])

        # Keep original dates for later calculations
        sale_date_orig = lien_data["sale_date"]
        redemption_deadline_orig = lien_data["redemption_deadline"]

        # Add required fields
        lien_data["lien_id"] = lien_id
        lien_data["tenant_id"] = tenant_id
        lien_data["created_at"] = datetime.now()
        lien_data["updated_at"] = datetime.now()

        # Convert types for Firestore compatibility
        lien_data["purchase_amount"] = float(lien_data["purchase_amount"])
        lien_data["interest_rate"] = float(lien_data["interest_rate"])
        lien_data["sale_date"] = sale_date_orig.isoformat()
        lien_data["redemption_deadline"] = redemption_deadline_orig.isoformat()

        # Create lien using generic create method
        await storage.create(
            collection_name="liens",
            data=lien_data,
            tenant_id=tenant_id
        )

        # Store lien with original dates for payment calculations
        lien_copy = lien_data.copy()
        lien_copy["sale_date"] = sale_date_orig  # Restore original date object
        created_liens.append(lien_copy)

        status_icon = "✓" if lien_data["status"] == "ACTIVE" else "💰"
        print(f"  {status_icon} [{i:2d}/12] {lien_data['certificate_number']:20s} - ${lien_data['purchase_amount']:>7,.0f} ({lien_data['status']})")

    print(f"\n✓ Created {len(created_liens)} liens")

    # Create deadlines
    print(f"\n⏰ Creating deadlines...")
    active_liens = [l for l in created_liens if l["status"] == "ACTIVE"]
    lien_ids = [l["lien_id"] for l in active_liens[:4]]

    deadlines = create_mock_deadlines(lien_ids)

    for i, deadline_data in enumerate(deadlines, 1):
        deadline_id = f"deadline_{deadline_data['lien_id']}_{deadline_data['deadline_type']}"
        deadline_data["deadline_id"] = deadline_id
        deadline_data["tenant_id"] = tenant_id

        # Calculate days until before converting to string
        days_until = (deadline_data['due_date'] - date.today()).days

        # Convert dates for Firestore compatibility
        deadline_data["due_date"] = deadline_data["due_date"].isoformat()

        await storage.create(
            collection_name="deadlines",
            data=deadline_data,
            tenant_id=tenant_id
        )

        print(f"  ⏰ [{i}/4] {deadline_data['deadline_type']:20s} - Due in {days_until:3d} days")

    print(f"\n✓ Created {len(deadlines)} deadlines")

    # Create payments for redeemed liens
    redeemed_liens = [l for l in created_liens if l["status"] == "REDEEMED"]

    if redeemed_liens:
        print(f"\n💵 Creating payment records for redeemed liens...")
        payments = create_mock_payments(redeemed_liens)

        for i, payment_data in enumerate(payments, 1):
            payment_id = f"payment_{payment_data['lien_id']}_{int(datetime.now().timestamp())}"
            payment_data["payment_id"] = payment_id
            payment_data["tenant_id"] = tenant_id

            # Convert types for Firestore compatibility
            payment_data["amount"] = float(payment_data["amount"])
            payment_data["payment_date"] = payment_data["payment_date"].isoformat()

            await storage.create(
                collection_name="payments",
                data=payment_data,
                tenant_id=tenant_id
            )

            print(f"  💰 [{i}/{len(payments)}] Redemption payment: ${payment_data['amount']:>8,.2f}")

        print(f"\n✓ Created {len(payments)} payment records")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    active_count = len([l for l in created_liens if l["status"] == "ACTIVE"])
    redeemed_count = len([l for l in created_liens if l["status"] == "REDEEMED"])
    total_invested = sum(l["purchase_amount"] for l in created_liens)

    print(f"\n✓ Loaded {len(created_liens)} total liens")
    print(f"  • {active_count} ACTIVE liens")
    print(f"  • {redeemed_count} REDEEMED liens")
    print(f"  • Total invested: ${total_invested:,.2f}")
    print(f"\n✓ Loaded {len(deadlines)} deadlines")
    print(f"✓ Loaded {len(payments)} payment records")

    print(f"\n🎉 Mock data successfully loaded for tenant '{tenant_id}'!")
    print(f"\nYou can now view this data in:")
    print(f"  • Frontend: Connect with X-Tenant-ID: {tenant_id}")
    print(f"  • API: https://lien-os-402756129398.us-central1.run.app/docs")
    print("=" * 60)


def main():
    """Main entry point."""
    import asyncio

    # Get tenant ID from command line or use default
    tenant_id = sys.argv[1] if len(sys.argv) > 1 else "demo-user"

    # Run async function
    asyncio.run(load_data_async(tenant_id))


if __name__ == "__main__":
    main()
