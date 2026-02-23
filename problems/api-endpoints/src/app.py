from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory data stores
books = {}
users = {}
carts = {}  # user_id -> [{"book_id": ..., "quantity": ...}]
orders = {}
next_id = {"books": 1, "users": 1, "orders": 1}


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/books", methods=["GET"])
def list_books():
    # TODO: Implement pagination with page/limit params
    # TODO: Implement filtering by genre and author
    return jsonify({"error": "Not implemented"}), 501


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    # TODO: Return book by ID, 404 if not found
    return jsonify({"error": "Not implemented"}), 501


@app.route("/books", methods=["POST"])
def create_book():
    # TODO: Validate required fields (title, author, price)
    # TODO: Validate price > 0, title non-empty
    # TODO: Generate ID, set defaults for optional fields
    return jsonify({"error": "Not implemented"}), 501


@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    # TODO: Partial update, 404 if not found
    # TODO: Validate same rules as create
    return jsonify({"error": "Not implemented"}), 501


@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    # TODO: Delete book, 404 if not found, return 204
    return jsonify({"error": "Not implemented"}), 501


@app.route("/users", methods=["POST"])
def register_user():
    # TODO: Validate required fields (username, email)
    # TODO: Username must be unique, email must contain @
    return jsonify({"error": "Not implemented"}), 501


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # TODO: Return user by ID, 404 if not found
    return jsonify({"error": "Not implemented"}), 501


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    # TODO: Partial update, 404 if not found
    # TODO: Validate email contains @, username unique
    return jsonify({"error": "Not implemented"}), 501


@app.route("/cart/<int:user_id>", methods=["GET"])
def get_cart(user_id):
    # TODO: Return cart items and total price
    return jsonify({"error": "Not implemented"}), 501


@app.route("/cart/<int:user_id>/items", methods=["POST"])
def add_to_cart(user_id):
    # TODO: Add book to cart
    # TODO: Check book exists and has sufficient stock
    return jsonify({"error": "Not implemented"}), 501


@app.route("/cart/<int:user_id>/items/<int:book_id>", methods=["DELETE"])
def remove_from_cart(user_id, book_id):
    # TODO: Remove item from cart, 404 if not in cart
    return jsonify({"error": "Not implemented"}), 501


@app.route("/orders", methods=["POST"])
def create_order():
    # TODO: Create order from cart
    # TODO: Cart must not be empty
    # TODO: Deduct stock, clear cart
    return jsonify({"error": "Not implemented"}), 501


@app.route("/orders", methods=["GET"])
def list_orders():
    # TODO: List orders for user_id query param
    # TODO: Sort by creation time descending
    return jsonify({"error": "Not implemented"}), 501


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    # TODO: Return order by ID, 404 if not found
    return jsonify({"error": "Not implemented"}), 501


if __name__ == "__main__":
    app.run(debug=True, port=5000)
