from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_api():
    print("=== 1. Testando Root & Health ===")
    r_html = client.get("/")
    assert r_html.status_code == 200
    r_garcom = client.get("/garcom")
    assert r_garcom.status_code == 200
    r = client.get("/api/health")
    assert r.status_code == 200
    print("[OK] Root e App Garçom servindo HTML com sucesso!")
    print("[OK] Health status:", r.json()["status"])

    print("\n=== 2. Testando Autenticação dos 3 Perfis ===")
    r_dono = client.post("/api/auth/login", json={"email": "dono@nalim.com.br", "senha": "dono123"})
    assert r_dono.status_code == 200
    token_dono = r_dono.json()["access_token"]
    print("[OK] Dono autenticado! Role:", r_dono.json()["role"])

    r_gerente = client.post("/api/auth/login", json={"email": "gerente@nalim.com.br", "senha": "gerente123"})
    assert r_gerente.status_code == 200
    token_gerente = r_gerente.json()["access_token"]
    print("[OK] Gerente autenticado! Role:", r_gerente.json()["role"])

    r_operador = client.post("/api/auth/login", json={"email": "operador@nalim.com.br", "senha": "operador123"})
    assert r_operador.status_code == 200
    token_operador = r_operador.json()["access_token"]
    print("[OK] Operador autenticado! Role:", r_operador.json()["role"])

    print("\n=== 3. Testando Permissões Rigorosas (RBAC) ===")
    # Operador tentando acessar rota de Gerencial (DRE) -> DEVE RETORNAR 403
    h_op = {"Authorization": f"Bearer {token_operador}"}
    r_op_dre = client.get("/api/gerencial/dre", headers=h_op)
    assert r_op_dre.status_code == 403
    print("[OK] Operador bloqueado do Gerencial (403 Forbidden):", r_op_dre.json()["detail"])

    # Operador tentando acessar Fichas Técnicas no Administrativo -> DEVE RETORNAR 403
    r_op_adm = client.get("/api/admin/produtos", headers=h_op)
    assert r_op_adm.status_code == 403
    print("[OK] Operador bloqueado do Administrativo (403 Forbidden):", r_op_adm.json()["detail"])

    # Gerente tentando acessar Gerencial (DRE) -> DEVE RETORNAR 403
    h_ger = {"Authorization": f"Bearer {token_gerente}"}
    r_ger_dre = client.get("/api/gerencial/dre", headers=h_ger)
    assert r_ger_dre.status_code == 403
    print("[OK] Gerente bloqueado do Gerencial (403 Forbidden):", r_ger_dre.json()["detail"])

    # Gerente acessando Fichas Técnicas no Administrativo -> DEVE RETORNAR 200
    r_ger_prods = client.get("/api/admin/produtos", headers=h_ger)
    assert r_ger_prods.status_code == 200
    print(f"[OK] Gerente acessou Administrativo: {len(r_ger_prods.json())} produtos retornados com CMV e margem!")

    # Dono acessando DRE no Gerencial -> DEVE RETORNAR 200
    h_dono = {"Authorization": f"Bearer {token_dono}"}
    r_dono_dre = client.get("/api/gerencial/dre?mes=2026-08&regime=ME_6", headers=h_dono)
    assert r_dono_dre.status_code == 200
    dre_data = r_dono_dre.json()
    print("[OK] Dono acessou DRE com sucesso!")
    print(f"     Receita Bruta: R$ {dre_data['receita_bruta']}")
    print(f"     CMV: R$ {dre_data['cmv_total']}")
    print(f"     Custos Fixos: R$ {dre_data['custos_fixos_total']}")
    print(f"     Resultado Líquido: R$ {dre_data['resultado_liquido']} ({dre_data['margem_liquida_pct']}%)")
    print(f"     Score Saúde Nalim: {dre_data['score_saude_nalim']}/100 ({dre_data['classificacao_saude']})")

    print("\n=== 4. Testando Criação de Pedido Operacional com Adicionais ===")
    pedido_novo = {
        "canal": "iFood",
        "identificacao": "Pedido iFood #9055",
        "ifood_order_id": "#9055",
        "ifood_cliente": "Juliana M.",
        "forma_pagto": "PIX",
        "itens": [
            {
                "produto_codigo": "PRD-02",
                "quantidade": 1,
                "modificacoes": "SEM Cebola • + EXTRA: Bacon Crocante",
                "preco_unitario": 45.00
            }
        ]
    }
    r_ped = client.post("/api/operacional/pedidos", json=pedido_novo, headers=h_op)
    assert r_ped.status_code == 200
    print("[OK] Pedido criado com sucesso:", r_ped.json())

    print("\n=== 5. Testando KDS (Cozinha em Tempo Real) ===")
    r_kds = client.get("/api/operacional/kds", headers=h_op)
    assert r_kds.status_code == 200
    print(f"[OK] KDS retornou {r_kds.json()['total_em_espera']} pedidos na chapa!")

    print("\n=== 6. Testando Webhook Oficial iFood (Injeção Direta) ===")
    webhook_payload = {
        "orderId": "#7712",
        "customer": {"name": "Rodrigo Alves"},
        "items": [
            {"name": "Burger Bacon Supremo", "quantity": 2, "price": 45.0, "observations": "Ponto menos"}
        ],
        "total": {"orderAmount": 90.0}
    }
    r_ifood = client.post("/api/ifood/webhook", json=webhook_payload)
    assert r_ifood.status_code == 200
    print("\n=== 7. Testando SaaS Master SuperAdmin (nalimgestao.com.br) ===")
    r_master = client.post("/api/auth/login", json={"email": "admin@nalimgestao.com.br", "senha": "nalim2026master"})
    assert r_master.status_code == 200
    token_master = r_master.json()["access_token"]
    assert r_master.json()["role"] == "master"
    print("[OK] SuperAdmin Master autenticado!")

    h_master = {"Authorization": f"Bearer {token_master}"}
    r_stats = client.get("/api/master/stats", headers=h_master)
    assert r_stats.status_code == 200
    print(f"[OK] Master Stats: {r_stats.json()['total_clientes']} clientes | MRR R$ {r_stats.json()['mrr_recorrente']}")

    # Criando novo cliente restaurante pelo painel master com timestamp para idempotência
    import time
    ts = int(time.time())
    novo_cliente = {
        "nome": f"Pizzaria Bella Napoli {ts}",
        "slug": f"bella-napoli-{ts}",
        "responsavel": "Marco Antonio",
        "telefone": "(11) 98888-7777",
        "plano": "PRO",
        "valor_mensalidade": 199.0,
        "status": "ATIVO",
        "vencimento_mensalidade": "10",
        "email_dono": f"marco_{ts}@bellanapoli.com.br",
        "senha_dono": "napoli_senha_123",
        "clonar_cardapio_modelo": True
    }
    r_create_tenant = client.post("/api/master/tenants", json=novo_cliente, headers=h_master)
    assert r_create_tenant.status_code == 200
    tenant_criado = r_create_tenant.json()
    tenant_id = tenant_criado["tenant_id"]
    print(f"[OK] Novo cliente criado com sucesso! ID: {tenant_id} - Slug: {tenant_criado['slug']}")

    # Testando Impersonation (login direto sem senha)
    r_impersonate = client.post(f"/api/master/tenants/{tenant_id}/impersonate", headers=h_master)
    assert r_impersonate.status_code == 200
    token_impersonate = r_impersonate.json()["access_token"]
    assert r_impersonate.json()["tenant_slug"] == tenant_criado["slug"]
    print(f"[OK] Impersonation executado com sucesso! Token gerado para tenant {r_impersonate.json()['tenant_nome']}")

    # Testando isolamento: acessando produtos da Bella Napoli com o token impersonado
    h_cliente = {"Authorization": f"Bearer {token_impersonate}"}
    r_prods_cliente = client.get("/api/admin/produtos", headers=h_cliente)
    assert r_prods_cliente.status_code == 200
    print(f"[OK] Cliente isolado acessado com sucesso! Produtos cadastrados: {len(r_prods_cliente.json())}")

    print("\n=======================================================")
    print("TODOS OS TESTES DO BACKEND PASSARAM COM 100% DE SUCESSO!")
    print("=======================================================")


if __name__ == "__main__":
    test_full_api()
