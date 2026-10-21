"""
Module 2 Final Project: AI Business Assistant
Builds an agentic AI assistant with custom tools, JSON data persistence,
WhatsApp order importing, and robust error handling.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

import httpx
import ollama
from langchain_core.tools import tool
from pydantic import ValidationError

# ==========================================
# CONSTANTS & FILE PATHS
# ==========================================
BUSINESS_FILE = "business.json"
ORDERS_FILE = "orders.json"
TRANSCRIPT_FILE = "transcript.json"
ERROR_LOG_FILE = "errors.log"
MODEL_NAME = "llama3.1"
MAX_STEPS = 5

# Global runtime metrics
SESSION_METRICS = {
    "questions": 0,
    "answered": 0,
    "errors": 0,
    "whatsapp_imports": 0,
    "orders_placed": 0,
    "tool_calls": {
        "get_price": 0,
        "get_info": 0,
        "order_status": 0,
        "place_order": 0,
    },
}

# ==========================================
# HELPER FUNCTIONS (Lesson 2.3 & 2.5)
# ==========================================

def log_error(error_msg: str) -> None:
    """Logs errors with timestamps to errors.log without crashing."""
    SESSION_METRICS["errors"] += 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {error_msg}\n")
    except Exception:
        pass


def load_json(filepath: str, default: Any) -> Any:
    """Safely loads a JSON file, returning a default if missing or corrupted."""
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        log_error(f"Corrupted file {filepath}: {e}")
        print(f"[Warning] Could not read {filepath}. Starting fresh.")
        return default


def save_json(filepath: str, data: Any) -> None:
    """Saves data to a JSON file with indent=2 and ensure_ascii=False."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_error(f"Failed to save {filepath}: {e}")


def calculate_total(item: str, quantity: int) -> float:
    """Calculates total price in Python based on business.json prices."""
    business_data = load_json(BUSINESS_FILE, {})
    prices = business_data.get("prices", {})
    item_lower = item.lower().strip()
    
    unit_price = prices.get(item_lower, 0)
    return float(unit_price * quantity)


# Assert test for pure function
assert calculate_total("brownie", 2) == 600.0, "Test failed for calculate_total()"


# ==========================================
# TOOLS DEFINITION (Lesson 2.8)
# ==========================================

