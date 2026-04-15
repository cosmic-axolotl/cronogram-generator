import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import create_db_and_tables, engine
from models import Settings
from routes import auth, cronogramas, professor, public


# ── lifespan: inicialização do banco ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    _seed_settings()
    yield


def _seed_settings():
    """Garante que a config open_registration existe com valor padrão."""
    with Session(engine) as session:
        existing = session.exec(
            select(Settings).where(Settings.key == "open_registration")
        ).first()
        if not existing:
            session.add(Settings(key="open_registration", value="true"))
            session.commit()


# ── app ───────────────────────────────────────────────────────────
app = FastAPI(
    title="OVL Cronogramas API",
    description="API de cronogramas acadêmicos — Observatório do Valongo · UFRJ",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — inclui GitHub Pages e localhost para dev
# Em produção, setar variável de ambiente ALLOWED_ORIGINS com as origens desejadas
_default_origins = ",".join([
    "https://cosmic-axolotl.github.io",  # GitHub Pages
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
    "null",  # file:// abre como "null" no browser
])
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ── rotas ─────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(professor.router)
app.include_router(cronogramas.router)
app.include_router(public.router)


@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "app": "OVL Cronogramas API",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
