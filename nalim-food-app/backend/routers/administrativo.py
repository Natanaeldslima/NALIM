from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Insumo, Produto, FichaTecnicaItem, Pedido, CustoFixo
from schemas import (
    InsumoCreate, InsumoResponse, 
    ProdutoCreate, ProdutoResponse, 
    CustoFixoCreate, CustoFixoResponse
)
from auth import require_role

router = APIRouter(prefix="/api/admin", tags=["Administrativo (Insumos, Fichas Técnicas & Custos)"])

# 1. Insumos CRUD
@router.get("/insumos", response_model=List[InsumoResponse])
def listar_insumos(
    categoria: Optional[str] = None,
    current_user: User = Depends(require_role(["gerente", "dono"])),
    db: Session = Depends(get_db)
):
    query = db.query(Insumo).filter(Insumo.tenant_id == current_user.tenant_id)
    if categoria:
        query = query.filter(Insumo.categoria == categoria)
    return query.order_by(Insumo.nome.asc()).all()

@router.post("/insumos", response_model=InsumoResponse)
def criar_insumo(
    dados: InsumoCreate,
    current_user: User = Depends(require_role(["gerente", "dono"])),
    db: Session = Depends(get_db)
):
    custo_unit = dados.preco_compra / (dados.fator_conversao if dados.fator_conversao > 0 else 1.0)
    novo_insumo = Insumo(
        tenant_id=current_user.tenant_id,
        codigo=dados.codigo,
        nome=dados.nome,
        categoria=dados.categoria,
        preco_compra=dados.preco_compra,
        und_compra=dados.und_compra,
        und_uso=dados.und_uso,
        fator_conversao=dados.fator_conversao,
        custo_unitario=custo_unit,
        preco_venda_extra=dados.preco_venda_extra
    )
    db.add(novo_insumo)
    db.commit()
    db.refresh(novo_insumo)
    return novo_insumo

# 2. Produtos & Fichas Técnicas (com cálculo de CMV e Margens)
@router.get("/produtos", response_model=List[ProdutoResponse])
def listar_produtos(
    current_user: User = Depends(require_role(["gerente", "dono"])),
    db: Session = Depends(get_db)
):
    prods = db.query(Produto).filter(
        Produto.tenant_id == current_user.tenant_id,
        Produto.ativo == True
    ).order_by(Produto.nome.asc()).all()

    resultado = []
    for p in prods:
        cmv_calc = 0.0
        ingredientes_resp = []
        for ft in p.ficha_tecnica:
            if ft.insumo:
                custo_total_item = ft.quantidade * ft.insumo.custo_unitario
                cmv_calc += custo_total_item
                ingredientes_resp.append({
                    "insumo_id": ft.insumo.id,
                    "insumo_nome": ft.insumo.nome,
                    "insumo_und": ft.insumo.und_uso,
                    "quantidade": ft.quantidade,
                    "custo_unitario": ft.insumo.custo_unitario,
                    "custo_total": custo_total_item
                })

        margem_salao = ((p.preco_salao - cmv_calc) / p.preco_salao * 100) if p.preco_salao > 0 else 0.0
        taxa_ifood = p.preco_ifood * 0.23
        margem_ifood = ((p.preco_ifood - cmv_calc - taxa_ifood) / p.preco_ifood * 100) if p.preco_ifood > 0 else 0.0

        resultado.append({
            "id": p.id,
            "codigo": p.codigo,
            "nome": p.nome,
            "categoria": p.categoria,
            "descricao": p.descricao,
            "preco_salao": p.preco_salao,
            "preco_ifood": p.preco_ifood,
            "cmv_estimado": round(cmv_calc, 2),
            "margem_salao_pct": round(margem_salao, 1),
            "margem_ifood_pct": round(margem_ifood, 1),
            "ingredientes": ingredientes_resp
        })

    return resultado

@router.post("/produtos")
def criar_produto_com_ficha(
    dados: ProdutoCreate,
    current_user: User = Depends(require_role(["gerente", "dono"])),
    db: Session = Depends(get_db)
):
    novo_prod = Produto(
        tenant_id=current_user.tenant_id,
        codigo=dados.codigo,
        nome=dados.nome,
        categoria=dados.categoria,
        descricao=dados.descricao,
        preco_salao=dados.preco_salao,
        preco_ifood=dados.preco_ifood,
        ativo=True
    )
    db.add(novo_prod)
    db.flush()

    for item in dados.ingredientes:
        db.add(FichaTecnicaItem(
            produto_id=novo_prod.id,
            insumo_id=item.insumo_id,
            quantidade=item.quantidade
        ))

    db.commit()
    return {"sucesso": True, "produto_id": novo_prod.id, "mensagem": "Produto e Ficha Técnica cadastrados com sucesso!"}

# 3. Histórico de Pedidos
@router.get("/pedidos/historico")
def historico_pedidos(
    mes: Optional[str] = Query(None, description="Filtro YYYY-MM"),
    canal: Optional[str] = None,
    current_user: User = Depends(require_role(["gerente", "dono"])),
    db: Session = Depends(get_db)
):
    query = db.query(Pedido).filter(Pedido.tenant_id == current_user.tenant_id)
    if canal:
        query = query.filter(Pedido.canal == canal)
    pedidos = query.order_by(Pedido.id.desc()).all()

    resp = []
    for p in pedidos:
        desc_itens = [f"{it.quantidade}x {it.nome_produto}" for it in p.itens]
        resp.append({
            "id": p.id,
            "comanda": p.numero_comanda,
            "data_hora": p.data_hora.strftime("%d/%m/%Y %H:%M"),
            "canal": p.canal,
            "identificacao": p.identificacao,
            "forma_pagto": p.forma_pagto,
            "valor_bruto": round(p.valor_bruto, 2),
            "cmv_total": round(p.cmv_total, 2),
            "taxa_canal": round(p.taxa_canal, 2),
            "lucro_liquido": round(p.lucro_liquido, 2),
            "status_kds": p.status_kds,
            "itens": desc_itens
        })

    return {"total_pedidos": len(resp), "pedidos": resp}

# 4. Custos Fixos com Vigência Mensal
@router.get("/custos-fixos", response_model=List[CustoFixoResponse])
def listar_custos_fixos(
    mes: str = Query("2026-08", description="Mês vigência YYYY-MM"),
    current_user: User = Depends(require_role(["gerente", "dono"])),
    db: Session = Depends(get_db)
):
    custos = db.query(CustoFixo).filter(
        CustoFixo.tenant_id == current_user.tenant_id,
        CustoFixo.mes_vigencia == mes
    ).all()
    return custos

@router.post("/custos-fixos", response_model=CustoFixoResponse)
def criar_custo_fixo(
    dados: CustoFixoCreate,
    current_user: User = Depends(require_role(["gerente", "dono"])),
    db: Session = Depends(get_db)
):
    custo = CustoFixo(
        tenant_id=current_user.tenant_id,
        mes_vigencia=dados.mes_vigencia,
        categoria=dados.categoria,
        fornecedor=dados.fornecedor,
        valor=dados.valor
    )
    db.add(custo)
    db.commit()
    db.refresh(custo)
    return custo
