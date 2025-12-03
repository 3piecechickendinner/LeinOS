"""
LienOS Root Agent - Orchestrates all tax lien management agents

This root agent coordinates 7 specialized agents:
1. Interest Calculator - Calculates accrued interest
2. Deadline Alert - Monitors redemption deadlines
3. Payment Monitor - Tracks and reconciles payments
4. Lien Tracker - Manages lien CRUD operations
5. Communication - Handles notifications and messaging
6. Portfolio Dashboard - Generates analytics and reports
7. Document Generator - Creates legal documents and receipts
"""

import asyncio
import os
from typing import Optional

import google.auth
from google.adk.agents import Agent
from google.adk.apps.app import App

# Configure Google Cloud settings
try:
    _, project_id = google.auth.default()
except Exception:
    # Fallback for local development
    project_id = os.getenv("GOOGLE_PROJECT_ID", "local-dev")

os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Import all LienOS agents
from agents.interest_calculator.agent import InterestCalculatorAgent
from agents.deadline_alert.agent import DeadlineAlertAgent
from agents.payment_monitor.agent import PaymentMonitorAgent
from agents.lien_tracker.agent import LienTrackerAgent
from agents.communication.agent import CommunicationAgent
from agents.portfolio_dashboard.agent import PortfolioDashboardAgent
from agents.document_generator.agent import DocumentGeneratorAgent
from core.storage import FirestoreClient

# Initialize storage
storage = FirestoreClient(project_id=project_id)


def _run_async(coro):
    """Helper to run async functions in sync context for ADK tools"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create a new one in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop exists, create one
        return asyncio.run(coro)


def calculate_lien_interest(lien_id: str) -> str:
    """Calculate accrued interest for a tax lien.

    Args:
        lien_id: The unique identifier of the lien (e.g., "lien_2024-001_20240115120000")

    Returns:
        JSON string with interest calculation details including principal, rate, days elapsed, interest accrued, and total owed
    """
    try:
        agent = InterestCalculatorAgent(storage=storage)
        result = _run_async(
            agent.run(
                tenant_id="system",
                task="calculate_interest",
                lien_ids=[lien_id]
            )
        )
        return f"Interest calculated successfully:\n{result}"
    except Exception as e:
        return f"Error calculating interest: {str(e)}"


def check_redemption_deadlines() -> str:
    """Check all redemption deadlines and send alerts for approaching dates.

    Checks all active liens and generates alerts for deadlines within 90, 60, 30, 14, 7, 3, and 1 days.

    Returns:
        Summary of deadlines checked and alerts sent
    """
    try:
        agent = DeadlineAlertAgent(storage=storage)
        result = _run_async(
            agent.run(
                tenant_id="system",
                task="check_deadlines"
            )
        )
        return f"Deadlines checked:\n{result}"
    except Exception as e:
        return f"Error checking deadlines: {str(e)}"


def record_payment(lien_id: str, amount: float, payment_date: Optional[str] = None) -> str:
    """Record a payment toward a tax lien.

    Args:
        lien_id: The unique identifier of the lien
        amount: Payment amount in dollars (e.g., 1500.00)
        payment_date: Optional payment date in YYYY-MM-DD format (defaults to today)

    Returns:
        Payment confirmation with updated balances and redemption status
    """
    try:
        agent = PaymentMonitorAgent(storage=storage)
        parameters = {"amount": amount}
        if payment_date:
            parameters["payment_date"] = payment_date

        result = _run_async(
            agent.run(
                tenant_id="system",
                task="record_payment",
                lien_ids=[lien_id],
                parameters=parameters
            )
        )
        return f"Payment recorded:\n{result}"
    except Exception as e:
        return f"Error recording payment: {str(e)}"


def list_liens(status: Optional[str] = None, county: Optional[str] = None, limit: int = 50) -> str:
    """List all tax liens with optional filters.

    Args:
        status: Filter by lien status (ACTIVE, REDEEMED, FORECLOSED, EXPIRED, etc.)
        county: Filter by county name (e.g., "Miami-Dade")
        limit: Maximum number of liens to return (default 50)

    Returns:
        List of liens matching the criteria with key details
    """
    try:
        agent = LienTrackerAgent(storage=storage)
        parameters = {"limit": limit, "order_by": "created_at"}
        if status:
            parameters["status"] = status
        if county:
            parameters["county"] = county

        result = _run_async(
            agent.run(
                tenant_id="system",
                task="list_liens",
                parameters=parameters
            )
        )
        return f"Liens found:\n{result}"
    except Exception as e:
        return f"Error listing liens: {str(e)}"


def get_portfolio_summary() -> str:
    """Get comprehensive portfolio summary with analytics.

    Calculates total invested, interest earned, current value, returns by county,
    average return rate, and average holding period.

    Returns:
        Portfolio statistics with performance metrics and recommendations
    """
    try:
        agent = PortfolioDashboardAgent(storage=storage)
        result = _run_async(
            agent.run(
                tenant_id="system",
                task="calculate_portfolio_summary"
            )
        )
        return f"Portfolio summary:\n{result}"
    except Exception as e:
        return f"Error generating portfolio summary: {str(e)}"


def send_notification(notification_type: str, title: str, message: str,
                      lien_id: Optional[str] = None) -> str:
    """Send a notification to the user.

    Args:
        notification_type: Type of notification (deadline_alert, payment_received, lien_updated, system_alert)
        title: Notification title (short summary)
        message: Notification message body (detailed information)
        lien_id: Optional lien ID associated with notification

    Returns:
        Notification confirmation with notification ID
    """
    try:
        agent = CommunicationAgent(storage=storage)
        parameters = {
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "channels": ["in_app"]
        }
        if lien_id:
            parameters["lien_id"] = lien_id

        result = _run_async(
            agent.run(
                tenant_id="system",
                task="send_notification",
                parameters=parameters
            )
        )
        return f"Notification sent:\n{result}"
    except Exception as e:
        return f"Error sending notification: {str(e)}"


def generate_redemption_notice(lien_id: str) -> str:
    """Generate a legal redemption notice document for a lien.

    Creates a professional document with lien details, payment information,
    and redemption deadlines formatted for official use.

    Args:
        lien_id: The unique identifier of the lien

    Returns:
        Document generation confirmation with document ID and content
    """
    try:
        agent = DocumentGeneratorAgent(storage=storage)
        result = _run_async(
            agent.run(
                tenant_id="system",
                task="generate_redemption_notice",
                lien_ids=[lien_id]
            )
        )
        return f"Redemption notice generated:\n{result}"
    except Exception as e:
        return f"Error generating redemption notice: {str(e)}"


def list_available_agents() -> str:
    """List all available specialized agents and their capabilities.

    Returns:
        Description of each agent and what tasks they can perform
    """
    return """Available LienOS Agents:

