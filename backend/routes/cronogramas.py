from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from auth import get_current_professor
from database import get_session
from models import Cronograma, CronogramaCreate, CronogramaPublic, Professor, Turma

router = APIRouter(prefix="/cronogramas", tags=["cronogramas"])


def _get_own_cronograma(turma_id: int, professor_id: int, session: Session) -> Turma:
    """Verifica que a turma pertence ao professor."""
    turma = session.get(Turma, turma_id)
    if not turma or turma.professor_id != professor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada.",
        )
    return turma


@router.get("/{turma_id}", response_model=CronogramaPublic)
def get_cronograma(
    turma_id: int,
    current: Professor = Depends(get_current_professor),
    session: Session = Depends(get_session),
):
    """Retorna o cronograma (rascunho ou publicado) de uma turma do professor."""
    _get_own_cronograma(turma_id, current.id, session)

    crono = session.exec(
        select(Cronograma).where(Cronograma.turma_id == turma_id)
    ).first()
    if not crono:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado.")
    return crono


@router.put("/{turma_id}/salvar", response_model=CronogramaPublic)
def salvar(
    turma_id: int,
    data: CronogramaCreate,
    current: Professor = Depends(get_current_professor),
    session: Session = Depends(get_session),
):
    """Salva (ou atualiza) o rascunho do cronograma. Não publica."""
    _get_own_cronograma(turma_id, current.id, session)

    crono = session.exec(
        select(Cronograma).where(Cronograma.turma_id == turma_id)
    ).first()

    if crono:
        crono.config_json = data.config_json
        crono.updated_at = datetime.utcnow()
    else:
        crono = Cronograma(
            turma_id=turma_id,
            config_json=data.config_json,
            publicado=False,
        )
    session.add(crono)
    session.commit()
    session.refresh(crono)
    return crono


@router.post("/{turma_id}/publicar", response_model=CronogramaPublic)
def publicar(
    turma_id: int,
    data: CronogramaCreate,
    current: Professor = Depends(get_current_professor),
    session: Session = Depends(get_session),
):
    """Salva e publica o cronograma — torna visível na URL pública."""
    _get_own_cronograma(turma_id, current.id, session)

    crono = session.exec(
        select(Cronograma).where(Cronograma.turma_id == turma_id)
    ).first()

    if crono:
        crono.config_json = data.config_json
        crono.publicado = True
        crono.updated_at = datetime.utcnow()
    else:
        crono = Cronograma(
            turma_id=turma_id,
            config_json=data.config_json,
            publicado=True,
        )
    session.add(crono)
    session.commit()
    session.refresh(crono)
    return crono


@router.post("/{turma_id}/despublicar", response_model=CronogramaPublic)
def despublicar(
    turma_id: int,
    current: Professor = Depends(get_current_professor),
    session: Session = Depends(get_session),
):
    """Remove o cronograma da visualização pública (volta para rascunho)."""
    _get_own_cronograma(turma_id, current.id, session)

    crono = session.exec(
        select(Cronograma).where(Cronograma.turma_id == turma_id)
    ).first()
    if not crono:
        raise HTTPException(status_code=404, detail="Cronograma não encontrado.")

    crono.publicado = False
    crono.updated_at = datetime.utcnow()
    session.add(crono)
    session.commit()
    session.refresh(crono)
    return crono