import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.models import ReimbursementScheme, SchemeType, Medicine, Base

DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Seed Medicines (to ensure categories are available)
        medicines_data = [
            Medicine(
                drug_name="Cetirizine",
                therapeutic_class="Allergy Medicines", 
                uses="Allergies, Hay fever, Urticaria",
                side_effects="Drowsiness, Dry mouth",
                substitutes="Levocetirizine",
                chemical_class="Diphenylmethylpiperazine",
                habit_forming="No",
                action_class="H1 receptor antagonist",
                dosage="Adults: 10mg once daily. Children: Consult physician.",
                contraindications="Hypersensitivity to cetirizine, Severe kidney failure"
            ),
             Medicine(
                drug_name="Paracetamol",
                therapeutic_class="Analgesics/Antipyretics",
                uses="Fever, Pain",
                side_effects="Nausea, Liver damage (high dose)",
                substitutes="Acetaminophen",
                chemical_class="Anilide",
                habit_forming="No",
                action_class="COX inhibitor",
                dosage="Adults: 500mg-1000mg every 4-6 hours. Max 4g/day.",
                contraindications="Severe liver disease, Hypersensitivity"
            ),
            Medicine(
                drug_name="Ibuprofen",
                therapeutic_class="NSAID",
                uses="Pain, Inflammation, Fever",
                side_effects="Stomach pain, Heartburn",
                substitutes="Advil, Motrin",
                chemical_class="Propionic acid derivative",
                habit_forming="No",
                action_class="COX inhibitor",
                dosage="Adults: 200mg-400mg every 4-6 hours.",
                contraindications="Active stomach ulcer, Severe heart failure, Pregnancy (3rd trimester)"
            ),
            Medicine(
                drug_name="Metformin",
                therapeutic_class="Antidiabetics",
                uses="Type 2 Diabetes",
                side_effects="Nausea, Stomach upset",
                substitutes="Glucophage",
                chemical_class="Biguanide",
                habit_forming="No",
                action_class="AMPK activator",
                dosage="Initial: 500mg once/twice daily with meals.",
                contraindications="Severe kidney disease, Metabolic acidosis"
            ),
            Medicine(
                drug_name="Atorvastatin",
                therapeutic_class="Statins",
                uses="High Cholesterol, Heart Disease Prevention",
                side_effects="Muscle pain, Liver damage",
                substitutes="Lipitor",
                chemical_class="Statin",
                habit_forming="No",
                action_class="HMG-CoA reductase inhibitor",
                dosage="10mg-80mg once daily.",
                contraindications="Active liver disease, Pregnancy, Breastfeeding"
            ),
            Medicine(
                drug_name="Amoxicillin",
                therapeutic_class="Antibiotics",
                uses="Bacterial Infections",
                side_effects="Diarrhea, Rash",
                substitutes="Amoxil",
                chemical_class="Penicillin",
                habit_forming="No",
                action_class="Cell wall synthesis inhibitor",
                dosage="250mg-500mg every 8 hours.",
                contraindications="Penicillin allergy"
            ),
            Medicine(
                drug_name="Pantoprazole",
                therapeutic_class="Proton Pump Inhibitors",
                uses="GERD, Acid Reflux",
                side_effects="Headache, Diarrhea",
                substitutes="Protonix",
                chemical_class="Benzimidazole",
                habit_forming="No",
                action_class="Proton pump inhibitor",
                dosage="40mg once daily before breakfast.",
                contraindications="Hypersensitivity, Severe liver impairment (caution)"
            ),
            Medicine(
                drug_name="Telmisartan",
                therapeutic_class="Antihypertensives",
                uses="High Blood Pressure",
                side_effects="Dizziness, Back pain",
                substitutes="Micardis",
                chemical_class="Angiotensin II receptor blocker",
                habit_forming="No",
                action_class="ARB",
                dosage="40mg-80mg once daily.",
                contraindications="Pregnancy, Biliary obstruction, Severe liver impairment"
            )
        ]
        session.add_all(medicines_data)

        schemes = [
            # Cetirizine Schemes (Matching User Request)
            ReimbursementScheme(
                drug_name="Cetirizine",
                scheme_type=SchemeType.GOVT,
                plan_name="CGHS (Central Government Health Scheme)",
                coverage_percent=100.0,
                copay_amount=0.0, 
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Cetirizine",
                scheme_type=SchemeType.GOVT,
                plan_name="ESI (Employees' State Insurance) Scheme",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Cetirizine",
                scheme_type=SchemeType.PRIVATE,
                plan_name="Max Bupa",
                coverage_percent=80.0, # Implies 20% copay
                copay_amount=0.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Cetirizine",
                scheme_type=SchemeType.PRIVATE,
                plan_name="Apollo Munich",
                coverage_percent=85.0, # Implies 15% copay
                copay_amount=0.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Cetirizine",
                scheme_type=SchemeType.PRIVATE,
                plan_name="Star Health",
                coverage_percent=75.0, # Implies 25% copay
                copay_amount=0.0,
                prior_authorization=False
            ),
            
            # Ibuprofen Schemes
            ReimbursementScheme(
                drug_name="Ibuprofen",
                scheme_type=SchemeType.GOVT,
                plan_name="Ayushman Bharat (PMJAY)",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=False
            ),
             ReimbursementScheme(
                drug_name="Ibuprofen",
                scheme_type=SchemeType.PRIVATE,
                plan_name="ICICI Lombard",
                coverage_percent=80.0,
                copay_amount=0.0,
                prior_authorization=False
            ),
            
            # Existing Data...
            # Government Schemes (Ayushman Bharat, CGHS, ECHS)
            ReimbursementScheme(
                drug_name="Paracetamol",
                scheme_type=SchemeType.GOVT,
                plan_name="Ayushman Bharat (PMJAY)",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Paracetamol",
                scheme_type=SchemeType.GOVT,
                plan_name="CGHS",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=False
            ),
             ReimbursementScheme(
                drug_name="Metformin",
                scheme_type=SchemeType.GOVT,
                plan_name="Ayushman Bharat (PMJAY)",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Metformin",
                scheme_type=SchemeType.GOVT,
                plan_name="CGHS",
                coverage_percent=90.0,
                copay_amount=50.0,
                prior_authorization=True
            ),
            ReimbursementScheme(
                drug_name="Atorvastatin",
                scheme_type=SchemeType.GOVT,
                plan_name="ECHS",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=True
            ),

            # Private Insurance (Star Health, HDFC Ergo, ICICI Lombard)
            ReimbursementScheme(
                drug_name="Paracetamol",
                scheme_type=SchemeType.PRIVATE,
                plan_name="Star Health Optima",
                coverage_percent=80.0,
                copay_amount=20.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Metformin",
                scheme_type=SchemeType.PRIVATE,
                plan_name="HDFC Ergo Health Suraksha",
                coverage_percent=75.0,
                copay_amount=100.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Atorvastatin",
                scheme_type=SchemeType.PRIVATE,
                plan_name="ICICI Lombard Complete",
                coverage_percent=70.0,
                copay_amount=150.0,
                prior_authorization=True
            ),
            ReimbursementScheme(
                drug_name="Amoxicillin",
                scheme_type=SchemeType.GOVT,
                plan_name="Ayushman Bharat (PMJAY)",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Amoxicillin",
                scheme_type=SchemeType.PRIVATE,
                plan_name="Max Bupa ReAssure",
                coverage_percent=85.0,
                copay_amount=50.0,
                prior_authorization=False
            ),
            ReimbursementScheme(
                drug_name="Pantoprazole",
                scheme_type=SchemeType.GOVT,
                plan_name="CGHS",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=False
            ),
             ReimbursementScheme(
                drug_name="Telmisartan",
                scheme_type=SchemeType.PRIVATE,
                plan_name="Tata AIG Medicare",
                coverage_percent=60.0,
                copay_amount=200.0,
                prior_authorization=True
            ),
        ]
        
        session.add_all(schemes)
        await session.commit()
        # ... (Existing manual entries maintained above) ... 
        
        # --- Synthetic Data Generation for 100+ Curated Drugs ---
        common_drugs = [
            ("Amoxycillin", "Antibiotics"), ("Azithromycin", "Antibiotics"), ("Ciprofloxacin", "Antibiotics"),
            ("Cefixime", "Antibiotics"), ("Doxycycline", "Antibiotics"), ("Ofloxacin", "Antibiotics"),
            ("Metronidazole", "Antibiotics"), ("Cephalexin", "Antibiotics"), ("Clindamycin", "Antibiotics"),
            
            ("Metformin", "Antidiabetics"), ("Glimepiride", "Antidiabetics"), ("Gliclazide", "Antidiabetics"),
            ("Sitagliptin", "Antidiabetics"), ("Vildagliptin", "Antidiabetics"), ("Insulin Glargine", "Antidiabetics"),
            ("Pioglitazone", "Antidiabetics"), ("Empagliflozin", "Antidiabetics"), ("Dapagliflozin", "Antidiabetics"),

            ("Amlodipine", "Antihypertensives"), ("Telmisartan", "Antihypertensives"), ("Losartan", "Antihypertensives"),
            ("Enalapril", "Antihypertensives"), ("Ramipril", "Antihypertensives"), ("Atenolol", "Antihypertensives"),
            ("Metoprolol", "Antihypertensives"), ("Propranolol", "Antihypertensives"), ("Bisoprolol", "Antihypertensives"),

            ("Atorvastatin", "Statins"), ("Rosuvastatin", "Statins"), ("Simvastatin", "Statins"),
            ("Fenofibrate", "Lipid Lowering"), ("Ezetimibe", "Lipid Lowering"),

            ("Pantoprazole", "Proton Pump Inhibitors"), ("Omeprazole", "Proton Pump Inhibitors"),
            ("Rabeprazole", "Proton Pump Inhibitors"), ("Esomeprazole", "Proton Pump Inhibitors"),
            ("Ranitidine", "H2 Blockers"), ("Famotidine", "H2 Blockers"), ("Domperidone", "Antiemetics"),
            ("Ondansetron", "Antiemetics"),

            ("Ibuprofen", "NSAID"), ("Diclofenac", "NSAID"), ("Aceclofenac", "NSAID"),
            ("Naproxen", "NSAID"), ("Etoricoxib", "NSAID"), ("Piroxicam", "NSAID"),
            ("Tramadol", "Analgesics"), ("Paracetamol", "Analgesics"),

            ("Cetirizine", "Antihistamines"), ("Levocetirizine", "Antihistamines"), ("Loratadine", "Antihistamines"),
            ("Fexofenadine", "Antihistamines"), ("Montelukast", "Antiasthmatics"), ("Salbutamol", "Bronchodilators"),
            ("Budesonide", "Corticosteroids"), ("Fluticasone", "Corticosteroids"),

            ("Alprazolam", "Anxiolytics"), ("Clonazepam", "Anxiolytics"), ("Lorazepam", "Anxiolytics"),
            ("Escitalopram", "Antidepressants"), ("Sertraline", "Antidepressants"), ("Fluoxetine", "Antidepressants"),

            ("Thyroxine", "Hormones"), ("Carbimazole", "Antithyroid"),
            ("Sildenafil", "Urology"), ("Tadalafil", "Urology"), ("Tamsulosin", "Urology"),

            ("Calcium Carbonate", "Supplements"), ("Vitamin D3", "Supplements"), ("Iron Folic Acid", "Supplements"),
            ("Methylcobalamin", "Supplements"), ("Multivitamins", "Supplements"),
            
            # Additional common drugs to reach 100+
            ("Aspirin", "Antiplatelets"), ("Clopidogrel", "Antiplatelets"), ("Warfarin", "Anticoagulants"),
            ("Heparin", "Anticoagulants"), ("Digoxin", "Cardiac Glycosides"), 
            ("Nitroglycerin", "Antianginal"), ("Isosorbide Mononitrate", "Antianginal"),
            ("Furosemide", "Diuretics"), ("Torsemide", "Diuretics"), ("Spironolactone", "Diuretics"),
            ("Hydrochlorothiazide", "Diuretics"), ("Chlorthalidone", "Diuretics"),
            ("Prednisolone", "Corticosteroids"), ("Methylprednisolone", "Corticosteroids"), ("Dexamethasone", "Corticosteroids"),
            ("Methotrexate", "Antimetabolites"), ("Hydroxychloroquine", "DMARDs"),
            ("Allopurinol", "Gout"), ("Febuxostat", "Gout"),
            ("Gabapentin", "Anticonvulsants"), ("Pregabalin", "Anticonvulsants"), ("Levetiracetam", "Anticonvulsants"),
            ("Phenytoin", "Anticonvulsants"), ("Carbamazepine", "Anticonvulsants"), ("Sodium Valproate", "Anticonvulsants"),
            ("Amitriptyline", "Tricyclic Antidepressants"), ("Duloxetine", "SNRI"),
            ("Quetiapine", "Antipsychotics"), ("Olanzapine", "Antipsychotics"), ("Risperidone", "Antipsychotics"),
            ("Levothyroxine", "Thyroid Hormones"),
            ("Dicyclomine", "Antispasmodics"), ("Drotaverine", "Antispasmodics"),
            ("Loperamide", "Antidiarrheals"), ("Lactulose", "Laxatives"), ("Bisacodyl", "Laxatives")
        ]

        # Use a set to track added drugs to avoid duplicates with manual entries
        existing_drug_names = {m.drug_name for m in medicines_data}

        import random

        for drug, category in common_drugs:
            if drug in existing_drug_names:
                continue
            
            # Add Medicine
            medicines_data.append(Medicine(
                drug_name=drug,
                therapeutic_class=category,
                uses=f"Common treatment for conditions related to {category}.",
                side_effects="Nausea, Dizziness, Headache (Common). Consult doctor for details.",
                substitutes="Generic equivalents available.",
                chemical_class="Variable",
                habit_forming="No",
                action_class="Therapeutic agent",
                dosage="Standard adult dosage. Consult physician for specifics.",
                contraindications="Hypersensitivity, specific conditions apply."
            ))
            existing_drug_names.add(drug)

            # Add Schemes (1 Govt, 1-2 Private)
            # Govt
            schemes.append(ReimbursementScheme(
                drug_name=drug,
                scheme_type=SchemeType.GOVT,
                plan_name="Ayushman Bharat (PMJAY)" if random.choice([True, False]) else "CGHS",
                coverage_percent=100.0,
                copay_amount=0.0,
                prior_authorization=random.choice([True, False])
            ))

            # Private 1
            insurer = random.choice(["Star Health", "HDFC Ergo", "Max Bupa", "ICICI Lombard", "Apollo Munich"])
            schemes.append(ReimbursementScheme(
                drug_name=drug,
                scheme_type=SchemeType.PRIVATE,
                plan_name=insurer,
                coverage_percent=random.choice([70.0, 80.0, 85.0, 90.0]),
                copay_amount=random.choice([0.0, 50.0, 100.0]),
                prior_authorization=False
            ))

             # Private 2 (Optional)
            if random.random() > 0.5:
                insurer2 = random.choice(["Tata AIG", "Bajaj Allianz", "Niva Bupa"])
                schemes.append(ReimbursementScheme(
                    drug_name=drug,
                    scheme_type=SchemeType.PRIVATE,
                    plan_name=insurer2,
                    coverage_percent=random.choice([60.0, 75.0, 80.0]),
                    copay_amount=random.choice([0.0, 200.0]),
                    prior_authorization=True
                ))

        session.add_all(medicines_data)
        session.add_all(schemes)
        await session.commit()
        print(f"Data seeded successfully! Added {len(medicines_data)} medicines and {len(schemes)} schemes.")


if __name__ == "__main__":
    asyncio.run(seed_data())
