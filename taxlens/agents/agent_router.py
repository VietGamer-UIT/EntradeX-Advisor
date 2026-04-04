"""
LangGraph Multi-Tenant Cyclic Orchestrator (B2B SaaS Edition)
MULTI-CLASS ML DATA PIPELINE & BULLETPROOF GEMINI.
"""
from typing import Annotated, Dict, Any, List, TypedDict, Sequence
import operator
import pandas as pd
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

try:
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
except ImportError:
    pass

from taxlens.agents.tools import (
    tool_reconcile_vat_3_way,
    tool_calculate_cit_adjustment,
    tool_fct_tp_scanner,
    tool_parse_vn_einvoice_xml
)
from taxlens.agents.tools_web import tool_live_vietnam_tax_search

class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    raw_data: Dict[str, Any]
    working_papers: Dict[str, Any]
    audit_firm_name: str
    client_name: str
    review_note: str
    is_approved: bool

# Danh sách TCTN độc quyền
VALID_TCTN = ["Viettel", "VNPT", "MobiFone", "FPT", "BKAV", "MISA", "Thái Sơn", "TS24", "CyberLotus"]

def node_hunter_agent(state: GraphState) -> Dict[str, Any]:
    """Hunter Agent: Real Pandas Big Data Ingestion for 5000+ rows."""
    papers = state.get("working_papers", {})
    raw = state.get("raw_data", {})
    paths = raw.get("uploaded_paths", [])
    review_note = state.get("review_note", "")
    
    prefix = f"Re-run Requested: '{review_note}'. " if review_note and not state.get("is_approved", True) else ""
    findings = []
    import time
    start_time = time.time()
    
    try:
        count_rows = 0
        for path in paths:
            if path.endswith(".csv"):
                df = pd.read_csv(path)
                count_rows += len(df)
                
                # Check column compliance
                req_cols = ["NhaCungCap_HDDT", "TaiKhoan", "SoTien", "TienThue", "ChungTuHopLe"]
                if all(col in df.columns for col in req_cols):
                    df['TaiKhoan'] = df['TaiKhoan'].astype(str).str.strip()
                    df['ChungTuHopLe'] = df['ChungTuHopLe'].astype(str).str.upper()
                    
                    # 1. Quét CLASS_2_FAKE_INVOICE (Hóa đơn không qua TCTN chuẩn)
                    df_fake_tctn = df[~df['NhaCungCap_HDDT'].isin(VALID_TCTN)]
                    for _, row in df_fake_tctn.iterrows():
                        ngay_gd = row.get('NgayGiaoDich', row.get('Transaction_Date', 'N/A'))
                        findings.append({
                            "Class_Risk": "CLASS_2_FAKE_INVOICE",
                            "Mã rủi ro": f"FAKE_TCTN_{row.get('Transaction_ID', 'ID')}",
                            "Ngày Giao Dịch": str(ngay_gd),
                            "Tên Công Ty/App": str(row.get('NhaCungCap_HDDT', 'Unknown')),
                            "Số Tiền Gốc": f"{row.get('SoTien', 0):,.0f} VND",
                            "Số Tiền Lệch": f"{row.get('SoTien', 0):,.0f} VND",
                            "Khoản mục": f"Hóa đơn {row.get('SoTien', 0):,.0f} VND từ App lậu {row.get('NhaCungCap_HDDT', 'Unknown')} ngày {ngay_gd}",
                            "Số tiền chênh lệch": f"{row.get('SoTien', 0):,.0f} VND",
                            "Cơ sở pháp lý": "NĐ 123/2020/NĐ-CP - Hóa đơn bất hợp pháp",
                            "Đề xuất": "Từ chối thanh toán, báo cáo rủi ro phạt hành chính và trốn thuế."
                        })
                    
                    # 2. Quét CLASS_3_CIT_REJECT (Chi phí lớn k chứng từ)
                    df_cit_reject = df[(df['TaiKhoan'].str.startswith('642')) & (df['SoTien'] > 20000000) & (df['ChungTuHopLe'] == 'FALSE')]
                    for _, row in df_cit_reject.iterrows():
                        ngay_gd = row.get('NgayGiaoDich', row.get('Transaction_Date', 'N/A'))
                        findings.append({
                            "Class_Risk": "CLASS_3_CIT_REJECT",
                            "Mã rủi ro": f"CIT_LOSS_{row.get('Transaction_ID', 'ID')}",
                            "Ngày Giao Dịch": str(ngay_gd),
                            "Tên Công Ty/App": str(row.get('NhaCungCap_HDDT', 'Unknown')),
                            "Số Tiền Gốc": f"{row.get('SoTien', 0):,.0f} VND",
                            "Số Tiền Lệch": f"{row.get('SoTien', 0):,.0f} VND",
                            "Khoản mục": f"Chi phí {row.get('TaiKhoan', 'N/A')} số tiền {row.get('SoTien', 0):,.0f} VND thiếu Invoice ngày {ngay_gd}",
                            "Số tiền chênh lệch": f"{row.get('SoTien', 0):,.0f} VND",
                            "Cơ sở pháp lý": "VBHN 66/VBHN-BTC (Sửa đổi TT 78) - Chi phí không được trừ",
                            "Đề xuất": "Bóc ngay khỏi chi phí hợp lý để tính TNDN"
                        })
                        
                    # 3. Quét CLASS_1_VAT_LEAK (Lệch thuế VAT 10% cơ bản)
                    # Giả định hàng hóa phổ thông là 10%, nếu độ lệch tiền thuế lớn hơn 100k so với 10% -> Cảnh báo
                    df_vat_leak = df[(abs(df['TienThue'] - (df['SoTien'] * 0.1)) > 100000) & (df['TienThue'] > 0)]
                    for _, row in df_vat_leak.iterrows():
                        ngay_gd = row.get('NgayGiaoDich', row.get('Transaction_Date', 'N/A'))
                        lech_vat = abs(row['TienThue'] - (row['SoTien'] * 0.1)) if not pd.isna(row.get('TienThue')) and not pd.isna(row.get('SoTien')) else 0
                        findings.append({
                            "Class_Risk": "CLASS_1_VAT_LEAK",
                            "Mã rủi ro": f"VAT_LEAK_{row.get('Transaction_ID', 'ID')}",
                            "Ngày Giao Dịch": str(ngay_gd),
                            "Tên Công Ty/App": str(row.get('NhaCungCap_HDDT', 'Unknown')),
                            "Số Tiền Gốc": f"{row.get('SoTien', 0):,.0f} VND",
                            "Số Tiền Lệch": f"{lech_vat:,.0f} VND",
                            "Khoản mục": f"Lệch VAT {lech_vat:,.0f} VND của {row.get('NhaCungCap_HDDT', 'Unknown')} ngày {ngay_gd}",
                            "Số tiền chênh lệch": f"{lech_vat:,.0f} VND",
                            "Cơ sở pháp lý": "TT 219/2013/TT-BTC - Kê khai sai thuế GTGT",
                            "Đề xuất": "Ghi nhận âm tờ khai hoặc làm phụ lục điều chỉnh"
                        })
                        
    except Exception as e:
         findings.append({"Class_Risk": "SYS_ERR", "Mã rủi ro": "FATAL_PANDAS", "Khoản mục": "Data Pipeline", "Số tiền chênh lệch": "0", "Cơ sở pháp lý": "N/A", "Đề xuất": f"Lỗi đọc Data: {e}"})
         count_rows = 0
         
    process_time = (time.time() - start_time) * 1000
    papers["standardized_findings"] = findings
    msg_content = f"[Hunter Agent]: {prefix}Quét Model hoàn tất. Xử lý {count_rows} dòng dữ liệu trong {process_time:.2f}ms. Found {len(findings)} Anomalies."
    return {"messages": [AIMessage(content=msg_content)], "working_papers": papers}

