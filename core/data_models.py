"""Pydantic data models for LienOS tax lien management system."""

from decimal import Decimal
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class AssetType(str, Enum):
    """Type of asset."""
    TAX_LIEN = "TAX_LIEN"
    CIVIL_JUDGMENT = "CIVIL_JUDGMENT"
    PROBATE = "PROBATE"
    MINERAL_RIGHT = "MINERAL_RIGHT"
    SURPLUS_FUND = "SURPLUS_FUND"


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


class NotificationType(str, Enum):
    """Type of notification."""
    DEADLINE_APPROACHING = "DEADLINE_APPROACHING"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    PAYMENT_OVERDUE = "PAYMENT_OVERDUE"
    REDEMPTION_PERIOD_ENDING = "REDEMPTION_PERIOD_ENDING"
    DOCUMENT_GENERATED = "DOCUMENT_GENERATED"
    INTEREST_CALCULATED = "INTEREST_CALCULATED"


class DocumentType(str, Enum):
    """Type of generated document."""
    REDEMPTION_NOTICE = "REDEMPTION_NOTICE"
    PORTFOLIO_REPORT = "PORTFOLIO_REPORT"
    PAYMENT_RECEIPT = "PAYMENT_RECEIPT"
    TAX_FORM = "TAX_FORM"


class Asset(BaseModel):
    """Base model for all assets."""
    asset_id: str = Field(..., description="Unique identifier for the asset")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    asset_type: AssetType = Field(..., description="Type of asset")
    purchase_amount: Decimal = Field(..., description="Amount paid to purchase the asset")
    interest_rate: Decimal = Field(..., description="Interest rate as a percentage")
    status: str = Field(..., description="Current status of the asset")
    county: str = Field(..., description="County where the asset is located")
    created_at: datetime = Field(..., description="Timestamp when the asset was created")
    updated_at: datetime = Field(..., description="Timestamp when the asset was last updated")

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

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime, _info) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()


class TaxLien(Asset):
    """Tax lien model."""
    asset_type: AssetType = Field(default=AssetType.TAX_LIEN, description="Type of asset")
    certificate_number: str = Field(..., description="Tax lien certificate number")
    sale_date: date = Field(..., description="Date the lien was sold")
    redemption_deadline: date = Field(..., description="Deadline for redemption")
    status: LienStatus = Field(..., description="Current status of the lien")
    property_address: str = Field(..., description="Address of the property")
    parcel_id: str = Field(..., description="Parcel identifier")

    @property
    def lien_id(self) -> str:
        """Alias for asset_id for backward compatibility."""
        return self.asset_id

    @field_serializer('sale_date', 'redemption_deadline')
    def serialize_date(self, value: date, _info) -> str:
        """Serialize date to ISO format string."""
        return value.isoformat()