@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Read the price of a specific menu item.

    Args:
        item: The name of the item to look up.
    """
    SESSION_METRICS["tool_calls"]["get_price"] += 1
    business = load_json(BUSINESS_FILE, {})
    prices = business.get("prices", {})
    item_key = item.lower().strip()
    
    if item_key in prices:
        return f"{item} costs {prices[item_key]} PKR"
    return f"Sorry, '{item}' is not currently on our menu."


@tool(parse_docstring=True)
def get_info(topic: str) -> str:
    """Read general business information such as hours, delivery, or location.

    Args:
        topic: The topic or key to look up (e.g., hours, delivery, city).
    """
    SESSION_METRICS["tool_calls"]["get_info"] += 1
    business = load_json(BUSINESS_FILE, {})
    
    if topic.lower() in business:
        return f"{topic}: {business[topic.lower()]}"
    
    # Search keys loosely
    for k, v in business.items():
        if topic.lower() in k.lower():
            return f"{k}: {v}"
            
    return f"Information about '{topic}' is not available."


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check the status of an existing order from orders.json.

    Args:
        order_id: The unique ID of the order (e.g., A101).
    """
    SESSION_METRICS["tool_calls"]["order_status"] += 1
    orders = load_json(ORDERS_FILE, [])
    
    for order in orders:
        if order.get("id", "").upper() == order_id.upper():
            return (
                f"Order {order['id']} for {order['customer']} is "
                f"{order['status']}, total {order['total']} PKR"
            )
            
    return f"Order ID '{order_id}' was not found in our records."


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Place a new customer order after calculating total and getting owner approval.

    Args:
        item: The menu item being ordered.
        quantity: The quantity of the item.
        customer: The name of the customer placing the order.
    """
    SESSION_METRICS["tool_calls"]["place_order"] += 1
    
    # Verify item exists and calculate total in Python
    business = load_json(BUSINESS_FILE, {})
    prices = business.get("prices", {})
    item_lower = item.lower().strip()
    
    if item_lower not in prices:
        return f"Cannot place order: '{item}' is not on the menu."
        
    total = calculate_total(item_lower, quantity)
    
    # Ask for owner approval via input()
    print(f"\n  [approve] {quantity} x {item} for {customer} = {total} PKR. Place it? (yes/no): ", end="")
    approval = input().strip().lower()
    
    if approval not in ["yes", "y"]:
        return "Order placement cancelled by the owner."
        
    orders = load_json(ORDERS_FILE, [])
    order_id = f"A{101 + len(orders)}"
    
    new_order = {
        "id": order_id,
        "customer": customer,
        "items": [{item: quantity}],
        "total": total,
        "status": "received"
    }
    
    orders.append(new_order)
    save_json(ORDERS_FILE, orders)
    SESSION_METRICS["orders_placed"] += 1
    
    return f"Order {order_id} placed: {quantity} x {item}, total {total} PKR"


TOOLS_MAP = {
    "get_price": get_price,
    "get_info": get_info,
    "order_status": order_status,
    "place_order": place_order,
}


# ==========================================
# WHATSAPP EXTRACTOR SCHEMA (Lesson 2.7)
# ==========================================
class ExtractedOrder(BaseModel):
    is_order: bool = Field(description="True if the message is a customer order, False otherwise.")
    customer_name: Optional[str] = Field(description="Customer name if present, else null.")
    item: Optional[str] = Field(description="Menu item requested.")
    quantity: Optional[int] = Field(description="Quantity requested.")
    address: Optional[str] = Field(description="Delivery address if mentioned.")


# ==========================================
# MAIN APPLICATION LOOP
# ==========================================
def main() -> None:
    # 1. Startup Checks
    if not os.path.exists(BUSINESS_FILE):
        print(f"Error: {BUSINESS_FILE} not found. Please create it before running.")
        sys.exit(1)

    business_data = load_json(BUSINESS_FILE, {})
    business_name = business_data.get("name", "Business Assistant")

    print("=" * 60)
    print(f"    {business_name} AI Business Assistant")
    print("=" * 60)
    print("Ask anything, or use: /import, /orders, /reset, bye")

    # Load persistent chat transcript
    transcript: List[Dict[str, str]] = load_json(TRANSCRIPT_FILE, [])

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # Command handling
        cmd = user_input.lower()
        if cmd == "bye":
            print("Assistant: Goodbye! Everything is saved.")
            break
        elif cmd == "/reset":
            transcript = []
            save_json(TRANSCRIPT_FILE, transcript)
            print("Assistant: Chat memory has been reset.")
            continue
        elif cmd == "/orders":
            orders = load_json(ORDERS_FILE, [])
            if not orders:
                print("Assistant: No orders on file.")
            else:
                print("Assistant Orders on File:")
                for idx, o in enumerate(orders, 1):
                    print(f"  {idx}. {o['id']} | {o['customer']} | {o['total']} PKR | {o['status']}")
            continue
        elif cmd == "/import":
            SESSION_METRICS["whatsapp_imports"] += 1
            wa_msg = input("Paste the WhatsApp message: ").strip()
            if not wa_msg:
                print("Assistant: Empty message, import cancelled.")
                continue

            print("Analyzing WhatsApp message...")
            try:
                extraction_prompt = (
                    f"Extract order info from this WhatsApp message: '{wa_msg}'. "
                    f"Menu items available: {list(business_data.get('prices', {}).keys())}"
                )
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": extraction_prompt}],
                    format=ExtractedOrder.model_json_schema(),
                    options={"temperature": 0}
                )
                parsed = ExtractedOrder.model_validate_json(response["message"]["content"])
                
                if not parsed.is_order:
                    print("CHECK: Not an order message. Needs a human reply.")
                    continue

                item = parsed.item or ""
                qty = parsed.quantity or 1
                cust = parsed.customer_name or ""
                
                # Validation checks
                prices = business_data.get("prices", {})
                print(f"  {qty} x {item} = {calculate_total(item, qty)} PKR")
                print(f"  Customer: {cust if cust else '[Missing]'}")
                
                if item.lower() not in prices:
                    print(f"  CHECK: '{item}' is not on the menu")
                if not cust or cust.lower() in ["unknown", "none"]:
                    print("  CHECK: customer name is missing or invented")

                print(f"  [approve] Save this order? (yes/no): ", end="")
                app = input().strip().lower()
                if app in ["yes", "y"]:
                    orders = load_json(ORDERS_FILE, [])
                    order_id = f"A{101 + len(orders)}"
                    total = calculate_total(item, qty)
                    new_o = {
                        "id": order_id,
                        "customer": cust if cust else "WhatsApp Customer",
                        "items": [{item: qty}],
                        "total": total,
                        "status": "received"
                    }
                    orders.append(new_o)
                    save_json(ORDERS_FILE, orders)
                    SESSION_METRICS["orders_placed"] += 1
                    print("  Order saved successfully!")
                else:
                    print("  Not saved.")
            except (ValidationError, Exception) as e:
                log_error(f"WhatsApp import error: {e}")
                print(f"CHECK: Error processing message format ({e}).")
            continue

        # Standard AI Agent Turn
        SESSION_METRICS["questions"] += 1
        
        # Build system message & memory (last 8 messages)
        system_msg = {
            "role": "system",
            "content": (
                f"You are the AI assistant for {business_name}. "
                "Use the provided tools to check prices, business info, order status, or place orders. "
                "Never guess prices, hours, or order statuses; always use tools. "
                "Be polite, professional, and concise."
            )
        }
        
        memory = transcript[-8:] if len(transcript) >= 8 else transcript
        messages = [system_msg] + memory + [{"role": "user", "content": user_input}]
        
        # Agent execution loop with MAX_STEPS
        step = 0
        final_answer = ""
        
        while step < MAX_STEPS:
            step += 1
            try:
                res = ollama.chat(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=[get_price, get_info, order_status, place_order]
                )
            except (httpx.ConnectError, ollama.ResponseError) as e:
                log_error(str(e))
                print("Assistant: Connection error. Please check if Ollama is running.")
                final_answer = "Sorry, I am currently offline."
                break
            except Exception as e:
                log_error(str(e))
                print("Assistant: Something went wrong.")
                final_answer = "Sorry, an unexpected error occurred."
                break

            msg = res["message"]
            messages.append(msg)

            if msg.get("tool_calls"):
                for tool_call in msg["tool_calls"]:
                    fn_name = tool_call["function"]["name"]
                    fn_args = tool_call["function"]["arguments"]
                    
                    print(f"  [tool] {fn_name}({fn_args})")
                    
                    if fn_name in TOOLS_MAP:
                        try:
                            tool_result = TOOLS_MAP[fn_name](**fn_args)
                        except Exception as e:
                            tool_result = f"Error executing tool: {e}"
                            log_error(tool_result)
                    else:
                        tool_result = f"Error: Tool {fn_name} not found."

                    print(f"         -> {tool_result}")
                    
                    messages.append({
                        "role": "tool",
                        "content": str(tool_result),
                        "name": fn_name,
                    })
            else:
                final_answer = msg.get("content", "")
                break
        else:
            final_answer = "I'm sorry, I exceeded maximum processing steps for this request."

        print(f"Assistant: {final_answer}")
        SESSION_METRICS["answered"] += 1

        # Append plain dictionaries to transcript memory
        transcript.append({"role": "user", "content": user_input})
        transcript.append({"role": "assistant", "content": final_answer})
        save_json(TRANSCRIPT_FILE, transcript)

    # Print Session Report
    print("\n" + "=" * 60)
    print("Session report")
    print(f"Questions: {SESSION_METRICS['questions']} | Answered: {SESSION_METRICS['answered']} | Errors: {SESSION_METRICS['errors']}")
    print(f"WhatsApp imports: {SESSION_METRICS['whatsapp_imports']} | Orders placed: {SESSION_METRICS['orders_placed']} | Orders on file: {len(load_json(ORDERS_FILE, []))}")
    print("Tool calls:")
    for t_name, count in SESSION_METRICS["tool_calls"].items():
        print(f"  {t_name}: {count}")
    print("=" * 60)


if __name__ == "__main__":
    main()