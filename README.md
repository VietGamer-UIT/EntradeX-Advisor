<div align="center">
  <h1>⚖️ TaxLens-AI: Open-Core Edition</h1>
  <h3>The Ultimate 3-Headed Enterprise AI Auditor</h3>
  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/Streamlit-1.32+-red.svg" alt="Streamlit">
    <img src="https://img.shields.io/badge/LangGraph-0.0.30-orange.svg" alt="LangGraph">
    <img src="https://img.shields.io/badge/Open--Core-Startup-purple.svg" alt="OpenCore">
  </p>
</div>

---

**TaxLens-AI** marks its definitive pivot into an **Enterprise Open-Core Product**, engineered specifically for international Big 4 audit firms (e.g., Forvis Mazars). We have aggressively decoupled operations into a unified Role-Based Access Control (RBAC) architecture orchestrated by a 3-Headed LangGraph Agent system.

## 🚀 The 3 Pillars of Power (Core Features)

1. **🛡️ Thợ Săn Lỗi (Hunter Agent - Junior Level)**
   - **Mục Định:** Đóng vai trò Data Cruncher.
   - **Sức Mạnh:** Tiêu thụ hàng loạt file báo cáo khổng lồ (Sổ cái, Trial Balance, XML Invoices). Áp dụng thuật toán đối chiếu siêu tốc (VAT, CIT, FCT/Transfer Pricing) mà không sập hệ thống.
2. **🧠 Từ Điển Sống (Oracle Agent - Senior Level)**
   - **Mục Định:** Khám phá Luật Thuế Real-time.
   - **Sức Mạnh:** Xóa bỏ khái niệm Vector Database tốn dung lượng ổ đĩa. Sử dụng **Stealth RAG Cổng Thông Tin Chính Phủ VN**. Nó bẻ gãy Cloudflare 403 bằng `fake-useragent` và retry thông minh để đem về các phân tích từ LLM sống trên Ram.
3. **✒️ Máy In Báo Cáo (Report Agent - Manager Level)**
   - **Mục Định:** Khâu ấn định dòng tiền và danh dự pháp lý của Big 4.
   - **Sức Mạnh:** Dựa vào nút bấm duy nhất của Manager (PHÊ DUYỆT), tự động sinh chuỗi **Management Letter** đẹp tiêu chuẩn, gãy gọn mọi rủi ro với phong cách văn bản pháp lý cứng cáp.

## 🏗️ 3-Headed RBAC Architecture

```mermaid
graph TD
    A([🔐 Login Select Role]) --> B{Streamlit User RBAC}
    
    B -->|Junior| C[File Uploader Drag/Drop]
    B -->|Senior| D[Chatbot Oracle RAG]
    B -->|Manager| E[Command Center Dashboard]
    
    C -->|Trigger| F(Hunter Agent)
    D -->|Chat Query| G(Oracle Agent)
    E -->|Click Approve| H(Report Agent)
    
    F --> I[(Working Papers State)]
    G --> I
    I --> H
    H --> J[📄 Markdown Management Letter]
```

## ⚡ Quick Start

```bash
# Cài đặt siêu tân binh
pip install -r requirements.txt

# Khởi động RBAC UI (nhớ điền API Key vào Sidebar)
streamlit run frontend/app.py
```

*Built by Antigravity as the Ultimate Startup Tax Blueprint.*
