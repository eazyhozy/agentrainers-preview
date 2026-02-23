"""Hidden tests: edge cases and validation for the Online Bookstore API."""


# --- Book pagination and filtering ---

def test_pagination_default(client):
    """Default pagination returns page 1 with limit 10."""
    for i in range(15):
        client.post("/books", json={
            "title": f"Book {i}",
            "author": "Author",
            "price": 10000,
        })
    resp = client.get("/books")
    data = resp.get_json()
    assert data["page"] == 1
    assert data["limit"] == 10
    assert len(data["books"]) == 10
    assert data["total"] == 15


def test_pagination_custom_page_and_limit(client):
    """Custom page and limit parameters work correctly."""
    for i in range(25):
        client.post("/books", json={
            "title": f"Book {i}",
            "author": "Author",
            "price": 10000,
        })
    resp = client.get("/books?page=2&limit=10")
    data = resp.get_json()
    assert data["page"] == 2
    assert len(data["books"]) == 10
    assert data["total"] == 25


def test_pagination_out_of_range(client):
    """Requesting a page beyond available data returns empty list."""
    client.post("/books", json={"title": "Solo", "author": "A", "price": 5000})
    resp = client.get("/books?page=100")
    data = resp.get_json()
    assert data["books"] == []
    assert data["total"] == 1


def test_filter_by_genre(client):
    """Filtering books by genre returns only matching books."""
    client.post("/books", json={
        "title": "Sci-Fi Novel",
        "author": "A",
        "price": 10000,
        "genre": "scifi",
    })
    client.post("/books", json={
        "title": "Romance Novel",
        "author": "B",
        "price": 12000,
        "genre": "romance",
    })
    resp = client.get("/books?genre=scifi")
    data = resp.get_json()
    assert data["total"] == 1
    assert data["books"][0]["genre"] == "scifi"


def test_filter_by_author(client):
    """Filtering books by author returns only matching books."""
    client.post("/books", json={"title": "Book1", "author": "Alice", "price": 10000})
    client.post("/books", json={"title": "Book2", "author": "Bob", "price": 10000})
    client.post("/books", json={"title": "Book3", "author": "Alice", "price": 15000})
    resp = client.get("/books?author=Alice")
    data = resp.get_json()
    assert data["total"] == 2
    assert all(b["author"] == "Alice" for b in data["books"])


def test_filter_combined_genre_and_author(client):
    """Combining genre and author filters returns correct subset."""
    client.post("/books", json={
        "title": "A1", "author": "Alice", "price": 10000, "genre": "tech",
    })
    client.post("/books", json={
        "title": "A2", "author": "Alice", "price": 10000, "genre": "fiction",
    })
    client.post("/books", json={
        "title": "B1", "author": "Bob", "price": 10000, "genre": "tech",
    })
    resp = client.get("/books?genre=tech&author=Alice")
    data = resp.get_json()
    assert data["total"] == 1
    assert data["books"][0]["title"] == "A1"


# --- Book validation ---

def test_create_book_missing_title(client):
    """Creating a book without title returns 400."""
    resp = client.post("/books", json={"author": "A", "price": 10000})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_book_empty_title(client):
    """Creating a book with empty title returns 400."""
    resp = client.post("/books", json={"title": "", "author": "A", "price": 10000})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_book_negative_price(client):
    """Creating a book with negative price returns 400."""
    resp = client.post("/books", json={
        "title": "Bad", "author": "A", "price": -100,
    })
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_book_zero_price(client):
    """Creating a book with zero price returns 400."""
    resp = client.post("/books", json={
        "title": "Free", "author": "A", "price": 0,
    })
    assert resp.status_code == 400
    assert "error" in resp.get_json()


# --- Book not found ---