def node_oracle_agent(state: GraphState) -> Dict[str, Any]:
    """Oracle Agent: The Ultimate Legal Oracle (Bulletproof Gemini)."""
    papers = state.get("working_papers", {})
    review_note = state.get("review_note", "")
    
    findings = papers.get("standardized_findings", [])
    findings_str = "\n".join([f"- {f['Mã rủi ro']}: {f['Khoản mục']} - Lệch: {f['Số Tiền Lệch']}" for f in findings[:20]])
    question = f"Từ danh sách lỗi sau, hãy viết Management Letter phân tích rủi ro hình sự, phạt hành chính nếu không nộp thuế đúng hạn:\n{findings_str}"
    if review_note: question = f"Special Request từ Trưởng nhóm: {review_note}\n\n{question}"
    
    sys_prompt = """Bạn là Trưởng Phòng Pháp Chế Thuế của một hãng Big 4 tại Việt Nam.
NGHIÊM CẤM ẢO GIÁC LUẬT (NO HALLUCINATIONS). Bắt buộc phải trích dẫn theo khung luật hiện hành:
1. Hóa đơn điện tử & TCTN: Phải viện dẫn Nghị định 123/2020/NĐ-CP và Thông tư 78/2021/TT-BTC.
2. Quản lý Thuế: Phải trích dẫn Luật số 38/2019/QH14 và Thông tư 80/2021/TT-BTC.
3. Thuế TNDN: Không được dùng TT 78/2014 độc lập, BẮT BUỘC dùng Văn bản hợp nhất số 66/VBHN-BTC (đã gộp các sửa đổi).
Ghi rõ ràng, mạch lạc, có tính quyết đoán. Trả về bài phân tích hoàn chỉnh."""

    analysis = "Trống."
    try:
         web_data = tool_live_vietnam_tax_search.invoke({"query": question})
         content = web_data.get("content", "")
         
         import os
         api_key = state.get("raw_data", {}).get("api_key") or os.environ.get("GOOGLE_API_KEY", "")
         if not api_key:
             raise ValueError("MISSING GOOGLE_API_KEY: Vui lòng nhập API Key trong Settings hoặc cấu hình biến môi trường.")
             
         from langchain_google_genai import ChatGoogleGenerativeAI
         from langchain_core.messages import SystemMessage, HumanMessage
         import os
         os.environ["GOOGLE_API_KEY"] = api_key # Explicitly set for genai components
         
         try:
             # BẮT BUỘC dùng gemini-1.5-flash-latest
             llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.2, max_retries=2)
             prompt = f"Tham khảo thông tin RAG từ Web: {content[:3000]}\n\nYêu cầu phân tích: {question}"
             ans = llm.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=prompt)]).content
             analysis = f"🌍 Nguồn pháp lý & Phân tích chuyên sâu (Model: gemini-1.5-flash-latest):\n\n{ans}"
         except Exception as api_err:
             err_str = str(api_err).lower()
             if "404" in err_str or "not found" in err_str:
                 analysis = "⚠️ LỖI GEMINI: Model name không hợp lệ."
             elif "403" in err_str or "permission" in err_str or "api_key" in err_str:
                 analysis = "⚠️ LỖI GEMINI 403: API Key không hợp lệ."
             elif "429" in err_str or "quota" in err_str:
                 analysis = "⚠️ LỖI GEMINI 429: Hết hạn mức Rate Limit API."
             else:
                 analysis = f"⚠️ LỖI GEMINI: {api_err}"
                 
    except Exception as e:
         analysis = f"Oracle Fatal SYS ERR: {e}"
         
    papers["Legal_Context"] = analysis
    return {"messages": [AIMessage(content=analysis)], "working_papers": papers}

