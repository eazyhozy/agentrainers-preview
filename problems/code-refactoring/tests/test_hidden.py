import pytest
from src.inventory import (
    add_product,
    get_product,
    remove_product,
    update_stock,
    search_products,
    process_order,
    cancel_order,
    get_order,
    generate_report,
    apply_discount,
    bulk_update_prices,
)


def test_add_product_duplicate_name():
    p1 = add_product("Widget", "Electronics", 10.00, 5)
    p2 = add_product("Widget", "Electronics", 10.00, 5)
    assert p1["id"] != p2["id"]
    assert p1["name"] == p2["name"]


def test_remove_nonexistent_product():
    result = remove_product("PROD-9999")
    assert result is False


def test_update_stock_insufficient():
    product = add_product("Screw", "Hardware", 0.50, 10)
    with pytest.raises(ValueError, match="Insufficient stock"):
        update_stock(product["id"], -20)


def test_update_stock_to_zero():
    product = add_product("Nail", "Hardware", 0.10, 15)
    updated = update_stock(product["id"], -15)
    assert updated["quantity"] == 0


def test_search_multiple_filters():
    add_product("Cheap Gadget", "Electronics", 5.00, 10)
    add_product("Expensive Gadget", "Electronics", 500.00, 0)
    add_product("Mid Gadget", "Electronics", 50.00, 5)
    add_product("Mid Tool", "Tools", 50.00, 5)

    results = search_products(
        category="Electronics", min_price=10.00, max_price=100.00, in_stock=True
    )
    assert len(results) == 1
    assert results[0]["name"] == "Mid Gadget"


def test_search_no_results():
    add_product("Laptop", "Electronics", 999.99, 10)
    results = search_products(query="nonexistent")
    assert len(results) == 0


def test_search_by_price_range():
    add_product("Cheap", "Misc", 5.00, 10)
    add_product("Medium", "Misc", 50.00, 10)
    add_product("Expensive", "Misc", 500.00, 10)

    results = search_products(min_price=10.00, max_price=100.00)
    assert len(results) == 1
    assert results[0]["name"] == "Medium"


def test_process_order_empty_items():
    result = process_order([])
    assert result["success"] is False


def test_process_order_insufficient_stock():
    p = add_product("Rare Item", "Special", 100.00, 2)
    result = process_order([{"product_id": p["id"], "quantity": 5}])
    assert result["success"] is False
    assert "issues" in result


def test_process_order_nonexistent_product():
    result = process_order([{"product_id": "PROD-9999", "quantity": 1}])
    assert result["success"] is False
    assert "issues" in result


def test_process_order_multiple_items():
    p1 = add_product("Item A", "Cat", 10.00, 50)
    p2 = add_product("Item B", "Cat", 20.00, 30)
    result = process_order([
        {"product_id": p1["id"], "quantity": 2},
        {"product_id": p2["id"], "quantity": 3},
    ])
    assert result["success"] is True
    assert len(result["order"]["items"]) == 2


def test_process_order_stock_deduction():
    p = add_product("Trackable", "Cat", 25.00, 100)
    process_order([{"product_id": p["id"], "quantity": 10}])
    updated = get_product(p["id"])
    assert updated["quantity"] == 90


def test_cancel_order():
    p = add_product("Cancelable", "Cat", 50.00, 20)
    order_result = process_order([{"product_id": p["id"], "quantity": 5}])
    order_id = order_result["order"]["id"]

    cancel_result = cancel_order(order_id)
    assert cancel_result["success"] is True
    assert cancel_result["order"]["status"] == "cancelled"

    restored = get_product(p["id"])
    assert restored["quantity"] == 20


def test_cancel_already_cancelled_order():
    p = add_product("Item", "Cat", 10.00, 50)
    order_result = process_order([{"product_id": p["id"], "quantity": 1}])
    order_id = order_result["order"]["id"]

    cancel_order(order_id)
    result = cancel_order(order_id)
    assert result["success"] is False
    assert "already cancelled" in result["error"].lower()


def test_cancel_nonexistent_order():
    result = cancel_order("ORD-9999")
    assert result["success"] is False


def test_get_nonexistent_order():
    result = get_order("ORD-9999")
    assert result is None


def test_apply_percentage_discount():
    p = add_product("Discountable", "Cat", 100.00, 10)
    updated = apply_discount(p["id"], "percentage", 25)
    assert updated["price"] == 75.00
    assert updated["discount_applied"] is True


def test_apply_fixed_discount():
    p = add_product("Fixed Disc", "Cat", 80.00, 10)
    updated = apply_discount(p["id"], "fixed", 30)
    assert updated["price"] == 50.00
    assert updated["discount_applied"] is True


def test_apply_discount_exceeds_price():
    p = add_product("Tiny Price", "Cat", 5.00, 10)
    updated = apply_discount(p["id"], "fixed", 100)
    assert updated["price"] == 0.01


def test_bulk_update_prices():
    add_product("A", "Electronics", 100.00, 10)
    add_product("B", "Electronics", 200.00, 5)
    add_product("C", "Tools", 50.00, 20)

    updated = bulk_update_prices("Electronics", "percentage", 10)
    assert len(updated) == 2
    prices = sorted([u["price"] for u in updated])
    assert prices == [110.00, 220.00]


def test_generate_sales_report():
    p = add_product("Sellable", "Cat", 50.00, 100)
    process_order([{"product_id": p["id"], "quantity": 3}])
    process_order([{"product_id": p["id"], "quantity": 2}])

    report = generate_report("sales")
    assert report["type"] == "sales"
    assert report["total_orders"] == 2
    assert report["total_items_sold"] == 5
    assert report["total_revenue"] > 0


def test_generate_low_stock_report():
    add_product("Low Stock", "Cat", 10.00, 3)
    add_product("Plenty", "Cat", 10.00, 500)
    add_product("Almost Out", "Cat", 10.00, 1)

    report = generate_report("low_stock")
    assert report["type"] == "low_stock"
    assert report["total_low_stock"] == 2
    names = [p["name"] for p in report["products"]]
    assert "Low Stock" in names
    assert "Almost Out" in names
    assert "Plenty" not in names
    # Should be sorted by quantity ascending
    assert report["products"][0]["quantity"] <= report["products"][1]["quantity"]
