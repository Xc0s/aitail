#The logic to be executed in any event that requires inventory to be adjusted in consequence

from Database.db import update_inventory
    



def adjust_inventory(sku: str, qty_change: int):
    return update_inventory(sku, qty_change=qty_change)