#Simulation of store events for my orchestrated to act on
#must return sku and qty data for state stream and module use

import random
import Database.db import get_inventory
from Database.models import CreateStoreEventInput

#Type code that runs for a specified amount of time that has randomized events trigger. 
#These events are limited to potentially real events in a physical/digital store, not any fantastical event.


def simulate_sale() -> CreateStoreEventInput:
    inventory = get_inventory()

    if not inventory:
        return CreateStoreEventInput(
            event_type="StockOut_Detected",
            message="No inventory found."
        )

    item = random.choice(inventory)
    qty_sold = random.randint(1, 3)

    if item["on_hand"] <= 0:
        return f"{item['sku']} is already out of stock."

    qty_sold = min(qty_sold, item["on_hand"])
    return CreateStoreEventInput(
        event_type="Sale_Made",
        sku=item["sku"],
        qty=qty_sold,
        message=f"Sale made: {qty_sold} unit(s) of {item['sku']} sold"
    )


    