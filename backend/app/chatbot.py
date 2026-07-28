"""
Core chatbot logic.

Uses OpenAI's tool calling (function calling) so the model itself decides
when it needs to look up an order or a product, rather than us hand-writing
intent classification / keyword matching. This is the same pattern you'd
extend in a real engagement by swapping data.py's mock lookups for calls to
the client's live systems.
"""

import json
import os
from typing import List

from openai import OpenAI

from .data import find_order, find_product
from .models import Message

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """You are Aria, the customer support assistant for an online store.

Your job:
- Answer general questions about the store (shipping, returns, hours) helpfully and briefly.
- Look up product information using the get_product_info tool whenever a customer
  asks about a specific product, price, or stock availability. Do not guess.
- Look up order status using the get_order_status tool whenever a customer asks
  about a shipment, delivery date, or order status. Ask for the order ID if
  they haven't given one.
- If a request is something you can't resolve (a refund decision, a complaint
  that needs a person, anything outside store policy), call escalate_to_human
  and let the customer know a team member will follow up.
- Keep replies short, warm, and to the point. No corporate filler.
- Never invent order numbers, tracking numbers, prices, or stock status.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": "Look up a product by SKU or name to get its price, "
            "description, and stock status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Product SKU (e.g. 'sku-100') or product name/keyword.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up an order by its order ID to get shipping "
            "status, carrier, tracking number, and estimated delivery date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID, e.g. 'ord-1001'.",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Flag the conversation for a human support agent to "
            "follow up on, for anything the assistant can't or shouldn't resolve itself.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Short summary of why this needs a human.",
                    }
                },
                "required": ["reason"],
            },
        },
    },
]


def _run_tool(name: str, tool_input: dict) -> str:
    if name == "get_product_info":
        product = find_product(tool_input.get("query", ""))
        if not product:
            return "No matching product found."
        return (
            f"{product['name']} ({product['sku']}) - ${product['price']:.2f}. "
            f"{'In stock' if product['in_stock'] else 'Out of stock'}. "
            f"{product['description']}"
        )

    if name == "get_order_status":
        order = find_order(tool_input.get("order_id", ""))
        if not order:
            return "No order found with that ID. Double-check the order ID with the customer."
        return (
            f"Order {order['order_id']}: status={order['status']}, "
            f"carrier={order['carrier'] or 'not yet assigned'}, "
            f"tracking_number={order['tracking_number'] or 'not yet available'}, "
            f"estimated_delivery={order['estimated_delivery']}."
        )

    if name == "escalate_to_human":
        # In production: create a ticket in Zendesk/Intercom/etc. and notify the team.
        reason = tool_input.get("reason", "unspecified")
        return f"Escalation logged for a human agent. Reason: {reason}"

    return f"Unknown tool: {name}"


def get_reply(conversation: List[Message]) -> tuple[str, list[str]]:
    """
    Send the conversation to the model, resolve any tool calls locally, and
    return (final_reply_text, list_of_tool_names_used).
    """
    client = OpenAI()  # reads OPENAI_API_KEY from env

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m.role, "content": m.content} for m in conversation
    ]
    used_tools: list[str] = []

    for _ in range(5):  # cap tool-use loops so a stuck model can't loop forever
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return (message.content or "").strip(), used_tools

        # Model wants to call one or more tools. Run them and feed results back.
        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
        )

        for tool_call in message.tool_calls:
            used_tools.append(tool_call.function.name)
            try:
                tool_input = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                tool_input = {}
            result_text = _run_tool(tool_call.function.name, tool_input)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_text,
                }
            )

    return (
        "Sorry, I'm having trouble finishing that request. "
        "Let me flag this for a teammate to help.",
        used_tools,
    )
