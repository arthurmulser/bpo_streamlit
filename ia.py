import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Configuração básica
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Criação do modelo
model = ChatGroq(
    temperature=0.7,
    model_name="llama3-8b-8192",  # ou "llama3-70b-8192"
    api_key=groq_api_key
)

print("\n🤖 Assistente de IA Simples (Digite 'sair' para encerrar)\n")

while True:
    pergunta = input("👉 Você: ").strip()
    
    if pergunta.lower() in ['sair', 'exit', 'quit']:
        break
    
    try:
        resposta = model.invoke(pergunta)
        print("\n🧠 Resposta:", resposta.content)
    except Exception as e:
        print(f"\n⚠️ Erro: {str(e)}")
    
    print("\n" + "-"*50 + "\n")

print("\nAté mais! 👋")