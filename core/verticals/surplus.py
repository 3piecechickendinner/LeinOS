from decimal import Decimal
from datetime import date
from typing import Optional

from pydantic import Field, field_serializer

from core.data_models import Asset, AssetType

class SurplusFund(Asset):
    """Surplus fund model."""
    asset_type: AssetType = Field(default=AssetType.SURPLUS_FUND, description="Type of asset")
    foreclosure_date: date = Field(..., description="Date of foreclosure sale")
    winning_bid_amount: Decimal = Field(..., description="Amount of the winning bid")
    total_debt_owed: Decimal = Field(..., description="Total debt owed at time of sale")
    surplus_amount: Decimal = Field(..., description="Calculated surplus amount")
    claim_deadline: date = Field(..., description="Deadline to file a claim")

    @field_serializer('foreclosure_date', 'claim_deadline')
    def serialize_date(self, value: date, _info) -> str:
        """Serialize date to ISO format string."""
        return value.isoformat()

    @field_serializer('winning_bid_amount', 'total_debt_owed', 'surplus_amount')
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Serialize Decimal to float."""
        return float(value)
