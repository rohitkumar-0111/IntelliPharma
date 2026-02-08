import asyncio
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.models import Medicine
from difflib import get_close_matches

async def check_data():
    async with AsyncSessionLocal() as session:
        # 1. Check for Cetirizine (Exact)
        stmt = select(Medicine.drug_name).where(Medicine.drug_name.ilike("Cetirizine"))
        result = await session.execute(stmt)
        found = result.scalars().first()
        print(f"Exact match for 'Cetirizine': {found}")

        # 2. Check for Citrizine (Typo)
        stmt = select(Medicine.drug_name).where(Medicine.drug_name.ilike("Citrizine"))
        result = await session.execute(stmt)
        found_typo = result.scalars().first()
        print(f"Exact match for 'Citrizine': {found_typo}")

        # 3. Test Fuzzy Logic simulation
        if not found_typo:
            print("Simulating Fuzzy Search...")
            # Fetch all drug names (In production, maybe limit or use DB extension if available, but SQLite doesn't have native fuzzy)
            # For this scale (200k), in-memory might be slow, but let's see. 
            # Actually, querying 200k names into memory for every search is bad.
            # But maybe we can try finding names starting with 'C' first?
            
            # For now, let's just fetch ALL to test the concept or fetch a subset
            stmt = select(Medicine.drug_name)
            result = await session.execute(stmt)
            all_drugs = result.scalars().all()
            
            matches = get_close_matches("Citrizine", all_drugs, n=3, cutoff=0.6)
            print(f"Fuzzy matches for 'Citrizine': {matches}")

if __name__ == "__main__":
    asyncio.run(check_data())
