import re
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import (
    Tenant, User, Produto, Insumo, Pedido, 
    ConfiguracaoEmpresa, FichaTecnicaItem
)
from auth import require_role, hash_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/master", tags=["SuperAdmin / Gestão de Clientes SaaS"])

# Schemas Pydantic específicos para o Master Admin
class TenantCreateInput(BaseModel):
    nome: str
    cnpj: Optional[str] = None
    slug: Optional[str] = None
    responsavel: Optional[str] = None
    telefone: Optional[str] = None
    email_dono: str
    senha_dono: str
    plano: Optional[str] = "PRO"
    valor_mensalidade: Optional[float] = 199.00
    status: Optional[str] = "ATIVO"
    vencimento_mensalidade: Optional[str] = None
    observacoes: Optional[str] = None
    clonar_cardapio_modelo: Optional[bool] = True

class TenantUpdateInput(BaseModel):
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    slug: Optional[str] = None
    responsavel: Optional[str] = None
    telefone: Optional[str] = None
    email_contato: Optional[str] = None
    plano: Optional[str] = None
    valor_mensalidade: Optional[float] = None
    status: Optional[str] = None
    vencimento_mensalidade: Optional[str] = None
    observacoes: Optional[str] = None
    nova_senha_dono: Optional[str] = None

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

# Helper de verificação de permissão master ou superadmin
def verificar_acesso_master(current_user: User = Depends(get_current_user)):
    # Permite acesso se role for 'master' ou se for o dono principal (tenant 1 / id 1)
    if current_user.role != "master" and not (current_user.tenant_id == 1 and current_user.role == "dono"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito: Requer credencial de Administrador Master NALIM."
        )
    return current_user

# 1. Estatísticas Gerais do SaaS (MRR, Clientes Ativos, Pedidos Totais)
@router.get("/stats")
def obter_stats_saas(
    db: Session = Depends(get_db),
    admin: User = Depends(verificar_acesso_master)
):
    tenants = db.query(Tenant).all()
    total_tenants = len(tenants)
    ativos = sum(1 for t in tenants if (t.status or 'ATIVO').upper() == 'ATIVO')
    trial = sum(1 for t in tenants if (t.status or '').upper() == 'TRIAL')
    suspensos = sum(1 for t in tenants if (t.status or '').upper() == 'SUSPENSO')
    mrr_total = sum((t.valor_mensalidade or 0.0) for t in tenants if (t.status or 'ATIVO').upper() == 'ATIVO')

    total_pedidos_geral = db.query(Pedido).count()
    total_usuarios_geral = db.query(User).count()

    return {
        "total_clientes": total_tenants,
        "clientes_ativos": ativos,
        "clientes_trial": trial,
        "clientes_suspensos": suspensos,
        "mrr_recorrente": mrr_total,
        "total_pedidos_plataforma": total_pedidos_geral,
        "total_usuarios_plataforma": total_usuarios_geral,
        "dominio_padrao": "nalimgestao.com.br"
    }

# 2. Listagem de Todos os Clientes (Restaurantes)
@router.get("/tenants")
def listar_clientes_saas(
    db: Session = Depends(get_db),
    admin: User = Depends(verificar_acesso_master)
):
    tenants = db.query(Tenant).order_by(Tenant.id.desc()).all()
    lista = []
    
    for t in tenants:
        dono = db.query(User).filter(User.tenant_id == t.id, User.role == "dono").first()
        total_pedidos = db.query(Pedido).filter(Pedido.tenant_id == t.id).count()
        total_produtos = db.query(Produto).filter(Produto.tenant_id == t.id, Produto.ativo == True).count()
        total_users = db.query(User).filter(User.tenant_id == t.id, User.ativo == True).count()

        lista.append({
            "id": t.id,
            "nome": t.nome,
            "cnpj": t.cnpj or "",
            "slug": t.slug,
            "responsavel": t.responsavel or (dono.nome if dono else "Não informado"),
            "telefone": t.telefone or "",
            "email_contato": t.email_contato or (dono.email if dono else ""),
            "dono_nome": dono.nome if dono else "",
            "dono_email": dono.email if dono else "",
            "plano": t.plano or "PRO",
            "valor_mensalidade": t.valor_mensalidade or 199.00,
            "status": t.status or "ATIVO",
            "vencimento_mensalidade": t.vencimento_mensalidade or "",
            "observacoes": t.observacoes or "",
            "total_pedidos": total_pedidos,
            "total_produtos": total_produtos,
            "total_usuarios": total_users,
            "created_at": t.created_at.strftime("%d/%m/%Y") if t.created_at else "",
            "links": {
                "painel": f"https://nalimgestao.com.br/login",
                "garcom": f"https://nalimgestao.com.br/garcom",
                "cardapio": f"https://nalimgestao.com.br/cardapio?tenant={t.slug}"
            }
        })

    return lista

