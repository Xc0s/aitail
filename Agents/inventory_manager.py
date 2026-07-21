#The node that acts on inventory thresholds and monitors purchase order status'

import langchain_core
from pydantic import (BaseModel, Field, model_validator)
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from Database.db import get_inventory
from Database.models import InventoryItem, AgentFinalOutput
from Tools.PO_tools import PO_tools

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


tool_map = {
    tool.name: tool for tool in PO_tools
}

llm_with_tools = llm.bind_tools(PO_tools)
structured_llm = llm.with_structured_output(
    AgentFinalOutput,
    method="json_schema"
)

SYSTEM_PROMPT = """
You are an inventory orchestration agent for a simulated convenience store.

Rules:
- Review the inventory data.
- If on_hand is below reorder_point, create a purchase order.
- Quantity should be target_stock minus on_hand.
- Use the PO_tools to create a purchase order when needed.
- After creating a purchase order, monitor the purchase order status through event listeners.
- Use the PO_tools to update order status.
- Only update status when a status transition is confirmed.
- Do not create duplicate purchase orders for the same SKU, and do not create another purchase order for a SKU you already made one for, when the status of that particular purchase order has not been set to 'delivered'.
- Do not invent products, vendors, quantities, or SKUs.
- If no reorder is needed, explain that no action was taken.
"""


def run_llm_agent_check():
    raw_inventory = get_inventory()

    inventory = [
        InventoryItem.model_validate(item).model_dump()
        for item in raw_inventory
    ]

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Current inventory: {inventory}")
    ]

    first_response = llm_with_tools.invoke(messages)
    messages.append(first_response)

    if not first_response.tool_calls:
        return {
            "final_response": first_response.content,
            "tool_results": []
        }

    tool_results = []

    for tool_call in first_response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        selected_tool = tool_map[tool_name]
        result = selected_tool.invoke(tool_args)

        tool_results.append(result)

        messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
        )

    final_output = structured_llm.invoke(messages)

    return {
        "final_response": final_output,
        "tool_results": tool_results
    }