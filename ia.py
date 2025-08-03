import os # acessar variáveis de ambiente;
from dotenv import load_dotenv
from langchain_groq import ChatGroq # biblioteca grog;

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    temperature=0.7,
    model_name="llama3-8b-8192",  # ou "llama3-70b-8192"
    api_key=groq_api_key
)

print("\n🤖 assistente de ia simples (digite 'sair' para encerrar)\n")

while True:
    pergunta = input("👉 você: ").strip()
    
    if pergunta.lower() in ['sair', 'exit', 'quit']:
        break
    
    try:
        resposta = model.invoke(pergunta)
        print("\n🧠 resposta:", resposta.content)
    except Exception as e:
        print(f"\n⚠️ erro: {str(e)}")
    
    print("\n" + "-"*50 + "\n")

print("\naté mais! 👋")