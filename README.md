<div align="center">
  <h1>⚖️ TaxLens-AI: Enterprise 1-Click Edition</h1>
  <h3>Full-Stack SaaS for Big 4 Audit Firms</h3>
  <p>
    <img src="https://img.shields.io/badge/FastAPI-0.110+-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/Frontend-Vanilla_JS_Tailwind-blue.svg" alt="Frontend">
    <img src="https://img.shields.io/badge/LangGraph-Gemini_Flash-orange.svg" alt="LangGraph">
  </p>
</div>

---

**TaxLens-AI** marks its definitive pivot into a **Full-Stack Web App** tailored for 1-click startup experiences on Windows. The core has been stripped of slow Streamlit UI and local Ollama dependencies, shifting to a high-speed FastAPI + HTML/Tailwind frontend powered entirely by Google Gemini 1.5 Flash API.

## 🚀 The 4 Pillars (No-NPM Architecture)

1. **The Backend Engine:** FastAPI runs on `127.0.0.1:8000`, injecting `UploadFile` endpoints directly into a LangGraph `GraphState`.
2. **The Frontend UI:** 100% Vanilla JS and TailwindCSS via CDN served as static files over FastAPI. No Node.js required.
3. **The Multi-Agent AI:** Hunter Agent crunches Pandas DataFrame errors. Oracle Agent fetches real-time web laws.
4. **1-Click Magic:** `start_taxlens.bat` sets up mock data, launches the server, and pops up the browser.

## 🏗️ Technical Architecture

```text
┌──────────────────────────┐         ┌───────────────────────────┐         ┌─────────────────────┐
│  Browser (index.html)    │ ────────▶ FastAPI Backend (main.py) │ ────────▶ LangGraph Engine    │
│  - TailwindCSS           │   JSON  │ - POST /api/v1/audit      │  State  │ - Hunter Node       │
│  - File Drag & Drop      │ ◀──────── │ - StaticFiles Mount       │ ◀──────── - Oracle RAG Node   │
└──────────────────────────┘         └───────────────────────────┘         └─────────────────────┘
                                                                                      | API
                                                                                      ▼
                                                                           Google Gemini 1.5 Flash
```

## ⚡ Quick Start (The Manager Way)

1. Mở file `.env` và nhập API key của bạn:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
2. Cài đặt Python Dependencies:
```bash
pip install -r requirements.txt
```
3. Khởi động **1-Click**: Click đúp vào file `start_taxlens.bat`.
4. Kéo các file mock trong thư mục `sample_data/` vào giao diện và cảm nhận.

*Powered by TaxLens-AI Engine. Core architecture created by Đoàn Hoàng Việt (Việt Gamer).*
