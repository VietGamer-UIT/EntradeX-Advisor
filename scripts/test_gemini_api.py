import os
import time
from google import genai
from dotenv import load_dotenv

# Tải biến môi trường
load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("❌ Lỗi: Chưa tìm thấy API Key trong file .env!")
    exit(1)

# Khởi tạo Client theo chuẩn SDK 2026
client = genai.Client(api_key=api_key)

# Gọi thẳng 2 alias mới nhất
models_to_test = ["gemini-flash-latest", "gemini-pro-latest"]

print("╔══════════════════════════════════════════════════════════╗")
print("║  TaxLens-AI — Gemini API Health Check (2026 SDK)         ║")
print("╚══════════════════════════════════════════════════════════╝\n")

for model_name in models_to_test:
    print(f"→ Đang gọi {model_name}...")
    start_time = time.time()
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Trả lời ngắn gọn (1 câu): Theo luật Việt Nam, thuế GTGT phổ thông là bao nhiêu %?"
        )
        latency = (time.time() - start_time) * 1000
        print(f"  ✅ [SUCCESS] Latency: {latency:.2f} ms")
        print(f"  💬 Phản hồi : {response.text.strip()}\n")
    except Exception as e:
        print(f"  ❌ [FAIL] Lỗi: {e}\n")