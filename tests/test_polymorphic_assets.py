import pytest
from datetime import date, datetime
from decimal import Decimal
from core.data_models import Asset, TaxLien, CivilJudgment, AssetType, Lien

def test_tax_lien_creation():
    lien = TaxLien(
        asset_id="lien-123",
        tenant_id="tenant-1",
        certificate_number="CERT-001",
        purchase_amount=Decimal("1000.00"),
        interest_rate=Decimal("12.0"),
        sale_date=date(2023, 1, 1),
        redemption_deadline=date(2024, 1, 1),
        status="ACTIVE",
        property_address="123 Main St",
        parcel_id="PARCEL-1",
        county="Test County",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert lien.asset_type == AssetType.TAX_LIEN
    assert lien.lien_id == "lien-123"
    assert isinstance(lien, Asset)

def test_civil_judgment_creation():
    judgment = CivilJudgment(
        asset_id="judg-123",
        tenant_id="tenant-1",
        purchase_amount=Decimal("5000.00"), # Usually 0 or cost to acquire
        interest_rate=Decimal("5.0"),
        status="ACTIVE",
        county="Test County",
        case_number="CASE-001",
        court_name="Superior Court",
        judgment_date=date(2023, 6, 1),
        defendant_name="John Doe",
        judgment_amount=Decimal("5000.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert judgment.asset_type == AssetType.CIVIL_JUDGMENT
    assert judgment.asset_id == "judg-123"
    assert isinstance(judgment, Asset)

def test_lien_alias():
    # Test that Lien alias works and creates a TaxLien
    lien = Lien(
        lien_id="lien-alias-123", # Note: using lien_id alias if supported, or asset_id
        asset_id="lien-alias-123", # Pydantic might require the actual field name if alias not set in Field
        tenant_id="tenant-1",
        certificate_number="CERT-ALIAS",
        purchase_amount=Decimal("2000.00"),
        interest_rate=Decimal("10.0"),
        sale_date=date(2023, 1, 1),
        redemption_deadline=date(2024, 1, 1),
        status="ACTIVE",
        property_address="456 Elm St",
        parcel_id="PARCEL-2",
        county="Test County",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert isinstance(lien, TaxLien)
    assert lien.asset_type == AssetType.TAX_LIEN

def test_polymorphism():
    assets = [
        TaxLien(
            asset_id="1", tenant_id="t1", certificate_number="C1", purchase_amount=Decimal("100"), interest_rate=Decimal("10"),
            sale_date=date.today(), redemption_deadline=date.today(), status="ACTIVE", property_address="A", parcel_id="P1", county="C",
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        ),
        CivilJudgment(
            asset_id="2", tenant_id="t1", purchase_amount=Decimal("0"), interest_rate=Decimal("5"), status="A", county="C",
            case_number="CN1", court_name="CN", judgment_date=date.today(), defendant_name="DN", judgment_amount=Decimal("500"),
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
    ]
    
    assert len(assets) == 2
    assert isinstance(assets[0], Asset)
    assert isinstance(assets[1], Asset)
    assert assets[0].asset_type == AssetType.TAX_LIEN
    assert assets[1].asset_type == AssetType.CIVIL_JUDGMENT
