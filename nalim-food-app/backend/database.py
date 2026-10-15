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
    except Exception:
        pass

executar_migracoes(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
