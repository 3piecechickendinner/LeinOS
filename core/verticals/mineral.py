from decimal import Decimal
from typing import Optional
from datetime import date

from pydantic import Field, field_serializer

from core.data_models import Asset, AssetType

class MineralRight(Asset):
    """Mineral right model."""
    asset_type: AssetType = Field(default=AssetType.MINERAL_RIGHT, description="Type of asset")
    legal_description: str = Field(..., description="Legal description of the property")
    net_mineral_acres: Decimal = Field(..., description="Net mineral acres owned")
    royalty_decimal: Decimal = Field(..., description="Royalty interest decimal")
    operator_name: str = Field(..., description="Name of the operator")
    lease_expiration_date: Optional[date] = Field(None, description="Expiration date of the current lease")

    @field_serializer('net_mineral_acres', 'royalty_decimal')
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Serialize Decimal to float."""
        return float(value)
