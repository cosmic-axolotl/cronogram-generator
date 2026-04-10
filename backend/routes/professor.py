from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth import get_current_professor
from database import get_session
from models import Professor, Turma, TurmaCreate, TurmaPublic

router = APIRouter(prefix="/professor", tags=["professor"])


@router.get("/turmas", response_model=list[TurmaPublic])
def list_turmas(
    current: Professor = Depends(get_current_professor),
    session: Session = Depends(get_session),
):
    """Lista todas as turmas do professor logado."""
    turmas = session.exec(
        select(Turma).where(Turma.professor_id == current.id)
    ).all()
    return turmas


@router.post("/turmas", response_model=TurmaPublic, status_code=201)
def create_turma(
    data: TurmaCreate,
    current: Professor = Depends(get_current_professor),
    session: Session = Depends(get_session),
):
    """Cria uma nova turma para o professor logado."""
    # Verificar duplicata (mesmo professor, mesmo código, mesmo semestre)
    existing = session.exec(
        select(Turma).where(
            Turma.professor_id == current.id,
            Turma.codigo == data.codigo,
            Turma.semestre == data.semestre,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Turma {data.codigo} já cadastrada para {data.semestre}.",
        )

    turma = Turma(**data.model_dump(), professor_id=current.id)
    session.add(turma)
    session.commit()
    session.refresh(turma)
    return turma


@router.put("/turmas/{turma_id}", response_model=TurmaPublic)
def update_turma(
    turma_id: int,
    data: TurmaCreate,
    current: Professor = Depends(get_current_professor),
    session: Session = Depends(get_session),
):
    turma = _get_own_turma(turma_id, current.id, session)
    for key, value in data.model_dump().items():
        setattr(turma, key, value)
    session.add(turma)
    session.commit()
    session.refresh(turma)
    return turma


@router.delete("/turmas/{turma_id}", status_code=204)
def delete_turma(
    turma_id: int,
    current: Professor = Depends(get_current_professor),
    session: Session = Depends(get_session),
):
    turma = _get_own_turma(turma_id, current.id, session)
    session.delete(turma)
    session.commit()


# ── helper ────────────────────────────────────────────────────────
def _get_own_turma(turma_id: int, professor_id: int, session: Session) -> Turma:
    turma = session.get(Turma, turma_id)
    if not turma or turma.professor_id != professor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada.",
        )
    return turma