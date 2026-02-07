from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, Text
from core.database import Base
import enum

class SchemeType(str, enum.Enum):
    GOVT = "GOVT"
    PRIVATE = "PRIVATE"

class ReimbursementScheme(Base):
    __tablename__ = "reimbursement_schemes"

    id = Column(Integer, primary_key=True, index=True)
    drug_name = Column(String, index=True)
    scheme_type = Column(Enum(SchemeType))
    plan_name = Column(String)
    coverage_percent = Column(Float)
    copay_amount = Column(Float)
    prior_authorization = Column(Boolean, default=False)

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True)
    drug_name = Column(String, index=True)
    substitutes = Column(Text)
    side_effects = Column(Text)
    uses = Column(Text)
    chemical_class = Column(String)
    habit_forming = Column(String)
    therapeutic_class = Column(String)
    action_class = Column(String)
    dosage = Column(Text)
    contraindications = Column(Text)
