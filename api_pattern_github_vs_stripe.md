**Stripe**: REST + Webhooks - thiết kế đơn giản, tập trung vào CRUD và event-driven cho thanh toán. Ít hypermedia, ưu tiên dễ dùng.

**GitHub**: REST + GraphQL + Webhooks - đa dạng lựa chọn. REST cho tương thích rộng, GraphQL cho truy vấn phức tạp, HATEOAS mạnh với nhiều links trong response.

**Điểm chung**: Cả hai đều dùng webhooks mạnh mẽ cho event-driven architecture.

## Stripe API

**CRUD cơ bản**

Stripe tổ chức API theo tài nguyên như Customer, Charge, PaymentIntent:
- `POST /v1/charges` - tạo giao dịch mới
- `GET /v1/charges/{id}` - lấy thông tin giao dịch
- `POST /v1/charges/{id}` - cập nhật (dùng POST thay vì PUT)
- `DELETE /v1/customers/{id}` - xóa khách hàng

**Query pattern**

Hai cách tìm kiếm:
- **List API**: Cursor-based pagination với `starting_after`, `ending_before`, `limit`
- **Search API**: Endpoint `/search` với query language: `status:"failed" AND created>1640995200`

**Event-driven với Webhooks**

Mọi thay đổi trạng thái tạo ra Event object và gửi qua webhook:
- `charge.succeeded` - thanh toán thành công
- `customer.subscription.created` - đăng ký mới
- `payment_intent.requires_action` - cần xác thực thêm

Tính năng:
- Signature verification bảo mật
- Tự động retry khi thất bại
- Idempotency keys xử lý trùng lặp

Ví dụ: Thanh toán cần 3D Secure → Stripe gửi webhook `payment_intent.succeeded` khi hoàn tất → Server cập nhật đơn hàng, gửi email.

**HATEOAS**

API v1: Không có hypermedia, client tự ghép URL.

API v2 (2024): Bắt đầu thêm `next_page_url` cho pagination, thuận tiện hơn.

## GitHub API

**CRUD với REST**

Resource-oriented theo repository, issues, users:
- `POST /repos/{owner}/{repo}/issues` - tạo issue
- `GET /repos/{owner}/{repo}/issues` - list issues
- `PATCH /repos/{owner}/{repo}/issues/{number}` - update issue
- `PUT /user/starred/{owner}/{repo}` - star repo

**HATEOAS mạnh**

Response chứa nhiều links liên quan:

```json
{
  "login": "launchany",
  "followers_url": "https://api.github.com/users/launchany/followers",
  "repos_url": "https://api.github.com/users/launchany/repos",
  "events_url": "https://api.github.com/users/launchany/events"
}
```

Dùng `Link` header cho pagination:
```
Link: <https://api.github.com/repos/123/issues?page=2>; rel="next"
```

**GraphQL - Query linh hoạt**

Giải quyết vấn đề N+1 requests của REST.

REST cần 11 requests để lấy 10 followers và followers của họ.

GraphQL chỉ cần 1 query:

```graphql
{
  viewer {
    followers(first: 10) {
      nodes {
        login
        followers(first: 10) {
          nodes { login }
        }
      }
    }
  }
}
```

Ưu điểm:
- Giảm số request, tiết kiệm bandwidth
- Client chọn chính xác field cần thiết
- Tránh over-fetching

Nhược điểm:
- Phức tạp hơn để implement
- Khó cache
- Cần học syntax mới

**Event-driven với Webhooks**

Hàng trăm event types: push, pull_request, issues, release, check_suite, deployment_status...

Ví dụ: Webhook "push" → Mỗi lần push code → GitHub POST đến Jenkins → Tự động chạy build/test.

Phù hợp cho CI/CD, notifications, automation workflows.
