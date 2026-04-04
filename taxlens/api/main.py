import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load môi trường
load_dotenv()

# Khởi tạo Graph
from taxlens.agents.agent_router import build_tax_audit_graph
graph = build_tax_audit_graph()

app = FastAPI(title="TaxLens Enterprise API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phục vụ Frontend HTML Tĩnh
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/v1/audit")
async def process_audit(
    files: list[UploadFile] = File(...),
    audit_firm_name: str = Form("Forvis Mazars"),
    client_name: str = Form("Vinamilk")
):
    """API cốt lõi xử lý Audit Fieldwork đến Reporting"""
    # 1. Đọc files
    file_info = []
    for file in files:
        content = await file.read()
        file_info.append({"filename": file.filename, "size": len(content)})

    # 2. Setup State (Bypass HitL by auto-approving for full 1-click flow)
    thread_id = "api_thread_" + os.urandom(4).hex()
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "messages": [HumanMessage(content="Start Audit")],
        "raw_data": {"files": file_info},
        "audit_firm_name": audit_firm_name,
        "client_name": client_name,
        "is_approved": True, # Tự động duyệt để lấy Báo cáo cuối luôn
        "review_note": ""
    }
    
    try:
        # Chạy một mạch từ Hunter -> Oracle -> Manager -> Report -> END
        res = graph.invoke(initial_state, config)
        
        # 3. Trích xuất JSON Response
        working_papers = res.get("working_papers", {}).get("standardized_findings", [])
        legal_context = res.get("working_papers", {}).get("Legal_Context", "")
        management_letter = res.get("messages", [])[-1].content if res.get("messages") else "Lỗi sinh báo cáo"
        
        return JSONResponse(content={
            "status": "success",
            "audit_firm": audit_firm_name,
            "client": client_name,
            "data": {
                "working_papers": working_papers,
                "legal_context": legal_context,
                "management_letter": management_letter
            }
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
