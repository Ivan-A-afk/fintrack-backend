from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.sql import func
from database import Base

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(10), default='💳')

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    commerce = Column(String(200))
    description = Column(Text)
    date = Column(TIMESTAMP, server_default=func.now())
    image_path = Column(Text)