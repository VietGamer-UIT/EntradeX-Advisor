"""
TaxLens-AI v3.0 — FastAPI Backend
Hardened with: Idempotency, UUID temp dirs, HitL Resume endpoint, WAL SQLite.
Phát triển bởi Đoàn Hoàng Việt (Việt Gamer)
"""
import os
import shutil
import json
import warnings
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, Form, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

# ── Database & Models ──────────────────────────────────────────────
from taxlens.api.database import engine, Base, get_db
from taxlens.api.models import AuditReport

Base.metadata.create_all(bind=engine)

# Enable WAL mode for concurrent SQLite writes (prevents lock contention)
with engine.connect() as conn:
    conn.execute(__import__("sqlalchemy").text("PRAGMA journal_mode=WAL"))

# ── LangGraph ─────────────────────────────────────────────────────
from taxlens.agents.agent_router import build_tax_audit_graph

graph = build_tax_audit_graph()

# ── FastAPI App ───────────────────────────────────────────────────
app = FastAPI(
    title="TaxLens Enterprise API v3.0",
    version="3.0.0",
    description="Forensic Tax Audit AI — Phát triển bởi Đoàn Hoàng Việt (Việt Gamer)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()


# ── GET: Report History ───────────────────────────────────────────
@app.get("/api/v1/reports")
def get_reports(db: Session = Depends(get_db)):
    """Fetch lịch sử Audit từ SQLite."""
    reports = db.query(AuditReport).order_by(AuditReport.created_at.desc()).all()
    results = []
    for r in reports:
        results.append({
            "id": r.id,
            "tenant_firm": r.tenant_firm,
            "client_name": r.client_name,
            "created_at": r.created_at.strftime("%d/%m/%Y %H:%M"),
            "working_papers": json.loads(r.working_papers) if r.working_papers else [],
            "management_letter": r.management_letter,
        })
    return {"status": "success", "data": results}


# ── POST: New Audit ───────────────────────────────────────────────
@app.post("/api/v1/audit")
async def process_audit(
    files: list[UploadFile] = File(...),
    audit_firm_name: str = Form(default="Independent Audit Firm"),
    client_name: str = Form(default="Client Corporation"),
    api_key: str = Form(default=""),
    x_idempotency_key: str = Header(default=""),
    db: Session = Depends(get_db),
):
    """
    API cốt lõi: Upload file → LangGraph Pipeline → SQLite.

    Headers:
      X-Idempotency-Key: <UUID>  — Nếu cung cấp, tránh duplicate submissions.

    Race Condition Fix:
      Mỗi request lưu file vào temp dir riêng (UUID-based) tránh file collision.
    """

    # ── IDEMPOTENCY CHECK ───────────────────────────────────────
    if x_idempotency_key:
        existing = db.query(AuditReport).filter(
            AuditReport.idempotency_key == x_idempotency_key
        ).first()
        if existing:
            # Trả về kết quả cached — không chạy lại pipeline
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "idempotency": "cached",
                    "data": {
                        "id": existing.id,
                        "working_papers": json.loads(existing.working_papers) if existing.working_papers else [],
                        "management_letter": existing.management_letter,
                    },
                },
            )

    # ── SAVE UPLOADED FILES (UUID temp dir — no collision) ────────
    request_uuid = uuid4().hex
    temp_dir = os.path.join("temp_uploads", request_uuid)
    os.makedirs(temp_dir, exist_ok=True)
    saved_file_paths = []

    for file in files:
        # Sanitize filename
        safe_name = os.path.basename(file.filename or "upload.csv")
        file_path = os.path.join(temp_dir, safe_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_file_paths.append(file_path)

    # ── CLEAN UP LEGACY DEBUG FILES ──────────────────────────────
    for junk in ["debug_out.txt", "audit.jsonl"]:
        if os.path.exists(junk):
            try:
                os.remove(junk)
            except Exception:
                pass

    # ── BUILD & RUN LANGGRAPH ─────────────────────────────────────
    thread_id = f"audit_{request_uuid}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "messages": [HumanMessage(content="Start Forensic Audit v3.0")],
        "raw_data": {"uploaded_paths": saved_file_paths, "api_key": api_key},
        "audit_firm_name": audit_firm_name,
        "client_name": client_name,
        "is_approved": True,   # Auto-approve: skip HitL for API full-flow
        "review_note": "",
    }

    try:
        res = graph.invoke(initial_state, config)

        working_papers = res.get("working_papers", {}).get("standardized_findings", [])
        legal_context = res.get("working_papers", {}).get("Legal_Context", "")
        management_letter = (
            res.get("messages", [])[-1].content
            if res.get("messages") else "Lỗi sinh báo cáo"
        )

        # ── PERSIST TO SQLite ─────────────────────────────────────
        new_report = AuditReport(
            tenant_firm=audit_firm_name,
            client_name=client_name,
            working_papers=json.dumps(working_papers, ensure_ascii=False),
            management_letter=management_letter,
            idempotency_key=x_idempotency_key or None,
            thread_id=thread_id,
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        response_payload = {
            "status": "success",
            "audit_firm": audit_firm_name,
            "client": client_name,
            "thread_id": thread_id,
            "data": {
                "id": new_report.id,
                "working_papers": working_papers,
                "legal_context": legal_context,
                "management_letter": management_letter,
            },
        }
    except Exception as e:
        response_payload = {"status": "error", "message": f"Graph Execution Failed: {e}"}
    finally:
        # ── CLEANUP TEMP FILES ────────────────────────────────────
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    return JSONResponse(status_code=200, content=response_payload)


# ── POST: HitL Resume Endpoint ────────────────────────────────────
class ReviewPayload(BaseModel):
    is_approved: bool = True
    review_note: str = ""


@app.post("/api/v1/audit/{thread_id}/review")
async def resume_audit_review(
    thread_id: str,
    payload: ReviewPayload,
    db: Session = Depends(get_db),
):
    """
    Human-in-the-Loop Resume: Kế toán trưởng gửi quyết định.
    Graph tiếp tục từ checkpoint (MemorySaver) với is_approved và review_note.
    """
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Update state & resume graph from HitL checkpoint
        updated_state = {
            "is_approved": payload.is_approved,
            "review_note": payload.review_note,
        }
        graph.update_state(config, updated_state)
        res = graph.invoke(None, config)  # None = resume from checkpoint

        management_letter = (
            res.get("messages", [])[-1].content
            if res.get("messages") else "Lỗi sinh báo cáo sau review"
        )
        working_papers = res.get("working_papers", {}).get("standardized_findings", [])

        # Update existing report nếu có
        existing = db.query(AuditReport).filter(AuditReport.thread_id == thread_id).first()
        if existing:
            existing.working_papers = json.dumps(working_papers, ensure_ascii=False)
            existing.management_letter = management_letter
            db.commit()

        return JSONResponse(status_code=200, content={
            "status": "success",
            "thread_id": thread_id,
            "action": "approved" if payload.is_approved else "rejected_rerun",
            "data": {
                "working_papers": working_papers,
                "management_letter": management_letter,
            },
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume failed: {e}")
