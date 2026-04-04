import os

def generate_mock_data():
    os.makedirs("sample_data", exist_ok=True)
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<HDon>
    <DLHDon>
        <NDHDon>
            <TienChuaThue>10000000</TienChuaThue>
            <ThueSuat>10</ThueSuat>
            <!-- LỖI CỐ TÌNH: Thuế suất 10% nhưng tiền thuế ghi 1,200,000 để AI bắt lỗi -->
            <TienThue>1200000</TienThue>
        </NDHDon>
    </DLHDon>
</HDon>
"""
    with open("sample_data/hoa_don_loi_1.xml", "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    csv_content = """NgayGhiSo,DienGiai,TaiKhoan,SoTien,ChungTuHopLe
01/01/2026,Chi phí chạy Quảng cáo Facebook,641,200000000,FALSE
05/01/2026,Chi phí tiếp khách không hóa đơn,642,50000000,FALSE
"""
    with open("sample_data/so_cai_2026.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)
        
    print("[SUCCESS] Đã tạo thành công thư mục sample_data/ chứa dữ liệu lỗi cố tình để AI trổ tài bắt nghiệp vụ.")

if __name__ == "__main__":
    generate_mock_data()
