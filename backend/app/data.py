"""
Mock 'database' for the demo.

In a real engagement this would be swapped for calls to the client's
actual product catalog and order-management system (Shopify, WooCommerce,
a custom REST API, etc.). Keeping it in-memory here means the whole demo
runs with zero external dependencies.
"""

from datetime import date, timedelta

PRODUCTS = {
    "sku-100": {
        "sku": "sku-100",
        "name": "Aurora Wireless Headphones",
        "price": 129.00,
        "in_stock": True,
        "description": "Over-ear wireless headphones with active noise cancellation "
        "and 30-hour battery life.",
    },
    "sku-101": {
        "sku": "sku-101",
        "name": "Aurora Wireless Headphones - Travel Case",
        "price": 24.00,
        "in_stock": True,
        "description": "Hard-shell travel case sized for the Aurora Wireless Headphones.",
    },
    "sku-200": {
        "sku": "sku-200",
        "name": "Pulse Smart Water Bottle",
        "price": 45.00,
        "in_stock": False,
        "description": "Insulated bottle that tracks hydration and syncs to the Pulse app. "
        "Currently out of stock, restocking in 2 weeks.",
    },
}

ORDERS = {
    "ord-1001": {
        "order_id": "ord-1001",
        "status": "shipped",
        "carrier": "UPS",
        "tracking_number": "1Z999AA10123456784",
        "estimated_delivery": (date.today() + timedelta(days=2)).isoformat(),
        "items": ["sku-100"],
    },
    "ord-1002": {
        "order_id": "ord-1002",
        "status": "processing",
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": (date.today() + timedelta(days=5)).isoformat(),
        "items": ["sku-200"],
    },
    "ord-1003": {
        "order_id": "ord-1003",
        "status": "delivered",
        "carrier": "FedEx",
        "tracking_number": "789123456120",
        "estimated_delivery": (date.today() - timedelta(days=3)).isoformat(),
        "items": ["sku-100", "sku-101"],
    },
}


def find_product(query: str):
    """Very small fuzzy-ish lookup by SKU or name substring."""
    query_lower = query.strip().lower()
    if query_lower in PRODUCTS:
        return PRODUCTS[query_lower]
    for product in PRODUCTS.values():
        if query_lower in product["name"].lower():
            return product
    return None


def find_order(order_id: str):
    return ORDERS.get(order_id.strip().lower())
