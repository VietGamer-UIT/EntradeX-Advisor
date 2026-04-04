"""
TaxLens B2B Enterprise UI
Maker-Checker Workflow with White-label Support
"""
import streamlit as st
import pandas as pd
import time
from langchain_core.messages import HumanMessage
from taxlens.agents.agent_router import build_tax_audit_graph

st.set_page_config(page_title="TaxLens Enterprise Workspace", layout="wide", page_icon="🏢")

# 1. State Initialize
if "graph" not in st.session_state:
    st.session_state["graph"] = build_tax_audit_graph()
    st.session_state["thread_id"] = "b2b_audit_thread_1"
    
if "raw_data" not in st.session_state:
    st.session_state["raw_data"] = {}
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 2. White-Label Sidebar (Tenant Settings)
st.sidebar.title("🏢 Tenant Settings")
audit_firm = st.sidebar.text_input("Tên Hãng Kiểm Toán (vd: Forvis Mazars)", "My Audit Firm")
client_name = st.sidebar.text_input("Khách Hàng Đang Kiểm Toán", "Công ty ABC")
st.sidebar.markdown("---")
api_key = st.sidebar.text_input("Khóa OpenAI/Gemini API", type="password")
st.session_state["raw_data"]["api_key"] = api_key

st.title(f"Kiểm toán {client_name}")
st.caption("Workspace được thiết kế theo chuẩn Enterprise Maker-Checker HitL.")

# 3. Main Workspace Tabs
tab1, tab2, tab3 = st.tabs(["📁 1. Fieldwork (Junior Maker)", "⚖️ 2. Manager Review (HitL Checker)", "📄 3. Reporting Center"])

config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

# --- TAB 1: FIELDWORK ---
with tab1:
    st.subheader("Fieldwork Data Ingestion")
    st.file_uploader("Kéo thả Sổ Cân Đối / Hóa Đơn (Mô phỏng 100 files)", accept_multiple_files=True)
    
    if st.button("🚀 Bắt đầu Quét Lỗi AI (Execute Fieldwork)", type="primary"):
        with st.status("Hunter & Oracle Agent đang crunching dữ liệu...", expanded=True) as status:
            prog = st.progress(0)
            for i in range(100):
                 time.sleep(0.01)
                 prog.progress(i + 1)
                 
            # Initial state
            initial_state = {
                "AuditContext": "Start", # triggers start
                "raw_data": st.session_state["raw_data"],
                "audit_firm_name": audit_firm,
                "client_name": client_name,
                "is_approved": False,
                "review_note": ""
            }
            
            try:
                # Runs until interrupt_before Manager_Review_Node
                st.session_state["graph"].invoke(initial_state, config)
                st.success("Tạo Working Papers thành công! Đang chờ Sếp review ở Tab 2.")
                status.update(label="Hoàn tất!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Lỗi: {e}")

# --- TAB 2: MANAGER REVIEW ---
with tab2:
    st.subheader("Trạm Kiểm Soát Chuyên Gia (HitL)")
    state_snap = st.session_state["graph"].get_state(config)
    
    # Check if suspended at Manager Review
    if state_snap and state_snap.next and "Manager_Review_Node" in state_snap.next:
        papers = state_snap.values.get("working_papers", {})
        findings = papers.get("standardized_findings", [])
        
        st.write("### Working Papers (Rủi ro trọng yếu đã phát hiện)")
        if findings:
            df = pd.DataFrame(findings)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Không có dữ liệu rủi ro.")
            
        with st.expander("Ghi chú Pháp Lý (Oracle RAG)"):
            st.markdown(papers.get("Legal_Context", "Trống."))
            
        review_note = st.text_area("✍️ Feedback/Review Note (Bắt làm lại nếu phát hiện sai sót):", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
             if st.button("❌ TỪ CHỐI & BẮT LÀM LẠI (Reject)", type="secondary", use_container_width=True):
                 st.session_state["graph"].update_state(config, {"review_note": review_note, "is_approved": False})
                 # Continue graph (will execute review node, then fall into cycle back to Hunter)
                 st.session_state["graph"].invoke(None, config)
                 st.rerun()
        with col2:
             if st.button("✅ PHÊ DUYỆT (Approve)", type="primary", use_container_width=True):
                 st.session_state["graph"].update_state(config, {"review_note": review_note, "is_approved": True})
                 st.session_state["graph"].invoke(None, config)
                 st.rerun()
    else:
        st.info("Chưa có Working Papers nào đang chờ duyệt. Vui lòng chạy Fieldwork ở Tab 1 hoặc Báo cáo đã hoàn tất ở Tab 3.")

# --- TAB 3: REPORTING CENTER ---
with tab3:
    st.subheader("Báo Cáo Tư Vấn Thuế")
    state_snap = st.session_state["graph"].get_state(config)
    
    is_done = state_snap and not state_snap.next and state_snap.values.get("is_approved")
    
    if is_done:
        final_messages = state_snap.values.get("messages", [])
        if final_messages:
            # Lấy tin nhắn cuối cùng (từ Report Agent)
            report_text = final_messages[-1].content
            with st.container(border=True):
                 st.markdown(report_text)
            
            st.download_button("⬇️ Tải file Docx", data=report_text, file_name=f"{client_name}_Management_Letter.md", mime="text/markdown")
    else:
        st.warning("Báo cáo chỉ xuất sau khi Trạm Kiểm Soát (HitL) phê duyệt.")
        
# --- FOOTER ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<div align='center' style='color: #888888; font-size: 13px;'><i>Powered by TaxLens-AI - Core Engine created by Đoàn Hoàng Việt (Việt Gamer)</i></div>", unsafe_allow_html=True)
