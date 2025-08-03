import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import mysql.connector
import pandas as pd

load_dotenv()

db_config = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}

model = ChatGroq(
    temperature=0.7,
    model_name="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY")
)

def query_mysql(query: str) -> pd.DataFrame:
    """executa uma query no mysql e retorna um dataframe."""
    conn = mysql.connector.connect(**db_config)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def analyze_with_ai(context: str, question: str) -> str:
    """envia dados + pergunta para a ia."""
    prompt = f"""
    contexto (dados do banco mysql):
    {context}

    pergunta:
    {question}

    analise os dados acima e responda de forma clara.
    """
    response = model.invoke(prompt)
    return response.content

print("\n🤖 assistente de ia com análise de mysql (digite 'sair' para encerrar)\n")

while True:
    pergunta = input("👉 você: ").strip()
    
    if pergunta.lower() in ['sair', 'exit', 'quit']:
        break
    
    try:
        tabelas = query_mysql("show tables;")
        print(f"\n📊 tabelas disponíveis: {', '.join(tabelas.iloc[:, 0]).lower()}")

        tabela_alvo = input("👉 qual tabela analisar? ").strip()
        dados = query_mysql(f"SELECT * FROM {tabela_alvo} LIMIT 5;") 

        resposta = analyze_with_ai(
            context=f"dados da tabela {tabela_alvo}:\n{dados.to_markdown()}",
            question=pergunta
        )
        print(f"\n🧠 resposta:\n{resposta.lower()}")

    except Exception as e:
        print(f"\n⚠️ erro: {str(e).lower()}")
    
    print("\n" + "-"*50 + "\n")

print("\naté mais! 👋")