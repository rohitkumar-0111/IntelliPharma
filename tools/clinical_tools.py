from langchain_core.tools import tool
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.models import Medicine
import difflib

@tool
async def lookup_clinical_data(query: str) -> str:
    """
    Look up detailed clinical data for a drug, including uses, side effects, 
    substitutes, and pharmacological classes.
    """
    async with AsyncSessionLocal() as session:
        try:
            # 1. Try to find the drug in the database (Exact Match)
            # We assume query might be the drug name or contain it.
            # Simple heuristic: exact match first, then fuzzy.
            
            # Fetch all drug names for fuzzy matching logic
            stmt_all = select(Medicine.drug_name).distinct()
            result_all = await session.execute(stmt_all)
            all_drugs = result_all.scalars().all()
            
            # Find closest match to the full query or parts of it?
            # Let's try to match the whole query as a drug name first.
            # If query is "side effects of Centirizine", this fails.
            # But the agent extracts drug name before calling this tool usually?
            # Actually, the agent calls `lookup_clinical_data.invoke(search_term)` check agent_graph.py
            # In agent_graph, `search_term` is `extracted_drug` if available.
            
            drug_name = query
            matches = difflib.get_close_matches(drug_name, all_drugs, n=1, cutoff=0.5)
            
            if not matches:
                 # If no direct match, maybe the query key words + drug? 
                 # But sticking to simple fuzzy for 'drug name' input is safest if agent does extraction.
                 # If agent passes "side effects of X", we might miss.
                 # Let's trust the agent's extraction for now or rely on fuzzy to catch "Centrizine" from "Centrizine".
                 return "No specific clinical data found for this drug in the internal database."

            target_drug = matches[0]
            
            stmt = select(Medicine).where(Medicine.drug_name == target_drug)
            result = await session.execute(stmt)
            med = result.scalars().first()
            
            if not med:
                return "No details found."

            # Format Structured Output
            output = [
                f"### Clinical Info: {med.drug_name}",
                f"- **Therapeutic Class**: {med.therapeutic_class or 'N/A'}",
                f"- **Chemical Class**: {med.chemical_class or 'N/A'}",
                f"- **Mechanism of Action**: {med.action_class or 'N/A'}",
                f"- **Uses**: {med.uses or 'N/A'}",
                f"- **Side Effects**: {med.side_effects or 'N/A'}",
                f"- **Dosage**: {med.dosage or 'Consult Physician'}",
                f"- **Contraindications**: {med.contraindications or 'N/A'}",
                f"- **Habit Forming**: {med.habit_forming or 'No'}",
                f"- **Substitutes**: {med.substitutes or 'None listed'}"
            ]
            
            return "\n".join(output)

        except Exception as e:
            return f"Error looking up clinical data: {str(e)}"
