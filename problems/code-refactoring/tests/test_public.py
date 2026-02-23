from src.inventory import (
    add_product,
    get_product,
    remove_product,
    update_stock,
    search_products,
    process_order,
    generate_report,
)


def test_add_and_get_product():
    product = add_product("Widget", "Electronics", 29.99, 100)
    assert product["name"] == "Widget"
    assert product["category"] == "Electronics"
    assert product["price"] == 29.99
    assert product["quantity"] == 100

    fetched = get_product(product["id"])
    assert fetched is not None
    assert fetched["id"] == product["id"]
    assert fetched["name"] == "Widget"


def test_remove_product():
    product = add_product("Gadget", "Electronics", 49.99, 50)
    result = remove_product(product["id"])
    assert result is True

    fetched = get_product(product["id"])
    assert fetched is None


def test_update_stock():
    product = add_product("Bolt", "Hardware", 1.50, 200)
    updated = update_stock(product["id"], 50)
    assert updated["quantity"] == 250

    updated = update_stock(product["id"], -100)
    assert updated["quantity"] == 150


def test_search_by_category():
    add_product("Laptop", "Electronics", 999.99, 10)
    add_product("Phone", "Electronics", 599.99, 25)
    add_product("Hammer", "Tools", 19.99, 100)

    results = search_products(category="Electronics")
    assert len(results) == 2
    names = [r["name"] for r in results]
    assert "Laptop" in names
    assert "Phone" in names


def test_process_order_basic():
    p1 = add_product("Monitor", "Electronics", 299.99, 10)
    result = process_order([{"product_id": p1["id"], "quantity": 2}])
    assert result["success"] is True
    assert "order" in result
    assert result["order"]["status"] == "completed"
    assert len(result["order"]["items"]) == 1

    updated = get_product(p1["id"])
    assert updated["quantity"] == 8


def test_generate_inventory_report():
    add_product("Item A", "Cat1", 10.00, 5)
    add_product("Item B", "Cat1", 20.00, 10)
    add_product("Item C", "Cat2", 30.00, 3)

    report = generate_report("inventory")
    assert report["type"] == "inventory"
    assert report["total_products"] == 3
    assert report["total_items"] == 18
    assert report["total_value"] == 10.00 * 5 + 20.00 * 10 + 30.00 * 3
