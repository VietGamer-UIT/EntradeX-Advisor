"""
TaxLens Enterprise 3-Headed RBAC 
"""
import streamlit as st
import time
from langchain_core.messages import HumanMessage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from taxlens.agents.agent_router import build_tax_audit_graph

st.set_page_config(page_title="TaxLens Enterprise", layout="wide", page_icon="⚖️")

if "graph" not in st.session_state:
    st.session_state["graph"] = build_tax_audit_graph()
    st.session_state["thread_id"] = "enterprise_thread_1"
    
if "raw_data" not in st.session_state:
    st.session_state["raw_data"] = {}
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "manager_approval" not in st.session_state:
    st.session_state["manager_approval"] = False
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.sidebar.title("🏢 TaxLens Open-Core")
st.session_state["api_key"] = st.sidebar.text_input("OpenAI API Key (Optional)", type="password")

role = st.sidebar.radio("🔑 ĐĂNG NHẬP (RBAC):", ["Junior", "Senior", "Manager"])

def run_agent(target_role, msg_input=None):
    config = {"configurable": {"thread_id": st.session_state["thread_id"]}}
    st.session_state["raw_data"]["api_key"] = st.session_state["api_key"]
    
    msgs = [HumanMessage(content=msg_input)] if msg_input else []
    
    initial_state = {
        "messages": msgs, 
        "raw_data": st.session_state["raw_data"],
        "manager_approval": st.session_state["manager_approval"],
        "target_role": target_role
    }
    
    try:
        res = st.session_state["graph"].invoke(initial_state, config)
        if res.get("messages"):
            return res["messages"][-1].content
        return "Xong."
    except Exception as e:
        return f"Lỗi thực thi Agent: {e}"

if role == "Junior":
    st.title("🛡️ Thợ Săn Lỗi (Hunter Agent)")
    st.caption("Crunching 100+ Excel/XML files with extreme prejudice")
    
    upload = st.file_uploader("Kéo thả hàng loạt Excel / XML (Mô phỏng)", accept_multiple_files=True)
    if st.button("🚀 BẾ BÓNG (Execute Fieldwork)"):
        with st.status("Hunter Agent đang ăn dữ liệu...", expanded=True) as status:
            prog = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                prog.progress(i + 1)
            st.session_state["raw_data"]["xml_content"] = "<VAT><TGTGT>50000</TGTGT></VAT>" # Mock
            
            st.write("Đang đối soát VAT, CIT, TP...")
            result = run_agent("Hunter")
            st.success(result)
            status.update(label="Hoàn tất Fieldwork!", state="complete", expanded=False)

elif role == "Senior":
    st.title("🧠 Từ Điển Sống (Oracle Agent)")
    st.caption("Stealth Mode RAG - Chống Cloudflare Firewall Web Việt Nam")

    for msg in st.session_state["chat_history"]:
        st.chat_message(msg["role"]).write(msg["content"])
        
    user_input = st.chat_input("Hỏi luật thuế Việt Nam...")
    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Oracle Agent đang kích hoạt Stealth Scraper..."):
                response = run_agent("Oracle", user_input)
                st.markdown(response)
                st.session_state["chat_history"].append({"role": "assistant", "content": response})

elif role == "Manager":
    st.title("✒️ Command Center (Report Agent)")
    st.caption("In báo cáo Big 4 chỉ với nút Phê Duyệt")
    
    if st.button("✅ PHÊ DUYỆT (Manager Approve)"):
        st.session_state["manager_approval"] = True
        with st.spinner("Đang render Management Letter Markdown..."):
            letter = run_agent("Manager")
            st.markdown(letter)
