from langchain_core.tools import tool
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.models import Medicine

@tool
async def get_drug_details(drug_name: str) -> str:
    """
    Get detailed information about a specific drug, including uses, side effects, substitutes, and more.
    Useful for answering questions about safety, alternatives, and indications.
    """
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(Medicine).where(
                Medicine.drug_name.ilike(drug_name)
            )
            result = await session.execute(stmt)
            medicine = result.scalars().first()

            if not medicine:
                # Try a partial match if exact match fails? 
                # For now, strict match or maybe simple wildcard
                stmt = select(Medicine).where(
                    Medicine.drug_name.ilike(f"%{drug_name}%")
                )
                result = await session.execute(stmt)
                medicine = result.scalars().first()
                if not medicine:
                    return f"No details found for drug: {drug_name}"

            # Format the output
            response = [
                f"Found {medicine.drug_name}.",
                f"Uses: {medicine.uses}",
                f"Side Effects: {medicine.side_effects[:200]}..." if medicine.side_effects else "Side Effects: None listed", # Truncate if too long
                f"Habit Forming: {medicine.habit_forming}",
                f"Therapeutic Class: {medicine.therapeutic_class}",
                f"Substitutes: {medicine.substitutes}"
            ]
            
            return "\n".join(response)

        except Exception as e:
            return f"Error retrieving drug details: {str(e)}"
