import asyncio
from tools.drug_db_tool import get_drug_details

async def test():
    # Test single drug (should show enhanced details)
    print("\n--- Testing Single Drug (Cetirizine) ---")
    result = await get_drug_details.ainvoke("Cetirizine")
    print(result)

    # Test multiple drugs (should show both)
    print("\n--- Testing Multiple Drugs (Paracetamol, Ibuprofen) ---")
    result = await get_drug_details.ainvoke("Paracetamol, Ibuprofen")
    print(result)

if __name__ == "__main__":
    asyncio.run(test())