def node_manager_review(state: GraphState) -> Dict[str, Any]:
    return {"messages": [AIMessage(content="HitL Paused")]}

def node_report_agent(state: GraphState) -> Dict[str, Any]:
    papers = state.get("working_papers", {})
    firm = state.get("audit_firm_name", "[Company]")
    client = state.get("client_name", "[Client]")
    findings = papers.get("standardized_findings", [])
    legal = papers.get("Legal_Context", "Trống.")
    
    draft = f"""# MANAGEMENT LETTER / BÁO CÁO TƯ VẤN THUẾ
<div style="color: gray; font-size: 14px; text-transform: uppercase;">
<b>Kính gửi:</b> Ban Giám Đốc {client}<br>
<b>Đơn vị kiểm toán:</b> {firm}<br>
<b>Ngày xuất báo cáo:</b> Hôm nay
</div>

---

### I. CÁC VẤN ĐỀ TRỌNG YẾU PHÁT HIỆN QUA DATA PIPELINE
"""
    if findings:
        from itertools import groupby
        findings_sorted = sorted([x for x in findings if isinstance(x, dict) and "Class_Risk" in x], key=lambda x: x["Class_Risk"])
        
        for key, group in groupby(findings_sorted, key=lambda x: x["Class_Risk"]):
            draft += f"#### PHÂN LOẠI RỦI RO: `{key}`\n"
            for item in list(group)[:10]: # Hiển thị max 10 lỗi mẫu mỗi class tránh tràn output
                draft += f"- **[{item['Mã rủi ro']}] {item['Khoản mục']}**:\n"
                draft += f"  - Chênh lệch: `{item['Số tiền chênh lệch']}`\n"
                draft += f"  - Rủi ro pháp lý: {item['Cơ sở pháp lý']}\n"
                draft += f"  - Khuyến nghị: *{item['Đề xuất']}*\n\n"
            draft += "*... (Và các dòng rủi ro tương tự trong DB)*\n\n"
    else:
        draft += "> Khách hàng có hệ thống Kiểm soát nội bộ xuất sắc, Không phát hiện rủi ro.\n\n"

    draft += "### II. THAM CHIẾU PHÁP LÝ CHUẨN MỰC TỪ TRƯỞNG PHÒNG PHÁP CHẾ (AI)\n"
    draft += f"{legal}\n\n"
    
    draft += "---\n*Powered by TaxLens-AI - Core Engine created by Đoàn Hoàng Việt (Việt Gamer)*"
    return {"messages": [AIMessage(content=draft)]}

def feedback_router(state: GraphState) -> str:
    return "Report_Agent" if state.get("is_approved") else "Hunter_Agent"

def build_tax_audit_graph() -> Any:
    workflow = StateGraph(GraphState)
    workflow.add_node("Hunter_Agent", node_hunter_agent)
    workflow.add_node("Oracle_Agent", node_oracle_agent)
    workflow.add_node("Manager_Review_Node", node_manager_review)
    workflow.add_node("Report_Agent", node_report_agent)
    
    workflow.add_edge(START, "Hunter_Agent")
    workflow.add_edge("Hunter_Agent", "Oracle_Agent")
    workflow.add_edge("Oracle_Agent", "Manager_Review_Node")
    workflow.add_conditional_edges("Manager_Review_Node", feedback_router)
    workflow.add_edge("Report_Agent", END)
    
    return workflow.compile(checkpointer=MemorySaver(), interrupt_before=["Manager_Review_Node"])
