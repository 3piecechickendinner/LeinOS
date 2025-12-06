from datetime import date, datetime
from decimal import Decimal
from core.data_models import Lien, LienStatus, AssetType

try:
    lien = Lien(
        asset_id="test-123",
        tenant_id="tenant-1",
        certificate_number="CERT-001",
        purchase_amount=Decimal("1000.00"),
        interest_rate=Decimal("12.0"),
        sale_date=date(2023, 1, 1),
        redemption_deadline=date(2024, 1, 1),
        status=LienStatus.ACTIVE,
        county="Test County",
        property_address="123 Main St",
        parcel_id="PARCEL-1",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    print("Success!")
    print(lien.model_dump())
except Exception as e:
    print(f"Error: {e}")
