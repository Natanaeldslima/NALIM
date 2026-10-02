import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from seed import seed_database
from routers import auth, operacional, administrativo, gerencial, ifood

# Cria tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NALIM — Gestão Financeira Food Service API",
    description="Backend completo para gestão operacional e financeira de restaurantes, hamburguerias e delivery.",
    version="1.0.0"
)

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminhos absolutos para as interfaces HTML
FRONTEND_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
GARCOM_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "garcom.html"))
LOGIN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "login.html"))
CARDAPIO_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cardapio.html"))

# Auto-seed no startup
@app.on_event("startup")
def startup_event():
    seed_database()

# Inclusão dos Roteadores da API
app.include_router(auth.router)
app.include_router(operacional.router)
app.include_router(administrativo.router)
app.include_router(gerencial.router)
app.include_router(ifood.router)

# Rota Raiz: Serve tela de Login como porta de entrada
@app.get("/")
def serve_root():
    if os.path.exists(LOGIN_FILE):
        return FileResponse(LOGIN_FILE)
    elif os.path.exists(FRONTEND_FILE):
        return FileResponse(FRONTEND_FILE)
    return {"mensagem": "Interface NALIM não encontrada."}

# Rota do Login Oficial
@app.get("/login")
def serve_login():
    if os.path.exists(LOGIN_FILE):
        return FileResponse(LOGIN_FILE)
    return {"mensagem": "Arquivo login.html não encontrado."}

# Rota do Sistema de Gestão (Dono & Gerente)
@app.get("/app")
def serve_app():
    if os.path.exists(FRONTEND_FILE):
        return FileResponse(FRONTEND_FILE)
    return {"mensagem": "Arquivo index.html não encontrado."}

# Rota do Aplicativo Mobile do Garçom (Comanda Digital no celular)
@app.get("/garcom")
def serve_garcom():
    if os.path.exists(GARCOM_FILE):
        return FileResponse(GARCOM_FILE)
    return {"mensagem": "Arquivo garcom.html não encontrado."}

# Rota do Cardápio Digital & Delivery Próprio (WhatsApp)
@app.get("/cardapio")
@app.get("/delivery")
def serve_cardapio():
    if os.path.exists(CARDAPIO_FILE):
        return FileResponse(CARDAPIO_FILE)
    return {"mensagem": "Arquivo cardapio.html não encontrado."}

@app.get("/api")
def api_info():
    return {
        "sistema": "NALIM Gestão Financeira Food Service",
        "versao": "1.0.0",
        "status": "Online",
        "docs": "/docs",
        "perfis_padrao": {
            "dono": "dono@nalim.com.br / dono123",
            "gerente": "gerente@nalim.com.br / gerente123",
            "operador": "operador@nalim.com.br / operador123"
        }
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "banco_de_dados": "conectado"}
