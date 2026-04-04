<div align="center">
  <h1>🏢 TaxLens-AI: Enterprise B2B SaaS</h1>
  <h3>The Ultimate Multi-Class AI Tax Audit Pipeline</h3>
  <p>
    <img src="https://img.shields.io/badge/Backend-FastAPI_SQLAlchemy-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/Frontend-Vanilla_JS_Tailwind-blue.svg" alt="Frontend">
    <img src="https://img.shields.io/badge/AI_Engine-LangGraph_Gemini-orange.svg" alt="LangGraph">
  </p>
</div>

---

**TaxLens-AI** đã lột xác hoàn toàn thành một nền tảng **Enterprise B2B SaaS** sẵn sàng phục vụ cấp độ Production cho các hãng Kiểm toán Độc lập. Phá vỡ giới hạn truyền thống, nền tảng sử dụng kiến trúc Single Page Application (SPA), tích hợp Database truy xuất lịch sử, cùng năng lực xử lý hàng ngàn dòng Pandas song song cùng Google Gemini 1.5 Pro.

## 🚀 Tính năng Cốt lõi
- **Kiến trúc Database-Driven:** SQLAlchemy + SQLite. Lưu toàn bộ JSON Working Papers và Management Letter vĩnh viễn.
- **Enterprise Dashboard:** Giao diện SPA siêu tốc, phân quyền Admin, 4 Metrics KPI thời thực.
- **Data Pipeline Đa Nhãn (Multi-class):** Phân loại rủi ro kế toán `[CLASS_1_VAT_LEAK]`, `[CLASS_2_FAKE_INVOICE]`, `[CLASS_3_CIT_REJECT]`.
- **Luật Sư Thép (Bulletproof Oracle):** Tích hợp Try..Except bắt 404, không ảo giác, trích dẫn cứng luật hiện hành (NĐ 123/2020, Thông tư 78/2021).

## 🏗️ Kiến trúc Hệ thống
*Hoàn toàn không sử dụng Streamlit hay Node.js. 100% Cấu trúc Tối giản*
```text
taxlens/
├── api/             # Backend FastAPI Core
│   ├── main.py      # Routers & Dependencies 
│   ├── database.py  # SQLAlchemy Connection
│   └── models.py    # Database Models (AuditReport)
├── agents/          # Langgraph AI Multi-Agents
│   └── agent_router.py 
frontend/            
└── index.html       # Single Page Application (Tailwind/JS)
```

## ⚡ Bắt Đầu Nhanh (1-Click Deploy)

1. Tải bộ máy: `git clone https://github.com/VietGamer-UIT/TaxLens-AI.git`
2. Mở file `.env` và nhập API key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
3. Cài cắm thư viện:
```bash
pip install -r requirements.txt
```
4. **Khởi Động 1 Nốt Nhạc:** Click đúp file `start_taxlens.bat` trên Windows (Máy sẽ tự tạo Database SQLite, sinh 5000 dòng file Test và mở trình duyệt).

---
*Developed by Đoàn Hoàng Việt (Việt Gamer) - Principal Developer.*
