import datetime
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Produto, Insumo, Pedido, ItemPedido, FechamentoCaixa, Mesa, ConfiguracaoEmpresa, Tenant
from schemas import (
    PedidoCreate, KdsUpdateStatus, FechamentoCaixaCreate,
    AdicionarItensMesaInput, FecharMesaRequest,
    ConfigTaxasCartaoInput, ConfigTaxasCartaoResponse
)
from auth import require_role, SECRET_KEY, ALGORITHM
import jwt

router = APIRouter(prefix="/api/operacional", tags=["Operacional (PDV, Cozinha & Caixa)"])

def get_tenant_id_permissive(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> int:
    """Extrai tenant_id do token se fornecido, ou faz fallback para o tenant principal (para telas de cozinha / abas anônimas)."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub", 0))
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return user.tenant_id
        except Exception:
            pass
    first_tenant = db.query(Tenant).first()
    return first_tenant.id if first_tenant else 1

def obter_data_hora_brasilia() -> datetime.datetime:
    """Retorna datetime no fuso horário oficial de Brasília (UTC-3) para evitar deslocamento de data em servidores em nuvem."""
    fuso_br = datetime.timezone(datetime.timedelta(hours=-3))
    return datetime.datetime.now(fuso_br).replace(tzinfo=None)

# 1. Cardápio Limpo para Atendimento (SEM CMV, SEM LUCRO)
@router.get("/cardapio")
def listar_cardapio_operacional(
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    produtos = db.query(Produto).filter(
        Produto.tenant_id == tenant_id,
        Produto.ativo == True
    ).all()

    insumos_extras = db.query(Insumo).filter(
        Insumo.tenant_id == tenant_id,
        Insumo.preco_venda_extra > 0
    ).all()

    cardapio = []
    for p in produtos:
        ingredientes_nomes = [it.insumo.nome for it in p.ficha_tecnica if it.insumo]
        cardapio.append({
            "codigo": p.codigo,
            "nome": p.nome,
            "categoria": p.categoria,
            "descricao": p.descricao,
            "preco": p.preco_salao,
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
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    if not dados.itens:
        raise HTTPException(status_code=400, detail="O pedido deve conter ao menos um item.")

    ultimo_pedido = db.query(Pedido).filter(Pedido.tenant_id == tenant_id).order_by(Pedido.id.desc()).first()
    numero_comanda = (ultimo_pedido.numero_comanda + 1) if ultimo_pedido and ultimo_pedido.numero_comanda else 101

    identificacao_final = dados.identificacao or "Balcão"
    if dados.canal == "iFood" and dados.ifood_order_id:
        identificacao_final = f"Pedido iFood {dados.ifood_order_id} ({dados.ifood_cliente or 'Cliente'})"

    solicitante_final = dados.solicitante or ("Balcão" if dados.canal == "Balcão" else "Garçom")

    novo_pedido = Pedido(
        tenant_id=tenant_id,
        numero_comanda=numero_comanda,
        data_hora=obter_data_hora_brasilia(),
        canal=dados.canal,
        identificacao=identificacao_final,
        solicitante=solicitante_final,
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
            Produto.tenant_id == tenant_id,
            Produto.codigo == item_input.produto_codigo
        ).first()

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
            nome_produto=item_input.nome or (prod.nome if prod else item_input.produto_codigo),
            quantidade=item_input.quantidade,
            preco_unitario=item_input.preco_unitario,
            cmv_unitario=cmv_prod,
            modificacoes=item_input.modificacoes
        )
        db.add(item_db)

    taxa_canal = total_bruto * 0.23 if dados.canal == "iFood" else total_bruto * 0.02
    lucro_liquido = total_bruto - cmv_total - taxa_canal

    novo_pedido.valor_bruto = total_bruto
    novo_pedido.cmv_total = cmv_total
    novo_pedido.taxa_canal = taxa_canal
    novo_pedido.lucro_liquido = lucro_liquido

    db.commit()

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

# 2.1 Listar Todos os Pedidos (Para Saúde Financeira e Histórico de Vendas)
@router.get("/pedidos")
def listar_todos_pedidos(
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    pedidos = db.query(Pedido).filter(Pedido.tenant_id == tenant_id).order_by(Pedido.id.desc()).all()
    resultado = []
    for p in pedidos:
        resultado.append({
            "id": p.id,
            "numero_comanda": p.numero_comanda,
            "data_hora": p.data_hora.strftime("%Y-%m-%d %H:%M") if p.data_hora else "",
            "data_iso": p.data_hora.strftime("%Y-%m-%d") if p.data_hora else "",
            "canal": p.canal,
            "identificacao": p.identificacao,
            "forma_pagto": p.forma_pagto,
            "solicitante": p.solicitante or "Balcão",
            "vendedor": p.solicitante or "Balcão",
            "status_kds": p.status_kds,
            "valor_bruto": round(p.valor_bruto or 0.0, 2),
            "cmv_total": round(p.cmv_total or 0.0, 2),
            "taxa_canal": round(p.taxa_canal or 0.0, 2),
            "lucro_liquido": round(p.lucro_liquido or 0.0, 2),
            "itens": [{
                "nome": it.nome_produto,
                "quantidade": it.quantidade,
                "preco_unitario": it.preco_unitario,
                "cmv_unitario": it.cmv_unitario,
                "modificacoes": it.modificacoes
            } for it in p.itens]
        })
    return {"pedidos": resultado}


# 3. KDS — Painel da Cozinha em Tempo Real (Funciona com ou sem Token para Telas e Abas Anônimas)
@router.get("/kds")
@router.get("/kds/realtime")
def listar_pedidos_kds(
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    pedidos = db.query(Pedido).filter(
        Pedido.tenant_id == tenant_id,
        Pedido.status_kds.in_(["Na Chapa", "Pronto"])
    ).order_by(Pedido.id.desc()).all()

    tickets = []
    for p in pedidos:
        tickets.append({
            "id": p.id,
            "numero_comanda": p.numero_comanda,
            "data_hora": p.data_hora.strftime("%H:%M") if p.data_hora else datetime.datetime.now().strftime("%H:%M"),
            "canal": p.canal,
            "identificacao": p.identificacao,
            "solicitante": p.solicitante or ("Balcão" if p.canal == "Balcão" else "Garçom"),
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
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    pedido = db.query(Pedido).filter(
        (Pedido.id == pedido_id) | (Pedido.numero_comanda == pedido_id)
    ).order_by(Pedido.id.desc()).first()

    if not pedido:
        return {"sucesso": False, "aviso": "Pedido não encontrado no banco, mantido em cache local."}

    pedido.status_kds = dados.status_kds
    db.commit()

    # Se o pedido ficou 'Pronto' na cozinha, dispara notificação Web Push em segundo plano
    if dados.status_kds == "Pronto":
        try:
            from push_service import notificar_garcom_push
            notificar_garcom_push(
                mesa=pedido.identificacao or f"Comanda #{pedido.numero_comanda}",
                comanda_num=pedido.numero_comanda or pedido.id,
                solicitante=pedido.solicitante or pedido.canal
            )
        except Exception:
            pass

    return {"sucesso": True, "pedido_id": pedido.id, "numero_comanda": pedido.numero_comanda, "novo_status": pedido.status_kds}

# Endpoints Web Push no Roteador Operacional
@router.get("/vapid-public-key")
def obter_chave_publica_vapid():
    from push_service import VAPID_PUBLIC_KEY
    return {"public_key": VAPID_PUBLIC_KEY}

@router.post("/subscribe")
def registrar_push_subscription(dados: dict):
    from push_service import salvar_subscription
    garcom = dados.get("garcom", "Garçom")
    sub = dados.get("subscription")
    ok = salvar_subscription(garcom, sub)
    return {"sucesso": ok}

@router.post("/push-test")
def disparar_push_teste(dados: dict = None):
    from push_service import enviar_push_teste
    garcom = (dados or {}).get("garcom", "Garçom")
    enviar_push_teste(garcom)
    return {"sucesso": True, "mensagem": "Push de teste enviado"}


# 5. GESTÃO DE MESAS (Comanda Acumulada, Status Livre/Ocupada e Zeramento)
@router.get("/mesas")
def listar_mesas(
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    mesas_existentes = db.query(Mesa).filter(Mesa.tenant_id == tenant_id).order_by(Mesa.id.asc()).all()

    # Se ainda não existem mesas cadastradas para este tenant, inicializa Mesa 01 a 10 + Balcão
    if not mesas_existentes:
        nomes_padrao = [f"Mesa {i:02d}" for i in range(1, 11)] + ["Balcão"]
        for nome in nomes_padrao:
            m = Mesa(
                tenant_id=tenant_id,
                numero=nome,
                status="LIVRE",
                consumo_acumulado=0.0,
                itens_json="[]"
            )
            db.add(m)
        db.commit()
        mesas_existentes = db.query(Mesa).filter(Mesa.tenant_id == tenant_id).order_by(Mesa.id.asc()).all()

    resultado = []
    for m in mesas_existentes:
        try:
            itens_parsed = json.loads(m.itens_json or "[]")
        except Exception:
            itens_parsed = []

        resultado.append({
            "id": m.id,
            "numero": m.numero,
            "status": m.status,
            "consumo_acumulado": round(m.consumo_acumulado, 2),
            "itens": itens_parsed,
            "aberta_em": m.aberta_em.strftime("%H:%M") if m.aberta_em else None
        })

    return {"mesas": resultado}

@router.post("/mesas/{mesa_identificador}/adicionar-itens")
def adicionar_itens_mesa(
    mesa_identificador: str,
    dados: AdicionarItensMesaInput,
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    if not dados.itens:
        raise HTTPException(status_code=400, detail="Nenhum item informado.")

    # Busca a mesa por número (ex: 'Mesa 03' ou 'Balcão')
    mesa = db.query(Mesa).filter(
        Mesa.tenant_id == tenant_id,
        Mesa.numero == mesa_identificador
    ).first()

    if not mesa:
        mesa = Mesa(
            tenant_id=tenant_id,
            numero=mesa_identificador,
            status="LIVRE",
            consumo_acumulado=0.0,
            itens_json="[]"
        )
        db.add(mesa)
        db.flush()

    try:
        itens_acumulados = json.loads(mesa.itens_json or "[]")
    except Exception:
        itens_acumulados = []

    subtotal_rodada = 0.0
    agora_br = obter_data_hora_brasilia()
    agora_hora = agora_br.strftime("%H:%M")

    for it in dados.itens:
        prod = db.query(Produto).filter(
            Produto.tenant_id == tenant_id,
            Produto.codigo == it.produto_codigo
        ).first()
        preco_unit = float(it.preco_unitario or (prod.preco_salao if prod else 0.0))
        nome_prod = it.nome or (prod.nome if prod else it.produto_codigo)
        total_item = preco_unit * it.quantidade
        subtotal_rodada += total_item
        itens_acumulados.append({
            "produto_codigo": it.produto_codigo,
            "nome": nome_prod,
            "quantidade": it.quantidade,
            "preco_unitario": preco_unit,
            "total": total_item,
            "modificacoes": it.modificacoes,
            "hora": agora_hora
        })

    mesa.consumo_acumulado += subtotal_rodada
    mesa.itens_json = json.dumps(itens_acumulados, ensure_ascii=False)
    mesa.status = "OCUPADA"
    if not mesa.aberta_em:
        mesa.aberta_em = agora_br

    # Gera Pedido automático no KDS para a cozinha produzir a rodada imediatamente
    ultimo_pedido = db.query(Pedido).filter(Pedido.tenant_id == tenant_id).order_by(Pedido.id.desc()).first()
    numero_comanda = (ultimo_pedido.numero_comanda + 1) if ultimo_pedido and ultimo_pedido.numero_comanda else 101

    solicitante_final = dados.solicitante or "Garçom"

    pedido_kds = Pedido(
        tenant_id=tenant_id,
        numero_comanda=numero_comanda,
        data_hora=agora_br,
        canal="Salão",
        identificacao=f"{mesa.numero} (Salão)",
        solicitante=solicitante_final,
        forma_pagto="Em Aberto (Mesa)",
        status_kds="Na Chapa",
        valor_bruto=subtotal_rodada,
        cmv_total=subtotal_rodada * 0.30,  # Estimativa inicial 30%
        taxa_canal=subtotal_rodada * 0.02,
        lucro_liquido=subtotal_rodada * 0.68
    )
    db.add(pedido_kds)
    db.flush()

    for it in dados.itens:
        prod = db.query(Produto).filter(
            Produto.tenant_id == tenant_id,
            Produto.codigo == it.produto_codigo
        ).first()

        preco_unit = float(it.preco_unitario or (prod.preco_salao if prod else 0.0))
        nome_prod = it.nome or (prod.nome if prod else it.produto_codigo)

        db.add(ItemPedido(
            pedido_id=pedido_kds.id,
            produto_id=prod.id if prod else None,
            nome_produto=nome_prod,
            quantidade=it.quantidade,
            preco_unitario=preco_unit,
            cmv_unitario=preco_unit * 0.30,
            modificacoes=it.modificacoes
        ))

    db.commit()

    return {
        "sucesso": True,
        "mesa": mesa.numero,
        "status": mesa.status,
        "consumo_acumulado": round(mesa.consumo_acumulado, 2),
        "total_itens": len(itens_acumulados),
        "pedido_kds_id": pedido_kds.id,
        "numero_comanda": pedido_kds.numero_comanda,
        "mensagem": f"Rodada adicionada com sucesso! Pedido #{pedido_kds.numero_comanda} despachado para a Cozinha/KDS."
    }

@router.post("/mesas/{mesa_identificador}/fechar")
def fechar_e_zerar_mesa(
    mesa_identificador: str,
    dados: FecharMesaRequest,
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    mesa = db.query(Mesa).filter(
        Mesa.tenant_id == tenant_id,
        Mesa.numero == mesa_identificador
    ).first()

    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")

    valor_consumido = mesa.consumo_acumulado
    vendedor_final = dados.vendedor or dados.solicitante or "Garçom"

    # Atualiza pedidos desta mesa: forma de pagamento, vendedor/atendente e status no KDS para Entregue
    pedidos_mesa = db.query(Pedido).filter(
        Pedido.tenant_id == tenant_id,
        Pedido.identificacao.like(f"%{mesa_identificador}%")
    ).order_by(Pedido.id.desc()).all()

    # Prioriza pedidos que estavam em aberto nesta mesa
    pedidos_em_aberto = [p for p in pedidos_mesa if p.forma_pagto == "Em Aberto (Mesa)"]
    pedidos_alvo = pedidos_em_aberto if pedidos_em_aberto else pedidos_mesa

    agora_br = obter_data_hora_brasilia()
    for p_mesa in pedidos_alvo:
        p_mesa.forma_pagto = dados.forma_pagto
        if vendedor_final and (not p_mesa.solicitante or p_mesa.solicitante in ["Balcão", "Garçom"]):
            p_mesa.solicitante = vendedor_final
        if p_mesa.status_kds in ["Na Chapa", "Pronto"]:
            p_mesa.status_kds = "Entregue"
        if not p_mesa.data_hora:
            p_mesa.data_hora = agora_br

    # ZERA A MESA COMPLETAMENTE PARA LIBERAR PARA O PRÓXIMO CLIENTE
    mesa.status = "LIVRE"
    mesa.consumo_acumulado = 0.0
    mesa.itens_json = "[]"
    mesa.aberta_em = None

    db.commit()

    return {
        "sucesso": True,
        "mesa": mesa_identificador,
        "status": "LIVRE",
        "consumo_fechado": round(valor_consumido, 2),
        "valor_total_pago": round(dados.valor_total_pago, 2),
        "forma_pagto": dados.forma_pagto,
        "vendedor": vendedor_final,
        "pedidos_atualizados": len(pedidos_alvo),
        "mensagem": f"{mesa_identificador} fechada e recebida em {dados.forma_pagto}! Mesa livre para novos clientes."
    }

# 6. CONFIGURAÇÃO DE TAXAS E JUROS DA MÁQUINA DE CARTÃO
@router.get("/config-taxas")
def obter_config_taxas(
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    config = db.query(ConfiguracaoEmpresa).filter(ConfiguracaoEmpresa.tenant_id == tenant_id).first()
    if not config:
        config = ConfiguracaoEmpresa(
            tenant_id=tenant_id,
            taxa_debito=1.99,
            taxa_credito_vista=3.49,
            taxa_credito_parcelado=4.99,
            repassar_taxa_cartao=False
        )
        db.add(config)
        db.commit()

    return {
        "taxa_debito": config.taxa_debito if hasattr(config, "taxa_debito") else 1.99,
        "taxa_credito_vista": config.taxa_credito_vista if hasattr(config, "taxa_credito_vista") else 3.49,
        "taxa_credito_parcelado": config.taxa_credito_parcelado if hasattr(config, "taxa_credito_parcelado") else 4.99,
        "repassar_taxa_cartao": config.repassar_taxa_cartao if hasattr(config, "repassar_taxa_cartao") else False
    }

@router.post("/config-taxas")
def salvar_config_taxas(
    dados: ConfigTaxasCartaoInput,
    tenant_id: int = Depends(get_tenant_id_permissive),
    db: Session = Depends(get_db)
):
    config = db.query(ConfiguracaoEmpresa).filter(ConfiguracaoEmpresa.tenant_id == tenant_id).first()
    if not config:
        config = ConfiguracaoEmpresa(tenant_id=tenant_id)
        db.add(config)

    config.taxa_debito = dados.taxa_debito
    config.taxa_credito_vista = dados.taxa_credito_vista
    config.taxa_credito_parcelado = dados.taxa_credito_parcelado
    config.repassar_taxa_cartao = dados.repassar_taxa_cartao

    db.commit()
    return {
        "sucesso": True,
        "taxa_debito": config.taxa_debito,
        "taxa_credito_vista": config.taxa_credito_vista,
        "taxa_credito_parcelado": config.taxa_credito_parcelado,
        "repassar_taxa_cartao": config.repassar_taxa_cartao,
        "mensagem": "Taxas de cartão e maquininha salvas com sucesso!"
    }

# 7. Fechamento de Caixa Diário
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

# 8. Cardápio Público para Clientes Finais (Delivery / WhatsApp)
@router.get("/public/cardapio")
def listar_cardapio_publico(
    tenant: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    tenant_obj = None
    if tenant:
        if tenant.isdigit():
            tenant_obj = db.query(Tenant).filter(Tenant.id == int(tenant)).first()
        if not tenant_obj:
            tenant_obj = db.query(Tenant).filter(Tenant.slug == tenant).first()

    if not tenant_obj:
        tenant_obj = db.query(Tenant).first()

    tenant_id = tenant_obj.id if tenant_obj else 1

    produtos = db.query(Produto).filter(
        Produto.tenant_id == tenant_id,
        Produto.ativo == True
    ).all()
    insumos_extras = db.query(Insumo).filter(
        Insumo.tenant_id == tenant_id,
        Insumo.preco_venda_extra > 0
    ).all()

    cardapio = []
    for p in produtos:
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

    return {
        "restaurante": {
            "id": tenant_obj.id if tenant_obj else 1,
            "nome": tenant_obj.nome if tenant_obj else "NALIM Food",
            "slug": tenant_obj.slug if tenant_obj else "nalim",
            "telefone": tenant_obj.telefone if tenant_obj else ""
        },
        "produtos": cardapio,
        "extras": extras
    }

# 9. Criar Pedido Público vindo do Cardápio Digital (sem autenticação)
@router.post("/public/pedidos")
def criar_pedido_publico(
    dados: PedidoCreate,
    tenant: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if not dados.itens:
        raise HTTPException(status_code=400, detail="O pedido deve conter ao menos um item.")

    tenant_obj = None
    if tenant:
        if tenant.isdigit():
            tenant_obj = db.query(Tenant).filter(Tenant.id == int(tenant)).first()
        if not tenant_obj:
            tenant_obj = db.query(Tenant).filter(Tenant.slug == tenant).first()

    if not tenant_obj:
        tenant_obj = db.query(Tenant).first()

    tenant_id = tenant_obj.id if tenant_obj else 1

    ultimo_pedido = db.query(Pedido).filter(Pedido.tenant_id == tenant_id).order_by(Pedido.id.desc()).first()
    numero_comanda = (ultimo_pedido.numero_comanda + 1) if ultimo_pedido and ultimo_pedido.numero_comanda else 101

    novo_pedido = Pedido(
        tenant_id=tenant_id,
        numero_comanda=numero_comanda,
        data_hora=datetime.datetime.utcnow(),
        canal=dados.canal or "Cardápio Digital",
        identificacao=dados.identificacao or f"Cardápio Digital #{numero_comanda}",
        forma_pagto=dados.forma_pagto,
        status_kds="Na Chapa"
    )
    db.add(novo_pedido)
    db.flush()

    total_bruto = 0.0
    cmv_total = 0.0

    for item_input in dados.itens:
        prod = db.query(Produto).filter(
            Produto.tenant_id == tenant_id,
            Produto.codigo == item_input.produto_codigo
        ).first()

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
            nome_produto=item_input.nome or (prod.nome if prod else item_input.produto_codigo),
            quantidade=item_input.quantidade,
            preco_unitario=item_input.preco_unitario,
            cmv_unitario=cmv_prod,
            modificacoes=item_input.modificacoes
        )
        db.add(item_db)

    taxa_canal = total_bruto * 0.015 if ("Cartão" in dados.forma_pagto) else 0.0
    lucro_liquido = total_bruto - cmv_total - taxa_canal

    novo_pedido.valor_bruto = total_bruto
    novo_pedido.cmv_total = cmv_total
    novo_pedido.taxa_canal = taxa_canal
    novo_pedido.lucro_liquido = lucro_liquido

    db.commit()
    db.refresh(novo_pedido)

    return {
        "sucesso": True,
        "numero_comanda": novo_pedido.numero_comanda,
        "pedido_id": novo_pedido.id,
        "total": round(total_bruto, 2),
        "status_kds": novo_pedido.status_kds,
        "mensagem": "Pedido recebido com sucesso na cozinha!"
    }