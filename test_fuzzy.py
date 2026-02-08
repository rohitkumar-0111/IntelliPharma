import asyncio
from tools.drug_db_tool import get_drug_details

async def test():
    print("\n--- Testing Typo: Citrizine ---")
    # Should resolve to Cetirizine
    result = await get_drug_details.ainvoke("Citrizine")
    print(result)

    print("\n--- Testing Typo: Paracutamal ---")
    # Should resolve to Paracetamol
    result = await get_drug_details.ainvoke("Paracutamal")
    print(result)

    print("\n--- Testing Enriched Data: Vildagliptin ---")
    # Should show detailed dosage
    result = await get_drug_details.ainvoke("Vildagliptin")
    print(result)

if __name__ == "__main__":
    asyncio.run(test())
