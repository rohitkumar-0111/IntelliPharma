from langchain_core.tools import tool
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.models import Medicine

@tool
async def get_drug_details(drug_names: str) -> str:
    """
    Get detailed information about one or more drugs. 
    Input can be a single drug name or a comma-separated list of drug names.
    Returns comprehensive details including dosage, contraindications, and class.
    """
    drug_list = [d.strip() for d in drug_names.split(',')]
    results = []

    async with AsyncSessionLocal() as session:
        for drug_name in drug_list:
            try:
                # 1. Exact Match
                stmt = select(Medicine).where(Medicine.drug_name.ilike(drug_name))
                result = await session.execute(stmt)
                medicine = result.scalars().first()

                # 2. Pattern Match
                if not medicine:
                    stmt = select(Medicine).where(Medicine.drug_name.ilike(f"%{drug_name}%"))
                    result = await session.execute(stmt)
                    medicine = result.scalars().first()

                # 3. Fuzzy Match (Robust Fallback)
                if not medicine:
                    # Fetch all names to find closest match
                    # Optimized: Only fetch if input length > 3 to avoid noise
                    if len(drug_name) > 3:
                        stmt = select(Medicine.drug_name)
                        result = await session.execute(stmt)
                        all_drug_names = result.scalars().all()
                        
                        from difflib import get_close_matches
                        matches = get_close_matches(drug_name, all_drug_names, n=1, cutoff=0.6)
                        
                        if matches:
                            corrected_name = matches[0]
                            stmt = select(Medicine).where(Medicine.drug_name == corrected_name)
                            result = await session.execute(stmt)
                            medicine = result.scalars().first()
                            results.append(f"**Note**: '{drug_name}' not found. Showing results for closest match: **{corrected_name}**.\n")

                if not medicine:
                    results.append(f"No details found for drug: {drug_name}")
                    continue

                # Format Output (Comprehensive)
                details = [
                    f"Drug: {medicine.drug_name}",
                    f"Therapeutic Class: {medicine.therapeutic_class or 'N/A'}",
                    f"Action Class: {medicine.action_class or 'N/A'}",
                    f"Chemical Class: {medicine.chemical_class or 'N/A'}",
                    f"Habit Forming: {medicine.habit_forming or 'No'}",
                    f"Uses: {medicine.uses}",
                    f"Dosage: {medicine.dosage or 'Consult physician'}",
                    f"Contraindications: {medicine.contraindications or 'Consult physician'}",
                    f"Side Effects: {medicine.side_effects or 'None listed'}",
                    f"Substitutes: {medicine.substitutes or 'None'}",
                    "-" * 30 
                ]
                results.append("\n".join(details))

            except Exception as e:
                results.append(f"Error retrieving details for {drug_name}: {str(e)}")
    
    return "\n\n".join(results)
