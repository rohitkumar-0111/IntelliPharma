import asyncio
from sqlalchemy import select, update
from core.database import AsyncSessionLocal
from models.models import Medicine

# High-quality curated data for common drugs
# This replaces generic placeholders from seed_db or CSV defaults
CURATED_DATA = [
    {
        "drug_name": "Vildagliptin",
        "uses": "Type 2 Diabetes Mellitus (used alone or with other drugs)",
        "dosage": "50 mg twice daily when used with metformin or as monotherapy. 50 mg once daily in morning when used with sulphonylurea.",
        "contraindications": "Hypersensitivity to vildagliptin, Diabetic ketoacidosis, Severe liver impairment, Heart failure (NYHA Class IV).",
        "side_effects": "Dizziness, Headache, Tremors (hypoglycemia), Nausea, Hyperhidrosis",
        "therapeutic_class": "Antidiabetics",
        "action_class": "DPP-4 Inhibitor",
        "chemical_class": "Cyanopyrrolidine"
    },
    {
        "drug_name": "Sitagliptin",
        "uses": "Type 2 Diabetes Mellitus",
        "dosage": "100 mg once daily. Adjust for renal impairment: 50 mg (CrCl 30-45) or 25 mg (CrCl <30).",
        "contraindications": "History of serious hypersensitivity reaction (angioedema, anaphylaxis), Pancreatitis history.",
        "side_effects": "Stuffy/runny nose, Sore throat, Headache, Joint pain, Acute pancreatitis (rare)",
        "therapeutic_class": "Antidiabetics",
        "action_class": "DPP-4 Inhibitor",
        "chemical_class": "Beta-amino acid derivative"
    },
    {
        "drug_name": "Metformin",
        "uses": "Type 2 Diabetes, PCOS",
        "dosage": "Initial: 500mg once/twice daily with meals. Maintenance: 850-1000mg twice daily. Max: 2550mg/day.",
        "contraindications": "eGFR < 30 mL/min, Metabolic acidosis, Severe liver disease, Alcoholism.",
        "side_effects": "Nausea, Diarrhea, Abdominal pain, B12 deficiency, Lactic acidosis (rare but serious)",
        "therapeutic_class": "Antidiabetics",
        "action_class": "Biguanide",
        "chemical_class": "Biguanide"
    },
    {
        "drug_name": "Paracetamol",
        "uses": "Fever (Antipyretic), Mild to moderate pain (Analgesic)",
        "dosage": "Adults: 500-1000mg every 4-6 hours. Max 4g/day. Children: 10-15mg/kg every 4-6 hours.",
        "contraindications": "Severe hepatic insufficiency, Hypersensitivity.",
        "side_effects": "Generally well tolerated. Rare: Skin rash, Blood disorders. Liver damage in overdose.",
        "therapeutic_class": "Analgesics/Antipyretics",
        "action_class": "COX Inhibitor (Central)",
        "chemical_class": "Para-aminophenol derivative"
    },
    {
        "drug_name": "Ibuprofen",
        "uses": "Pain, Inflammation, Fever, Dysmenorrhea, Arthritis",
        "dosage": "Adults: 200-400mg every 4-6 hours up to 1200mg/day (OTC) or 3200mg/day (Rx). Take with food.",
        "contraindications": "Active peptic ulcer, GI bleeding, Severe heart failure, History of NSAID-induced asthma.",
        "side_effects": "Epigastric pain, Nausea, Heartburn, GI bleeding, Hypertension, Kidney impairment",
        "therapeutic_class": "NSAID",
        "action_class": "Non-selective COX inhibitor",
        "chemical_class": "Propionic acid derivative"
    },
    {
        "drug_name": "Cetirizine",
        "uses": "Allergic rhinitis, Urticaria (Hives), Itching",
        "dosage": "Adults: 10mg once daily. Children (6-12): 5mg twice daily or 10mg once daily.",
        "contraindications": "Hypersensitivity to cetirizine/hydroxyzine, Severe renal impairment (CrCl < 10).",
        "side_effects": "Drowsiness, Fatigue, Dry mouth, Headache",
        "therapeutic_class": "Antihistamines",
        "action_class": "H1 Receptor Antagonist (Second Gen)",
        "chemical_class": "Piperazine derivative"
    },
    {
        "drug_name": "Amoxicillin",
        "uses": "Bacterial infections (ENT, Respiratory, UTI, Skin)",
        "dosage": "Adults: 250-500mg every 8 hours or 500-875mg every 12 hours.",
        "contraindications": "History of Penicillin allergy.",
        "side_effects": "Diarrhea, Nausea, Skin rash. Stop if allergic reaction occurs.",
        "therapeutic_class": "Antibiotics",
        "action_class": "Cell wall synthesis inhibitor",
        "chemical_class": "Penicillin (Aminopenicillin)"
    },
     {
        "drug_name": "Azithromycin",
        "uses": "Respiratory infections, Skin infections, STD (Chlamydia)",
        "dosage": "500mg once daily for 3 days OR 500mg Day 1 then 250mg Days 2-5.",
        "contraindications": "Hypersensitivity to macrolides, History of cholestatic jaundice/hepatic dysfunction.",
        "side_effects": "Diarrhea, Abdominal pain, Nausea, QT prolongation",
        "therapeutic_class": "Antibiotics",
        "action_class": "Protein synthesis inhibitor (50S subunit)",
        "chemical_class": "Macrolide"
    },
    {
        "drug_name": "Pantoprazole",
        "uses": "GERD, Erosive Esophagitis, Zollinger-Ellison Syndrome",
        "dosage": "40mg once daily, preferably 30 mins before breakfast.",
        "contraindications": "Hypersensitivity to PPIs.",
        "side_effects": "Headache, Diarrhea, Abdominal pain, Flatulence. Long term: Bone fracture risk, B12 deficiency.",
        "therapeutic_class": "Proton Pump Inhibitors",
        "action_class": "Proton pump inhibitor",
        "chemical_class": "Substituted Benzimidazole"
    },
    {
        "drug_name": "Atorvastatin",
        "uses": "Hyperlipidemia, Prevention of Cardiovascular Disease",
        "dosage": "10mg to 80mg once daily, any time of day.",
        "contraindications": "Active liver disease, Unexplained persistent elevation of transaminases, Pregnancy, Lactation.",
        "side_effects": "Myopathy (muscle pain), Diarrhea, Nausea, Liver enzyme elevation",
        "therapeutic_class": "Statins (Lipid Lowering)",
        "action_class": "HMG-CoA Reductase Inhibitor",
        "chemical_class": "Stains"
    },
    {
        "drug_name": "Telmisartan",
        "uses": "Hypertension, Cardiovascular risk reduction",
        "dosage": "40mg to 80mg once daily.",
        "contraindications": "Pregnancy (Cat D), Biliary obstruction, Severe hepatic impairment, Concomitant use with aliskiren in diabetes.",
        "side_effects": "Dizziness, Back pain, Sinusitis, Diarrhea, Hyperkalemia",
        "therapeutic_class": "Antihypertensives",
        "action_class": "Angiotensin II Receptor Blocker (ARB)",
        "chemical_class": "Benzimidazole derivative"
    }
]

async def enrich_data():
    print("Starting data enrichment...")
    async with AsyncSessionLocal() as session:
        count = 0
        for data in CURATED_DATA:
            drug_name = data["drug_name"]
            print(f"Updating {drug_name}...")
            
            stmt = select(Medicine).where(Medicine.drug_name.ilike(drug_name))
            result = await session.execute(stmt)
            medicine = result.scalars().first()
            
            if medicine:
                # Update attributes
                medicine.uses = data["uses"]
                medicine.dosage = data["dosage"]
                medicine.contraindications = data["contraindications"]
                medicine.side_effects = data["side_effects"]
                medicine.therapeutic_class = data["therapeutic_class"]
                medicine.action_class = data["action_class"]
                medicine.chemical_class = data["chemical_class"]
                count += 1
            else:
                # If seed_db was skipped or something, insert? 
                # For now just print warning, as ingest_data likely handled it or seed_db handled it
                print(f"Warning: {drug_name} not found in DB!")
                
        await session.commit()
        print(f"Enrichment complete. Updated {count} common medicines with premium data.")

if __name__ == "__main__":
    asyncio.run(enrich_data())
