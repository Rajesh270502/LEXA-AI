from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

class ExtractedClause(Base):
    __tablename__ = "extracted_clauses"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    effective_date = Column(String, nullable=True)
    expiry_date = Column(String, nullable=True)
    payment_terms = Column(Text, nullable=True)
    termination_clause = Column(Text, nullable=True)
    confidentiality_clause = Column(Text, nullable=True)
    governing_law = Column(String, nullable=True)

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    risk_score = Column(Integer, nullable=False)
    high_risks = Column(Text, nullable=True)
    medium_risks = Column(Text, nullable=True)
    low_risks = Column(Text, nullable=True)