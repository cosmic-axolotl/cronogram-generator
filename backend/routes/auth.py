from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from auth import (
    create_access_token,
    get_current_professor,
    hash_password,
    verify_password,
)
from database import get_session
from models import Professor, ProfessorCreate, ProfessorPublic, Settings

router = APIRouter(prefix="/auth", tags=["auth"])


def is_registration_open(session: Session) -> bool:
    """Lê a configuração open_registration da tabela settings.
    Padrão: True (registro aberto). Para fechar, setar value='false'."""
    setting = session.exec(
        select(Settings).where(Settings.key == "open_registration")
    ).first()
    if not setting:
        return True  # padrão: aberto
    return setting.value.lower() == "true"


@router.post("/register", response_model=ProfessorPublic, status_code=201)
def register(data: ProfessorCreate, session: Session = Depends(get_session)):
    # Verificar se registro está aberto
    if not is_registration_open(session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registro desativado. Entre em contato com o administrador.",
        )

    # Verificar duplicata de email
    existing = session.exec(
        select(Professor).where(Professor.email == data.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado.",
        )

    professor = Professor(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    session.add(professor)
    session.commit()
    session.refresh(professor)
    return professor


@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    professor = session.exec(
        select(Professor).where(Professor.email == form.username)
    ).first()

    if not professor or not verify_password(form.password, professor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not professor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada.",
        )

    token = create_access_token(professor.id, professor.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "professor": {
            "id": professor.id,
            "name": professor.name,
            "email": professor.email,
        },
    }


@router.get("/me", response_model=ProfessorPublic)
def me(current: Professor = Depends(get_current_professor)):
    return current