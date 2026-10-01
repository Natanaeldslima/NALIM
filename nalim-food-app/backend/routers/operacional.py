import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Produto, Insumo, Pedido, ItemPedido, FechamentoCaixa
from schemas import PedidoCreate, KdsUpdateStatus, FechamentoCaixaCreate
from auth import require_role

router = APIRouter(prefix="/api/operacional", tags=["Operacional (PDV, Cozinha & Caixa)"])

# 1. Cardápio Limpo para Atendimento (SEM CMV, SEM LUCRO)
@router.get("/cardapio")
def listar_cardapio_operacional(
    current_user: User = Depends(require_role(["operador", "gerente", "dono"])),
    db: Session = Depends(get_db)
):
    produtos = db.query(Produto).filter(
        Produto.tenant_id == current_user.tenant_id,
        Produto.ativo == True
    ).all()

    insumos_extras = db.query(Insumo).filter(
        Insumo.tenant_id == current_user.tenant_id,
        Insumo.preco_venda_extra > 0
    ).all()

    cardapio = []
    for p in produtos:
        # Puxa ingredientes apenas com nomes para a personalização ("SEM Cebola")
        ingredientes_nomes = [it.insumo.nome for it in p.ficha_tecnica if it.insumo]
        cardapio.append({
            "codigo": p.codigo,
            "nome": p.nome,
            "categoria": p.categoria,
            "descricao": p.descricao,
            "preco_salao": p.preco_salao,
            "preco_ifood": p.preco_ifood,
            "ingredientes": ingredientes_nomes
        })

    extras = [{
        "codigo": i.codigo,
        "nome": i.nome,
        "preco_extra": i.preco_venda_extra
    } for i in insumos_extras]

    return {"produtos": cardapio, "extras": extras}

# 2. Criar Pedido / Enviar para a Cozinha
@router.post("/pedidos")
def criar_pedido(
    dados: PedidoCreate,
    current_user: User = Depends(require_role(["operador", "gerente", "dono"])),
    db: Session = Depends(get_db)
):
    if not dados.itens:
        raise HTTPException(status_code=400, detail="O pedido deve conter ao menos um item.")

    # Gera próximo número de comanda
    ultimo_pedido = db.query(Pedido).filter(Pedido.tenant_id == current_user.tenant_id).order_by(Pedido.id.desc()).first()
    numero_comanda = (ultimo_pedido.numero_comanda + 1) if ultimo_pedido and ultimo_pedido.numero_comanda else 101

    identificacao_final = dados.identificacao or "Balcão"
    if dados.canal == "iFood" and dados.ifood_order_id:
        identificacao_final = f"Pedido iFood {dados.ifood_order_id} ({dados.ifood_cliente or 'Cliente'})"

    novo_pedido = Pedido(
        tenant_id=current_user.tenant_id,
        numero_comanda=numero_comanda,
        data_hora=datetime.datetime.utcnow(),
        canal=dados.canal,
        identificacao=identificacao_final,
        ifood_order_id=dados.ifood_order_id,
        ifood_cliente=dados.ifood_cliente,
        forma_pagto=dados.forma_pagto,
        status_kds="Na Chapa"
    )
    db.add(novo_pedido)
    db.flush()

    total_bruto = 0.0
    cmv_total = 0.0

    for item_input in dados.itens:
        prod = db.query(Produto).filter(
            Produto.tenant_id == current_user.tenant_id,
            Produto.codigo == item_input.produto_codigo
        ).first()

        # Calcula CMV da receita no servidor
        cmv_prod = 0.0
        if prod:
            for ft in prod.ficha_tecnica:
                if ft.insumo:
                    cmv_prod += ft.quantidade * ft.insumo.custo_unitario

        item_total = item_input.preco_unitario * item_input.quantidade
        total_bruto += item_total
        cmv_total += cmv_prod * item_input.quantidade

        item_db = ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=prod.id if prod else None,
            nome_produto=prod.nome if prod else item_input.produto_codigo,
            quantidade=item_input.quantidade,
            preco_unitario=item_input.preco_unitario,
            cmv_unitario=cmv_prod,
            modificacoes=item_input.modificacoes
        )
        db.add(item_db)

    # Taxa estimada de canal (iFood 23% vs Salão/Balcão 2% máquina)
    taxa_canal = total_bruto * 0.23 if dados.canal == "iFood" else total_bruto * 0.02
    lucro_liquido = total_bruto - cmv_total - taxa_canal

    novo_pedido.valor_bruto = total_bruto
    novo_pedido.cmv_total = cmv_total
    novo_pedido.taxa_canal = taxa_canal
    novo_pedido.lucro_liquido = lucro_liquido

    db.commit()

    # Retorno limpo para o operador (sem lucro ou cmv)
    return {
        "sucesso": True,
        "pedido_id": novo_pedido.id,
        "numero_comanda": novo_pedido.numero_comanda,
        "valor_a_cobrar": round(total_bruto, 2),
        "canal": novo_pedido.canal,
        "identificacao": novo_pedido.identificacao,
        "status_kds": novo_pedido.status_kds,
        "mensagem": "Pedido registrado com sucesso e enviado para a Cozinha/KDS!"
    }