1. Interest Calculator Agent
   - Calculate accrued interest on liens
   - Project future interest earnings
   - Calculate total amounts owed

2. Deadline Alert Agent
   - Monitor redemption deadlines
   - Send proactive alerts (90, 60, 30, 14, 7, 3, 1 days)
   - Track deadline compliance

3. Payment Monitor Agent
   - Record payments received
   - Detect full redemptions
   - Reconcile payment histories
   - Track outstanding balances

4. Lien Tracker Agent
   - Create, read, update, delete liens
   - Search and filter lien records
   - Manage lien lifecycle

5. Communication Agent
   - Send notifications (in-app, email, SMS)
   - Queue messages for delivery
   - Track notification history

6. Portfolio Dashboard Agent
   - Calculate portfolio summaries
   - Generate performance analytics
   - Provide investment recommendations
   - Track returns by county

7. Document Generator Agent
   - Generate redemption notices
   - Create payment receipts
   - Produce tax forms (1099-INT)
   - Generate portfolio reports

Use these agents by asking me natural questions like:
- "Calculate interest for lien_2024-001_20240115120000"
- "List all active liens in Miami-Dade county"
- "Show me my portfolio summary"
- "Check upcoming deadlines"
"""


# Create the root agent with all LienOS capabilities
root_agent = Agent(
    name="lien_os_orchestrator",
    model="gemini-2.0-flash-exp",
    instruction="""You are LienOS, an AI assistant for managing tax lien investment portfolios. You coordinate 7 specialized agents to help users:

**Core Capabilities:**
- Calculate interest accrued on tax liens
- Monitor and alert on redemption deadlines
- Track and reconcile payments
- Manage lien data (create, update, search)
- Generate portfolio analytics and reports
- Send notifications and communications
- Create legal documents and receipts

**Communication Style:**
- Be clear, professional, and accurate
- When performing calculations, show your work
- Use appropriate decimal precision for financial data
- Be proactive in alerting users to important deadlines
- Provide actionable recommendations based on portfolio data

**Available Tools:**
You have access to specialized agents through these tools. Always use the appropriate tool for each task:
- calculate_lien_interest() - for interest calculations
- record_payment() - for recording payments
- list_liens() - for searching liens
- check_redemption_deadlines() - for deadline monitoring
- get_portfolio_summary() - for portfolio analytics
- send_notification() - for alerts and messages
- generate_redemption_notice() - for legal documents
- list_available_agents() - to show what you can do

When users ask general questions about capabilities, use list_available_agents(). When they request specific actions, use the appropriate specialized tool.""",
    tools=[
        calculate_lien_interest,
        check_redemption_deadlines,
        record_payment,
        list_liens,
        get_portfolio_summary,
        send_notification,
        generate_redemption_notice,
        list_available_agents,
    ],
)

# Create the ADK app
# Note: app name must match the directory name "agents" for ADK to find it
app = App(root_agent=root_agent, name="agents")
