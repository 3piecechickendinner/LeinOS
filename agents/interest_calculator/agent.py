from typing import Dict, Any, List

from datetime import datetime, date

from decimal import Decimal



from core.base_agent import LienOSBaseAgent

from core.data_models import AgentContext, InterestCalculation

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

        if not context.lien_ids or len(context.lien_ids) == 0:

            raise ValueError("lien_id required in context.lien_ids")

        

        lien_id = context.lien_ids[0]

        

        # Get lien from storage

        lien_data = await self.storage.get("liens", lien_id, context.tenant_id)

        if not lien_data:

            raise ValueError(f"Lien {lien_id} not found or unauthorized")

        

        # Extract calculation parameters

        principal = Decimal(str(lien_data["purchase_amount"]))

        interest_rate = Decimal(str(lien_data["interest_rate"]))

        sale_date = lien_data["sale_date"]

        

        # Calculate days elapsed

        if isinstance(sale_date, str):

            sale_date = date.fromisoformat(sale_date)

        

        days_elapsed = (date.today() - sale_date).days

        

        # Simple interest formula: I = P × R × T

        # Where T = days / 365, R is annual rate as decimal (e.g., 18% = 0.18)

        interest_accrued = principal * (interest_rate / 100) * (Decimal(days_elapsed) / Decimal(365))

        total_owed = principal + interest_accrued

        

        # Create InterestCalculation record

        calculation = InterestCalculation(

            lien_id=lien_id,

            tenant_id=context.tenant_id,

            calculation_date=date.today(),

            principal=principal,

            interest_rate=interest_rate,

            days_elapsed=days_elapsed,

            interest_accrued=interest_accrued,

            total_owed=total_owed,

            calculated_at=datetime.utcnow()

        )

        

        # Save to storage

        calc_dict = calculation.model_dump()

        calc_dict["calculation_id"] = f"{lien_id}_{date.today().isoformat()}"

        await self.storage.create("interest_calculations", calc_dict, context.tenant_id)

        

        self.log_info(f"Calculated interest for lien {lien_id}: ${interest_accrued:.2f}")

        

        return {

            "lien_id": lien_id,

            "principal": float(principal),

            "interest_rate": float(interest_rate),

            "days_elapsed": days_elapsed,

            "interest_accrued": float(interest_accrued),

            "total_owed": float(total_owed),

            "calculation_date": date.today().isoformat()

        }

