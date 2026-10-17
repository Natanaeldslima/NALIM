from typing import List, Optional
from pydantic import BaseModel

# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    nome: str
    tenant_slug: str

class LoginRequest(BaseModel):
    email: str
    senha: str

class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    role: str

# Insumos Schemas
class InsumoBase(BaseModel):
    codigo: str
    nome: str
    categoria: str = "Geral"
    preco_compra: float
    und_compra: str = "kg"
    und_uso: str = "g"
    fator_conversao: float = 1000.0
    custo_unitario: float
    preco_venda_extra: float = 0.0

class InsumoCreate(InsumoBase):
    pass

class InsumoResponse(InsumoBase):
    id: int
    class Config:
        from_attributes = True

# Ficha Técnica e Produtos
class FichaItemCreate(BaseModel):
    insumo_id: int
    quantidade: float

class FichaItemResponse(BaseModel):
    insumo_id: int
    insumo_nome: str
    insumo_und: str
    quantidade: float
    custo_unitario: float
    custo_total: float

class ProdutoCreate(BaseModel):
    codigo: str
    nome: str
    categoria: str = "Hambúrguer"
    descricao: Optional[str] = None
    preco_salao: float
    preco_ifood: float
    ingredientes: List[FichaItemCreate] = []

class ProdutoResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    categoria: str
    descricao: Optional[str]
    preco_salao: float
    preco_ifood: float
    cmv_estimado: float
    margem_salao_pct: float
    margem_ifood_pct: float
    ingredientes: List[FichaItemResponse] = []
    class Config:
        from_attributes = True

# Pedidos e PDV
class ItemPedidoInput(BaseModel):
    produto_codigo: str
    nome: Optional[str] = None
    quantidade: int = 1
    modificacoes: Optional[str] = None
    preco_unitario: float = 0.0

class PedidoCreate(BaseModel):
    canal: str = "Salão"  # Salão, Balcão, iFood
    identificacao: Optional[str] = "Balcão"
    solicitante: Optional[str] = "Balcão"
    ifood_order_id: Optional[str] = None
    ifood_cliente: Optional[str] = None
    forma_pagto: str = "PIX"
    itens: List[ItemPedidoInput]

class PedidoResponse(BaseModel):
    id: int
    numero_comanda: int
    data_hora: str
    canal: str
    identificacao: str
    forma_pagto: str
    valor_bruto: float
    status_kds: str
    # Métricas restritas para gerente/dono:
    cmv_total: Optional[float] = None
    taxa_canal: Optional[float] = None
    lucro_liquido: Optional[float] = None
    itens_desc: List[str] = []
    class Config:
        from_attributes = True

# KDS Cozinha
class KdsUpdateStatus(BaseModel):
    status_kds: str  # 'Na Chapa', 'Pronto', 'Entregue'

# Custos Fixos
class CustoFixoCreate(BaseModel):
    mes_vigencia: str = "2026-08"
    categoria: str
    fornecedor: str
    valor: float
    data_vencimento: Optional[str] = None
    dia_vencimento: Optional[int] = None
    encaminhar_previsao: Optional[bool] = True

class CustoFixoResponse(BaseModel):
    id: int
    mes_vigencia: str
    categoria: str
    fornecedor: str
    valor: float
    data_vencimento: Optional[str] = None
    dia_vencimento: Optional[int] = None
    encaminhar_previsao: Optional[bool] = True
    class Config:
        from_attributes = True

# Fechamento de Caixa
class FechamentoCaixaCreate(BaseModel):
    data_turno: str
    faturamento_total: float
    total_pedidos: int
    pix: float
    cartao: float
    dinheiro: float
    perdas_descartes: float = 0.0

class FechamentoCaixaResponse(BaseModel):
    id: int
    data_turno: str
    faturamento_total: float
    total_pedidos: int
    diferenca: float
    status_conferencia: str
    class Config:
        from_attributes = True

# DRE & Saúde Gerencial
class DreResponse(BaseModel):
    mes_vigencia: str
    regime_tributario: str
    receita_bruta: float
    deducoes_impostos: float
    taxas_canais_ifood: float
    receita_liquida: float
    cmv_total: float
    lucro_bruto: float
    margem_bruta_pct: float
    custos_fixos_total: float
    total_perdas: float = 0.0
    resultado_liquido: float
    margem_liquida_pct: float
    ponto_equilibrio_mensal: float
    ponto_equilibrio_diario: float
    score_saude_nalim: float
    classificacao_saude: str

# Perdas & Desperdício
class PerdaItemCreate(BaseModel):
    data: Optional[str] = None
    item_nome: str
    quantidade: float = 1.0
    custo_unitario: float = 0.0
    motivo: str = "descarte"  # validade, erro_cozinha, descarte, avaria
    observacao: Optional[str] = None

class PerdaItemResponse(BaseModel):
    id: int
    data: str
    item_nome: str
    quantidade: float
    custo_unitario: float
    motivo: str
    observacao: Optional[str] = None
    custo_total: float
    class Config:
        from_attributes = True
# Mesas & Comandas
class ItemMesaInput(BaseModel):
    produto_codigo: str
    nome: Optional[str] = None
    quantidade: int = 1
    preco_unitario: float = 0.0
    modificacoes: Optional[str] = None

class AdicionarItensMesaInput(BaseModel):
    solicitante: Optional[str] = "Garçom"
    itens: List[ItemMesaInput]

class FecharMesaRequest(BaseModel):
    forma_pagto: str = "PIX"
    parcelas: int = 1
    taxa_aplicada: float = 0.0
    valor_total_pago: float
    solicitante: Optional[str] = None
    vendedor: Optional[str] = None

class ConfigTaxasCartaoInput(BaseModel):
    taxa_debito: float = 1.99
    taxa_credito_vista: float = 3.49
    taxa_credito_parcelado: float = 4.99
    repassar_taxa_cartao: bool = False

class ConfigTaxasCartaoResponse(BaseModel):
    taxa_debito: float
    taxa_credito_vista: float
    taxa_credito_parcelado: float
    repassar_taxa_cartao: bool