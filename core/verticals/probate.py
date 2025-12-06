from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import Field, field_serializer

from core.data_models import Asset, AssetType

class ProbateEstate(Asset):
    """Probate estate model."""
    asset_type: AssetType = Field(default=AssetType.PROBATE, description="Type of asset")
    deceased_name: str = Field(..., description="Name of the deceased person")
    date_of_death: date = Field(..., description="Date of death")
    case_status: str = Field(..., description="Status of the probate case (e.g., Open, Closed)")
    attorney_contact: Optional[str] = Field(None, description="Contact information for the attorney")
    probate_filing_date: Optional[date] = Field(None, description="Date when probate was filed")
    estimated_value: Decimal = Field(default=Decimal("0.0"), description="Estimated total value of the estate")
    mortgages_amount: Decimal = Field(default=Decimal("0.0"), description="Total mortgage debt")
    liens_amount: Decimal = Field(default=Decimal("0.0"), description="Total other liens debt")

    @field_serializer('probate_filing_date', 'date_of_death')
    def serialize_date(self, value: date, _info) -> str:
        """Serialize date to ISO format string."""
        if value is None:
            return None
        return value.isoformat()

    @field_serializer('estimated_value', 'mortgages_amount', 'liens_amount')
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Serialize Decimal to float."""
        return float(value)
