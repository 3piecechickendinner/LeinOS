"""Pydantic data models for LienOS tax lien management system."""

from decimal import Decimal
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class LienStatus(str, Enum):
    """Status of a tax lien."""
    ACTIVE = "ACTIVE"
    REDEEMED = "REDEEMED"
    FORECLOSED = "FORECLOSED"
    EXPIRED = "EXPIRED"


class PaymentStatus(str, Enum):
    """Status of a payment."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Lien(BaseModel):
    """Tax lien model."""
    lien_id: str = Field(..., description="Unique identifier for the lien")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    certificate_number: str = Field(..., description="Tax lien certificate number")
    purchase_amount: Decimal = Field(..., description="Amount paid to purchase the lien")
    interest_rate: Decimal = Field(..., description="Interest rate as a percentage")
    sale_date: date = Field(..., description="Date the lien was sold")
    redemption_deadline: date = Field(..., description="Deadline for redemption")
    status: LienStatus = Field(..., description="Current status of the lien")
    county: str = Field(..., description="County where the property is located")
    property_address: str = Field(..., description="Address of the property")
    parcel_id: str = Field(..., description="Parcel identifier")
    created_at: datetime = Field(..., description="Timestamp when the lien was created")
    updated_at: datetime = Field(..., description="Timestamp when the lien was last updated")

    model_config = ConfigDict(
        json_encoders={
            Decimal: float,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
    )

    @field_serializer('purchase_amount', 'interest_rate')
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Serialize Decimal to float."""
        return float(value)

    @field_serializer('sale_date', 'redemption_deadline')
    def serialize_date(self, value: date, _info) -> str:
        """Serialize date to ISO format string."""
        return value.isoformat()

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime, _info) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()


class Payment(BaseModel):
    """Payment model for lien redemptions."""
    payment_id: str = Field(..., description="Unique identifier for the payment")
    lien_id: str = Field(..., description="Identifier of the associated lien")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    amount: Decimal = Field(..., description="Payment amount")
    payment_date: date = Field(..., description="Date of the payment")
    status: PaymentStatus = Field(..., description="Current status of the payment")
    created_at: datetime = Field(..., description="Timestamp when the payment was created")

    model_config = ConfigDict(
        json_encoders={
            Decimal: float,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
    )

    @field_serializer('amount')
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Serialize Decimal to float."""
        return float(value)

    @field_serializer('payment_date')
    def serialize_date(self, value: date, _info) -> str:
        """Serialize date to ISO format string."""
        return value.isoformat()

    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime, _info) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()


class InterestCalculation(BaseModel):
    """Interest calculation model for liens."""
    lien_id: str = Field(..., description="Identifier of the associated lien")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    calculation_date: date = Field(..., description="Date for which the calculation is performed")
    principal: Decimal = Field(..., description="Principal amount")
    interest_rate: Decimal = Field(..., description="Interest rate as a percentage")
    days_elapsed: int = Field(..., description="Number of days elapsed since lien purchase")
    interest_accrued: Decimal = Field(..., description="Total interest accrued")
    total_owed: Decimal = Field(..., description="Total amount owed (principal + interest)")
    calculated_at: datetime = Field(..., description="Timestamp when the calculation was performed")

    model_config = ConfigDict(
        json_encoders={
            Decimal: float,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
    )

    @field_serializer('principal', 'interest_rate', 'interest_accrued', 'total_owed')
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Serialize Decimal to float."""
        return float(value)

    @field_serializer('calculation_date')
    def serialize_date(self, value: date, _info) -> str:
        """Serialize date to ISO format string."""
        return value.isoformat()

    @field_serializer('calculated_at')
    def serialize_datetime(self, value: datetime, _info) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()


class AgentContext(BaseModel):
    """Context model for agent communication."""
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    requesting_agent: str = Field(..., description="Identifier of the requesting agent")
    task: str = Field(..., description="Task description or identifier")
    lien_ids: Optional[List[str]] = Field(None, description="List of lien IDs relevant to the task")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for the task")
    response: Optional[Dict[str, Any]] = Field(None, description="Response data from the agent")
    error: Optional[str] = Field(None, description="Error message if task failed")
    timestamp: datetime = Field(..., description="Timestamp when the context was created")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )

    @field_serializer('timestamp')
    def serialize_datetime(self, value: datetime, _info) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()

