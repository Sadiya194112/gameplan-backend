from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:3b", base_url="http://127.0.0.1:11434")
response = llm.invoke("Hello, how are you?")
print(response.content)
