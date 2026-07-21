import mysql.connector
from Database.models import UpdatePurchaseOrderStatusResult, CreateStoreEventInput, InventoryItem

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pos_sim"
    )

def get_inventory():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

def get_specific_inventory_item(sku: str) -> InventoryItem | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM inventory
            WHERE sku = %s
            """,
            (sku,)
        )

        item = cursor.fetchone()

        if item is None:
            return None

        return InventoryItem.model_validate(item)

    finally:
        cursor.close()
        conn.close() 

def update_inventory(sku, qty_change):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE inventory SET on_hand = on_hand + %s WHERE sku = %s",
        (qty_change, sku)
    )

    conn.commit()
    cursor.close()
    conn.close()

def get_purchase_orders():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM purchase_orders ORDER BY created_at DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

def create_purchase_order(sku, qty):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO purchase_orders (sku, qty, status, created_by)
            VALUES (%s, %s, %s, %s)
            """,
            (sku, qty, "pending_approval", "inventory_manager")
        )

        conn.commit()

        po_id = cursor.lastrowid
        return po_id
    
    finally:
        cursor.close()
        conn.close()

ALLOWED_PO_TRANSITIONS = {
    "pending_approval": ["approved", "cancelled"],
    "approved": ["ordered", "cancelled"],
    "ordered": ["delivered", "cancelled"],
    "delivered": ["closed"],
    "closed": [],
    "cancelled": []
}


def update_purchase_order_status(po_id: int, new_status: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, status
            FROM purchase_orders
            WHERE id = %s
            """,
            (po_id,)
        )

        po = cursor.fetchone()

        if not po:
            result = UpdatePurchaseOrderStatusResult(
                po_id=po_id,
                old_status=None,
                new_status=new_status,
                rows_updated=0,
                message=f"Purchase order {po_id} not found."
            )
            return result.model_dump()

        old_status = po["status"]

        allowed_next_statuses = ALLOWED_PO_TRANSITIONS.get(old_status, [])

        if new_status not in allowed_next_statuses:
            result = UpdatePurchaseOrderStatusResult(
                po_id=po_id,
                old_status=old_status,
                new_status=new_status,
                rows_updated=0,
                message=f"Invalid transition: {old_status} → {new_status}"
            )
            return result.model_dump()

        cursor.execute(
            """
            UPDATE purchase_orders
            SET status = %s
            WHERE id = %s
            """,
            (new_status, po_id)
        )

        conn.commit()

        result = UpdatePurchaseOrderStatusResult(
            po_id=po_id,
            old_status=old_status,
            new_status=new_status,
            rows_updated=cursor.rowcount,
            message=f"Purchase order {po_id} updated from {old_status} to {new_status}."
        )

        return result.model_dump()

    finally:
        cursor.close()
        conn.close()


def create_store_event(**kwargs):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    event = CreateStoreEventInput(**kwargs)  # 🔥 VALIDATION RUNS HERE
    event_dict = event.model_dump(exclude_none=True)

    columns = ", ".join(event_dict.keys())
    placeholders = ", ".join(["%s"] * len(event_dict))
    values = tuple(event_dict.values())

    query = f"""
        INSERT INTO store_events ({columns})
        VALUES ({placeholders})
    """

    # Only valid events reach this point
    cursor.execute(query, values)
    conn.commit()

    event_id = cursor.lastrow
    
    cursor.close()
    conn.close()

    return {
        "id": event_id,
        **event_dict
    }