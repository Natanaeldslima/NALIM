from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse, UserResponse
from auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])

@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == dados.email, User.ativo == True).first()
    if not user or not verify_password(dados.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role, "tenant_id": user.tenant_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "nome": user.nome,
        "tenant_slug": user.tenant.slug
    }

@router.post("/token", response_model=TokenResponse)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username, User.ativo == True).first()
    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role, "tenant_id": user.tenant_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "nome": user.nome,
        "tenant_slug": user.tenant.slug
    }

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email,
        "role": current_user.role
    }
