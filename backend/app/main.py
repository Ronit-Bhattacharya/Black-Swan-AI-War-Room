import json
import uuid

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from .classifier import classify_case
from .planner import build_investigation_plan
from .orchestrator import run_orchestration
from .config import settings
from .database import (
    Base,
    engine,
    get_db,
)
from .models import (
    AuditEvent,
    Case,
)
from .schemas import (
    AnalysisRequest,
    CaseCreate,
    ClassificationRequest,
)
from .security import (
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)
from .service import (
    analyze,
    audit,
)


Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title=settings.app_name,
    version="2.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
    ],
    allow_headers=[
        "Content-Type",
    ],
)

app.add_middleware(
    RequestSizeLimitMiddleware
)

app.add_middleware(
    SecurityHeadersMiddleware
)


@app.get("/")
def root():
    return {
        "application": settings.app_name,
        "status": "running",
        "version": "2.2.0",
        "health": "/api/health",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "environment": settings.environment,
        "ollama_enabled": settings.enable_ollama,
        "ollama_model": settings.ollama_model,
    }


@app.post("/api/classify")
async def classify_decision(
    payload: ClassificationRequest,
):
    try:
        classification = await classify_case(
            title=payload.title,
            decision=payload.decision,
            context=payload.context,
        )

        plan = build_investigation_plan(
            classification
        )

        return {
            "classification": classification,
            "plan": plan,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@app.post(
    "/api/cases",
    status_code=201,
)
async def create_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
):
    try:
        classification = await classify_case(
            title=payload.title,
            decision=payload.decision,
            context=payload.context,
        )

        plan = build_investigation_plan(
            classification
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    complete_decision = (
        payload.decision.strip()
    )

    if payload.context.strip():
        complete_decision += (
            "\n\nAdditional context:\n"
            + payload.context.strip()
        )

    result_json = json.dumps(
        {
            "classification": classification,
            "plan": plan,
        },
        ensure_ascii=False,
    )

    case_status = (
        "INPUT_REQUIRED"
        if classification.get(
            "missing_inputs"
        )
        else "CLASSIFIED"
    )

    case = Case(
        id=str(uuid.uuid4()),
        title=payload.title.strip(),
        decision=complete_decision,
        status=case_status,
        result_json=result_json,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    selected_agents = ", ".join(
        classification.get(
            "required_agents",
            [],
        )
    )

    audit(
        db,
        case.id,
        "Case Understanding Agent",
        "CASE_CLASSIFIED",
        (
            f"Domain: "
            f"{classification.get('domain')}; "
            f"Industry: "
            f"{classification.get('industry')}; "
            f"Decision type: "
            f"{classification.get('decision_type')}; "
            f"Selected capabilities: "
            f"{selected_agents}; "
            f"Investigation steps: "
            f"{len(plan.get('investigation_steps', []))}."
        ),
    )

    return serialize(case)


@app.get("/api/cases")
def list_cases(
    db: Session = Depends(get_db),
):
    rows = db.scalars(
        select(Case).order_by(
            Case.created_at.desc()
        )
    ).all()

    return [
        serialize(case)
        for case in rows
    ]


@app.get("/api/cases/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(
        Case,
        case_id,
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return serialize(case)


@app.post(
    "/api/cases/{case_id}/analyze"
)
def analyze_case(
    case_id: str,
    payload: AnalysisRequest,
    db: Session = Depends(get_db),
):
    case = db.get(
        Case,
        case_id,
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    try:
        return analyze(
            db,
            case,
            payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/cases/{case_id}/orchestrate"
)
async def orchestrate_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(
        Case,
        case_id,
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    result = safe_json(
        case.result_json
    )

    classification = result.get(
        "classification",
        {},
    )

    analysis_result = {
    "financial": result.get(
        "financial",
        {}
    ),
    "scenario": result.get(
        "scenario",
        {}
    ),
    "dependencies": result.get(
        "dependencies",
        {}
    ),
}

    orchestration = await run_orchestration(
        case_id=case.id,
        classification=classification,
        analysis_result=analysis_result,
    )

    result["orchestration"] = (
        orchestration
    )

    case.result_json = json.dumps(
        result,
        ensure_ascii=False,
    )

    db.commit()
    db.refresh(case)

    audit(
        db,
        case.id,
        "War Room Commander",
        "ORCHESTRATION_EXECUTED",
        (
            f"Executed "
            f"{len(orchestration['executed_agents'])} "
            f"agents."
        ),
    )

    return orchestration


@app.get(
    "/api/cases/{case_id}/audit"
)
def case_audit(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(
        Case,
        case_id,
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    rows = db.scalars(
        select(AuditEvent)
        .where(
            AuditEvent.case_id
            == case_id
        )
        .order_by(
            AuditEvent.created_at
        )
    ).all()

    return [
        {
            "id": event.id,
            "agent": event.agent,
            "event_type": event.event_type,
            "summary": event.summary,
            "created_at": event.created_at.isoformat(),
        }
        for event in rows
    ]


def safe_json(
    value: str | None,
) -> dict:
    try:
        parsed = json.loads(
            value or "{}"
        )

        if isinstance(
            parsed,
            dict,
        ):
            return parsed

        return {}

    except json.JSONDecodeError:
        return {}


def serialize(
    case: Case,
) -> dict:
    return {
        "id": case.id,
        "title": case.title,
        "decision": case.decision,
        "status": case.status,
        "assumptions": safe_json(
            case.assumptions_json
        ),
        "result": safe_json(
            case.result_json
        ),
    }