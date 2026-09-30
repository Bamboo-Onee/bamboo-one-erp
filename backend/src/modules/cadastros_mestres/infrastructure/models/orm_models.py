"""Modelos ORM do SQLAlchemy 2.0 para persistência de Cadastros Mestres."""

from sqlalchemy import Boolean, Column, Float, Integer, String, Text
from src.core.database import Base


class ProductORM(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, default="Geral")
    price = Column(Float, nullable=False, default=0.0)
    weight_kg = Column(Float, nullable=False)
    length_m = Column(Float, nullable=False)
    width_m = Column(Float, nullable=False)
    height_m = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    stackable = Column(Boolean, default=True)
    max_stack_layers = Column(Integer, default=2)
    can_rotate = Column(Boolean, default=True)
    fragile = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class CustomerORM(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    document = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=False)
    delivery_address = Column(String(300), nullable=False)
    credit_limit = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)


class VehicleORM(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plate = Column(String(20), unique=True, nullable=False, index=True)
    model = Column(String(100), nullable=False)
    body_type = Column(String(50), nullable=False, default="Baú")
    length_m = Column(Float, nullable=False)
    width_m = Column(Float, nullable=False)
    height_m = Column(Float, nullable=False)
    max_payload_kg = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
