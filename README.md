
# 📊 Funding Fee Tracker - Binance Futures (Streamlit App)

Ứng dụng này giúp bạn tra cứu lịch sử phí funding của các vị thế đang mở trong tài khoản Binance Futures, hiển thị kết quả trực quan và gửi báo cáo qua email.

---

## 🚀 Tính năng chính

- Nhập API Key/Secret Binance để truy cập vị thế đang mở
- Nhập email gửi/nhận để tự động gửi báo cáo funding fee
- Chọn khoảng thời gian cần tra cứu
- Hiển thị kết quả tổng funding fee theo coin (phân loại Long/Short)
- Tải báo cáo Excel + Biểu đồ tổng quan
- Giao diện web chạy bằng Streamlit

---

## 📁 Cấu trúc thư mục

```
.
├── funding_fee_app.py         # File chính chạy app
├── requirements.txt           # Danh sách thư viện Python cần cài
├── .env.example               # File cấu hình mẫu (KHÔNG đẩy .env thật lên Git)
└── README.md                  # File hướng dẫn này
```

---

## ⚙️ Hướng dẫn sử dụng

### ✅ Bước 1: Clone repo này
```bash
git clone https://github.com/your-username/funding-fee-tracker.git
cd funding-fee-tracker
```

### ✅ Bước 2: Tạo file `.env` từ mẫu
```bash
cp .env.example .env
```
Điền thông tin API và Gmail App Password vào file `.env`

---

### ✅ Bước 3: Cài thư viện
```bash
pip install -r requirements.txt
```

---

### ✅ Bước 4: Chạy ứng dụng
```bash
streamlit run funding_fee_app.py
```

---

## 🔐 Ghi chú quan trọng

- **Không commit file `.env` thật** chứa thông tin bảo mật
- Cần bật App Password cho Gmail: https://myaccount.google.com/apppasswords
- Nên dùng Python 3.9–3.11 để tương thích tốt nhất

---

## 🧠 Tác giả & bản quyền

Dự án này được xây dựng cho mục đích học tập, nghiên cứu cá nhân.  
Bạn có thể fork, cải tiến hoặc triển khai theo nhu cầu riêng.

---
