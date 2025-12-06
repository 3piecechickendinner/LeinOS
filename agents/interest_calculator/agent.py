from typing import Dict, Any, List

from datetime import datetime, date

from decimal import Decimal



from core.base_agent import LienOSBaseAgent

from core.data_models import AgentContext, InterestCalculation, TaxLien, CivilJudgment

from core.storage import FirestoreClient





class InterestCalculatorAgent(LienOSBaseAgent):

    """

    Agent that calculates interest accrued on tax liens.

    Uses simple interest formula: Interest = Principal × Rate × (Days / 365)

    """

    

    def __init__(self, storage: FirestoreClient):

        super().__init__(

            agent_name="InterestCalculator",

            storage=storage,

            model_name="gemini-2.0-flash-exp"

        )

    

    def _define_capabilities(self) -> List[str]:

        """This agent can calculate interest"""

        return ["calculate_interest", "calculate_total_owed"]

    

    def _register_tools(self) -> None:

        """No external tools needed for basic interest calculation"""

        pass

    

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:

        """

        Calculate interest for a lien.

        

        Expects context.lien_ids to have one lien_id.

        

        Returns:

            Dict with interest_accrued, total_owed, days_elapsed

        """

        if not context.lien_ids and not context.asset_ids:
            # Fallback to check empty lists
            if (not context.lien_ids or len(context.lien_ids) == 0) and \
               (not context.asset_ids or len(context.asset_ids) == 0):
                raise ValueError("lien_id or asset_id required in context")

        # Prefer asset_id if available, else lien_id
        asset_id = context.asset_ids[0] if context.asset_ids else context.lien_ids[0]
        
        # Try getting as Tax Lien first (default collection "liens")
        asset_data = await self.storage.get("liens", asset_id, context.tenant_id)
        asset_type = "TAX_LIEN"
        
        if not asset_data:
            # Check other verticals
            collections = {
                "judgments": "CIVIL_JUDGMENT",
                "probate_estates": "PROBATE",
                "minerals": "MINERAL_RIGHT",
                "surplus_funds": "SURPLUS_FUND"
            }
            
            found = False
            for coll, type_name in collections.items():
                asset_data = await self.storage.get(coll, asset_id, context.tenant_id)
                if asset_data:
                    asset_type = type_name
                    found = True
                    break
            
            if not found:
                 raise ValueError(f"Asset {asset_id} not found or unauthorized")

        # Logic based on Asset Type
        if asset_type == "PROBATE":
            estimated_value = Decimal(str(asset_data.get("estimated_value", "0.0")))
            mortgages = Decimal(str(asset_data.get("mortgages_amount", "0.0")))
            liens = Decimal(str(asset_data.get("liens_amount", "0.0")))
            equity = estimated_value - (mortgages + liens)
            
            return {
                "asset_id": asset_id,
                "asset_type": asset_type,
                "label": "Estimated Equity",
                "value": float(equity),
                "calculation_date": date.today().isoformat()
            }
            
        elif asset_type == "MINERAL_RIGHT":
            acres = Decimal(str(asset_data.get("net_mineral_acres", "0.0")))
            royalty = Decimal(str(asset_data.get("royalty_decimal", "0.0")))
            # Constants for estimation: $80/bbl oil price, 30 bbl/acre yield
            # TODO: Make these configurable
            oil_price = Decimal("80.0")
            yield_per_acre = Decimal("30.0")
            
            monthly_revenue = acres * royalty * oil_price * yield_per_acre
            
            return {
                "asset_id": asset_id,
                "asset_type": asset_type,
                "label": "Monthly Revenue Estimate",
                "value": float(monthly_revenue),
                "calculation_date": date.today().isoformat()
            }
            
        elif asset_type == "SURPLUS_FUND":
            surplus_amount = Decimal(str(asset_data.get("surplus_amount", "0.0")))
            # 30% recovery fee
            potential_fee = surplus_amount * Decimal("0.30")
            
            return {
                "asset_id": asset_id,
                "asset_type": asset_type,
                "label": "Potential Fee",
                "value": float(potential_fee),
                "calculation_date": date.today().isoformat()
            }

        # Existing Tax Lien and Judgment Logic (using simple interest)
        else:
            # Extract calculation parameters
            if asset_type == "TAX_LIEN":
                principal = Decimal(str(asset_data.get("purchase_amount", 0)))
                rate = Decimal(str(asset_data.get("interest_rate", 0)))
                if "purchase_date" in asset_data:
                    start_date = datetime.strptime(asset_data["purchase_date"], "%Y-%m-%d").date()
                else:
                    start_date = date.today()
            else: # CIVIL_JUDGMENT
                principal = Decimal(str(asset_data.get("judgment_amount", 0)))
                # Default to 0 if not present
                rate = Decimal(str(asset_data.get("interest_rate", 0)))
                if "judgment_date" in asset_data:
                    start_date = datetime.strptime(asset_data["judgment_date"], "%Y-%m-%d").date()
                else:
                    start_date = date.today()

            end_date = date.today()
            days_elapsed = (end_date - start_date).days
            
            if days_elapsed < 0:
                days_elapsed = 0

            # Interest = Principal * (Rate/100) * (Days/365)
            interest = principal * (rate / Decimal(100)) * (Decimal(days_elapsed) / Decimal(365))
            total_owed = principal + interest

            return {
                "asset_id": asset_id,
                "asset_type": asset_type,
                "label": "Total Owed",
                "principal": float(principal),
                "interest_accrued": float(interest),
                "total_owed": float(total_owed),
                "days_elapsed": days_elapsed,
                "calculation_date": end_date.isoformat()
            }
