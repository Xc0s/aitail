from flask import Flask, jsonify, request

app = Flask(__name__)

# Fake in-memory inventory database
inventory = [
    {
        "sku": "WATER_24PK",
        "name": "Water Bottles 24 Pack",
        "on_hand": 12,
        "reorder_point": 20,
        "target_stock": 60
    },
    {
        "sku": "COKE_20OZ",
        "name": "Coca-Cola 20oz",
        "on_hand": 30,
        "reorder_point": 24,
        "target_stock": 72
    }
]

purchase_orders = []


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory)


@app.route("/purchase-orders", methods=["POST"])
def create_purchase_order():
    data = request.get_json()

    po = {
        "po_id": len(purchase_orders) + 1,
        "sku": data["sku"],
        "qty": data["qty"],
        "status": "created",
        "created_by": "AI_AGENT"
    }

    purchase_orders.append(po)

    return jsonify(po), 201


@app.route("/purchase-orders", methods=["GET"])
def get_purchase_orders():
    return jsonify(purchase_orders)


@app.route("/simulate-sale", methods=["POST"])
def simulate_sale():
    data = request.get_json()

    sku = data["sku"]
    qty = data["qty"]

    for item in inventory:
        if item["sku"] == sku:
            item["on_hand"] = max(0, item["on_hand"] - qty)

            return jsonify({
                "message": f"Simulated sale of {qty} unit(s) of {sku}",
                "item": item
            })

    return jsonify({"error": "SKU not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)