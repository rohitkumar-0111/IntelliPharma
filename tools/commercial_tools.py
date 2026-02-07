from langchain_core.tools import tool
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.models import ReimbursementScheme, SchemeType, Medicine

@tool
async def compare_reimbursement_schemes(drug_name: str) -> str:
    """
    Compare reimbursement schemes for a specific drug.
    Separates government and private schemes and provides a financial comparison.
    """
    async with AsyncSessionLocal() as session:
        with open("debug.log", "a") as f:
            f.write(f"\n[Tool] Input: {drug_name}\n")
        try:
            # 1. Fetch Reimbursement Schemes
            stmt = select(ReimbursementScheme).where(
                ReimbursementScheme.drug_name.ilike(drug_name)
            )
            result = await session.execute(stmt)
            schemes = result.scalars().all()

            if not schemes:
                # 1b. Try Advanced Fuzzy Matching (Python-side)
                # Fetch all variable drug names to find closest match
                stmt_all = select(ReimbursementScheme.drug_name).distinct()
                result_all = await session.execute(stmt_all)
                all_drugs = result_all.scalars().all()
                
                import difflib
                # cutoff=0.6 allows for "centrizine" -> "Cetirizine"
                matches = difflib.get_close_matches(drug_name, all_drugs, n=1, cutoff=0.5)
                
                if matches:
                    corrected_name = matches[0]
                    with open("debug.log", "a") as f:
                        f.write(f"[Tool] Fuzzy Match: {drug_name} -> {corrected_name}\n")
                    # Query again with corrected name
                    stmt = select(ReimbursementScheme).where(
                        ReimbursementScheme.drug_name == corrected_name
                    )
                    result = await session.execute(stmt)
                    schemes = result.scalars().all()
                    
                    # Update drug_name for display
                    drug_name = corrected_name

                if not schemes:
                    return ""

            # 2. Fetch Medicine Details for Category (Therapeutic Class)
            stmt_med = select(Medicine).where(
                Medicine.drug_name.ilike(drug_name)
            )
            result_med = await session.execute(stmt_med)
            medicine = result_med.scalars().first()
            
            category = "General Medicine"
            if medicine and medicine.therapeutic_class:
                category = medicine.therapeutic_class
            elif medicine and medicine.chemical_class:
                # Fallback to chemical class if therapeutic class is missing
                category = medicine.chemical_class

            govt_schemes = []
            private_schemes = []

            for scheme in schemes:
                # Format requested:
                # [Plan Name]: [Reimburses/Covers] [drug_name] under the "[Category]" category [financials].
                
                # Logic:
                # Govt -> "Reimburses"
                # Private -> "Covers"
                
                verb = "Reimburses" if scheme.scheme_type == SchemeType.GOVT else "Covers"
                
                financials = ""
                if scheme.scheme_type == SchemeType.PRIVATE:
                    # Specific request: "with a co-pay of X%."
                    # Calculate copay percentage if not stored directly
                    copay_percent = 100 - int(scheme.coverage_percent)
                    financials = f" with a co-pay of {copay_percent}%."
                else:
                    financials = "."

                info = f"**{scheme.plan_name}**: {verb} {drug_name} under the \"{category}\" category{financials}"
                
                if scheme.scheme_type == SchemeType.GOVT:
                    govt_schemes.append(info)
                else:
                    private_schemes.append(info)

            # Constructing Final Output
            response = [f"### Reimbursement Schemes for {drug_name}:"]
            
            if govt_schemes:
                response.append("\n**Government Schemes:**")
                response.extend([f"- {s}" for s in govt_schemes])
                
            if private_schemes:
                response.append("\n**Private Insurance Companies:**")
                response.extend([f"- {s}" for s in private_schemes])

            response.append("\n*Please note that reimbursement schemes and co-pays may vary depending on the specific policy, provider, and location. It is essential to verify the information with the relevant insurance company or healthcare provider for accurate details.*")

            return "\n".join(response)

        except Exception as e:
            return f"Error comparing schemes: {str(e)}"
