import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, executar_migracoes
from seed import seed_database
from routers import auth, operacional, administrativo, gerencial, ifood, master_admin

# Cria tabelas no banco de dados e executa migrações
Base.metadata.create_all(bind=engine)
executar_migracoes(engine)

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
ADMIN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "admin.html"))
LANDING_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "landing-page.html"))
SW_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sw.js"))

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
app.include_router(master_admin.router)

NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}

# Rota Raiz: Serve tela de Login como porta de entrada
@app.get("/")
def serve_root():
    if os.path.exists(LOGIN_FILE):
        return FileResponse(LOGIN_FILE, headers=NO_CACHE_HEADERS)
    elif os.path.exists(FRONTEND_FILE):
        return FileResponse(FRONTEND_FILE, headers=NO_CACHE_HEADERS)
    return {"mensagem": "Interface NALIM não encontrada."}

# Rota do Login Oficial
@app.get("/login")
@app.get("/login.html")
def serve_login():
    if os.path.exists(LOGIN_FILE):
        return FileResponse(LOGIN_FILE, headers=NO_CACHE_HEADERS)
    return {"mensagem": "Arquivo login.html não encontrado."}

# Rota da Landing Page Comercial (Apresentação & Vendas)
@app.get("/landing")
@app.get("/landing-page")
@app.get("/landing-page.html")
@app.get("/sobre")
@app.get("/planos")
@app.get("/site")
@app.get("/vendas")
def serve_landing():
    if os.path.exists(LANDING_FILE):
        return FileResponse(LANDING_FILE, headers=NO_CACHE_HEADERS)
    return {"mensagem": "Arquivo landing-page.html não encontrado."}

# Rota do Sistema de Gestão (Dono & Gerente)
@app.get("/app")
@app.get("/index.html")
def serve_app():
    if os.path.exists(FRONTEND_FILE):
        return FileResponse(FRONTEND_FILE, headers=NO_CACHE_HEADERS)
    return {"mensagem": "Arquivo index.html não encontrado."}

# Rota do Aplicativo Mobile do Garçom (Comanda Digital no celular)
@app.get("/garcom")
def serve_garcom():
    if os.path.exists(GARCOM_FILE):
        return FileResponse(GARCOM_FILE, headers=NO_CACHE_HEADERS)
    return {"mensagem": "Arquivo garcom.html não encontrado."}

# Rota do Cardápio Digital & Delivery Próprio (WhatsApp)
@app.get("/cardapio")
@app.get("/delivery")
def serve_cardapio():
    if os.path.exists(CARDAPIO_FILE):
        return FileResponse(CARDAPIO_FILE, headers=NO_CACHE_HEADERS)
    return {"mensagem": "Arquivo cardapio.html não encontrado."}

# Rota do Portal Master SaaS (SuperAdmin / Dono do Software)
@app.get("/admin")
@app.get("/master")
def serve_admin():
    if os.path.exists(ADMIN_FILE):
        return FileResponse(ADMIN_FILE, headers=NO_CACHE_HEADERS)
    return {"mensagem": "Arquivo admin.html não encontrado."}

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

# Service Worker servido na raiz do domínio com escopo global "/"
@app.get("/sw.js")
def serve_service_worker():
    if os.path.exists(SW_FILE):
        return FileResponse(
            SW_FILE,
            media_type="application/javascript",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Service-Worker-Allowed": "/"
            }
        )
    return FileResponse(FRONTEND_FILE, media_type="application/javascript")

# Endpoints diretos de Web Push (compatíveis com /api/subscribe e /api/vapid-public-key)
@app.get("/api/vapid-public-key")
def get_vapid_key_root():
    from push_service import VAPID_PUBLIC_KEY
    return {"public_key": VAPID_PUBLIC_KEY}

@app.post("/api/subscribe")
def subscribe_push_root(dados: dict):
    from push_service import salvar_subscription
    garcom = dados.get("garcom", "Garçom")
    subscription = dados.get("subscription")
    sucesso = salvar_subscription(garcom, subscription)
    return {"sucesso": sucesso}

@app.post("/api/push-test")
def test_push_root(dados: dict = None):
    from push_service import enviar_push_teste
    garcom = (dados or {}).get("garcom", "Garçom")
    enviar_push_teste(garcom)
    return {"sucesso": True, "mensagem": "Push de teste disparado com sucesso."}

