import datetime
import math

_products = {}
_orders = {}
_order_counter = [0]
_tax_rate = [0.1]
_discount_log = []
_report_cache = {}
_low_stock_threshold = [10]


def init_inventory():
    global _products, _orders, _order_counter, _tax_rate, _discount_log, _report_cache, _low_stock_threshold
    _products = {}
    _orders = {}
    _order_counter = [0]
    _tax_rate = [0.1]
    _discount_log = []
    _report_cache = {}
    _low_stock_threshold = [10]


def add_product(name, category, price, quantity, description="", supplier=""):
    if name is None or name == "":
        raise ValueError("Product name cannot be empty")
    if price < 0:
        raise ValueError("Price cannot be negative")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if category is None or category == "":
        raise ValueError("Category cannot be empty")

    id = "PROD-" + str(len(_products) + 1).zfill(4)

    p = {}
    p["id"] = id
    p["name"] = name
    p["category"] = category
    p["price"] = price
    p["quantity"] = quantity
    p["description"] = description
    p["supplier"] = supplier
    p["created_at"] = datetime.datetime.now().isoformat()
    p["updated_at"] = datetime.datetime.now().isoformat()
    p["original_price"] = price
    p["discount_applied"] = False
    p["discount_value"] = 0
    p["active"] = True

    _products[id] = p

    if "inventory" in _report_cache:
        del _report_cache["inventory"]
    if "low_stock" in _report_cache:
        del _report_cache["low_stock"]

    return dict(p)


def remove_product(product_id):
    if product_id in _products:
        if _products[product_id]["active"] == True:
            _products[product_id]["active"] = False
            _products[product_id]["updated_at"] = datetime.datetime.now().isoformat()
            if "inventory" in _report_cache:
                del _report_cache["inventory"]
            if "low_stock" in _report_cache:
                del _report_cache["low_stock"]
            return True
        else:
            return False
    else:
        return False


def update_stock(product_id, quantity_change):
    if product_id not in _products:
        raise ValueError("Product not found: " + str(product_id))
    if _products[product_id]["active"] == False:
        raise ValueError("Product is inactive: " + str(product_id))

    p = _products[product_id]
    new_qty = p["quantity"] + quantity_change

    if new_qty < 0:
        raise ValueError("Insufficient stock. Current: " + str(p["quantity"]) + ", Requested change: " + str(quantity_change))

    p["quantity"] = new_qty
    p["updated_at"] = datetime.datetime.now().isoformat()

    if "inventory" in _report_cache:
        del _report_cache["inventory"]
    if "low_stock" in _report_cache:
        del _report_cache["low_stock"]

    return dict(p)


def get_product(product_id):
    if product_id in _products:
        if _products[product_id]["active"] == True:
            return dict(_products[product_id])
        else:
            return None
    else:
        return None


