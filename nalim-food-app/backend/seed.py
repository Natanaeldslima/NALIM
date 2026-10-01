import datetime
from database import SessionLocal, engine, Base
from models import (
    Tenant, User, Insumo, Produto, FichaTecnicaItem, 
    Pedido, ItemPedido, CustoFixo, ConfiguracaoEmpresa
)
from auth import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Verifica se já está populado
    if db.query(Tenant).first():
        print("Banco de dados já possui dados.")
        db.close()
        return

    print("Iniciando Seed do Banco de Dados Nalim...")

    # 1. Tenant
    tenant = Tenant(
        nome="NALIM Hamburgueria & Bar",
        cnpj="42.891.023/0001-90",
        slug="nalim-hamburgueria"
    )
    db.add(tenant)
    db.flush()

    # 2. Configurações da Empresa
    config = ConfiguracaoEmpresa(
        tenant_id=tenant.id,
        regime_tributario="ME_6",
        dias_trabalhados_mes=26,
        meta_lucro_desejada=3000.0,
        aliquota_ifood=0.23
    )
    db.add(config)

    # 3. Usuários Padrão (3 Perfis)
    usuarios = [
        User(tenant_id=tenant.id, nome="Carlos Nalim (Dono)", email="dono@nalim.com.br", senha_hash=hash_password("dono123"), role="dono"),
        User(tenant_id=tenant.id, nome="Mariana Silva (Gerente)", email="gerente@nalim.com.br", senha_hash=hash_password("gerente123"), role="gerente"),
        User(tenant_id=tenant.id, nome="Pedro Lucas (Caixa/Garçom)", email="operador@nalim.com.br", senha_hash=hash_password("operador123"), role="operador"),
    ]
    db.add_all(usuarios)
    db.flush()

    # 4. Insumos (Mapeados da Planilha NALIM)
    insumos_data = [
        Insumo(tenant_id=tenant.id, codigo="INS-01", nome="Pão Brioche Artesanal", categoria="Pães", preco_compra=36.00, und_compra="pct 20un", und_uso="un", fator_conversao=20.0, custo_unitario=1.80, preco_venda_extra=0.0),
        Insumo(tenant_id=tenant.id, codigo="INS-02", nome="Blend Bovino Fresco 160g", categoria="Carnes", preco_compra=38.00, und_compra="kg", und_uso="g", fator_conversao=1000.0, custo_unitario=0.038, preco_venda_extra=10.0),
        Insumo(tenant_id=tenant.id, codigo="INS-03", nome="Queijo Cheddar Inglês Fatiado", categoria="Queijos", preco_compra=45.00, und_compra="kg", und_uso="g", fator_conversao=1000.0, custo_unitario=0.045, preco_venda_extra=3.50),
        Insumo(tenant_id=tenant.id, codigo="INS-04", nome="Bacon Artesanal Defumado", categoria="Carnes", preco_compra=42.00, und_compra="kg", und_uso="g", fator_conversao=1000.0, custo_unitario=0.042, preco_venda_extra=4.00),
        Insumo(tenant_id=tenant.id, codigo="INS-05", nome="Cebola Roxa Caramelizada", categoria="Hortifruti", preco_compra=8.50, und_compra="kg", und_uso="g", fator_conversao=1000.0, custo_unitario=0.0085, preco_venda_extra=2.00),
        Insumo(tenant_id=tenant.id, codigo="INS-06", nome="Molho Especial Nalim (Defumado)", categoria="Molhos", preco_compra=24.00, und_compra="litro", und_uso="ml", fator_conversao=1000.0, custo_unitario=0.024, preco_venda_extra=2.50),
        Insumo(tenant_id=tenant.id, codigo="INS-07", nome="Batata Palito Congelada", categoria="Acompanhamentos", preco_compra=28.00, und_compra="pct 2.5kg", und_uso="g", fator_conversao=2500.0, custo_unitario=0.0112, preco_venda_extra=5.00),
        Insumo(tenant_id=tenant.id, codigo="INS-08", nome="Embalagem Burger Térmica", categoria="Embalagens", preco_compra=65.00, und_compra="pct 100un", und_uso="un", fator_conversao=100.0, custo_unitario=0.65, preco_venda_extra=0.0),
        Insumo(tenant_id=tenant.id, codigo="INS-09", nome="Refrigerante Lata 350ml", categoria="Bebidas", preco_compra=3.10, und_compra="un", und_uso="un", fator_conversao=1.0, custo_unitario=3.10, preco_venda_extra=0.0),
    ]
    db.add_all(insumos_data)
    db.flush()

    ins_map = {i.codigo: i for i in insumos_data}

    # 5. Produtos e Fichas Técnicas
    p1 = Produto(tenant_id=tenant.id, codigo="PRD-01", nome="Burger Clássico Nalim", categoria="Hambúrguer", descricao="Pão brioche selado, blend 160g, queijo cheddar inglês, cebola roxa e molho especial.", preco_salao=32.00, preco_ifood=38.00)
    p2 = Produto(tenant_id=tenant.id, codigo="PRD-02", nome="Burger Bacon Supremo", categoria="Hambúrguer", descricao="Blend 160g, fatias crocantes de bacon artesanal, dobro de cheddar e molho especial da casa.", preco_salao=38.00, preco_ifood=45.00)
    p3 = Produto(tenant_id=tenant.id, codigo="PRD-03", nome="Combo Clássico (Burger + Fritas + Refri)", categoria="Combo", descricao="Burger clássico + porção de batatas fritas crocantes + refrigerante gelado.", preco_salao=46.00, preco_ifood=55.00)
    p4 = Produto(tenant_id=tenant.id, codigo="PRD-04", nome="Batata Frita Rústica (Porção)", categoria="Porção", descricao="Batatas fritas sequinhas temperadas com páprica doce e alecrim.", preco_salao=22.00, preco_ifood=26.00)
    p5 = Produto(tenant_id=tenant.id, codigo="PRD-05", nome="Coca-Cola Original 350ml", categoria="Bebida", descricao="Lata 350ml servida estupidamente gelada.", preco_salao=7.00, preco_ifood=8.50)

    db.add_all([p1, p2, p3, p4, p5])
    db.flush()

    # Fichas Técnicas (Receitas exatas)
    fichas = [
        # P1: Clássico
        FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_map["INS-01"].id, quantidade=1.0),
        FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_map["INS-02"].id, quantidade=160.0),
        FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_map["INS-03"].id, quantidade=40.0),
        FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_map["INS-05"].id, quantidade=30.0),
        FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_map["INS-06"].id, quantidade=30.0),
        FichaTecnicaItem(produto_id=p1.id, insumo_id=ins_map["INS-08"].id, quantidade=1.0),

        # P2: Bacon Supremo
        FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_map["INS-01"].id, quantidade=1.0),
        FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_map["INS-02"].id, quantidade=160.0),
        FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_map["INS-03"].id, quantidade=60.0),
        FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_map["INS-04"].id, quantidade=50.0),
        FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_map["INS-06"].id, quantidade=35.0),
        FichaTecnicaItem(produto_id=p2.id, insumo_id=ins_map["INS-08"].id, quantidade=1.0),

        # P3: Combo
        FichaTecnicaItem(produto_id=p3.id, insumo_id=ins_map["INS-01"].id, quantidade=1.0),
        FichaTecnicaItem(produto_id=p3.id, insumo_id=ins_map["INS-02"].id, quantidade=160.0),
        FichaTecnicaItem(produto_id=p3.id, insumo_id=ins_map["INS-03"].id, quantidade=40.0),
        FichaTecnicaItem(produto_id=p3.id, insumo_id=ins_map["INS-07"].id, quantidade=180.0),
        FichaTecnicaItem(produto_id=p3.id, insumo_id=ins_map["INS-09"].id, quantidade=1.0),
        FichaTecnicaItem(produto_id=p3.id, insumo_id=ins_map["INS-08"].id, quantidade=1.0),

        # P4: Batata
        FichaTecnicaItem(produto_id=p4.id, insumo_id=ins_map["INS-07"].id, quantidade=350.0),
        FichaTecnicaItem(produto_id=p4.id, insumo_id=ins_map["INS-08"].id, quantidade=1.0),

        # P5: Refri
        FichaTecnicaItem(produto_id=p5.id, insumo_id=ins_map["INS-09"].id, quantidade=1.0),
    ]
    db.add_all(fichas)

    # 6. Custos Fixos (Agosto 2026 e Setembro 2026)
    custos_agosto = [
        ("Ocupação / Aluguel", "Imobiliária Central", 2800.00),
        ("Energia Elétrica", "Enel / Concessionária", 1150.00),
        ("Água & Esgoto", "Sabesp / Sanepar", 280.00),
        ("Internet & Telefonia", "Vivo Fibra Empresas", 150.00),
        ("Sistema de Gestão", "NALIM Gestão Financeira SaaS", 180.00),
        ("Contabilidade", "Assessoria Contábil Silva", 650.00),
        ("Marketing & Ads", "Google Ads & Tráfego Local", 800.00),
        ("Pró-Labore Sócio", "Retirada Mensal Diretor", 3000.00),
    ]
    for cat, forn, val in custos_agosto:
        db.add(CustoFixo(tenant_id=tenant.id, mes_vigencia="2026-08", categoria=cat, fornecedor=forn, valor=val))
        db.add(CustoFixo(tenant_id=tenant.id, mes_vigencia="2026-09", categoria=cat, fornecedor=forn, valor=val * 1.05))
        db.add(CustoFixo(tenant_id=tenant.id, mes_vigencia="2026-10", categoria=cat, fornecedor=forn, valor=val * 1.05))

    # 7. Pedidos Iniciais de Exemplo no KDS
    ped1 = Pedido(
        tenant_id=tenant.id,
        numero_comanda=101,
        data_hora=datetime.datetime.utcnow() - datetime.timedelta(minutes=14),
        canal="Salão",
        identificacao="Mesa 04 (Salão)",
        forma_pagto="Cartão",
        valor_bruto=70.00,
        cmv_total=24.50,
        taxa_canal=1.40,
        lucro_liquido=44.10,
        status_kds="Na Chapa"
    )
    db.add(ped1)
    db.flush()

    db.add(ItemPedido(pedido_id=ped1.id, produto_id=p1.id, nome_produto="Burger Clássico Nalim", quantidade=1, preco_unitario=32.00, cmv_unitario=11.20, modificacoes="SEM Cebola Roxa"))
    db.add(ItemPedido(pedido_id=ped1.id, produto_id=p2.id, nome_produto="Burger Bacon Supremo", quantidade=1, preco_unitario=38.00, cmv_unitario=13.30, modificacoes="+ EXTRA: Bacon Crocante"))

    ped2 = Pedido(
        tenant_id=tenant.id,
        numero_comanda=102,
        data_hora=datetime.datetime.utcnow() - datetime.timedelta(minutes=6),
        canal="iFood",
        identificacao="Pedido iFood #4092 (Lucas R.)",
        ifood_order_id="#4092",
        ifood_cliente="Lucas R.",
        forma_pagto="iFood Pay",
        valor_bruto=55.00,
        cmv_total=17.80,
        taxa_canal=12.65,
        lucro_liquido=24.55,
        status_kds="Na Chapa"
    )
    db.add(ped2)
    db.flush()

    db.add(ItemPedido(pedido_id=ped2.id, produto_id=p3.id, nome_produto="Combo Clássico", quantidade=1, preco_unitario=55.00, cmv_unitario=17.80, modificacoes="Carne ao ponto • Coca bem gelada"))

    db.commit()
    db.close()
    print("Seed concluído com sucesso!")

if __name__ == "__main__":
    seed_database()
