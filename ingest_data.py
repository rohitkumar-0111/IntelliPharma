import asyncio
import csv
import sys
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.models import Medicine

# Increase CSV field size limit just in case
csv.field_size_limit(sys.maxsize)

# Chunk size for database insertion
BATCH_SIZE = 1000

async def ingest_data():
    print("Starting data ingestion...")
    
    file_path = 'data/medicine_dataset.csv'
    medicines_to_add = []
    
    # Get existing drugs to avoid duplicates
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Medicine.drug_name))
            existing_drugs = set(result.scalars().all())
            print(f"Found {len(existing_drugs)} existing drugs in database.")
    except Exception as e:
        print(f"Error accessing database: {e}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            # Identify columns groups
            use_cols = [c for c in fieldnames if c.startswith('use')]
            side_effect_cols = [c for c in fieldnames if c.startswith('sideEffect')]
            substitute_cols = [c for c in fieldnames if c.startswith('substitute')]
            
            print(f"Processing CSV with {len(use_cols)} use cols, {len(side_effect_cols)} sideEffect cols...")

            count = 0
            duplicate_count = 0
            
            for row in reader:
                drug_name = row['name'].strip() if row['name'] else "Unknown"
                
                if drug_name in existing_drugs:
                    duplicate_count += 1
                    if duplicate_count % 5000 == 0:
                        print(f"Skipped {duplicate_count} duplicates...")
                    continue
                
                # Helper to join cols
                def get_joined_values(cols):
                    values = []
                    for c in cols:
                        val = row.get(c, '').strip()
                        if val:
                            values.append(val)
                    return ", ".join(values)

                uses = get_joined_values(use_cols)
                side_effects = get_joined_values(side_effect_cols)
                substitutes = get_joined_values(substitute_cols)
                
                # Create Medicine object
                medicine = Medicine(
                    drug_name=drug_name,
                    uses=uses,
                    side_effects=side_effects,
                    substitutes=substitutes,
                    chemical_class=row.get('Chemical Class', '').strip() or None,
                    habit_forming=row.get('Habit Forming', '').strip() or "No",
                    therapeutic_class=row.get('Therapeutic Class', '').strip() or None,
                    action_class=row.get('Action Class', '').strip() or None,
                    dosage="Consult physician", # Default
                    contraindications="Consult physician" # Default
                )
                
                medicines_to_add.append(medicine)
                existing_drugs.add(drug_name)
                count += 1
                
                # Batch Insert
                if len(medicines_to_add) >= BATCH_SIZE:
                    async with AsyncSessionLocal() as session:
                        session.add_all(medicines_to_add)
                        await session.commit()
                        print(f"Committed batch. Total added: {count}")
                        medicines_to_add = []
            
            # Insert remaining
            if medicines_to_add:
                async with AsyncSessionLocal() as session:
                    session.add_all(medicines_to_add)
                    await session.commit()
                    print(f"Committed final batch. Total added: {count}")

            print(f"Ingestion complete. Added {count} new medicines. Skipped {duplicate_count} duplicates.")
            
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(ingest_data())