def test_get_book_not_found(client):
    """Getting a non-existent book returns 404."""
    resp = client.get("/books/999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_update_book_not_found(client):
    """Updating a non-existent book returns 404."""
    resp = client.put("/books/999", json={"title": "New"})
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_delete_book_not_found(client):
    """Deleting a non-existent book returns 404."""
    resp = client.delete("/books/999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_update_book_partial(client):
    """Partial update changes only specified fields."""
    client.post("/books", json={
        "title": "Original",
        "author": "Writer",
        "price": 10000,
        "genre": "tech",
    })
    resp = client.put("/books/1", json={"price": 15000})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["price"] == 15000
    assert data["title"] == "Original"
    assert data["author"] == "Writer"
    assert data["genre"] == "tech"


# --- User validation ---

def test_register_user_duplicate_username(client):
    """Registering with a duplicate username returns 400."""
    client.post("/users", json={
        "username": "alice",
        "email": "alice@example.com",
    })
    resp = client.post("/users", json={
        "username": "alice",
        "email": "alice2@example.com",
    })
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_register_user_invalid_email(client):
    """Registering with an email missing @ returns 400."""
    resp = client.post("/users", json={
        "username": "bob",
        "email": "invalid-email",
    })
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_get_user_not_found(client):
    """Getting a non-existent user returns 404."""
    resp = client.get("/users/999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


# --- Cart edge cases ---

def test_cart_add_nonexistent_book(client):
    """Adding a non-existent book to cart returns 404."""
    resp = client.post("/cart/1/items", json={"book_id": 999, "quantity": 1})
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_cart_add_insufficient_stock(client):
    """Adding more than available stock returns 400."""
    client.post("/books", json={
        "title": "Limited",
        "author": "A",
        "price": 10000,
        "stock": 2,
    })
    resp = client.post("/cart/1/items", json={"book_id": 1, "quantity": 5})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_cart_remove_nonexistent_item(client):
    """Removing an item not in cart returns 404."""
    resp = client.delete("/cart/1/items/999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


# --- Order edge cases ---

def test_order_empty_cart(client):
    """Creating an order with empty cart returns 400."""
    resp = client.post("/orders", json={"user_id": 1})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_order_stock_deduction(client):
    """Stock is correctly deducted after placing an order."""
    client.post("/books", json={
        "title": "Stock Test",
        "author": "A",
        "price": 10000,
        "stock": 10,
    })
    client.post("/cart/1/items", json={"book_id": 1, "quantity": 3})
    client.post("/orders", json={"user_id": 1})

    book = client.get("/books/1").get_json()
    assert book["stock"] == 7


def test_order_clears_cart(client):
    """Cart is empty after placing an order."""
    client.post("/books", json={
        "title": "Cart Clear",
        "author": "A",
        "price": 10000,
        "stock": 5,
    })
    client.post("/cart/1/items", json={"book_id": 1, "quantity": 2})
    client.post("/orders", json={"user_id": 1})

    cart = client.get("/cart/1").get_json()
    assert cart["items"] == []
    assert cart["total"] == 0


def test_get_order_not_found(client):
    """Getting a non-existent order returns 404."""
    resp = client.get("/orders/999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_multiple_orders_same_user(client):
    """A user can place multiple orders."""
    client.post("/books", json={
        "title": "Multi Order",
        "author": "A",
        "price": 10000,
        "stock": 20,
    })

    # First order
    client.post("/cart/1/items", json={"book_id": 1, "quantity": 2})
    client.post("/orders", json={"user_id": 1})

    # Second order
    client.post("/cart/1/items", json={"book_id": 1, "quantity": 3})
    client.post("/orders", json={"user_id": 1})

    resp = client.get("/orders?user_id=1")
    data = resp.get_json()
    assert len(data["orders"]) == 2


def test_list_orders_empty(client):
    """Listing orders for a user with no orders returns empty array."""
    resp = client.get("/orders?user_id=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["orders"] == []


def test_delete_book_returns_204(client):
    """Deleting a book returns 204 with no body."""
    client.post("/books", json={"title": "Bye", "author": "A", "price": 5000})
    resp = client.delete("/books/1")
    assert resp.status_code == 204
