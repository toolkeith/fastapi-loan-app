from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True) # For Login
    # Registration fields
    firstname = Column(String(50))
    lastname = Column(String(50))
    age = Column(Integer)
    address = Column(String(255))
    monthly_income = Column(Float)

    # Relationship to Loans
    loans = relationship("Loan", back_populates="owner")

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    term_months = Column(Integer)
    status = Column(String(20), default="Pending")
    
    # Link back to the User
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="loans")