class CivilJudgment(Asset):
    """Civil judgment model."""
    asset_type: AssetType = Field(default=AssetType.CIVIL_JUDGMENT, description="Type of asset")
    case_number: str = Field(..., description="Court case number")
    court_name: str = Field(..., description="Name of the court")
    judgment_date: date = Field(..., description="Date the judgment was issued")
    defendant_name: str = Field(..., description="Name of the defendant")
    judgment_amount: Decimal = Field(..., description="Total judgment amount")
    statute_limitations_date: Optional[date] = Field(None, description="Date when the judgment expires or statute of limitations ends")

    @field_serializer('judgment_date', 'statute_limitations_date')
    def serialize_date(self, value: Optional[date], _info) -> Optional[str]:
        """Serialize date to ISO format string."""
        return value.isoformat() if value else None

    @field_serializer('judgment_amount')
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Serialize Decimal to float."""
        return float(value)


# Alias for backward compatibility
Lien = TaxLien


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
    asset_ids: Optional[List[str]] = Field(None, description="List of asset IDs relevant to the task")
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


class Deadline(BaseModel):
    """Deadline model for tracking lien deadlines and alerts."""
    deadline_id: str = Field(..., description="Unique identifier for the deadline")
    lien_id: str = Field(..., description="Identifier of the associated lien")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    deadline_type: str = Field(..., description="Type of deadline (e.g., redemption)")
    deadline_date: date = Field(..., description="The deadline date")
    description: str = Field(..., description="Description of the deadline")
    alert_days_before: List[int] = Field(default=[90, 60, 30, 14, 7, 3, 1], description="Days before deadline to send alerts")
    alerts_sent: List[date] = Field(default_factory=list, description="Dates when alerts were sent")
    is_completed: bool = Field(default=False, description="Whether the deadline has been completed")
    completed_at: Optional[datetime] = Field(None, description="When the deadline was completed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the deadline was created")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
    )

    @field_serializer('deadline_date')
    def serialize_date(self, value: date, _info) -> str:
        """Serialize date to ISO format string."""
        return value.isoformat()

    @field_serializer('alerts_sent')
    def serialize_alerts_sent(self, value: List[date], _info) -> List[str]:
        """Serialize list of dates to ISO format strings."""
        return [d.isoformat() for d in value]

    @field_serializer('created_at', 'completed_at')
    def serialize_datetime(self, value: Optional[datetime], _info) -> Optional[str]:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None


class Notification(BaseModel):
    """Notification model for alerts and messages."""
    notification_id: str = Field(..., description="Unique identifier for the notification")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    lien_id: Optional[str] = Field(None, description="Identifier of the associated lien")
    notification_type: NotificationType = Field(..., description="Type of notification")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message body")
    priority: str = Field(default="normal", description="Priority level (low, normal, high)")
    channels: List[str] = Field(default=["email"], description="Delivery channels")
    sent_at: Optional[datetime] = Field(None, description="When the notification was sent")
    read_at: Optional[datetime] = Field(None, description="When the notification was read")
    action_required: bool = Field(default=False, description="Whether user action is required")
    action_url: Optional[str] = Field(None, description="URL for the required action")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when created")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        }
    )

    @field_serializer('sent_at', 'read_at', 'created_at')
    def serialize_datetime(self, value: Optional[datetime], _info) -> Optional[str]:
        """Serialize datetime to ISO format string."""
        return value.isoformat() if value else None


class Portfolio(BaseModel):
    """Portfolio summary model for dashboard analytics."""
    portfolio_id: str = Field(..., description="Unique identifier for the portfolio snapshot")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    total_liens: int = Field(default=0, description="Total number of liens")
    active_liens: int = Field(default=0, description="Number of active liens")
    total_invested: Decimal = Field(default=Decimal("0"), description="Total amount invested")
    total_interest_earned: Decimal = Field(default=Decimal("0"), description="Total interest earned")
    total_redeemed: int = Field(default=0, description="Number of redeemed liens")
    liens_by_status: Dict[str, int] = Field(default_factory=dict, description="Lien count by status")
    liens_by_county: Dict[str, int] = Field(default_factory=dict, description="Lien count by county")
    average_return_rate: Decimal = Field(default=Decimal("0"), description="Average return rate percentage")
    average_holding_period_days: int = Field(default=0, description="Average holding period in days")
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="When the portfolio was calculated")

    model_config = ConfigDict(
        json_encoders={
            Decimal: float,
            datetime: lambda v: v.isoformat(),
        }
    )

    @field_serializer('total_invested', 'total_interest_earned', 'average_return_rate')
    def serialize_decimal(self, value: Decimal, _info) -> float:
        """Serialize Decimal to float."""
        return float(value)

    @field_serializer('calculated_at')
    def serialize_datetime(self, value: datetime, _info) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()


class Document(BaseModel):
    """Document model for generated documents."""
    document_id: str = Field(..., description="Unique identifier for the document")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    lien_id: Optional[str] = Field(None, description="Identifier of the associated lien")
    document_type: DocumentType = Field(..., description="Type of document")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content (HTML or text)")
    format: str = Field(default="html", description="Document format (html, pdf, txt)")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the document was generated")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )

    @field_serializer('generated_at')
    def serialize_datetime(self, value: datetime, _info) -> str:
        """Serialize datetime to ISO format string."""
        return value.isoformat()
