
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Plan(Base):
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    old_id = Column(String, unique=True)  # Keep the old string ID for reference
    short_name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    summary_of_benefits = Column(Text)
    summary_of_benefits_url = Column(Text)
    compressed_summary = Column(Text)
    
    # New optional columns
    plan_type = Column(Text)  # Medicare, Medicaid, Dual Eligible, or Marketplace
    plan_document_full_text = Column(Text)  # Full text of the plan document
    summary_of_benefit_coverage = Column(Text)  # Summary of benefit coverage (SBC)
    table_of_contents = Column(Text)  # Table of contents for the plan document
    document_type = Column(String(20))  # 'pdf' or 'website' - indicates the type of document linked

    def __repr__(self):
        return f"<Plan(id={self.id}, short_name='{self.short_name}', full_name='{self.full_name}', plan_type='{self.plan_type}')>"
