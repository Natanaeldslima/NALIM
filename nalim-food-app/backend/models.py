import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cnpj = Column(String(20), nullable=True)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    usuarios = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    insumos = relationship("Insumo", back_populates="tenant", cascade="all, delete-orphan")
    produtos = relationship("Produto", back_populates="tenant", cascade="all, delete-orphan")
    pedidos = relationship("Pedido", back_populates="tenant", cascade="all, delete-orphan")
    custos_fixos = relationship("CustoFixo", back_populates="tenant", cascade="all, delete-orphan")
    fechamentos = relationship("FechamentoCaixa", back_populates="tenant", cascade="all, delete-orphan")
    configuracoes = relationship("ConfiguracaoEmpresa", back_populates="tenant", uselist=False, cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="operador")  # 'dono', 'gerente', 'operador'
    ativo = Column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="usuarios")

class Insumo(Base):
    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    codigo = Column(String(20), index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50), default="Geral")
    preco_compra = Column(Float, default=0.0)
    und_compra = Column(String(20), default="kg")
    und_uso = Column(String(20), default="g")
    fator_conversao = Column(Float, default=1000.0)
    custo_unitario = Column(Float, default=0.0)  # preco_compra / fator_conversao
    preco_venda_extra = Column(Float, default=0.0)  # Preço se vendido como adicional

    tenant = relationship("Tenant", back_populates="insumos")
    ficha_itens = relationship("FichaTecnicaItem", back_populates="insumo")

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    codigo = Column(String(20), index=True, nullable=False)
    nome = Column(String(100), nullable=False)
    categoria = Column(String(50), default="Hambúrguer")
    descricao = Column(Text, nullable=True)
    preco_salao = Column(Float, default=0.0)
    preco_ifood = Column(Float, default=0.0)
    ativo = Column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="produtos")
    ficha_tecnica = relationship("FichaTecnicaItem", back_populates="produto", cascade="all, delete-orphan")

class FichaTecnicaItem(Base):
    __tablename__ = "ficha_tecnica_itens"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    insumo_id = Column(Integer, ForeignKey("insumos.id"), nullable=False)
    quantidade = Column(Float, default=1.0)

    produto = relationship("Produto", back_populates="ficha_tecnica")
    insumo = relationship("Insumo", back_populates="ficha_itens")

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    numero_comanda = Column(Integer, index=True)
    data_hora = Column(DateTime, default=datetime.datetime.utcnow)
    canal = Column(String(30), default="Salão")  # Salão, Balcão, iFood
    identificacao = Column(String(100), default="Balcão")
    ifood_order_id = Column(String(50), nullable=True)
    ifood_cliente = Column(String(100), nullable=True)
    forma_pagto = Column(String(30), default="PIX")
    
    # Valores financeiros calculados
    valor_bruto = Column(Float, default=0.0)
    cmv_total = Column(Float, default=0.0)
    taxa_canal = Column(Float, default=0.0)
    lucro_liquido = Column(Float, default=0.0)

    # Status operacional KDS
    status_kds = Column(String(30), default="Na Chapa")  # 'Na Chapa', 'Pronto', 'Entregue'

    tenant = relationship("Tenant", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    nome_produto = Column(String(100), nullable=False)
    quantidade = Column(Integer, default=1)
    preco_unitario = Column(Float, default=0.0)
    cmv_unitario = Column(Float, default=0.0)
    modificacoes = Column(Text, nullable=True)  # ex: 'SEM Cebola • + EXTRA: Bacon'

    pedido = relationship("Pedido", back_populates="itens")

class CustoFixo(Base):
    __tablename__ = "custos_fixos"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    mes_vigencia = Column(String(7), index=True, default="2026-08")  # Formato 'YYYY-MM'
    categoria = Column(String(50), nullable=False)
    fornecedor = Column(String(100), nullable=False)
    valor = Column(Float, default=0.0)

    tenant = relationship("Tenant", back_populates="custos_fixos")

class FechamentoCaixa(Base):
    __tablename__ = "fechamentos_caixa"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    data_turno = Column(String(10), index=True, default="2026-08-31")
    faturamento_total = Column(Float, default=0.0)
    total_pedidos = Column(Integer, default=0)
    pix = Column(Float, default=0.0)
    cartao = Column(Float, default=0.0)
    dinheiro = Column(Float, default=0.0)
    perdas_descartes = Column(Float, default=0.0)
    diferenca = Column(Float, default=0.0)
    status_conferencia = Column(String(30), default="BATEU 100%")

    tenant = relationship("Tenant", back_populates="fechamentos")

class ConfiguracaoEmpresa(Base):
    __tablename__ = "configuracoes_empresa"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), unique=True, nullable=False)
    regime_tributario = Column(String(20), default="ME_6")  # 'MEI' ou 'ME_6'
    dias_trabalhados_mes = Column(Integer, default=26)
    meta_lucro_desejada = Column(Float, default=3000.0)
    aliquota_ifood = Column(Float, default=0.23)

    tenant = relationship("Tenant", back_populates="configuracoes")
