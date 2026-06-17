"""
E-Commerce Backend - Flask version
-----------------------------------
A direct port of the original Node/Express + Sequelize backend, but using
plain in-memory Python lists instead of a database.

Why no database?
There's no user login, so there's no per-user data to keep separate, and the
only data that ever changes (cart items, orders) just needs to be shared
across requests while the server is running. A database is for data that
must survive a server restart or be queried in complex ways - neither
applies here. A simple list in memory does the job with far less code.

Trade-off: restarting this server resets the cart/orders back to the
seed data in data/*.json (same effect as calling POST /api/reset).
If you want that data to survive a restart later, the easy upgrade path
is SQLite (built into Python, no extra service to install).

Run with:
    pip install -r requirements.txt
    python app.py
Server runs on http://localhost:3000 (same port the original used).
"""

import json
import os
import time
import uuid

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

app = Flask(__name__)
CORS(app)  # allow requests from your React dev server (any origin, like the original)


# ---------------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------------

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def load_all_data():
    """Reads all four seed files fresh from disk. Used on startup and on /api/reset."""
    return {
        "products": load_json("products.json"),
        "delivery_options": load_json("delivery_options.json"),
        "cart": load_json("cart.json"),
        "orders": load_json("orders.json"),
    }


db = load_all_data()
products = db["products"]
delivery_options = db["delivery_options"]
cart = db["cart"]
orders = db["orders"]


# ---------------------------------------------------------------------------
# Small helpers (the Python equivalents of Product.findByPk, etc.)
# ---------------------------------------------------------------------------

def now_ms():
    """Current time in milliseconds, matching JS's Date.now()."""
    return int(time.time() * 1000)


def find_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def find_delivery_option(option_id):
    return next((d for d in delivery_options if d["id"] == option_id), None)


def find_cart_item(product_id):
    return next((c for c in cart if c["productId"] == product_id), None)


def find_order(order_id):
    return next((o for o in orders if o["id"] == order_id), None)


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@app.route("/api/products", methods=["GET"])
def get_products():
    search = request.args.get("search")

    if not search:
        return jsonify(products)

    lower_search = search.lower()
    matches = [
        p for p in products
        if lower_search in p["name"].lower()
        or any(lower_search in kw.lower() for kw in p["keywords"])
    ]
    return jsonify(matches)


# ---------------------------------------------------------------------------
# Delivery options
# ---------------------------------------------------------------------------

@app.route("/api/delivery-options", methods=["GET"])
def get_delivery_options():
    expand = request.args.get("expand")

    if expand == "estimatedDeliveryTime":
        result = []
        for option in delivery_options:
            estimated_ms = now_ms() + option["deliveryDays"] * 24 * 60 * 60 * 1000
            result.append({**option, "estimatedDeliveryTimeMs": estimated_ms})
        return jsonify(result)

    return jsonify(delivery_options)


# ---------------------------------------------------------------------------
# Cart items
# ---------------------------------------------------------------------------

@app.route("/api/cart-items", methods=["GET"])
def get_cart_items():
    expand = request.args.get("expand")

    if expand == "product":
        result = []
        for item in cart:
            product = find_product(item["productId"])
            result.append({**item, "product": product})
        return jsonify(result)

    return jsonify(cart)