# 3. KDS — Painel da Cozinha em Tempo Real
@router.get("/kds")
def listar_pedidos_kds(
    current_user: User = Depends(require_role(["operador", "gerente", "dono"])),
    db: Session = Depends(get_db)
):
    pedidos = db.query(Pedido).filter(
        Pedido.tenant_id == current_user.tenant_id,
        Pedido.status_kds.in_(["Na Chapa", "Pronto"])
    ).order_by(Pedido.id.asc()).all()

    tickets = []
    for p in pedidos:
        tickets.append({
            "id": p.id,
            "numero_comanda": p.numero_comanda,
            "data_hora": p.data_hora.strftime("%H:%M"),
            "canal": p.canal,
            "identificacao": p.identificacao,
            "status": p.status_kds,
            "itens": [{
                "nome": it.nome_produto,
                "quantidade": it.quantidade,
                "modificacoes": it.modificacoes
            } for it in p.itens]
        })

    return {"tickets": tickets, "total_em_espera": len(tickets)}

# 4. Atualizar Status no KDS (Na Chapa -> Pronto -> Entregue)
@router.patch("/kds/{pedido_id}/status")
def atualizar_status_kds(
    pedido_id: int,
    dados: KdsUpdateStatus,
    current_user: User = Depends(require_role(["operador", "gerente", "dono"])),
    db: Session = Depends(get_db)
):
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id,
        Pedido.tenant_id == current_user.tenant_id
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    pedido.status_kds = dados.status_kds
    db.commit()
    return {"sucesso": True, "pedido_id": pedido.id, "novo_status": pedido.status_kds}

# 5. Fechamento de Caixa Diário
@router.post("/caixa")
def registrar_fechamento_caixa(
    dados: FechamentoCaixaCreate,
    current_user: User = Depends(require_role(["operador", "gerente", "dono"])),
    db: Session = Depends(get_db)
):
    soma_formas = dados.pix + dados.cartao + dados.dinheiro
    diferenca = dados.faturamento_total - soma_formas
    status_conferencia = "BATEU 100%" if abs(diferenca) < 0.05 else f"DIVERGÊNCIA DE R$ {round(diferenca, 2)}"

    fechamento = FechamentoCaixa(
        tenant_id=current_user.tenant_id,
        data_turno=dados.data_turno,
        faturamento_total=dados.faturamento_total,
        total_pedidos=dados.total_pedidos,
        pix=dados.pix,
        cartao=dados.cartao,
        dinheiro=dados.dinheiro,
        perdas_descartes=dados.perdas_descartes,
        diferenca=diferenca,
        status_conferencia=status_conferencia
    )
    db.add(fechamento)
    db.commit()

    return {
        "sucesso": True,
        "id": fechamento.id,
        "diferenca": round(diferenca, 2),
        "status_conferencia": status_conferencia,
        "mensagem": "Fechamento de caixa gravado com sucesso!"
    }
