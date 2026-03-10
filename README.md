# 📈 Smart Advisor Bot - Tối ưu hóa đầu tư VN30 (Entrade X by DNSE)

![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![Visual Studio](https://img.shields.io/badge/Visual_Studio-5C2D91?style=for-the-badge&logo=visual-studio&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

## 💡 Giới thiệu dự án
Đây là một **Hệ chuyên gia tư vấn đầu tư (Rule-based Expert System)** được thiết kế độc quyền cho thao tác giao dịch trên ứng dụng **Entrade X by DNSE**. 

Dự án này giải quyết bài toán cá nhân của mình: Tối ưu hóa lợi nhuận cho chiến lược đầu tư thụ động (DCA) vào chứng chỉ quỹ ETF mô phỏng chỉ số VN30 (E1VFVN30). Thay vì trung bình giá mù quáng, Bot sẽ phân tích vĩ mô để hướng dẫn mình cách đi tiền thông minh nhất.

> 🔥 **Bản cập nhật V2.0:** Hệ thống tích hợp thêm thư viện `<filesystem>` và `<fstream>`, cho phép **tự động quét và đọc toàn bộ file lịch sử giao dịch (.csv)**. Từ đó tính toán chính xác số lượng chứng chỉ quỹ đang nắm giữ và **Giá vốn trung bình**, giúp lời khuyên bám sát 100% tình trạng danh mục thực tế.

> **🤖 Vibe Coding & AI Collaboration:** > Dự án này được phát triển theo phong cách **Vibe Coding**. Mình (với kiến thức của một sinh viên CNTT năm nhất) chịu trách nhiệm thiết kế logic hệ thống, luật đầu tư (Smart DCA), và luồng UI/UX. Toàn bộ mã nguồn C++, kiến trúc Lập trình hướng đối tượng (OOP) và kiến thức tài chính vĩ mô được hiện thực hóa với sự trợ giúp đắc lực của **Google Gemini**.

## 🧠 Cơ chế ra quyết định (Smart DCA Logic)
Hệ thống sử dụng 2 chỉ báo vĩ mô cốt lõi (P/E của VN-Index và Lãi suất ngân hàng) để tự động phân bổ tỷ trọng vốn:
- 🟢 **Thị trường bò (Bull Market) - Ổn định (11 <= P/E <= 15):** Khuyên giải ngân 80% ngân sách tháng, giữ 20% tiền mặt nhàn rỗi trên Entrade X.
- 🟡 **Thị trường bong bóng (Bubble) - Hưng phấn (P/E > 15):** Rủi ro cao. Khuyên chỉ giải ngân 40%, tích lũy phần còn lại để phòng thủ.
- 🔴 **Thị trường gấu (Bear Market) - Hoảng loạn (P/E < 11 hoặc Lãi suất > 8%):** Gửi tín hiệu đáy. Khuyên dồn toàn bộ quỹ dự phòng để bắt đáy kịch kim (x2 ngân sách).

## 🏗️ Kiến trúc Hệ thống (OOP Architecture)
Dự án áp dụng chuẩn Lập trình hướng đối tượng (Object-Oriented Programming):
- `MarketDataFetcher`: Lớp chịu trách nhiệm giao tiếp với người dùng, thu thập dữ liệu vĩ mô và giá chứng chỉ quỹ real-time.
- `SmartAdvisorBot`: "Não bộ" của hệ thống, quét file lịch sử CSV, đóng gói thuật toán tài chính, đưa ra quyết định và in ra phiếu lệnh giả lập chuẩn giao diện Entrade X.

## 📂 Hướng dẫn chuẩn bị dữ liệu lịch sử (File CSV)
Để Bot hoạt động thông minh nhất, bạn cần nạp lịch sử giao dịch từ app Entrade X vào hệ thống:
1. **Xuất dữ liệu:** Lên web/app Entrade X, vào phần *Lịch sử khớp lệnh*, chọn mốc thời gian và xuất file báo cáo (thường là file Excel `.xlsx`).
2. **Chuyển đổi:** Mở file Excel đó lên, chọn `Save As` và lưu lại dưới định dạng **CSV (Comma delimited) (*.csv)**.
3. **Làm sạch dữ liệu (QUAN TRỌNG):** Trong file CSV, bạn phải bôi đen cột *Khối lượng* và *Giá khớp*, đổi định dạng về dạng số bình thường (General/Number) và **xóa bỏ dấu phẩy ngăn cách hàng nghìn** (Ví dụ: `36,430` phải sửa thành `36430`). Nếu không C++ sẽ đọc sai cột.
4. **Nạp dữ liệu:** Copy tất cả các file `.csv` của bạn và dán thẳng vào thư mục chứa file `main.cpp` của dự án. Bot sẽ tự động lùng sục và cộng dồn dữ liệu của tất cả các file nó tìm thấy.
*(Lưu ý: File `.gitignore` đã chặn upload file `.csv`, nên thông tin giao dịch cá nhân của bạn sẽ an toàn tuyệt đối ở máy tính local, không bị đẩy lên mạng).*

## 🚀 Hướng dẫn sử dụng
1. Clone dự án về máy.
2. Đảm bảo bạn đã thả các file `.csv` lịch sử (nếu có) vào chung thư mục code.
3. Mở file `.slnx` bằng Visual Studio và bấm `F5` chạy chương trình.
4. **Nhập liệu linh hoạt:** Trả lời các câu hỏi trên màn hình console (Nhập ngân sách tháng này của bạn, P/E, Lãi suất và Giá E1VFVN30 hiện hành).
5. Nhận phiếu lệnh tư vấn và mở app Entrade X để thực thi!

---
*Developed by Đoàn Hoàng Việt (Việt Gamer) - Sinh viên UIT (Trường đại học Công nghệ Thông tin - ĐHQG TP.HCM).*
