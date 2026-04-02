"""
Enterprise Chat UI (Streamlit Layer).
Handles multi-file uploads, chat, and Strict Human-in-the-loop (Interrupts).
"""

import sys
import os
from pathlib import Path

# Fix relative imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import streamlit as st
import pandas as pd
from taxlens.agents.agent_router import build_tax_audit_graph
try:
    from langchain_core.messages import HumanMessage
except ImportError:
    HumanMessage = lambda content: content

# Initialize Graph Once
@st.cache_resource
def get_graph():
    return build_tax_audit_graph()

graph = get_graph()
config = {"configurable": {"thread_id": "audit_engagement_001"}}

st.set_page_config(page_title="TaxLens Enterprise", layout="wide", page_icon="⚖️")

# UI: Title
st.title("TaxLens-AI: Agentic Tax Audit Workspace (Big 4 Standard)")

# Default Raw Data (Pre-configured for demo)
if "raw_data" not in st.session_state:
    st.session_state["raw_data"] = {
        "gl_vat_total": 1000000,
        "tax_return_total": 1000000,
        "einvoice_total": 950000,
        "sample_expense": 500000,
        "has_valid_invoice": False,
        "vendor_loc": "Singapore",
        "is_related_party": True,
        "foreign_payment": 2000000
    }

# UI: Left Sidebar
with st.sidebar:
    st.header("🗂️ Audit Evidence")
    uploaded_files = st.file_uploader(
        "Upload Trial Balance / Invoices (CSV/Excel/PDF)", 
        accept_multiple_files=True
    )
    if uploaded_files:
        st.success(f"Nạp thành công {len(uploaded_files)} tệp chứng từ.")
        # Render a mock dataframe
        st.dataframe(pd.DataFrame({"Tài Khoản": ["1331", "3331", "642", "811"], "Dư Nợ": [500, 0, 100, 50], "Dư Có": [0, 500, 0, 0]}))

# Chat History
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Fetch current state from LangGraph Checkpointer
state_info = graph.get_state(config)
is_interrupted = False
working_papers = {}

if state_info and state_info.next:
    # If the graph has a "next" node pending, check if it's halted at Manager_Review_Node
    if "Manager_Review_Node" in state_info.next:
        is_interrupted = True
        if state_info.values and "working_papers" in state_info.values:
             working_papers = state_info.values["working_papers"]

# UI: Chat Container
chat_container = st.container(height=500)
with chat_container:
    # Read messages from LangGraph state directly if exist, otherwise fallback to session
    if state_info and state_info.values and "messages" in state_info.values:
        for msg in state_info.values["messages"]:
            # Basic parsing of Langchain BaseMessage
            role = "user" if getattr(msg, "type", "ai") == "human" else "assistant"
            st.chat_message(role).markdown(getattr(msg, "content", str(msg)))
    else:
        for msg in st.session_state["chat_history"]:
            st.chat_message(msg["role"]).markdown(msg["content"])

# UI: Human-in-the-Loop Checkpoint
if is_interrupted:
    st.warning("⚠️ CẢNH BÁO QUẢN LÝ: Các agent đã hoàn thành rà soát. Vui lòng phê duyệt Giấy làm việc (Working Papers) trước khi sinh Báo Cáo.")
    
    with st.expander("📄 XEM GIẤY LÀM VIỆC (WORKING PAPERS)", expanded=True):
        st.json(working_papers)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Phê duyệt & Tiếp tục (Approve)", use_container_width=True, type="primary"):
            # Provide approval status to state manually
            graph.update_state(config, {"manager_approval": True})
            # Resume graph (invoke with None advances past interrupt)
            graph.invoke(None, config)
            st.rerun()
    with col2:
        if st.button("❌ Từ chối & Hủy (Reject)", use_container_width=True):
            graph.update_state(config, {"manager_approval": False})
            graph.invoke(None, config)
            st.rerun()

# UI: Chat Input
# Disable input if we are waiting for manager approval
user_input = st.chat_input("Nhập yêu cầu kiểm toán...", disabled=is_interrupted)

if user_input:
    # Append user question
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    
    # Initialize the graph
    initial_state = {
        "messages": [HumanMessage(content=user_input)], 
        "raw_data": st.session_state["raw_data"],
        "working_papers": {},
        "manager_approval": False
    }
    
    # Execute Graph
    # If starting fresh, we pass initial state.
    # We should handle appending to thread or starting a new thread.
    # For MVP: overwrite current state
    with st.spinner("AI Agents đang phân tích sổ cái & hóa đơn..."):
        try:
             graph.invoke(initial_state, config)
        except Exception as e:
             st.chat_message("assistant").error(f"Execution Error: {e}")
             
    st.rerun()
