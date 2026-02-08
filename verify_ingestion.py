import asyncio
from sqlalchemy import select, func
from core.database import AsyncSessionLocal
from models.models import Medicine
import random

async def verify():
    async with AsyncSessionLocal() as session:
        # Check total count
        result = await session.execute(select(func.count(Medicine.id)))
        count = result.scalar()
        print(f"Total medicines in DB: {count}")
        
        # Get 5 random medicines
        # Using a simple offset method for randomness on large table
        random_ids = random.sample(range(1, count + 1), 5)
        stmt = select(Medicine).where(Medicine.id.in_(random_ids))
        result = await session.execute(stmt)
        medicines = result.scalars().all()
        
        print("\nRandom Sample Verification:")
        for m in medicines:
            print("-" * 40)
            print(f"Name: {m.drug_name}")
            print(f"Uses: {m.uses}")
            print(f"Side Effects: {m.side_effects}")
            print(f"Substitutes: {m.substitutes}")
            print(f"Class: {m.therapeutic_class}")

if __name__ == "__main__":
    asyncio.run(verify())