# 3. Cadastro de Novo Cliente Restaurante
@router.post("/tenants")
def cadastrar_novo_cliente(
    dados: TenantCreateInput,
    db: Session = Depends(get_db),
    admin: User = Depends(verificar_acesso_master)
):
    # Gera slug se não fornecido
    slug_base = dados.slug if dados.slug else slugify(dados.nome)
    slug_final = slug_base
    count = 1
    while db.query(Tenant).filter(Tenant.slug == slug_final).first():
        slug_final = f"{slug_base}-{count}"
        count += 1

    # Verifica se e-mail já existe
    if db.query(User).filter(User.email == dados.email_dono).first():
        raise HTTPException(
            status_code=400,
            detail=f"O e-mail '{dados.email_dono}' já está em uso por outro usuário."
        )

    # Vencimento padrão: +30 dias se não informado
    vencimento = dados.vencimento_mensalidade
    if not vencimento:
        vencimento = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()

    # 1. Cria Tenant
    novo_tenant = Tenant(
        nome=dados.nome,
        cnpj=dados.cnpj,
        slug=slug_final,
        responsavel=dados.responsavel or dados.nome,
        telefone=dados.telefone,
        email_contato=dados.email_dono,
        plano=dados.plano or "PRO",
        valor_mensalidade=dados.valor_mensalidade or 199.00,
        status=dados.status or "ATIVO",
        vencimento_mensalidade=vencimento,
        observacoes=dados.observacoes
    )
    db.add(novo_tenant)
    db.flush()

    # 2. Cria Usuário Dono
    user_dono = User(
        tenant_id=novo_tenant.id,
        nome=dados.responsavel or f"Dono - {dados.nome}",
        email=dados.email_dono,
        senha_hash=hash_password(dados.senha_dono),
        role="dono",
        ativo=True
    )
    db.add(user_dono)

    # 3. Cria Configurações Padrão da Empresa
    config = ConfiguracaoEmpresa(
        tenant_id=novo_tenant.id,
        regime_tributario="ME_6",
        dias_trabalhados_mes=26,
        meta_lucro_desejada=3000.0,
        aliquota_ifood=0.23,
        taxa_debito=1.99,
        taxa_credito_vista=3.49,
        taxa_credito_parcelado=4.99,
        repassar_taxa_cartao=False
    )
    db.add(config)
    db.flush()

    # 4. Pré-popular com Insumos e Produtos Modelo (se selecionado)
    if dados.clonar_cardapio_modelo:
        # Pão
        ins_pao = Insumo(tenant_id=novo_tenant.id, codigo="INS-01", nome="Pão Brioche Artesanal", categoria="Pães", preco_compra=36.00, und_compra="pct 20un", und_uso="un", fator_conversao=20.0, custo_unitario=1.80)
        # Carne
        ins_carne = Insumo(tenant_id=novo_tenant.id, codigo="INS-02", nome="Blend Bovino Fresco 160g", categoria="Carnes", preco_compra=38.00, und_compra="kg", und_uso="g", fator_conversao=1000.0, custo_unitario=0.038, preco_venda_extra=10.0)
        # Queijo
        ins_queijo = Insumo(tenant_id=novo_tenant.id, codigo="INS-03", nome="Queijo Cheddar Fatiado", categoria="Queijos", preco_compra=45.00, und_compra="kg", und_uso="g", fator_conversao=1000.0, custo_unitario=0.045, preco_venda_extra=3.50)
        # Bacon
        ins_bacon = Insumo(tenant_id=novo_tenant.id, codigo="INS-04", nome="Bacon Fatiado Crocante", categoria="Carnes", preco_compra=42.00, und_compra="kg", und_uso="g", fator_conversao=1000.0, custo_unitario=0.042, preco_venda_extra=4.00)
        # Batata
        ins_batata = Insumo(tenant_id=novo_tenant.id, codigo="INS-05", nome="Batata Frita Palito", categoria="Acompanhamentos", preco_compra=28.00, und_compra="pct 2.5kg", und_uso="g", fator_conversao=2500.0, custo_unitario=0.0112)
        
        db.add_all([ins_pao, ins_carne, ins_queijo, ins_bacon, ins_batata])
        db.flush()

        # Produtos
        p1 = Produto(tenant_id=novo_tenant.id, codigo="BUR-01", nome="Cheeseburger Clássico", categoria="Hambúrguer", descricao="Pão brioche, blend 160g e cheddar derretido", preco_salao=28.00, preco_ifood=34.00)
        p2 = Produto(tenant_id=novo_tenant.id, codigo="BUR-02", nome="Bacon Cheddar Burger", categoria="Hambúrguer", descricao="Pão brioche, blend 160g, cheddar e tiras de bacon crocante", preco_salao=34.00, preco_ifood=42.00)
        p3 = Produto(tenant_id=novo_tenant.id, codigo="BAT-01", nome="Batata Frita Individual 150g", categoria="Acompanhamentos", descricao="Batata sequinha e crocante", preco_salao=14.00, preco_ifood=18.00)
        p4 = Produto(tenant_id=novo_tenant.id, codigo="BEB-01", nome="Refrigerante Lata 350ml", categoria="Bebidas", descricao="Coca-Cola, Guaraná ou Fanta", preco_salao=7.00, preco_ifood=9.00)
        
        db.add_all([p1, p2, p3, p4])
        db.flush()

        # Fichas técnicas modelo
        ft1 = [FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_pao.id, quantidade=1), FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_carne.id, quantidade=160), FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_queijo.id, quantidade=40)]
        ft2 = [FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_pao.id, quantidade=1), FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_carne.id, quantidade=160), FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_queijo.id, quantidade=40), FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_bacon.id, quantidade=40)]
        ft3 = [FichaTecnicaItem(produto_id=p3.id, insumo_id=ins_batata.id, quantidade=150)]
        
        db.add_all(ft1 + ft2 + ft3)

    db.commit()
    db.refresh(novo_tenant)

    return {
        "sucesso": True,
        "mensagem": f"Restaurante '{novo_tenant.nome}' cadastrado com sucesso!",
        "tenant_id": novo_tenant.id,
        "slug": novo_tenant.slug,
        "dono_email": user_dono.email,
        "links": {
            "painel": "https://nalimgestao.com.br/login",
            "garcom": "https://nalimgestao.com.br/garcom",
            "cardapio": f"https://nalimgestao.com.br/cardapio?tenant={novo_tenant.slug}"
        }
    }

