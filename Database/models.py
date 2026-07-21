from pydantic import BaseModel, Field, model_validator
from typing import Literal, List, TypedDict
from datetime import datetime, timezone
from dataclasses import dataclass, field


class InventoryItem(BaseModel):
    sku: str
    name: str
    on_hand: int = Field(ge=0)
    reorder_point: int = Field(ge=0)
    target_stock: int = Field(ge=0)
    unit_cost: int = Field(ge=0)
    retail_cost: int = Field(ge=0)

StoreEvent = Literal[
    "Sale_Made",
    "Inventory_Updated",
    "Waste_Logged",
    "PO_Made",
    "PO_Status_Updated",
    "StockOut_Detected",
    "Delivery_Received",
    "No database detected" 
]

POStatus = Literal[
    "pending_approval",
    "approved",
    "ordered",
    "delivered",
    "closed",
    "cancelled"
]

class CreateStoreEventInput(BaseModel):
    event_type: StoreEvent = Field(description="The type of new store event")
    sku: str | None = None
    qty: int | None = Field(default=None, ge=0)
    po_id: int | None = Field(default=None, gt=0)
    old_status: POStatus | None = None
    new_status: POStatus | None = None
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_event_fields(self):

        inventory_events = {
            "Sale_Made",
            "Inventory_Updated",
            "Waste_Logged",
            "StockOut_Detected",
            "Delivery_Received",
        }

        if self.event_type in inventory_events:
            if self.sku is None or self.qty is None:
                raise ValueError("These event types require sku and qty")

        if self.event_type == "PO_Status_Updated":
            if (
                self.po_id is None 
                or self.old_status is None
                or self.new_status is None
            ):
                raise ValueError(
                    "PO_Status_Updated requires po_id, old_status, and new_status"
                )
        if self.event_type == "PO_Made":
            if self.po_id is None or self.new_status is None:
                raise ValueError(
                    "PO_Made requires po_id and new_status"
                )

        return self
    

class PurchaseOrderInput(BaseModel):
    sku: str = Field(description="The product SKU to reorder")
    qty: int = Field(gt=0, description="Quantity to order")


class PurchaseOrderResult(BaseModel):
    po_id: int
    sku: str
    qty: int
    status: Literal["pending_approval", "skipped", "error"]
    message: str


class AgentCheckResult(BaseModel):
    actions: list[PurchaseOrderResult]



class UpdatePurchaseOrderStatusInput(BaseModel):
    po_id: int = Field(gt=0, description="The purchase order ID")
    new_status: POStatus = Field(description="The new purchase order status")


class UpdatePurchaseOrderStatusResult(BaseModel):
    po_id: int
    old_status: str | None
    new_status: str
    rows_updated: int
    message: str

class AgentFinalOutput(BaseModel):
    summary: str = Field(description="short summary of what the agent did")
    actions_taken: List[str] = Field(description="Actions performed by the agent")
    tool_results: List[str] = Field(description="Important tool results")
    next_step: str = Field(description="Recommended next step")





#----------------------- States -----------------------------------------------


@dataclass
class StoreState:
    current_time: datetime
    close_time: datetime
    cash_register: float = 400.00
    revenue: float = 0.0
    refunds: float = 0.0
    transactions: int = 0
    payment_failures: int = 0
    support_contacts: int = 0
    staff_available: int = 1
    events_seen: int = 0
    inventory: list[InventoryItem] = field(default_factory=list)
    event_counts: dict[str, int] = field(default_factory=dict)



class AgentState(TypedDict):
    #Needs key value pairs
    pass

#Pricebook/Forecaster Orchestration State
#CR_Manager/Forecaster Orchestration State
#Supply_Chain_Agent/Forecaster Orchestration State
#Inventory_Manager/Forecaster orchestration State - can rely on Supply_Chain_Agent/Forecaster orchestration State
#Inventory_Manager/Spoilage_Optimizer Orchestration

@dataclass
class OrchestrationState:
    store: StoreState
    agent: AgentState
