from langchain.chat_models import init_chat_model

llm = init_chat_model(
    "llama3.2",
    model_provider="ollama"
)

response = llm.invoke([
    {
        "role": "user",
        "content": "Explain Python in 2 lines for a beginner."
    }
])

print(response.text)