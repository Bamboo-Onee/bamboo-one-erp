"""Modelos ORM Relacionais Compartilhados para todos os Módulos do Sistema Grupo Bamboo.

Mapeamento de persistência assíncrona SQLAlchemy 2.0 para:
- Compras Nacionais & Itens
- Importações Internacionais & Landed Cost
- Estoque, Saldos por Depósito e Movimentações
- Vendas / Comercial & Itens
- Produção & Entregas (Romaneios)
- Financeiro (Contas a Pagar e Contas a Receber)
- Recursos Humanos (Funcionários e Cargos)
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from src.core.database import Base


# ==============================================================================
# COMPRAS NACIONAIS
# ==============================================================================
class PurchaseOrderORM(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_name = Column(String(200), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="Rascunho")  # Rascunho, Enviado, Parcial, Recebido
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("PurchaseOrderItemORM", back_populates="order", cascade="all, delete-orphan")


class PurchaseOrderItemORM(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_sku = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0.0)
    total_price = Column(Float, nullable=False, default=0.0)

    order = relationship("PurchaseOrderORM", back_populates="items")


# ==============================================================================
# IMPORTAÇÕES INTERNACIONAIS
# ==============================================================================
class ImportProcessORM(Base):
    __tablename__ = "import_processes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    process_number = Column(String(50), unique=True, nullable=False, index=True)  # ex: IMP-2026-041
    supplier_name = Column(String(200), nullable=False)
    bl_number = Column(String(100), nullable=True)
    container_number = Column(String(50), nullable=True)
    origin_port = Column(String(100), nullable=False, default="Shanghai (CNSHA)")
    destination_port = Column(String(100), nullable=False, default="Santos (BRSSZ)")
    status = Column(String(50), nullable=False, default="Em trânsito")  # Em trânsito, Desembaraço, Concluído
    eta = Column(String(50), nullable=True)
    total_usd = Column(Float, nullable=False, default=0.0)
    landed_cost_brl = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==============================================================================
# ESTOQUE & RASTREABILIDADE
# ==============================================================================
class StockBalanceORM(Base):
    __tablename__ = "stock_balances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_sku = Column(String(50), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    warehouse_name = Column(String(100), nullable=False, default="CD Principal")
    quantity_available = Column(Integer, nullable=False, default=0)
    quantity_reserved = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StockMovementORM(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movement_number = Column(String(50), unique=True, nullable=False)
    movement_type = Column(String(50), nullable=False)  # Entrada, Saída, Transferência, Ajuste
    product_sku = Column(String(50), nullable=False)
    warehouse_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)
    user_name = Column(String(100), nullable=False, default="Operador")
    created_at = Column(DateTime, default=datetime.utcnow)


# ==============================================================================
# COMERCIAL & VENDAS
# ==============================================================================
class SalesOrderORM(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    representative_name = Column(String(100), nullable=True, default="Vendas Diretas")
    total_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="Confirmado")  # Orçamento, Confirmado, Separação, Expedido, Entregue
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("SalesOrderItemORM", back_populates="order", cascade="all, delete-orphan")


class SalesOrderItemORM(Base):
    __tablename__ = "sales_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    product_sku = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0.0)
    total_price = Column(Float, nullable=False, default=0.0)

    order = relationship("SalesOrderORM", back_populates="items")


# ==============================================================================
# PRODUÇÃO & EXPEDIÇÃO / ENTREGAS
# ==============================================================================
class DeliveryORM(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_number = Column(String(50), unique=True, nullable=False, index=True)  # ex: ENT-00618
    customer_name = Column(String(200), nullable=False)
    destination_city = Column(String(100), nullable=False)
    total_volumes = Column(Integer, nullable=False, default=1)
    vehicle_plate = Column(String(20), nullable=True)
    status = Column(String(50), nullable=False, default="Carga pronta")  # Pendente, Carga pronta, Em rota, Entregue
    created_at = Column(DateTime, default=datetime.utcnow)


# ==============================================================================
# FINANCEIRO (CONTAS A PAGAR E CONTAS A RECEBER)
# ==============================================================================
class FinancialEntryORM(Base):
    __tablename__ = "financial_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_type = Column(String(20), nullable=False)  # PAGAR ou RECEBER
    description = Column(String(200), nullable=False)
    entity_name = Column(String(200), nullable=False)  # Fornecedor ou Cliente
    category = Column(String(100), nullable=False, default="Operacional")
    amount = Column(Float, nullable=False)
    due_date = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="Pendente")  # Pendente, Liquidado, Cancelado
    created_at = Column(DateTime, default=datetime.utcnow)


# ==============================================================================
# RECURSOS HUMANOS (RH)
# ==============================================================================
class EmployeeORM(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    cpf = Column(String(20), unique=True, nullable=False)
    role = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    salary = Column(Float, nullable=False, default=0.0)
    admission_date = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="Ativo")  # Ativo, Férias, Inativo


# ==============================================================================
# AUTENTICAÇÃO & CONTROLE DE ACESSO (RBAC)
# ==============================================================================
class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="LOGISTICA")  # ADMIN, LOGISTICA, VENDAS, COMPRAS, FINANCEIRO
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