# 4. Atualizar Dados / Status do Cliente
@router.put("/tenants/{tenant_id}")
def atualizar_cliente(
    tenant_id: int,
    dados: TenantUpdateInput,
    db: Session = Depends(get_db),
    admin: User = Depends(verificar_acesso_master)
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    if dados.nome is not None: tenant.nome = dados.nome
    if dados.cnpj is not None: tenant.cnpj = dados.cnpj
    if dados.slug is not None:
        novo_slug = slugify(dados.slug)
        existente = db.query(Tenant).filter(Tenant.slug == novo_slug, Tenant.id != tenant_id).first()
        if existente:
            raise HTTPException(status_code=400, detail="Este slug já está sendo utilizado por outro restaurante.")
        tenant.slug = novo_slug
    if dados.responsavel is not None: tenant.responsavel = dados.responsavel
    if dados.telefone is not None: tenant.telefone = dados.telefone
    if dados.email_contato is not None: tenant.email_contato = dados.email_contato
    if dados.plano is not None: tenant.plano = dados.plano
    if dados.valor_mensalidade is not None: tenant.valor_mensalidade = dados.valor_mensalidade
    if dados.status is not None: tenant.status = dados.status.upper()
    if dados.vencimento_mensalidade is not None: tenant.vencimento_mensalidade = dados.vencimento_mensalidade
    if dados.observacoes is not None: tenant.observacoes = dados.observacoes

    # Reset de senha do dono se solicitado
    if dados.nova_senha_dono:
        dono = db.query(User).filter(User.tenant_id == tenant.id, User.role == "dono").first()
        if dono:
            dono.senha_hash = hash_password(dados.nova_senha_dono)

    db.commit()
    db.refresh(tenant)

    return {"sucesso": True, "mensagem": f"Dados de '{tenant.nome}' atualizados com sucesso."}

# 5. Impersonation: Acessar Painel do Cliente como Dono (1 Clique)
@router.post("/tenants/{tenant_id}/impersonate")
def impersonar_cliente(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(verificar_acesso_master)
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    dono = db.query(User).filter(User.tenant_id == tenant.id, User.role == "dono").first()
    if not dono:
        # Se não houver dono cadastrado, cria um usuário dono para o tenant
        dono = User(
            tenant_id=tenant.id,
            nome=tenant.responsavel or f"Dono {tenant.nome}",
            email=tenant.email_contato or f"dono@{tenant.slug}.com.br",
            senha_hash=hash_password("nalim123"),
            role="dono",
            ativo=True
        )
        db.add(dono)
        db.commit()
        db.refresh(dono)

    # Cria token válido daquele cliente
    token = create_access_token(data={
        "sub": str(dono.id),
        "role": dono.role,
        "tenant_id": tenant.id,
        "impersonated_by": admin.email
    })

    return {
        "sucesso": True,
        "access_token": token,
        "nome": dono.nome,
        "role": dono.role,
        "tenant_nome": tenant.nome,
        "tenant_slug": tenant.slug,
        "redirect_url": "/app"
    }

# 6. Excluir / Suspender Cliente
@router.delete("/tenants/{tenant_id}")
def suspender_ou_remover_cliente(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(verificar_acesso_master)
):
    if tenant_id == 1:
        raise HTTPException(status_code=400, detail="Não é permitido excluir o Tenant Matriz NALIM.")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    tenant.status = "SUSPENSO"
    db.commit()

    return {"sucesso": True, "mensagem": f"Restaurante '{tenant.nome}' foi marcado como SUSPENSO."}
