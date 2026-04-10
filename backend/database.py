import os
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./ovl_cronogramas.db"  # fallback local para dev
)

# psycopg2 usa postgresql://, SQLAlchemy aceita postgresql+psycopg2://
# Render entrega DATABASE_URL com postgres:// — corrigir se necessário
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session