def search_products(query=None, category=None, min_price=None, max_price=None, in_stock=None):
    res = []
    for k in _products:
        p = _products[k]
        if p["active"] == True:
            if query is not None:
                if query.lower() in p["name"].lower() or query.lower() in p["description"].lower():
                    if category is not None:
                        if p["category"].lower() == category.lower():
                            if min_price is not None:
                                if p["price"] >= min_price:
                                    if max_price is not None:
                                        if p["price"] <= max_price:
                                            if in_stock is not None:
                                                if in_stock == True:
                                                    if p["quantity"] > 0:
                                                        res.append(dict(p))
                                                else:
                                                    if p["quantity"] == 0:
                                                        res.append(dict(p))
                                            else:
                                                res.append(dict(p))
                                    else:
                                        if in_stock is not None:
                                            if in_stock == True:
                                                if p["quantity"] > 0:
                                                    res.append(dict(p))
                                            else:
                                                if p["quantity"] == 0:
                                                    res.append(dict(p))
                                        else:
                                            res.append(dict(p))
                                else:
                                    if max_price is not None:
                                        if p["price"] <= max_price:
                                            if in_stock is not None:
                                                if in_stock == True:
                                                    if p["quantity"] > 0:
                                                        res.append(dict(p))
                                                else:
                                                    if p["quantity"] == 0:
                                                        res.append(dict(p))
                                            else:
                                                res.append(dict(p))
                                    else:
                                        if in_stock is not None:
                                            if in_stock == True:
                                                if p["quantity"] > 0:
                                                    res.append(dict(p))
                                            else:
                                                if p["quantity"] == 0:
                                                    res.append(dict(p))
                                        else:
                                            res.append(dict(p))
                        else:
                            pass
                    else:
                        if min_price is not None:
                            if p["price"] >= min_price:
                                if max_price is not None:
                                    if p["price"] <= max_price:
                                        if in_stock is not None:
                                            if in_stock == True:
                                                if p["quantity"] > 0:
                                                    res.append(dict(p))
                                            else:
                                                if p["quantity"] == 0:
                                                    res.append(dict(p))
                                        else:
                                            res.append(dict(p))
                                else:
                                    if in_stock is not None:
                                        if in_stock == True:
                                            if p["quantity"] > 0:
                                                res.append(dict(p))
                                        else:
                                            if p["quantity"] == 0:
                                                res.append(dict(p))
                                    else:
                                        res.append(dict(p))
                        else:
                            if max_price is not None:
                                if p["price"] <= max_price:
                                    if in_stock is not None:
                                        if in_stock == True:
                                            if p["quantity"] > 0:
                                                res.append(dict(p))
                                        else:
                                            if p["quantity"] == 0:
                                                res.append(dict(p))
                                    else:
                                        res.append(dict(p))
                            else:
                                if in_stock is not None:
                                    if in_stock == True:
                                        if p["quantity"] > 0:
                                            res.append(dict(p))
                                    else:
                                        if p["quantity"] == 0:
                                            res.append(dict(p))
                                else:
                                    res.append(dict(p))
                else:
                    pass
            else:
                if category is not None:
                    if p["category"].lower() == category.lower():
                        if min_price is not None:
                            if p["price"] >= min_price:
                                if max_price is not None:
                                    if p["price"] <= max_price:
                                        if in_stock is not None:
                                            if in_stock == True:
                                                if p["quantity"] > 0:
                                                    res.append(dict(p))
                                            else:
                                                if p["quantity"] == 0:
                                                    res.append(dict(p))
                                        else:
                                            res.append(dict(p))
                                else:
                                    if in_stock is not None:
                                        if in_stock == True:
                                            if p["quantity"] > 0:
                                                res.append(dict(p))
                                        else:
                                            if p["quantity"] == 0:
                                                res.append(dict(p))
                                    else:
                                        res.append(dict(p))
                        else:
                            if max_price is not None:
                                if p["price"] <= max_price:
                                    if in_stock is not None:
                                        if in_stock == True:
                                            if p["quantity"] > 0:
                                                res.append(dict(p))
                                        else:
                                            if p["quantity"] == 0:
                                                res.append(dict(p))
                                    else:
                                        res.append(dict(p))
                            else:
                                if in_stock is not None:
                                    if in_stock == True:
                                        if p["quantity"] > 0:
                                            res.append(dict(p))
                                    else:
                                        if p["quantity"] == 0:
                                            res.append(dict(p))
                                else:
                                    res.append(dict(p))
                    else:
                        pass
                else:
                    if min_price is not None:
                        if p["price"] >= min_price:
                            if max_price is not None:
                                if p["price"] <= max_price:
                                    if in_stock is not None:
                                        if in_stock == True:
                                            if p["quantity"] > 0:
                                                res.append(dict(p))
                                        else:
                                            if p["quantity"] == 0:
                                                res.append(dict(p))
                                    else:
                                        res.append(dict(p))
                            else:
                                if in_stock is not None:
                                    if in_stock == True:
                                        if p["quantity"] > 0:
                                            res.append(dict(p))
                                    else:
                                        if p["quantity"] == 0:
                                            res.append(dict(p))
                                else:
                                    res.append(dict(p))
                    else:
                        if max_price is not None:
                            if p["price"] <= max_price:
                                if in_stock is not None:
                                    if in_stock == True:
                                        if p["quantity"] > 0:
                                            res.append(dict(p))
                                    else:
                                        if p["quantity"] == 0:
                                            res.append(dict(p))
                                else:
                                    res.append(dict(p))
                        else:
                            if in_stock is not None:
                                if in_stock == True:
                                    if p["quantity"] > 0:
                                        res.append(dict(p))
                                else:
                                    if p["quantity"] == 0:
                                        res.append(dict(p))
                            else:
                                res.append(dict(p))
    return res


