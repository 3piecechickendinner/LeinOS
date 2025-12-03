"""
LienOS FastAPI Application

REST API exposing all agent capabilities for tax lien management.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import date
from decimal import Decimal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.storage import FirestoreClient
from agents.interest_calculator.agent import InterestCalculatorAgent
from agents.deadline_alert.agent import DeadlineAlertAgent
from agents.payment_monitor.agent import PaymentMonitorAgent
from agents.lien_tracker.agent import LienTrackerAgent
from agents.communication.agent import CommunicationAgent
from agents.portfolio_dashboard.agent import PortfolioDashboardAgent
from agents.document_generator.agent import DocumentGeneratorAgent

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LienOS API",
    description="REST API for tax lien management with AI-powered agents",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage client
# For local development without Google Cloud credentials, set GOOGLE_PROJECT_ID to "local-dev"
# or leave it unset. The FirestoreClient will handle mock/local storage accordingly.
# For production, set GOOGLE_PROJECT_ID to your actual Google Cloud project ID.
project_id = os.getenv("GOOGLE_PROJECT_ID", "local-dev")
storage = FirestoreClient(project_id=project_id)


# =============================================================================
# Request/Response Models
# =============================================================================

# Common Models
class BaseResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


# Interest Calculator Models
class CalculateInterestRequest(BaseModel):
    lien_id: str


class CalculateInterestResponse(BaseModel):
    lien_id: str
    principal: float
    interest_rate: float
    days_elapsed: int
    interest_accrued: float
    total_owed: float
    calculation_date: str


# Deadline Alert Models
class CreateDeadlineRequest(BaseModel):
    lien_id: str


class CheckDeadlinesResponse(BaseModel):
    deadlines_checked: int
    alerts_sent: int
    check_date: str


# Payment Monitor Models
class RecordPaymentRequest(BaseModel):
    lien_id: str
    amount: float
    payment_date: Optional[str] = None


class RecordPaymentResponse(BaseModel):
    payment_id: str
    lien_id: str
    amount: float
    payment_date: str
    total_paid: float
    total_owed: float
    remaining_balance: float
    is_fully_redeemed: bool
    lien_status: str
    notification_id: str


class VerifyPaymentRequest(BaseModel):
    payment_id: str


class ReconcileLienRequest(BaseModel):
    lien_id: str


# Lien Tracker Models
class CreateLienRequest(BaseModel):
    certificate_number: str
    purchase_amount: float
    interest_rate: float
    sale_date: str
    redemption_deadline: str
    county: str
    property_address: str
    parcel_id: str
    lien_id: Optional[str] = None
    status: Optional[str] = "ACTIVE"


class UpdateLienRequest(BaseModel):
    lien_id: str
    updates: Dict[str, Any]


class ListLiensRequest(BaseModel):
    status: Optional[str] = None
    county: Optional[str] = None
    limit: Optional[int] = 100
    order_by: Optional[str] = "created_at"


class DeleteLienRequest(BaseModel):
    lien_id: str
    hard_delete: Optional[bool] = False


# Communication Models
class SendNotificationRequest(BaseModel):
    notification_type: str
    title: str
    message: str
    lien_id: Optional[str] = None
    priority: Optional[str] = "normal"
    channels: Optional[List[str]] = ["in_app"]
    action_required: Optional[bool] = False
    action_url: Optional[str] = None


class GetNotificationsRequest(BaseModel):
    unread_only: Optional[bool] = False
    lien_id: Optional[str] = None
    notification_type: Optional[str] = None
    priority: Optional[str] = None
    limit: Optional[int] = 50


class MarkNotificationReadRequest(BaseModel):
    notification_id: str


class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    from_email: Optional[str] = None
    html_body: Optional[str] = None
    notification_id: Optional[str] = None


class SendSmsRequest(BaseModel):
    to_phone: str
    message: str
    from_phone: Optional[str] = None
    notification_id: Optional[str] = None


# Portfolio Dashboard Models
class PortfolioSummaryResponse(BaseModel):
    portfolio_id: str
    total_liens: int
    active_liens: int
    total_invested: float
    total_interest_earned: float
    total_current_value: float
    total_redeemed: int
    liens_by_status: Dict[str, int]
    liens_by_county: Dict[str, int]
    average_return_rate: float
    average_holding_period_days: int
    calculated_at: str


# Document Generator Models
class GenerateRedemptionNoticeRequest(BaseModel):
    lien_id: str


class GeneratePaymentReceiptRequest(BaseModel):
    payment_id: str


class GenerateTaxFormRequest(BaseModel):
    tax_year: Optional[int] = None


class DocumentResponse(BaseModel):
    document_id: str
    document_type: str
    title: str
    format: str
    content: str
    generated_at: str


# =============================================================================
# Dependency: Tenant Authentication
# =============================================================================

async def get_tenant_id(x_tenant_id: str = Header(..., description="Tenant ID for authentication")) -> str:
    """
    Extract and validate tenant ID from header.
    In production, this would verify against an auth service.
    """
    if not x_tenant_id or len(x_tenant_id) < 3:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Tenant-ID header")
    return x_tenant_id


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "service": "LienOS API",
        "version": "1.0.0"
    }


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API info"""
    return {
        "service": "LienOS API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# =============================================================================
# Interest Calculator Endpoints
# =============================================================================

@app.post("/api/interest/calculate", tags=["Interest Calculator"], response_model=CalculateInterestResponse)
async def calculate_interest(
    request: CalculateInterestRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate accrued interest for a lien"""
    try:
        agent = InterestCalculatorAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="calculate_interest",
            lien_ids=[request.lien_id]
        )
        return CalculateInterestResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Deadline Alert Endpoints
# =============================================================================

@app.post("/api/deadlines/create", tags=["Deadline Alert"])
async def create_deadline(
    request: CreateDeadlineRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a redemption deadline for a lien"""
    try:
        agent = DeadlineAlertAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="create_deadline",
            lien_ids=[request.lien_id]
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deadlines/check", tags=["Deadline Alert"], response_model=CheckDeadlinesResponse)
async def check_deadlines(tenant_id: str = Depends(get_tenant_id)):
    """Check all deadlines and send alerts"""
    try:
        agent = DeadlineAlertAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="check_deadlines"
        )
        return CheckDeadlinesResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Payment Monitor Endpoints
# =============================================================================

@app.post("/api/payments/record", tags=["Payment Monitor"], response_model=RecordPaymentResponse)
async def record_payment(
    request: RecordPaymentRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Record a payment for a lien"""
    try:
        agent = PaymentMonitorAgent(storage=storage)

        parameters = {
            "amount": request.amount
        }
        if request.payment_date:
            parameters["payment_date"] = request.payment_date

        result = await agent.run(
            tenant_id=tenant_id,
            task="record_payment",
            lien_ids=[request.lien_id],
            parameters=parameters
        )
        return RecordPaymentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payments/verify", tags=["Payment Monitor"])
async def verify_payment(
    request: VerifyPaymentRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Verify a payment was properly recorded"""
    try:
        agent = PaymentMonitorAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="verify_payment",
            parameters={"payment_id": request.payment_id}
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payments/reconcile", tags=["Payment Monitor"])
async def reconcile_lien(
    request: ReconcileLienRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Reconcile all payments for a lien"""
    try:
        agent = PaymentMonitorAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="reconcile_lien",
            lien_ids=[request.lien_id]
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Lien Tracker Endpoints
# =============================================================================

@app.post("/api/liens", tags=["Lien Tracker"])
async def create_lien(
    request: CreateLienRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new lien"""
    try:
        agent = LienTrackerAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="create_lien",
            parameters=request.model_dump()
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/liens", tags=["Lien Tracker"])
async def list_liens(
    status: Optional[str] = None,
    county: Optional[str] = None,
    limit: int = 100,
    order_by: str = "created_at",
    tenant_id: str = Depends(get_tenant_id)
):
    """List all liens with optional filters"""
    try:
        agent = LienTrackerAgent(storage=storage)

        parameters = {
            "limit": limit,
            "order_by": order_by
        }
        if status:
            parameters["status"] = status
        if county:
            parameters["county"] = county

        result = await agent.run(
            tenant_id=tenant_id,
            task="list_liens",
            parameters=parameters
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/liens/{lien_id}", tags=["Lien Tracker"])
async def get_lien(
    lien_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get a specific lien by ID"""
    try:
        agent = LienTrackerAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="get_lien",
            lien_ids=[lien_id]
        )

        if not result.get("found"):
            raise HTTPException(status_code=404, detail=f"Lien {lien_id} not found")

        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/liens/{lien_id}", tags=["Lien Tracker"])
async def update_lien(
    lien_id: str,
    updates: Dict[str, Any],
    tenant_id: str = Depends(get_tenant_id)
):
    """Update an existing lien"""
    try:
        agent = LienTrackerAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="update_lien",
            lien_ids=[lien_id],
            parameters=updates
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/liens/{lien_id}", tags=["Lien Tracker"])
async def delete_lien(
    lien_id: str,
    hard_delete: bool = False,
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete a lien (soft delete by default)"""
    try:
        agent = LienTrackerAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="delete_lien",
            lien_ids=[lien_id],
            parameters={"hard_delete": hard_delete}
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Communication Endpoints
# =============================================================================

@app.post("/api/notifications", tags=["Communication"])
async def send_notification(
    request: SendNotificationRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Send a notification"""
    try:
        agent = CommunicationAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="send_notification",
            parameters=request.model_dump()
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notifications", tags=["Communication"])
async def get_notifications(
    unread_only: bool = False,
    lien_id: Optional[str] = None,
    notification_type: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get notifications for a tenant"""
    try:
        agent = CommunicationAgent(storage=storage)

        parameters = {
            "unread_only": unread_only,
            "limit": limit
        }
        if lien_id:
            parameters["lien_id"] = lien_id
        if notification_type:
            parameters["notification_type"] = notification_type
        if priority:
            parameters["priority"] = priority

        result = await agent.run(
            tenant_id=tenant_id,
            task="get_notifications",
            parameters=parameters
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/notifications/{notification_id}/read", tags=["Communication"])
async def mark_notification_read(
    notification_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Mark a notification as read"""
    try:
        agent = CommunicationAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="mark_notification_read",
            parameters={"notification_id": notification_id}
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/send", tags=["Communication"])
async def send_email(
    request: SendEmailRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Queue an email for sending"""
    try:
        agent = CommunicationAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="send_email",
            parameters=request.model_dump()
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sms/send", tags=["Communication"])
async def send_sms(
    request: SendSmsRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Queue an SMS for sending"""
    try:
        agent = CommunicationAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="send_sms",
            parameters=request.model_dump()
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Portfolio Dashboard Endpoints
# =============================================================================

@app.post("/api/portfolio/summary", tags=["Portfolio Dashboard"])
async def calculate_portfolio_summary(tenant_id: str = Depends(get_tenant_id)):
    """Calculate comprehensive portfolio summary"""
    try:
        agent = PortfolioDashboardAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="calculate_portfolio_summary"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio/stats", tags=["Portfolio Dashboard"])
async def get_portfolio_stats(tenant_id: str = Depends(get_tenant_id)):
    """Get latest saved portfolio statistics"""
    try:
        agent = PortfolioDashboardAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="get_portfolio_stats"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio/report", tags=["Portfolio Dashboard"])
async def generate_performance_report(tenant_id: str = Depends(get_tenant_id)):
    """Generate detailed performance report"""
    try:
        agent = PortfolioDashboardAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="generate_performance_report"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Document Generator Endpoints
# =============================================================================

@app.post("/api/documents/redemption-notice", tags=["Document Generator"])
async def generate_redemption_notice(
    request: GenerateRedemptionNoticeRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Generate a redemption notice for a lien"""
    try:
        agent = DocumentGeneratorAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="generate_redemption_notice",
            lien_ids=[request.lien_id]
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/portfolio-report", tags=["Document Generator"])
async def generate_portfolio_report_document(tenant_id: str = Depends(get_tenant_id)):
    """Generate a portfolio report document"""
    try:
        agent = DocumentGeneratorAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="generate_portfolio_report"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/payment-receipt", tags=["Document Generator"])
async def generate_payment_receipt(
    request: GeneratePaymentReceiptRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Generate a payment receipt"""
    try:
        agent = DocumentGeneratorAgent(storage=storage)
        result = await agent.run(
            tenant_id=tenant_id,
            task="generate_payment_receipt",
            parameters={"payment_id": request.payment_id}
        )
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/tax-form", tags=["Document Generator"])
async def generate_tax_form(
    request: GenerateTaxFormRequest,
    tenant_id: str = Depends(get_tenant_id)
):
    """Generate a 1099-INT style tax summary"""
    try:
        agent = DocumentGeneratorAgent(storage=storage)

        parameters = {}
        if request.tax_year:
            parameters["tax_year"] = request.tax_year

        result = await agent.run(
            tenant_id=tenant_id,
            task="generate_tax_form",
            parameters=parameters
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Run Application
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