@app.route("/api/cart-items", methods=["POST"])
def add_cart_item():
    body = request.get_json(silent=True) or {}
    product_id = body.get("productId")
    quantity = body.get("quantity")

    product = find_product(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 400

    if not isinstance(quantity, int) or quantity < 1 or quantity > 10:
        return jsonify({"error": "Quantity must be a number between 1 and 10"}), 400

    existing = find_cart_item(product_id)
    if existing:
        existing["quantity"] += quantity
        return jsonify(existing), 201

    new_item = {"productId": product_id, "quantity": quantity, "deliveryOptionId": "1"}
    cart.append(new_item)
    return jsonify(new_item), 201


@app.route("/api/cart-items/<product_id>", methods=["PUT"])
def update_cart_item(product_id):
    body = request.get_json(silent=True) or {}
    quantity = body.get("quantity")
    delivery_option_id = body.get("deliveryOptionId")

    item = find_cart_item(product_id)
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    if quantity is not None:
        if not isinstance(quantity, int) or quantity < 1:
            return jsonify({"error": "Quantity must be a number greater than 0"}), 400
        item["quantity"] = quantity

    if delivery_option_id is not None:
        if not find_delivery_option(delivery_option_id):
            return jsonify({"error": "Invalid delivery option"}), 400
        item["deliveryOptionId"] = delivery_option_id

    return jsonify(item)


@app.route("/api/cart-items/<product_id>", methods=["DELETE"])
def delete_cart_item(product_id):
    item = find_cart_item(product_id)
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    cart.remove(item)
    return "", 204


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@app.route("/api/orders", methods=["GET"])
def get_orders():
    expand = request.args.get("expand")
    sorted_orders = sorted(orders, key=lambda o: o["orderTimeMs"], reverse=True)

    if expand == "products":
        result = []
        for order in sorted_orders:
            expanded_products = [
                {**p, "product": find_product(p["productId"])}
                for p in order["products"]
            ]
            result.append({**order, "products": expanded_products})
        return jsonify(result)

    return jsonify(sorted_orders)


@app.route("/api/orders", methods=["POST"])
def create_order():
    if len(cart) == 0:
        return jsonify({"error": "Cart is empty"}), 400

    total_cost_cents = 0
    order_products = []

    for item in cart:
        product = find_product(item["productId"])
        delivery_option = find_delivery_option(item["deliveryOptionId"])

        product_cost = product["priceCents"] * item["quantity"]
        shipping_cost = delivery_option["priceCents"]
        total_cost_cents += product_cost + shipping_cost

        estimated_ms = now_ms() + delivery_option["deliveryDays"] * 24 * 60 * 60 * 1000
        order_products.append({
            "productId": item["productId"],
            "quantity": item["quantity"],
            "estimatedDeliveryTimeMs": estimated_ms,
        })

    total_cost_cents = round(total_cost_cents * 1.1)  # adds 10% tax, same as the original

    new_order = {
        "id": str(uuid.uuid4()),
        "orderTimeMs": now_ms(),
        "totalCostCents": total_cost_cents,
        "products": order_products,
    }
    orders.append(new_order)
    cart.clear()  # checkout empties the cart, same as the original

    return jsonify(new_order), 201


@app.route("/api/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    expand = request.args.get("expand")
    order = find_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if expand == "products":
        expanded_products = [
            {**p, "product": find_product(p["productId"])}
            for p in order["products"]
        ]
        return jsonify({**order, "products": expanded_products})

    return jsonify(order)


# ---------------------------------------------------------------------------
# Payment summary
# ---------------------------------------------------------------------------

@app.route("/api/payment-summary", methods=["GET"])
def get_payment_summary():
    total_items = 0
    product_cost_cents = 0
    shipping_cost_cents = 0

    for item in cart:
        product = find_product(item["productId"])
        delivery_option = find_delivery_option(item["deliveryOptionId"])
        total_items += item["quantity"]
        product_cost_cents += product["priceCents"] * item["quantity"]
        shipping_cost_cents += delivery_option["priceCents"]

    total_before_tax = product_cost_cents + shipping_cost_cents
    tax_cents = round(total_before_tax * 0.1)
    total_cost_cents = total_before_tax + tax_cents

    return jsonify({
        "totalItems": total_items,
        "productCostCents": product_cost_cents,
        "shippingCostCents": shipping_cost_cents,
        "totalCostBeforeTaxCents": total_before_tax,
        "taxCents": tax_cents,
        "totalCostCents": total_cost_cents,
    })


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

@app.route("/api/reset", methods=["POST"])
def reset_data():
    fresh = load_all_data()

    products.clear()
    products.extend(fresh["products"])
    delivery_options.clear()
    delivery_options.extend(fresh["delivery_options"])
    cart.clear()
    cart.extend(fresh["cart"])
    orders.clear()
    orders.extend(fresh["orders"])

    return "", 204


# ---------------------------------------------------------------------------
# Static images (optional - skip this if your React app already serves its
# own images from its public/ folder, which is common in the SuperSimpleDev
# course setup)
# ---------------------------------------------------------------------------

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(port=port)
