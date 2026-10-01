import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models import Tenant, Pedido, ItemPedido, Produto

router = APIRouter(prefix="/api/ifood", tags=["Integração Oficial iFood (Merchant API)"])

# 1. Webhook Oficial do iFood para Recepção Automática de Pedidos
@router.post("/webhook")
async def ifood_webhook_receiver(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint chamado pelos servidores do iFood quando um cliente fecha um pedido no aplicativo.
    O pedido cai DIRETAMENTE na Cozinha (KDS) e no banco de dados sem intervenção humana.
    """
    payload: Dict[str, Any] = await request.json()

    order_id = payload.get("orderId", f"#{datetime.datetime.utcnow().strftime('%M%S')}")
    customer_name = payload.get("customer", {}).get("name", "Cliente iFood")
    items_raw = payload.get("items", [])
    total_bruto = float(payload.get("total", {}).get("orderAmount", 0.0))

    # Pega o primeiro tenant disponível como exemplo
    tenant = db.query(Tenant).first()
    if not tenant:
        raise HTTPException(status_code=400, detail="Nenhum restaurante cadastrado.")

    ultimo_pedido = db.query(Pedido).filter(Pedido.tenant_id == tenant.id).order_by(Pedido.id.desc()).first()
    comanda_num = (ultimo_pedido.numero_comanda + 1) if ultimo_pedido and ultimo_pedido.numero_comanda else 201

    novo_pedido = Pedido(
        tenant_id=tenant.id,
        numero_comanda=comanda_num,
        data_hora=datetime.datetime.utcnow(),
        canal="iFood",
        identificacao=f"Pedido iFood {order_id} ({customer_name})",
        ifood_order_id=order_id,
        ifood_cliente=customer_name,
        forma_pagto="iFood Pay / Online",
        status_kds="Na Chapa"
    )
    db.add(novo_pedido)
    db.flush()

    cmv_acumulado = 0.0

    if not items_raw:
        # Item de exemplo se payload for teste
        items_raw = [{"name": "Burger Clássico Nalim", "quantity": 1, "price": 38.0, "observations": "SEM Cebola"}]
        total_bruto = 38.0

    for it in items_raw:
        prod_nome = it.get("name", "Item iFood")
        qtd = int(it.get("quantity", 1))
        preco_unit = float(it.get("price", 0.0))
        obs = it.get("observations", "")

        prod_db = db.query(Produto).filter(
            Produto.tenant_id == tenant.id,
            Produto.nome.ilike(f"%{prod_nome[:10]}%")
        ).first()

        cmv_unit = 0.0
        if prod_db:
            for ft in prod_db.ficha_tecnica:
                if ft.insumo:
                    cmv_unit += ft.quantidade * ft.insumo.custo_unitario

        cmv_acumulado += cmv_unit * qtd

        db.add(ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=prod_db.id if prod_db else None,
            nome_produto=prod_nome,
            quantidade=qtd,
            preco_unitario=preco_unit,
            cmv_unitario=cmv_unit,
            modificacoes=obs
        ))

    taxa_ifood = total_bruto * 0.23
    lucro = total_bruto - cmv_acumulado - taxa_ifood

    novo_pedido.valor_bruto = total_bruto
    novo_pedido.cmv_total = cmv_acumulado
    novo_pedido.taxa_canal = taxa_ifood
    novo_pedido.lucro_liquido = lucro

    db.commit()

    return {
        "status": "ACCEPTED",
        "pedido_id": novo_pedido.id,
        "ifood_order_id": order_id,
        "kds_status": "Enviado direto para a chapa!",
        "mensagem": "Pedido iFood ingerido com sucesso no banco de dados e KDS!"
    }

# 2. Polling de Eventos (Formato oficial do iFood Merchant API)
@router.get("/events:polling")
def ifood_polling_events():
    """
    Endpoint para simulação ou implementação da rotina de pooling GET do iFood.
    """
    return [
        {
            "id": "evt-98234-ifood",
            "code": "PLACED",
            "orderId": "#4092",
            "createdAt": datetime.datetime.utcnow().isoformat()
        }
    ]
