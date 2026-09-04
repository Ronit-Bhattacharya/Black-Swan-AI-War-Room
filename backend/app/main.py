import json, uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from .config import settings
from .database import Base, engine, get_db
from .models import Case, AuditEvent
from .schemas import CaseCreate, AnalysisRequest
from .security import RequestSizeLimitMiddleware, SecurityHeadersMiddleware
from .service import analyze, audit

Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=False, allow_methods=["GET","POST"], allow_headers=["Content-Type"])
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

@app.get("/api/health")
def health(): return {"status":"ok","environment":settings.environment}

@app.post("/api/cases", status_code=201)
def create_case(payload: CaseCreate, db: Session=Depends(get_db)):
    case=Case(id=str(uuid.uuid4()), title=payload.title, decision=payload.decision)
    db.add(case); db.commit(); db.refresh(case)
    audit(db, case.id, "War Room Commander", "CASE_CREATED", "Decision case created; critical assumptions required before quantitative analysis.")
    return serialize(case)

@app.get("/api/cases")
def list_cases(db: Session=Depends(get_db)):
    return [serialize(x) for x in db.scalars(select(Case).order_by(Case.created_at.desc())).all()]

@app.get("/api/cases/{case_id}")
def get_case(case_id: str, db: Session=Depends(get_db)):
    case=db.get(Case,case_id)
    if not case: raise HTTPException(404,"Case not found")
    return serialize(case)

@app.post("/api/cases/{case_id}/analyze")
def analyze_case(case_id: str, payload: AnalysisRequest, db: Session=Depends(get_db)):
    case=db.get(Case,case_id)
    if not case: raise HTTPException(404,"Case not found")
    try: return analyze(db,case,payload)
    except ValueError as e: raise HTTPException(422,str(e))

@app.get("/api/cases/{case_id}/audit")
def case_audit(case_id: str, db: Session=Depends(get_db)):
    if not db.get(Case,case_id): raise HTTPException(404,"Case not found")
    rows=db.scalars(select(AuditEvent).where(AuditEvent.case_id==case_id).order_by(AuditEvent.created_at)).all()
    return [{"id":x.id,"agent":x.agent,"event_type":x.event_type,"summary":x.summary,"created_at":x.created_at.isoformat()} for x in rows]

def serialize(case):
    return {"id":case.id,"title":case.title,"decision":case.decision,"status":case.status,"assumptions":json.loads(case.assumptions_json or "{}"),"result":json.loads(case.result_json or "{}")}
