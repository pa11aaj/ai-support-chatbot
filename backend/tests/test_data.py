from app.data import find_order, find_product


def test_find_product_by_sku():
    product = find_product("sku-100")
    assert product is not None
    assert product["name"] == "Aurora Wireless Headphones"


def test_find_product_by_name_substring():
    product = find_product("water bottle")
    assert product is not None
    assert product["sku"] == "sku-200"


def test_find_product_not_found():
    assert find_product("nonexistent") is None


def test_find_order_found():
    order = find_order("ord-1001")
    assert order is not None
    assert order["status"] == "shipped"


def test_find_order_case_insensitive():
    order = find_order("ORD-1001")
    assert order is not None


def test_find_order_not_found():
    assert find_order("ord-9999") is None
