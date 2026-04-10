from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from database import get_session
from models import Cronograma, CronogramaPublic, Professor, SearchResult, Turma

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/search", response_model=list[SearchResult])
def search(
    q: str = Query(default="", min_length=0, max_length=100),
    session: Session = Depends(get_session),
):
    """Busca pública — retorna apenas cronogramas publicados.
    Aceita termo livre: corresponde a código da disciplina, nome ou professor."""
    term = f"%{q.strip().lower()}%"

    # Join turmas + professors + cronogramas filtrando publicado=True
    results = session.exec(
        select(Turma, Professor, Cronograma)
        .join(Professor, Turma.professor_id == Professor.id)
        .join(Cronograma, Cronograma.turma_id == Turma.id)
        .where(Cronograma.publicado == True)  # noqa: E712
        .where(Professor.is_active == True)   # noqa: E712
    ).all()

    out = []
    for turma, prof, crono in results:
        # Filtrar pelo termo (se fornecido)
        if q.strip():
            haystack = (
                turma.codigo.lower()
                + turma.nome.lower()
                + turma.semestre.lower()
                + prof.name.lower()
            )
            if term.strip("%") not in haystack:
                continue
        out.append(
            SearchResult(
                turma_id=turma.id,
                cronograma_id=crono.id,
                codigo=turma.codigo,
                nome=turma.nome,
                semestre=turma.semestre,
                professor_name=prof.name,
                updated_at=crono.updated_at,
            )
        )

    # Ordenar por semestre (mais recente primeiro) e código
    out.sort(key=lambda r: (r.semestre, r.codigo), reverse=True)
    return out


@router.get("/turmas/{codigo}/{semestre}", response_model=CronogramaPublic)
def get_turma_publica(
    codigo: str,
    semestre: str,
    session: Session = Depends(get_session),
):
    """Retorna o cronograma publicado de uma turma pelo código e semestre.
    Usado pela tela /turmas/OVL514/2026.2 no frontend."""
    turma = session.exec(
        select(Turma).where(
            Turma.codigo == codigo.upper(),
            Turma.semestre == semestre,
        )
    ).first()

    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")

    crono = session.exec(
        select(Cronograma).where(
            Cronograma.turma_id == turma.id,
            Cronograma.publicado == True,  # noqa: E712
        )
    ).first()

    if not crono:
        raise HTTPException(
            status_code=404,
            detail="Cronograma não publicado ou não encontrado.",
        )
    return crono


@router.get("/turmas/{codigo}/{semestre}/meta")
def get_turma_meta(
    codigo: str,
    semestre: str,
    session: Session = Depends(get_session),
):
    """Retorna metadados públicos da turma (professor, última atualização).
    Usado pelo cabeçalho da tela de visualização pública."""
    turma = session.exec(
        select(Turma).where(
            Turma.codigo == codigo.upper(),
            Turma.semestre == semestre,
        )
    ).first()
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")

    prof = session.get(Professor, turma.professor_id)
    crono = session.exec(
        select(Cronograma).where(
            Cronograma.turma_id == turma.id,
            Cronograma.publicado == True,  # noqa: E712
        )
    ).first()
    if not crono:
        raise HTTPException(status_code=404, detail="Cronograma não publicado.")

    return {
        "codigo": turma.codigo,
        "nome": turma.nome,
        "semestre": turma.semestre,
        "professor": prof.name if prof else "—",
        "updated_at": crono.updated_at.strftime("%d/%m/%Y"),
    }