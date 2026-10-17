import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nalim_food.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def executar_migracoes(db_engine):
    """Garante que a coluna solicitante e tabelas existam no banco sem falhas de migração no Render."""
    try:
        from sqlalchemy import text
        with db_engine.connect() as conn:
            try:
                res = conn.execute(text("PRAGMA table_info(pedidos)")).fetchall()
                colunas = [r[1] for r in res]
                if colunas and "solicitante" not in colunas:
                    conn.execute(text("ALTER TABLE pedidos ADD COLUMN solicitante VARCHAR(100) DEFAULT 'Balcão'"))
                    conn.commit()
            except Exception:
                pass

            try:
                # Garante criação da tabela push_subscriptions se ainda não existir
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS push_subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        garcom_id VARCHAR(100) NOT NULL DEFAULT 'garcom',
                        endpoint TEXT NOT NULL UNIQUE,
                        subscription_json TEXT NOT NULL,
                        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
            except Exception:
                pass

            try:
                # Garante que custos_fixos tenha as colunas de data_vencimento, dia_vencimento e encaminhar_previsao
                res_cf = conn.execute(text("PRAGMA table_info(custos_fixos)")).fetchall()
                colunas_cf = [r[1] for r in res_cf]
                if colunas_cf:
                    if "data_vencimento" not in colunas_cf:
                        conn.execute(text("ALTER TABLE custos_fixos ADD COLUMN data_vencimento VARCHAR(10) NULL"))
                    if "dia_vencimento" not in colunas_cf:
                        conn.execute(text("ALTER TABLE custos_fixos ADD COLUMN dia_vencimento INTEGER NULL"))
                    if "encaminhar_previsao" not in colunas_cf:
                        conn.execute(text("ALTER TABLE custos_fixos ADD COLUMN encaminhar_previsao BOOLEAN DEFAULT 1"))
                    conn.commit()
            except Exception:
                pass

            try:
                # Garante que tenants tenha as colunas para gestão SaaS Multi-tenant
                res_tn = conn.execute(text("PRAGMA table_info(tenants)")).fetchall()
                colunas_tn = [r[1] for r in res_tn]
                if colunas_tn:
                    if "telefone" not in colunas_tn:
                        conn.execute(text("ALTER TABLE tenants ADD COLUMN telefone VARCHAR(30) NULL"))
                    if "responsavel" not in colunas_tn:
                        conn.execute(text("ALTER TABLE tenants ADD COLUMN responsavel VARCHAR(100) NULL"))
                    if "email_contato" not in colunas_tn:
                        conn.execute(text("ALTER TABLE tenants ADD COLUMN email_contato VARCHAR(100) NULL"))
                    if "plano" not in colunas_tn:
                        conn.execute(text("ALTER TABLE tenants ADD COLUMN plano VARCHAR(50) DEFAULT 'PRO'"))
                    if "valor_mensalidade" not in colunas_tn:
                        conn.execute(text("ALTER TABLE tenants ADD COLUMN valor_mensalidade FLOAT DEFAULT 199.0"))
                    if "status" not in colunas_tn:
                        conn.execute(text("ALTER TABLE tenants ADD COLUMN status VARCHAR(20) DEFAULT 'ATIVO'"))
                    if "vencimento_mensalidade" not in colunas_tn:
                        conn.execute(text("ALTER TABLE tenants ADD COLUMN vencimento_mensalidade VARCHAR(10) NULL"))
                    if "observacoes" not in colunas_tn:
                        conn.execute(text("ALTER TABLE tenants ADD COLUMN observacoes TEXT NULL"))
                    conn.commit()
            except Exception:
                pass

            try:
                # Garante que configuracoes_empresa tenha as colunas de taxas de cartão
                res_cfg = conn.execute(text("PRAGMA table_info(configuracoes_empresa)")).fetchall()
                colunas_cfg = [r[1] for r in res_cfg]
                if colunas_cfg:
                    if "taxa_debito" not in colunas_cfg:
                        conn.execute(text("ALTER TABLE configuracoes_empresa ADD COLUMN taxa_debito FLOAT DEFAULT 1.99"))
                    if "taxa_credito_vista" not in colunas_cfg:
                        conn.execute(text("ALTER TABLE configuracoes_empresa ADD COLUMN taxa_credito_vista FLOAT DEFAULT 3.49"))
                    if "taxa_credito_parcelado" not in colunas_cfg:
                        conn.execute(text("ALTER TABLE configuracoes_empresa ADD COLUMN taxa_credito_parcelado FLOAT DEFAULT 4.99"))
                    if "repassar_taxa_cartao" not in colunas_cfg:
                        conn.execute(text("ALTER TABLE configuracoes_empresa ADD COLUMN repassar_taxa_cartao BOOLEAN DEFAULT 0"))
                    conn.commit()
            except Exception:
                pass

            try:
                # Garante que usuarios tenha a coluna cargo
                res_usr = conn.execute(text("PRAGMA table_info(usuarios)")).fetchall()
                colunas_usr = [r[1] for r in res_usr]
                if colunas_usr and "cargo" not in colunas_usr:
                    conn.execute(text("ALTER TABLE usuarios ADD COLUMN cargo VARCHAR(100) DEFAULT 'Colaborador'"))
                    conn.commit()
            except Exception:
                pass
    except Exception:
        pass

executar_migracoes(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
