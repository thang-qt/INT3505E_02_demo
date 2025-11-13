## Chạy demo
```bash
cd versioning
python -m venv .venv && source .venv/bin/activate
pip install flask
python app.py
```

### Ví dụ gọi API
```bash
# v1 tạo payment đơn giản
curl -X POST http://127.0.0.1:5000/v1/payment \
  -H 'Content-Type: application/json' \
  -d '{"amount": 150000, "currency": "VND"}'

# v2 yêu cầu customer_id và hỗ trợ capture lifecycle
curl -X POST http://127.0.0.1:5000/v2/payment \
  -H 'Content-Type: application/json' \
  -d '{"amount": 150000, "currency": "VND", "customer_id": "cus_01", "capture_mode": "manual"}'

# capture thủ công v2
curl -X PATCH http://127.0.0.1:5000/v2/payment/<id>/capture
```

## Deprecation notice (gửi developers)
```
Chúng tôi đã phát hành Payments API v2 với các cải tiến:
• Chuẩn hóa cấu trúc amount, hỗ trợ nhiều vùng tiền tệ và metadata.
• Cho phép tuỳ chọn capture (manual/automatic) và ghi nhận fee, timestamps.
• Response thống nhất hơn với kế hoạch mở rộng card-on-file trong Q1/2025.

Lộ trình ngưng v1:
- 01/07/2024: cảnh báo trong response header `Deprecation: true`.
- 01/10/2024: bật logging & rate limit ưu tiên v2.
- 31/12/2024: tắt hẳn `/v1/payment`.

Việc bạn cần làm:
1. Cập nhật client sử dụng endpoint `/v2/payment` hoặc header `Accept-Version: 2`.
2. Kiểm tra trường mới `amount.value`, `amount.currency`, `customer_id` bắt buộc.
3. Tận dụng endpoint `PATCH /v2/payment/<id>/capture` nếu cần kiểm soát luồng capture.
```