def process_order(items):
    if items is None or len(items) == 0:
        return {"success": False, "error": "No items provided"}

    total = 0
    tmp = []
    bad = []

    for i in range(len(items)):
        d = items[i]
        pid = d.get("product_id")
        qty = d.get("quantity", 1)

        if pid is None:
            bad.append({"index": i, "error": "Missing product_id"})
            continue

        if pid not in _products:
            bad.append({"index": i, "product_id": pid, "error": "Product not found"})
            continue

        if _products[pid]["active"] == False:
            bad.append({"index": i, "product_id": pid, "error": "Product is inactive"})
            continue

        if qty <= 0:
            bad.append({"index": i, "product_id": pid, "error": "Invalid quantity"})
            continue

        p = _products[pid]

        if p["quantity"] < qty:
            bad.append({"index": i, "product_id": pid, "error": "Insufficient stock", "available": p["quantity"], "requested": qty})
            continue

        price = p["price"]
        subtotal = price * qty

        if subtotal > 1000:
            disc = subtotal * 0.05
            subtotal = subtotal - disc
        elif subtotal > 500:
            disc = subtotal * 0.02
            subtotal = subtotal - disc
        else:
            disc = 0

        tax = subtotal * _tax_rate[0]
        item_total = subtotal + tax
        item_total = math.floor(item_total * 100) / 100

        tmp.append({
            "product_id": pid,
            "product_name": p["name"],
            "quantity": qty,
            "unit_price": price,
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "discount": round(disc, 2),
            "total": item_total
        })

        total = total + item_total

    if len(tmp) == 0:
        return {"success": False, "error": "No valid items in order", "issues": bad}

    if len(bad) > 0:
        return {"success": False, "error": "Some items could not be processed", "issues": bad}

    for item in tmp:
        pid = item["product_id"]
        qty = item["quantity"]
        _products[pid]["quantity"] = _products[pid]["quantity"] - qty
        _products[pid]["updated_at"] = datetime.datetime.now().isoformat()

    _order_counter[0] = _order_counter[0] + 1
    oid = "ORD-" + str(_order_counter[0]).zfill(4)

    order = {}
    order["id"] = oid
    order["items"] = tmp
    order["total"] = round(total, 2)
    order["status"] = "completed"
    order["created_at"] = datetime.datetime.now().isoformat()
    order["cancelled"] = False

    _orders[oid] = order

    if "inventory" in _report_cache:
        del _report_cache["inventory"]
    if "low_stock" in _report_cache:
        del _report_cache["low_stock"]
    if "sales" in _report_cache:
        del _report_cache["sales"]

    return {"success": True, "order": dict(order)}


def cancel_order(order_id):
    if order_id not in _orders:
        return {"success": False, "error": "Order not found"}

    o = _orders[order_id]

    if o["cancelled"] == True:
        return {"success": False, "error": "Order already cancelled"}

    for item in o["items"]:
        pid = item["product_id"]
        qty = item["quantity"]
        if pid in _products:
            _products[pid]["quantity"] = _products[pid]["quantity"] + qty
            _products[pid]["updated_at"] = datetime.datetime.now().isoformat()

    o["cancelled"] = True
    o["status"] = "cancelled"
    o["cancelled_at"] = datetime.datetime.now().isoformat()

    if "inventory" in _report_cache:
        del _report_cache["inventory"]
    if "low_stock" in _report_cache:
        del _report_cache["low_stock"]
    if "sales" in _report_cache:
        del _report_cache["sales"]

    return {"success": True, "order": dict(o)}


def get_order(order_id):
    if order_id in _orders:
        return dict(_orders[order_id])
    else:
        return None


