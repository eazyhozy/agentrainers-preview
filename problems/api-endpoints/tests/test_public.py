"""Public tests: happy-path CRUD flows for the Online Bookstore API."""


def test_health_check(client):
    """Health endpoint returns status ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_create_book(client):
    """Creating a book returns 201 with generated ID."""
    resp = client.post("/books", json={
        "title": "Python Basics",
        "author": "John",
        "price": 25000,
        "genre": "programming",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == 1
    assert data["title"] == "Python Basics"
    assert data["author"] == "John"
    assert data["price"] == 25000
    assert data["genre"] == "programming"
    assert data["stock"] == 0


def test_get_book(client):
    """Retrieving a book by ID returns the correct book."""
    client.post("/books", json={
        "title": "Flask Web Dev",
        "author": "Miguel",
        "price": 35000,
    })
    resp = client.get("/books/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Flask Web Dev"
    assert data["author"] == "Miguel"


def test_list_books(client):
    """Listing books returns paginated results."""
    client.post("/books", json={"title": "Book A", "author": "A", "price": 10000})
    client.post("/books", json={"title": "Book B", "author": "B", "price": 20000})
    client.post("/books", json={"title": "Book C", "author": "C", "price": 30000})

    resp = client.get("/books")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 3
    assert len(data["books"]) == 3
    assert data["page"] == 1


def test_register_user(client):
    """Registering a user returns 201 with generated ID."""
    resp = client.post("/users", json={
        "username": "testuser",
        "email": "test@example.com",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == 1
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_add_to_cart_and_get_cart(client):
    """Adding a book to cart and retrieving the cart works correctly."""
    client.post("/books", json={
        "title": "Test Book",
        "author": "Author",
        "price": 15000,
        "stock": 5,
    })
    client.post("/users", json={
        "username": "buyer",
        "email": "buyer@example.com",
    })

    resp = client.post("/cart/1/items", json={"book_id": 1, "quantity": 2})
    assert resp.status_code == 200

    resp = client.get("/cart/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["book_id"] == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == 30000


def test_create_order(client):
    """Creating an order from cart deducts stock and clears cart."""
    client.post("/books", json={
        "title": "Order Book",
        "author": "Writer",
        "price": 20000,
        "stock": 10,
    })
    client.post("/users", json={
        "username": "orderer",
        "email": "orderer@example.com",
    })
    client.post("/cart/1/items", json={"book_id": 1, "quantity": 3})

    resp = client.post("/orders", json={"user_id": 1})
    assert resp.status_code == 201
    order = resp.get_json()
    assert order["user_id"] == 1
    assert order["total"] == 60000
    assert len(order["items"]) == 1

    # Cart should be empty after order
    cart_resp = client.get("/cart/1")
    cart = cart_resp.get_json()
    assert len(cart["items"]) == 0
    assert cart["total"] == 0

    # Stock should be deducted
    book_resp = client.get("/books/1")
    book = book_resp.get_json()
    assert book["stock"] == 7
