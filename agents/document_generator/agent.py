from typing import Dict, Any, List
from datetime import datetime, date
from decimal import Decimal

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext, Document, DocumentType
from core.storage import FirestoreClient
from agents.interest_calculator.agent import InterestCalculatorAgent
from agents.portfolio_dashboard.agent import PortfolioDashboardAgent


class DocumentGeneratorAgent(LienOSBaseAgent):
    """
    Agent that generates various documents for tax lien management.
    Creates redemption notices, portfolio reports, receipts, and tax forms.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="DocumentGenerator",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return [
            "generate_redemption_notice",
            "generate_portfolio_report",
            "generate_payment_receipt",
            "generate_tax_form"
        ]

    def _register_tools(self) -> None:
        """
        No external tools yet.
        Future: Register PDF generation tools (reportlab, weasyprint)
        """
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Main agent logic.

        Handles tasks:
        - generate_redemption_notice: Create notice with amount owed
        - generate_portfolio_report: Create portfolio summary document
        - generate_payment_receipt: Create payment receipt
        - generate_tax_form: Create 1099-INT style tax summary

        Returns:
            Dict with document details and content
        """
        if context.task == "generate_redemption_notice":
            return await self._generate_redemption_notice(context)
        elif context.task == "generate_portfolio_report":
            return await self._generate_portfolio_report(context)
        elif context.task == "generate_payment_receipt":
            return await self._generate_payment_receipt(context)
        elif context.task == "generate_tax_form":
            return await self._generate_tax_form(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _generate_redemption_notice(self, context: AgentContext) -> Dict[str, Any]:
        """
        Generate a redemption notice for a lien.

        Required:
        - lien_ids[0]: The lien ID

        Returns:
            Dict with document details and HTML content
        """
        if not context.lien_ids or len(context.lien_ids) == 0:
            raise ValueError("lien_id required in context.lien_ids")

        lien_id = context.lien_ids[0]

        # Get lien details
        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)
        if not lien_data:
            raise ValueError(f"Lien {lien_id} not found")

        # Calculate current amount owed
        interest_agent = InterestCalculatorAgent(storage=self.storage)
        interest_result = await interest_agent.run(
            tenant_id=context.tenant_id,
            task="calculate_interest",
            lien_ids=[lien_id]
        )

        # Generate HTML content
        today = date.today()
        redemption_deadline = lien_data.get("redemption_deadline")
        if isinstance(redemption_deadline, str):
            redemption_deadline = date.fromisoformat(redemption_deadline)

        days_remaining = (redemption_deadline - today).days

        html_content = self._build_redemption_notice_html(
            lien_data=lien_data,
            interest_result=interest_result,
            today=today,
            days_remaining=days_remaining
        )

        # Create document record
        document_id = f"doc_redemption_{lien_id}_{today.isoformat()}"
        document = Document(
            document_id=document_id,
            tenant_id=context.tenant_id,
            lien_id=lien_id,
            document_type=DocumentType.REDEMPTION_NOTICE,
            title=f"Redemption Notice - {lien_data.get('property_address')}",
            content=html_content,
            format="html",
            generated_at=datetime.utcnow()
        )

        # Save to storage
        doc_dict = document.model_dump()
        await self.storage.create("documents", doc_dict, context.tenant_id)

        self.log_info(f"Generated redemption notice for lien {lien_id}")

        return {
            "document_id": document_id,
            "document_type": DocumentType.REDEMPTION_NOTICE.value,
            "lien_id": lien_id,
            "title": document.title,
            "format": "html",
            "total_owed": interest_result.get("total_owed"),
            "days_remaining": days_remaining,
            "content": html_content,
            "generated_at": document.generated_at.isoformat()
        }

    def _build_redemption_notice_html(
        self,
        lien_data: Dict[str, Any],
        interest_result: Dict[str, Any],
        today: date,
        days_remaining: int
    ) -> str:
        """Build HTML content for redemption notice"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Redemption Notice</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .section {{ margin-bottom: 20px; }}
        .amount {{ font-size: 24px; font-weight: bold; color: #d32f2f; }}
        .deadline {{ font-size: 18px; color: #f57c00; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NOTICE OF TAX LIEN REDEMPTION</h1>
        <p>Date: {today.strftime('%B %d, %Y')}</p>
    </div>

    <div class="section">
        <h2>Property Information</h2>
        <table>
            <tr><th>Property Address:</th><td>{lien_data.get('property_address')}</td></tr>
            <tr><th>Parcel ID:</th><td>{lien_data.get('parcel_id')}</td></tr>
            <tr><th>County:</th><td>{lien_data.get('county')}</td></tr>
            <tr><th>Certificate Number:</th><td>{lien_data.get('certificate_number')}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Lien Details</h2>
        <table>
            <tr><th>Original Purchase Amount:</th><td>${float(lien_data.get('purchase_amount', 0)):,.2f}</td></tr>
            <tr><th>Interest Rate:</th><td>{float(lien_data.get('interest_rate', 0))}%</td></tr>
            <tr><th>Sale Date:</th><td>{lien_data.get('sale_date')}</td></tr>
            <tr><th>Days Elapsed:</th><td>{interest_result.get('days_elapsed', 0)} days</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Amount Due for Redemption</h2>
        <table>
            <tr><th>Principal:</th><td>${float(interest_result.get('principal', 0)):,.2f}</td></tr>
            <tr><th>Accrued Interest:</th><td>${float(interest_result.get('interest_accrued', 0)):,.2f}</td></tr>
            <tr><th><strong>Total Amount Due:</strong></th><td class="amount">${float(interest_result.get('total_owed', 0)):,.2f}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Redemption Deadline</h2>
        <p class="deadline">
            <strong>Deadline:</strong> {lien_data.get('redemption_deadline')}<br>
            <strong>Days Remaining:</strong> {days_remaining} days
        </p>
        <p>
            To redeem this property, the total amount shown above must be paid in full
            before the redemption deadline. Failure to redeem may result in foreclosure
            proceedings.
        </p>
    </div>

    <div class="footer">
        <p>This notice was generated on {today.strftime('%B %d, %Y')} and reflects amounts
        calculated as of this date. Interest continues to accrue daily until redemption.</p>
        <p>Generated by LienOS</p>
    </div>
</body>
</html>
"""

    async def _generate_portfolio_report(self, context: AgentContext) -> Dict[str, Any]:
        """
        Generate a comprehensive portfolio report.

        Returns:
            Dict with document details and HTML content
        """
        # Get portfolio stats
        dashboard_agent = PortfolioDashboardAgent(storage=self.storage)
        portfolio_result = await dashboard_agent.run(
            tenant_id=context.tenant_id,
            task="calculate_portfolio_summary"
        )

        today = date.today()

        # Generate HTML content
        html_content = self._build_portfolio_report_html(
            portfolio=portfolio_result,
            today=today
        )

        # Create document record
        document_id = f"doc_portfolio_{context.tenant_id}_{today.isoformat()}"
        document = Document(
            document_id=document_id,
            tenant_id=context.tenant_id,
            lien_id=None,
            document_type=DocumentType.PORTFOLIO_REPORT,
            title=f"Portfolio Report - {today.strftime('%B %Y')}",
            content=html_content,
            format="html",
            generated_at=datetime.utcnow()
        )

        # Save to storage
        doc_dict = document.model_dump()
        await self.storage.create("documents", doc_dict, context.tenant_id)

        self.log_info(f"Generated portfolio report for tenant {context.tenant_id}")

        return {
            "document_id": document_id,
            "document_type": DocumentType.PORTFOLIO_REPORT.value,
            "title": document.title,
            "format": "html",
            "total_liens": portfolio_result.get("total_liens"),
            "total_invested": portfolio_result.get("total_invested"),
            "content": html_content,
            "generated_at": document.generated_at.isoformat()
        }

    def _build_portfolio_report_html(
        self,
        portfolio: Dict[str, Any],
        today: date
    ) -> str:
        """Build HTML content for portfolio report"""
        # Build status breakdown rows
        status_rows = ""
        for status, count in portfolio.get("liens_by_status", {}).items():
            status_rows += f"<tr><td>{status}</td><td>{count}</td></tr>"

        # Build county breakdown rows
        county_rows = ""
        for county, count in portfolio.get("liens_by_county", {}).items():
            county_rows += f"<tr><td>{county}</td><td>{count}</td></tr>"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 28px; font-weight: bold; color: #1976d2; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f5f5f5; }}
        .summary-box {{ background-color: #e3f2fd; padding: 20px; border-radius: 8px; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PORTFOLIO REPORT</h1>
        <p>Report Date: {today.strftime('%B %d, %Y')}</p>
    </div>

    <div class="section summary-box">
        <h2>Portfolio Summary</h2>
        <div class="metric">
            <div class="metric-value">{portfolio.get('total_liens', 0)}</div>
            <div class="metric-label">Total Liens</div>
        </div>
        <div class="metric">
            <div class="metric-value">{portfolio.get('active_liens', 0)}</div>
            <div class="metric-label">Active Liens</div>
        </div>
        <div class="metric">
            <div class="metric-value">${float(portfolio.get('total_invested', 0)):,.2f}</div>
            <div class="metric-label">Total Invested</div>
        </div>
        <div class="metric">
            <div class="metric-value">${float(portfolio.get('total_interest_earned', 0)):,.2f}</div>
            <div class="metric-label">Interest Earned</div>
        </div>
        <div class="metric">
            <div class="metric-value">{float(portfolio.get('average_return_rate', 0)):.1f}%</div>
            <div class="metric-label">Avg Return Rate</div>
        </div>
    </div>

    <div class="section">
        <h2>Liens by Status</h2>
        <table>
            <tr><th>Status</th><th>Count</th></tr>
            {status_rows}
        </table>
    </div>

    <div class="section">
        <h2>Liens by County</h2>
        <table>
            <tr><th>County</th><th>Count</th></tr>
            {county_rows}
        </table>
    </div>

    <div class="section">
        <h2>Performance Metrics</h2>
        <table>
            <tr><th>Average Holding Period</th><td>{portfolio.get('average_holding_period_days', 0)} days</td></tr>
            <tr><th>Total Redeemed</th><td>{portfolio.get('total_redeemed', 0)} liens</td></tr>
            <tr><th>Current Portfolio Value</th><td>${float(portfolio.get('total_current_value', 0)):,.2f}</td></tr>
        </table>
    </div>

    <div class="footer">
        <p>This report was generated on {today.strftime('%B %d, %Y')}.</p>
        <p>Generated by LienOS</p>
    </div>
</body>
</html>
"""

    async def _generate_payment_receipt(self, context: AgentContext) -> Dict[str, Any]:
        """
        Generate a payment receipt.

        Required parameters:
        - payment_id: The payment ID

        Returns:
            Dict with document details and HTML content
        """
        payment_id = context.parameters.get("payment_id")
        if not payment_id:
            raise ValueError("payment_id required in parameters")

        # Get payment details
        payment_data = await self.storage.get("payments", payment_id, context.tenant_id)
        if not payment_data:
            raise ValueError(f"Payment {payment_id} not found")

        lien_id = payment_data.get("lien_id")

        # Get lien details
        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)
        if not lien_data:
            raise ValueError(f"Lien {lien_id} not found")

        today = date.today()

        # Generate HTML content
        html_content = self._build_payment_receipt_html(
            payment_data=payment_data,
            lien_data=lien_data,
            today=today
        )

        # Create document record
        document_id = f"doc_receipt_{payment_id}"
        document = Document(
            document_id=document_id,
            tenant_id=context.tenant_id,
            lien_id=lien_id,
            document_type=DocumentType.PAYMENT_RECEIPT,
            title=f"Payment Receipt - {payment_id}",
            content=html_content,
            format="html",
            generated_at=datetime.utcnow()
        )

        # Save to storage
        doc_dict = document.model_dump()
        await self.storage.create("documents", doc_dict, context.tenant_id)

        self.log_info(f"Generated payment receipt for payment {payment_id}")

        return {
            "document_id": document_id,
            "document_type": DocumentType.PAYMENT_RECEIPT.value,
            "payment_id": payment_id,
            "lien_id": lien_id,
            "title": document.title,
            "format": "html",
            "amount": payment_data.get("amount"),
            "content": html_content,
            "generated_at": document.generated_at.isoformat()
        }

    def _build_payment_receipt_html(
        self,
        payment_data: Dict[str, Any],
        lien_data: Dict[str, Any],
        today: date
    ) -> str:
        """Build HTML content for payment receipt"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Payment Receipt</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .receipt-box {{ border: 2px solid #4caf50; padding: 20px; border-radius: 8px; }}
        .section {{ margin-bottom: 20px; }}
        .amount {{ font-size: 32px; font-weight: bold; color: #4caf50; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #666; text-align: center; }}
        .checkmark {{ font-size: 48px; color: #4caf50; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="checkmark">&#10004;</div>
        <h1>PAYMENT RECEIPT</h1>
        <p>Receipt Date: {today.strftime('%B %d, %Y')}</p>
    </div>

    <div class="receipt-box">
        <div class="amount">${float(payment_data.get('amount', 0)):,.2f}</div>
        <p style="text-align: center; color: #666;">Payment Received</p>
    </div>

    <div class="section">
        <h2>Payment Details</h2>
        <table>
            <tr><th>Payment ID:</th><td>{payment_data.get('payment_id')}</td></tr>
            <tr><th>Payment Date:</th><td>{payment_data.get('payment_date')}</td></tr>
            <tr><th>Status:</th><td>{payment_data.get('status')}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Property Information</h2>
        <table>
            <tr><th>Property Address:</th><td>{lien_data.get('property_address')}</td></tr>
            <tr><th>Parcel ID:</th><td>{lien_data.get('parcel_id')}</td></tr>
            <tr><th>Certificate Number:</th><td>{lien_data.get('certificate_number')}</td></tr>
            <tr><th>County:</th><td>{lien_data.get('county')}</td></tr>
        </table>
    </div>

    <div class="footer">
        <p>Thank you for your payment.</p>
        <p>Please retain this receipt for your records.</p>
        <p>Generated by LienOS</p>
    </div>
</body>
</html>
"""

    async def _generate_tax_form(self, context: AgentContext) -> Dict[str, Any]:
        """
        Generate a 1099-INT style tax summary.

        Optional parameters:
        - tax_year: int (defaults to current year)

        Returns:
            Dict with document details and HTML content
        """
        tax_year = context.parameters.get("tax_year", date.today().year)

        # Get all interest calculations for the year
        calculations = await self.storage.query(
            "interest_calculations",
            context.tenant_id,
            filters=None
        )

        # Filter by year and aggregate
        total_interest = Decimal("0")
        lien_summaries = []

        for calc in calculations:
            calc_date = calc.get("calculation_date")
            if isinstance(calc_date, str):
                calc_date = date.fromisoformat(calc_date)

            if calc_date and calc_date.year == tax_year:
                interest = Decimal(str(calc.get("interest_accrued", 0)))
                total_interest += interest

                lien_summaries.append({
                    "lien_id": calc.get("lien_id"),
                    "interest_accrued": float(interest),
                    "calculation_date": calc_date.isoformat()
                })

        today = date.today()

        # Generate HTML content
        html_content = self._build_tax_form_html(
            tax_year=tax_year,
            total_interest=total_interest,
            lien_summaries=lien_summaries,
            today=today
        )

        # Create document record
        document_id = f"doc_tax_{context.tenant_id}_{tax_year}"
        document = Document(
            document_id=document_id,
            tenant_id=context.tenant_id,
            lien_id=None,
            document_type=DocumentType.TAX_FORM,
            title=f"Interest Income Summary - Tax Year {tax_year}",
            content=html_content,
            format="html",
            generated_at=datetime.utcnow()
        )

        # Save to storage
        doc_dict = document.model_dump()
        await self.storage.create("documents", doc_dict, context.tenant_id)

        self.log_info(f"Generated tax form for year {tax_year}")

        return {
            "document_id": document_id,
            "document_type": DocumentType.TAX_FORM.value,
            "tax_year": tax_year,
            "title": document.title,
            "format": "html",
            "total_interest": float(total_interest),
            "lien_count": len(lien_summaries),
            "content": html_content,
            "generated_at": document.generated_at.isoformat()
        }

    def _build_tax_form_html(
        self,
        tax_year: int,
        total_interest: Decimal,
        lien_summaries: List[Dict],
        today: date
    ) -> str:
        """Build HTML content for tax form"""
        # Build lien summary rows
        lien_rows = ""
        for summary in lien_summaries:
            lien_rows += f"""
            <tr>
                <td>{summary['lien_id']}</td>
                <td>${summary['interest_accrued']:,.2f}</td>
                <td>{summary['calculation_date']}</td>
            </tr>
            """

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interest Income Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .total-box {{ background-color: #fff3e0; padding: 20px; border-radius: 8px; text-align: center; }}
        .total-amount {{ font-size: 36px; font-weight: bold; color: #e65100; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f5f5f5; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #666; }}
        .disclaimer {{ background-color: #ffebee; padding: 15px; border-radius: 4px; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>INTEREST INCOME SUMMARY</h1>
        <h2>Tax Year {tax_year}</h2>
        <p>Form 1099-INT Reference Document</p>
    </div>

    <div class="section total-box">
        <div>Total Interest Income</div>
        <div class="total-amount">${float(total_interest):,.2f}</div>
        <div style="color: #666; font-size: 12px;">Box 1: Interest Income</div>
    </div>

    <div class="section">
        <h2>Interest by Lien</h2>
        <table>
            <tr>
                <th>Lien ID</th>
                <th>Interest Accrued</th>
                <th>Calculation Date</th>
            </tr>
            {lien_rows if lien_rows else '<tr><td colspan="3">No interest calculations found for this year</td></tr>'}
        </table>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <table>
            <tr><th>Tax Year</th><td>{tax_year}</td></tr>
            <tr><th>Total Liens with Interest</th><td>{len(lien_summaries)}</td></tr>
            <tr><th>Total Interest Income</th><td>${float(total_interest):,.2f}</td></tr>
        </table>
    </div>

    <div class="section disclaimer">
        <strong>Disclaimer:</strong> This document is for informational purposes only and is not
        an official IRS form. Please consult with a qualified tax professional for actual tax
        filing requirements. Interest income from tax liens may be subject to federal and state
        income taxes.
    </div>

    <div class="footer">
        <p>Document generated on {today.strftime('%B %d, %Y')}</p>
        <p>Generated by LienOS</p>
    </div>
</body>
</html>
"""
