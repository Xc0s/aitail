from langchain_core.tools import StructuredTool
from Database.models import (PurchaseOrderInput, PurchaseOrderResult, UpdatePurchaseOrderStatusInput)
from Database.db import create_purchase_order, update_purchase_order_status


def create_purchase_order_tool(sku: str, qty: int) -> dict:
    """
    Create a purchase order for inventory replenishment.
    """

    po_id = create_purchase_order(sku, qty)

    result = PurchaseOrderResult(
        po_id= po_id,
        sku=sku,
        qty=qty,
        status="pending_approval",
        message=f"Created PO for {qty} unit(s) of {sku}"
    )

    return result.model_dump()


create_po_structured_tool = StructuredTool.from_function(
    func=create_purchase_order_tool,
    name="create_purchase_order",
    description="Create a purchase order when inventory falls below reorder point.",
    args_schema=PurchaseOrderInput,
)


def update_po_status_tool(po_id: int, new_status: str) -> dict:
    '''
    Update a purchase order status using allowed state transitions
    '''
    return update_purchase_order_status(
        po_id = po_id,
        new_status=new_status
    )

update_po_status_structured_tool = StructuredTool.from_function(
    func=update_po_status_tool,
    name="update_purchase_order_status",
    description=(
        "Update a purchase order's status. "
        "Allowed flow: pending_approval → approved → ordered → delivered → closed. "
        "Purchase orders can also be cancelled before closure."
    ),
    args_schema=UpdatePurchaseOrderStatusInput,
)

PO_tools = [create_po_structured_tool, update_po_status_structured_tool]