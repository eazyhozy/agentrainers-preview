# Online Bookstore API

## 개요

온라인 서점을 위한 RESTful API를 Flask로 구현하는 문제입니다. 인메모리 데이터 저장소를 사용하며(데이터베이스 없음), 총 15개의 엔드포인트를 구현해야 합니다.

도서 관리(CRUD), 사용자 관리, 장바구니, 주문 기능을 포함합니다.

## 테스트 실행

```bash
docker compose run --rm runner
```

## 풀이 가이드

- `tests/test_public.py` — 공개 테스트입니다. 풀이 중 자유롭게 참고하세요.
- `tests/test_hidden.py` — 최종 채점용 엣지케이스 테스트입니다. 풀이 과정에서는 참고하지 않고, API 명세만 보고 구현해 보세요.

## API 명세

모든 요청/응답은 JSON 형식입니다. 오류 응답 형식: `{"error": "메시지"}`

---

### 1. GET /health

헬스 체크 엔드포인트.

**응답:**

- `200`: `{"status": "ok"}`

---

### 2. GET /books

도서 목록을 페이지네이션과 필터링을 지원하여 반환합니다.

**쿼리 파라미터:**

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `page` | 1 | 페이지 번호 (1부터 시작) |
| `limit` | 10 | 페이지당 항목 수 |
| `genre` | - | 장르로 필터링 |
| `author` | - | 저자명으로 필터링 |

**응답:**

- `200`:
```json
{
  "books": [
    {
      "id": 1,
      "title": "Python Basics",
      "author": "John",
      "price": 25000,
      "genre": "programming",
      "description": "",
      "stock": 10
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

---

### 3. GET /books/<id>

ID로 도서를 조회합니다.

**응답:**

- `200`: 도서 객체
- `404`: `{"error": "Book not found"}`

---

### 4. POST /books

새 도서를 등록합니다.

**요청 본문:**

| 필드 | 필수 | 설명 |
|-----|------|------|
| `title` | O | 도서 제목 (빈 문자열 불가) |
| `author` | O | 저자명 |
| `price` | O | 가격 (0보다 커야 함) |
| `genre` | X | 장르 |
| `description` | X | 설명 (기본값: `""`) |
| `stock` | X | 재고 수량 (기본값: `0`) |

**응답:**

- `201`: 생성된 도서 객체 (`id` 포함)
- `400`: `{"error": "Title is required"}`, `{"error": "Author is required"}`, `{"error": "Price must be greater than 0"}`

---

### 5. PUT /books/<id>

도서 정보를 수정합니다. 부분 업데이트를 지원합니다 (전송된 필드만 변경).

**요청 본문:** `title`, `author`, `price`, `genre`, `description`, `stock` 중 원하는 필드

**검증 규칙:**

- `title`이 포함된 경우 빈 문자열 불가
- `price`가 포함된 경우 0보다 커야 함

**응답:**

- `200`: 수정된 도서 객체
- `404`: `{"error": "Book not found"}`
- `400`: 검증 실패 시 오류 메시지

---

### 6. DELETE /books/<id>

도서를 삭제합니다.

**응답:**

- `204`: 본문 없음
- `404`: `{"error": "Book not found"}`

---

### 7. POST /users

사용자를 등록합니다.

**요청 본문:**

| 필드 | 필수 | 설명 |
|-----|------|------|
| `username` | O | 사용자명 (고유해야 함) |
| `email` | O | 이메일 (`@` 포함 필수) |

**응답:**

- `201`: 생성된 사용자 객체 (`id` 포함)
- `400`: `{"error": "Username is required"}`, `{"error": "Invalid email"}`, `{"error": "Username already exists"}`

---

### 8. GET /users/<id>

ID로 사용자를 조회합니다.

**응답:**

- `200`: 사용자 객체
- `404`: `{"error": "User not found"}`

---

### 9. PUT /users/<id>

사용자 정보를 수정합니다.

**요청 본문:** `username`, `email` 중 원하는 필드

**검증 규칙:**

- `email`이 포함된 경우 `@` 포함 필수
- `username`이 포함된 경우 다른 사용자와 중복 불가

**응답:**

- `200`: 수정된 사용자 객체
- `404`: `{"error": "User not found"}`
- `400`: 검증 실패 시 오류 메시지

---

### 10. GET /cart/<user_id>

사용자의 장바구니를 조회합니다.

**응답:**

- `200`:
```json
{
  "user_id": 1,
  "items": [
    {"book_id": 1, "quantity": 2, "title": "Python Basics", "price": 25000}
  ],
  "total": 50000
}
```

장바구니가 비어있는 경우에도 빈 배열과 total 0을 반환합니다.

---

### 11. POST /cart/<user_id>/items

장바구니에 도서를 추가합니다.

**요청 본문:**

| 필드 | 필수 | 설명 |
|-----|------|------|
| `book_id` | O | 도서 ID |
| `quantity` | X | 수량 (기본값: `1`) |

**검증:**

- 해당 도서가 존재해야 함
- 재고가 충분해야 함 (요청 수량 <= 재고)

**응답:**

- `200`: 업데이트된 장바구니 객체
- `404`: `{"error": "Book not found"}`
- `400`: `{"error": "Insufficient stock"}`

---

### 12. DELETE /cart/<user_id>/items/<book_id>

장바구니에서 특정 도서를 제거합니다.

**응답:**

- `200`: 업데이트된 장바구니 객체
- `404`: `{"error": "Item not in cart"}`

---

### 13. POST /orders

장바구니의 내용으로 주문을 생성합니다.

**요청 본문:**

| 필드 | 필수 | 설명 |
|-----|------|------|
| `user_id` | O | 사용자 ID |

**동작:**

1. 장바구니가 비어있으면 오류
2. 장바구니 항목을 기반으로 주문 생성
3. 각 도서의 재고를 차감
4. 장바구니를 비움

**응답:**

- `201`:
```json
{
  "id": 1,
  "user_id": 1,
  "items": [
    {"book_id": 1, "quantity": 2, "title": "Python Basics", "price": 25000}
  ],
  "total": 50000,
  "created_at": "2024-01-01T00:00:00"
}
```
- `400`: `{"error": "Cart is empty"}`

---

### 14. GET /orders?user_id=<id>

사용자의 주문 목록을 조회합니다. 생성 시간 기준 내림차순으로 정렬됩니다.

**쿼리 파라미터:**

| 파라미터 | 필수 | 설명 |
|---------|------|------|
| `user_id` | O | 사용자 ID |

**응답:**

- `200`: `{"orders": [...]}` (주문 배열, 최신순)

주문이 없는 경우 빈 배열을 반환합니다 (오류가 아님).

---

### 15. GET /orders/<id>

주문 상세를 조회합니다.

**응답:**

- `200`: 주문 객체
- `404`: `{"error": "Order not found"}`

---

## 데이터 모델

### Book

```json
{
  "id": 1,
  "title": "Python Basics",
  "author": "John",
  "price": 25000,
  "genre": "programming",
  "description": "A beginner's guide",
  "stock": 10
}
```

### User

```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com"
}
```

### Cart

```json
{
  "user_id": 1,
  "items": [
    {"book_id": 1, "quantity": 2, "title": "Python Basics", "price": 25000}
  ],
  "total": 50000
}
```

### Order

```json
{
  "id": 1,
  "user_id": 1,
  "items": [
    {"book_id": 1, "quantity": 2, "title": "Python Basics", "price": 25000}
  ],
  "total": 50000,
  "created_at": "2024-01-01T00:00:00"
}
```