def generate_report(report_type):
    if report_type == "inventory":
        data = []
        total_val = 0
        total_items = 0
        cats = {}

        for k in _products:
            p = _products[k]
            if p["active"] == True:
                val = p["price"] * p["quantity"]
                total_val = total_val + val
                total_items = total_items + p["quantity"]

                if p["category"] not in cats:
                    cats[p["category"]] = {"count": 0, "value": 0, "items": 0}
                cats[p["category"]]["count"] = cats[p["category"]]["count"] + 1
                cats[p["category"]]["value"] = cats[p["category"]]["value"] + val
                cats[p["category"]]["items"] = cats[p["category"]]["items"] + p["quantity"]

                data.append({
                    "id": p["id"],
                    "name": p["name"],
                    "category": p["category"],
                    "price": p["price"],
                    "quantity": p["quantity"],
                    "value": round(val, 2)
                })

        report = {
            "type": "inventory",
            "generated_at": datetime.datetime.now().isoformat(),
            "total_products": len(data),
            "total_items": total_items,
            "total_value": round(total_val, 2),
            "categories": cats,
            "products": data
        }

        return report

    elif report_type == "sales":
        data = []
        total_rev = 0
        total_orders = 0
        total_items_sold = 0

        for k in _orders:
            o = _orders[k]
            if o["cancelled"] == False:
                total_rev = total_rev + o["total"]
                total_orders = total_orders + 1
                for item in o["items"]:
                    total_items_sold = total_items_sold + item["quantity"]
                data.append({
                    "id": o["id"],
                    "total": o["total"],
                    "items_count": len(o["items"]),
                    "created_at": o["created_at"]
                })

        report = {
            "type": "sales",
            "generated_at": datetime.datetime.now().isoformat(),
            "total_orders": total_orders,
            "total_revenue": round(total_rev, 2),
            "total_items_sold": total_items_sold,
            "orders": data
        }

        return report

    elif report_type == "low_stock":
        data = []

        for k in _products:
            p = _products[k]
            if p["active"] == True:
                if p["quantity"] <= _low_stock_threshold[0]:
                    data.append({
                        "id": p["id"],
                        "name": p["name"],
                        "category": p["category"],
                        "quantity": p["quantity"],
                        "price": p["price"]
                    })

        data.sort(key=lambda x: x["quantity"])

        report = {
            "type": "low_stock",
            "generated_at": datetime.datetime.now().isoformat(),
            "threshold": _low_stock_threshold[0],
            "total_low_stock": len(data),
            "products": data
        }

        return report

    else:
        raise ValueError("Unknown report type: " + str(report_type))


def apply_discount(product_id, discount_type, value):
    if product_id not in _products:
        raise ValueError("Product not found: " + str(product_id))
    if _products[product_id]["active"] == False:
        raise ValueError("Product is inactive: " + str(product_id))
    if value < 0:
        raise ValueError("Discount value cannot be negative")

    p = _products[product_id]

    if discount_type == "percentage":
        if value > 100:
            raise ValueError("Percentage discount cannot exceed 100")
        disc = p["price"] * (value / 100)
        new_price = p["price"] - disc
        if new_price < 0.01:
            new_price = 0.01
        p["price"] = round(new_price, 2)
        p["discount_applied"] = True
        p["discount_value"] = value
        p["updated_at"] = datetime.datetime.now().isoformat()

        _discount_log.append({
            "product_id": product_id,
            "type": "percentage",
            "value": value,
            "old_price": p["original_price"],
            "new_price": p["price"],
            "applied_at": datetime.datetime.now().isoformat()
        })

        if "inventory" in _report_cache:
            del _report_cache["inventory"]

        return dict(p)

    elif discount_type == "fixed":
        new_price = p["price"] - value
        if new_price < 0.01:
            new_price = 0.01
        p["price"] = round(new_price, 2)
        p["discount_applied"] = True
        p["discount_value"] = value
        p["updated_at"] = datetime.datetime.now().isoformat()

        _discount_log.append({
            "product_id": product_id,
            "type": "fixed",
            "value": value,
            "old_price": p["original_price"],
            "new_price": p["price"],
            "applied_at": datetime.datetime.now().isoformat()
        })

        if "inventory" in _report_cache:
            del _report_cache["inventory"]

        return dict(p)

    else:
        raise ValueError("Unknown discount type: " + str(discount_type))


def bulk_update_prices(category, adjustment_type, value):
    updated = []

    for k in _products:
        p = _products[k]
        if p["active"] == True and p["category"].lower() == category.lower():
            if adjustment_type == "percentage":
                change = p["price"] * (value / 100)
                new_price = p["price"] + change
                if new_price < 0.01:
                    new_price = 0.01
                p["price"] = round(new_price, 2)
                p["updated_at"] = datetime.datetime.now().isoformat()
                updated.append(dict(p))
            elif adjustment_type == "fixed":
                new_price = p["price"] + value
                if new_price < 0.01:
                    new_price = 0.01
                p["price"] = round(new_price, 2)
                p["updated_at"] = datetime.datetime.now().isoformat()
                updated.append(dict(p))
            else:
                raise ValueError("Unknown adjustment type: " + str(adjustment_type))

    if "inventory" in _report_cache:
        del _report_cache["inventory"]

    return updated
