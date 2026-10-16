"""
AI Prompt Kit for a Local Business

This tool asks a business owner five simple questions and then prints
three ready-to-use AI prompts (marketing, customer service, growth).
The owner can paste them into any AI such as Ollama, Claude or ChatGPT.

Who it is for: small business owners (bakery, clinic, salon, tuition
centre, mobile shop) who want help from AI but don't know what to type.
"""

# Ask the five questions. input() always returns text (a string).
business_name = input("Business name: ")
business_type = input("Business type: ")
city = input("City: ")
customers = input("Main customers: ")

# Why int(): the budget arrives as text, and we want it as a real number
# so it can be used for maths later (for example in Module 2).
budget = int(input("Monthly budget (PKR): "))

# Why a separator line: it makes the output easy to read and tells the
# owner exactly where the prompts start.
print()
print("=" * 41)
print(f"   AI Prompt Kit for {business_name}")
print("=" * 41)

# Why each prompt has a role, task, audience and tone/number: specific
# prompts get specific answers, vague prompts get vague answers.
print()
print("[1] Marketing")
print(f"""Write a short Instagram post for {business_name}, a {business_type} in {city}.
Target {customers}. Friendly tone, 1 call to action.""")

print()
print("[2] Customer Service")
print(f"""You are the manager of {business_name}. Write a polite reply to a customer
whose order arrived late. Apologise and offer a small discount.""")

# Why the budget is placed inside the prompt: it stops the AI from
# suggesting expensive tools the owner cannot afford.
print()
print("[3] Growth")
print(f"""Suggest 3 low-cost AI tools a {business_type} in {city} can use
to attract {customers} with a budget of {budget} PKR per month.""")