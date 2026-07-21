#The logic to be executed when a sale event occurs in the simulated store

from Store_Logic.inventory_adjust_event import adjust_inventory
from Database.models import CreateStoreEventInput

def process_sale_event(event: CreateStoreEventInput):
    
    
    if event.sku is None:
        raise ValueError("Sale event requires a sku.")

    if event.qty is None:
        raise ValueError("Sale event requires a qty.")

    # Sale decreases inventory
    inventory_result = adjust_inventory(
        sku=event.sku,
        qty_change=-event.qty
    )

    return {
        "status": "success",
        "event_type": event.event_type,
        "sku": event.sku,
        "qty": event.qty,
        "inventory_result": inventory_result,
        "message": event.message,
        "timestamp": event.timestamp,
    }