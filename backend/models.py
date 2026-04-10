from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import json


# ── professors ────────────────────────────────────────────────────
class ProfessorBase(SQLModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(unique=True, index=True, max_length=200)


class Professor(ProfessorBase, table=True):
    __tablename__ = "professors"
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


class ProfessorCreate(ProfessorBase):
    password: str = Field(min_length=6, max_length=128)


class ProfessorPublic(ProfessorBase):
    id: int
    created_at: datetime


# ── turmas ────────────────────────────────────────────────────────
class TurmaBase(SQLModel):
    codigo: str = Field(max_length=20)   # ex: OVL514
    nome: str = Field(max_length=200)
    semestre: str = Field(max_length=10)  # ex: 2026.2


class Turma(TurmaBase, table=True):
    __tablename__ = "turmas"
    id: Optional[int] = Field(default=None, primary_key=True)
    professor_id: int = Field(foreign_key="professors.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TurmaCreate(TurmaBase):
    pass


class TurmaPublic(TurmaBase):
    id: int
    professor_id: int


# ── cronogramas ───────────────────────────────────────────────────
class CronogramaBase(SQLModel):
    turma_id: int = Field(foreign_key="turmas.id")
    config_json: str = Field(default="{}")  # JSON com toda a config do editor
    publicado: bool = Field(default=False)


class Cronograma(CronogramaBase, table=True):
    __tablename__ = "cronogramas"
    id: Optional[int] = Field(default=None, primary_key=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CronogramaCreate(SQLModel):
    config_json: str  # JSON serializado do editor


class CronogramaPublic(SQLModel):
    id: int
    turma_id: int
    config_json: str
    publicado: bool
    updated_at: datetime


# ── settings (registro aberto vs admin) ───────────────────────────
class Settings(SQLModel, table=True):
    __tablename__ = "settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True, max_length=100)
    value: str = Field(max_length=500)


# ── modelos de resposta da busca pública ──────────────────────────
class SearchResult(SQLModel):
    turma_id: int
    cronograma_id: int
    codigo: str
    nome: str
    semestre: str
    professor_name: str
    updated_at: datetime