from typing import Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from collections import defaultdict

from core.base_agent import LienOSBaseAgent
from core.data_models import AgentContext, Portfolio, LienStatus
from core.storage import FirestoreClient
from agents.interest_calculator.agent import InterestCalculatorAgent


class PortfolioDashboardAgent(LienOSBaseAgent):
    """
    Agent that provides portfolio analytics and performance reporting.
    Aggregates data from other agents to provide comprehensive insights.
    """

    def __init__(self, storage: FirestoreClient):
        super().__init__(
            agent_name="PortfolioDashboard",
            storage=storage,
            model_name="gemini-2.0-flash-exp"
        )

    def _define_capabilities(self) -> List[str]:
        """Define what this agent can do"""
        return [
            "calculate_portfolio_summary",
            "get_portfolio_stats",
            "generate_performance_report"
        ]

    def _register_tools(self) -> None:
        """No external tools needed for portfolio analytics"""
        pass

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Main agent logic.

        Handles tasks:
        - calculate_portfolio_summary: Full portfolio calculation and save
        - get_portfolio_stats: Return latest saved portfolio stats
        - generate_performance_report: Detailed report with all liens

        Returns:
            Dict with portfolio analytics
        """
        if context.task == "calculate_portfolio_summary":
            return await self._calculate_portfolio_summary(context)
        elif context.task == "get_portfolio_stats":
            return await self._get_portfolio_stats(context)
        elif context.task == "generate_performance_report":
            return await self._generate_performance_report(context)
        else:
            raise ValueError(f"Unknown task: {context.task}")

    async def _calculate_portfolio_summary(self, context: AgentContext) -> Dict[str, Any]:
        """
        Calculate comprehensive portfolio summary.

        Queries all liens, calculates interest for active liens,
        and aggregates statistics.

        Returns:
            Dict with full portfolio summary
        """
        # Get all liens for tenant
        all_liens = await self.storage.query(
            "liens",
            context.tenant_id,
            filters=None,
            order_by="created_at"
        )

        if not all_liens:
            return {
                "total_liens": 0,
                "active_liens": 0,
                "total_invested": 0,
                "total_interest_earned": 0,
                "message": "No liens found in portfolio"
            }

        # Initialize counters
        total_invested = Decimal("0")
        total_interest_earned = Decimal("0")
        total_current_value = Decimal("0")
        total_redeemed_value = Decimal("0")

        liens_by_status = defaultdict(int)
        liens_by_county = defaultdict(int)

        active_liens = []
        redeemed_liens = []
        holding_periods = []

        today = date.today()
        interest_agent = InterestCalculatorAgent(storage=self.storage)

        # Process each lien
        for lien in all_liens:
            lien_id = lien.get("lien_id")
            status = lien.get("status")
            county = lien.get("county", "Unknown")
            purchase_amount = Decimal(str(lien.get("purchase_amount", 0)))

            # Update counters
            total_invested += purchase_amount
            liens_by_status[status] += 1
            liens_by_county[county] += 1

            # Calculate holding period
            sale_date = lien.get("sale_date")
            if isinstance(sale_date, str):
                sale_date = date.fromisoformat(sale_date)

            if status == LienStatus.ACTIVE.value:
                # Calculate current interest for active liens
                try:
                    interest_result = await interest_agent.run(
                        tenant_id=context.tenant_id,
                        task="calculate_interest",
                        lien_ids=[lien_id]
                    )

                    interest_accrued = Decimal(str(interest_result.get("interest_accrued", 0)))
                    current_value = Decimal(str(interest_result.get("total_owed", 0)))

                    total_interest_earned += interest_accrued
                    total_current_value += current_value

                    holding_days = (today - sale_date).days
                    holding_periods.append(holding_days)

                    active_liens.append({
                        "lien_id": lien_id,
                        "property_address": lien.get("property_address"),
                        "purchase_amount": float(purchase_amount),
                        "interest_accrued": float(interest_accrued),
                        "current_value": float(current_value),
                        "holding_days": holding_days,
                        "county": county
                    })

                except Exception as e:
                    self.log_error(f"Failed to calculate interest for lien {lien_id}: {e}")
                    # Still count the principal
                    total_current_value += purchase_amount

            elif status == LienStatus.REDEEMED.value:
                # For redeemed liens, get the total payments received
                payments = await self.storage.query(
                    "payments",
                    context.tenant_id,
                    filters=[
                        ("lien_id", "==", lien_id),
                        ("status", "==", "COMPLETED")
                    ]
                )

                redeemed_amount = Decimal("0")
                for pmt in payments:
                    redeemed_amount += Decimal(str(pmt.get("amount", 0)))

                profit = redeemed_amount - purchase_amount
                total_redeemed_value += redeemed_amount
                total_interest_earned += profit

                # Calculate holding period until redemption
                updated_at = lien.get("updated_at")
                if updated_at:
                    if isinstance(updated_at, str):
                        redemption_date = date.fromisoformat(updated_at.split("T")[0])
                    else:
                        redemption_date = updated_at.date() if hasattr(updated_at, 'date') else today
                    holding_days = (redemption_date - sale_date).days
                else:
                    holding_days = (today - sale_date).days

                holding_periods.append(holding_days)

                redeemed_liens.append({
                    "lien_id": lien_id,
                    "property_address": lien.get("property_address"),
                    "purchase_amount": float(purchase_amount),
                    "redeemed_amount": float(redeemed_amount),
                    "profit": float(profit),
                    "holding_days": holding_days,
                    "county": county
                })

        # Calculate averages
        avg_holding_period = sum(holding_periods) / len(holding_periods) if holding_periods else 0

        # Calculate average return rate
        if total_invested > 0:
            avg_return_rate = (total_interest_earned / total_invested) * 100
        else:
            avg_return_rate = Decimal("0")

        # Create Portfolio record
        portfolio = Portfolio(
            portfolio_id=f"portfolio_{context.tenant_id}_{datetime.utcnow().strftime('%Y%m%d')}",
            tenant_id=context.tenant_id,
            total_liens=len(all_liens),
            active_liens=liens_by_status.get(LienStatus.ACTIVE.value, 0),
            total_invested=total_invested,
            total_interest_earned=total_interest_earned,
            total_redeemed=liens_by_status.get(LienStatus.REDEEMED.value, 0),
            liens_by_status=dict(liens_by_status),
            liens_by_county=dict(liens_by_county),
            average_return_rate=avg_return_rate,
            average_holding_period_days=int(avg_holding_period),
            calculated_at=datetime.utcnow()
        )

        # Save to storage
        portfolio_dict = portfolio.model_dump()
        await self.storage.create("portfolios", portfolio_dict, context.tenant_id)

        self.log_info(f"Portfolio summary calculated: {len(all_liens)} liens, ${float(total_invested):,.2f} invested")

        return {
            "portfolio_id": portfolio.portfolio_id,
            "total_liens": portfolio.total_liens,
            "active_liens": portfolio.active_liens,
            "total_invested": float(portfolio.total_invested),
            "total_interest_earned": float(portfolio.total_interest_earned),
            "total_current_value": float(total_current_value),
            "total_redeemed": portfolio.total_redeemed,
            "total_redeemed_value": float(total_redeemed_value),
            "liens_by_status": portfolio.liens_by_status,
            "liens_by_county": portfolio.liens_by_county,
            "average_return_rate": float(portfolio.average_return_rate),
            "average_holding_period_days": portfolio.average_holding_period_days,
            "calculated_at": portfolio.calculated_at.isoformat()
        }

    async def _get_portfolio_stats(self, context: AgentContext) -> Dict[str, Any]:
        """
        Return the latest saved portfolio stats.

        Returns:
            Dict with latest portfolio summary
        """
        # Query for most recent portfolio record
        portfolios = await self.storage.query(
            "portfolios",
            context.tenant_id,
            filters=None,
            order_by="calculated_at",
            limit=1
        )

        if not portfolios:
            return {
                "found": False,
                "message": "No portfolio stats found. Run calculate_portfolio_summary first."
            }

        portfolio = portfolios[0]

        return {
            "found": True,
            "portfolio_id": portfolio.get("portfolio_id"),
            "total_liens": portfolio.get("total_liens"),
            "active_liens": portfolio.get("active_liens"),
            "total_invested": portfolio.get("total_invested"),
            "total_interest_earned": portfolio.get("total_interest_earned"),
            "total_redeemed": portfolio.get("total_redeemed"),
            "liens_by_status": portfolio.get("liens_by_status"),
            "liens_by_county": portfolio.get("liens_by_county"),
            "average_return_rate": portfolio.get("average_return_rate"),
            "average_holding_period_days": portfolio.get("average_holding_period_days"),
            "calculated_at": portfolio.get("calculated_at")
        }

    async def _generate_performance_report(self, context: AgentContext) -> Dict[str, Any]:
        """
        Generate detailed performance report with all liens and their current values.

        Returns:
            Dict with comprehensive performance data
        """
        # First calculate the summary
        summary = await self._calculate_portfolio_summary(context)

        # Get all liens with detailed breakdown
        all_liens = await self.storage.query(
            "liens",
            context.tenant_id,
            filters=None,
            order_by="sale_date"
        )

        interest_agent = InterestCalculatorAgent(storage=self.storage)
        today = date.today()

        detailed_liens = []
        top_performers = []
        underperformers = []

        for lien in all_liens:
            lien_id = lien.get("lien_id")
            status = lien.get("status")
            purchase_amount = Decimal(str(lien.get("purchase_amount", 0)))
            interest_rate = Decimal(str(lien.get("interest_rate", 0)))

            sale_date = lien.get("sale_date")
            if isinstance(sale_date, str):
                sale_date = date.fromisoformat(sale_date)

            redemption_deadline = lien.get("redemption_deadline")
            if isinstance(redemption_deadline, str):
                redemption_deadline = date.fromisoformat(redemption_deadline)

            days_to_deadline = (redemption_deadline - today).days

            lien_detail = {
                "lien_id": lien_id,
                "certificate_number": lien.get("certificate_number"),
                "property_address": lien.get("property_address"),
                "county": lien.get("county"),
                "purchase_amount": float(purchase_amount),
                "interest_rate": float(interest_rate),
                "sale_date": sale_date.isoformat(),
                "redemption_deadline": redemption_deadline.isoformat(),
                "days_to_deadline": days_to_deadline,
                "status": status
            }

            if status == LienStatus.ACTIVE.value:
                try:
                    interest_result = await interest_agent.run(
                        tenant_id=context.tenant_id,
                        task="calculate_interest",
                        lien_ids=[lien_id]
                    )

                    interest_accrued = float(interest_result.get("interest_accrued", 0))
                    total_owed = float(interest_result.get("total_owed", 0))
                    roi = (interest_accrued / float(purchase_amount)) * 100 if purchase_amount > 0 else 0

                    lien_detail.update({
                        "interest_accrued": interest_accrued,
                        "total_owed": total_owed,
                        "roi_percent": round(roi, 2),
                        "days_held": interest_result.get("days_elapsed", 0)
                    })

                    # Categorize performance
                    if roi >= float(interest_rate):
                        top_performers.append(lien_detail)
                    elif roi < float(interest_rate) * 0.5:
                        underperformers.append(lien_detail)

                except Exception as e:
                    lien_detail["error"] = str(e)

            detailed_liens.append(lien_detail)

        # Sort top performers by ROI
        top_performers.sort(key=lambda x: x.get("roi_percent", 0), reverse=True)

        # Calculate portfolio health score (0-100)
        health_score = self._calculate_health_score(
            total_liens=len(all_liens),
            active_liens=summary.get("active_liens", 0),
            avg_return=summary.get("average_return_rate", 0),
            underperformers_count=len(underperformers)
        )

        return {
            "report_date": today.isoformat(),
            "summary": summary,
            "detailed_liens": detailed_liens,
            "top_performers": top_performers[:5],  # Top 5
            "underperformers": underperformers[:5],  # Bottom 5
            "portfolio_health_score": health_score,
            "recommendations": self._generate_recommendations(
                summary, top_performers, underperformers
            )
        }

    def _calculate_health_score(
        self,
        total_liens: int,
        active_liens: int,
        avg_return: float,
        underperformers_count: int
    ) -> int:
        """Calculate portfolio health score (0-100)"""
        score = 100

        # Deduct for low diversification
        if total_liens < 5:
            score -= 20
        elif total_liens < 10:
            score -= 10

        # Deduct for underperformers
        if total_liens > 0:
            underperformer_ratio = underperformers_count / total_liens
            score -= int(underperformer_ratio * 30)

        # Bonus for good returns
        if avg_return >= 15:
            score += 10
        elif avg_return >= 10:
            score += 5
        elif avg_return < 5:
            score -= 15

        return max(0, min(100, score))

    def _generate_recommendations(
        self,
        summary: Dict[str, Any],
        top_performers: List[Dict],
        underperformers: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations based on portfolio analysis"""
        recommendations = []

        total_liens = summary.get("total_liens", 0)
        avg_return = summary.get("average_return_rate", 0)
        liens_by_county = summary.get("liens_by_county", {})

        # Diversification recommendations
        if total_liens < 5:
            recommendations.append(
                "Consider expanding your portfolio. Having fewer than 5 liens "
                "increases concentration risk."
            )

        # County concentration
        if liens_by_county:
            max_county_count = max(liens_by_county.values())
            if total_liens > 0 and max_county_count / total_liens > 0.5:
                recommendations.append(
                    "Your portfolio is heavily concentrated in one county. "
                    "Consider diversifying across multiple counties."
                )

        # Return optimization
        if avg_return < 8:
            recommendations.append(
                "Your average return rate is below 8%. Consider targeting "
                "liens with higher interest rates or shorter redemption periods."
            )

        # Underperformer action
        if len(underperformers) > 0:
            recommendations.append(
                f"You have {len(underperformers)} underperforming lien(s). "
                "Review these liens for potential issues or early exit opportunities."
            )

        # Top performer insights
        if len(top_performers) >= 3:
            top_counties = set(l.get("county") for l in top_performers[:3])
            recommendations.append(
                f"Your top performers are in: {', '.join(top_counties)}. "
                "Consider focusing future acquisitions in these areas."
            )

        if not recommendations:
            recommendations.append(
                "Your portfolio is well-balanced. Continue monitoring deadlines "
                "and maintain diversification."
            )

        return recommendations
