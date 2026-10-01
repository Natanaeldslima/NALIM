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
    print("[OK] Webhook iFood processou pedido automaticamente:", r_ifood.json())

    print("\n=======================================================")
    print("TODOS OS TESTES DO BACKEND PASSARAM COM 100% DE SUCESSO!")
    print("=======================================================")

if __name__ == "__main__":
    test_full_api()
