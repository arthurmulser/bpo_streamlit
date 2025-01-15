import streamlit as x
import pymysql
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da conexão com o banco de dados
def get_db_connection():
    conn = pymysql.connect(
        host='135.148.122.162',
        user='vedvoyager_vedvoyager_bpo_views',
        password='Jordeci1@',
        database='vedvoyager_bpo'
    )
    return conn

# Consulta ajustada para somar receitas e despesas por mês e ano
# Consulta ajustada para somar receitas e despesas por mês e ano
def get_data_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Consulta SQL
    query = """
    SELECT 
        YEAR(DataPagamento) AS Ano,
        MONTH(DataPagamento) AS Mes,
        TipoConta,
        SUM(Valor) AS Total
    FROM view_realizados
    GROUP BY YEAR(DataPagamento), MONTH(DataPagamento), TipoConta
    ORDER BY YEAR(DataPagamento), MONTH(DataPagamento);
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convertendo os dados para um DataFrame
    df = pd.DataFrame(rows, columns=['Ano', 'Mes', 'TipoConta', 'Total'])
    
    # Criando uma coluna de "Mês/Ano" no formato datetime
    df['Mes_Ano'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mes'].astype(str) + '-01')
    
    # Ordenando os dados corretamente pelo ano e mês
    df = df.sort_values(by='Mes_Ano')
    
    # Convertendo "Mes_Ano" de volta para o formato string para exibição
    df['Mes_Ano'] = df['Mes_Ano'].dt.strftime('%Y/%m')
    
    return df


# Exibindo a interface do Streamlit
x.title("Gráfico de Receitas e Despesas por Mês/Ano")

# Botão para buscar dados e exibir o gráfico
if x.button('Gerar Gráfico'):
    data = get_data_from_db()
    
    if not data.empty:
        # Separando receitas e despesas em tabelas dinâmicas
        pivot_data = data.pivot(index='Mes_Ano', columns='TipoConta', values='Total')
        pivot_data = pivot_data.fillna(0)  # Substitui valores NaN por 0

        # Criando o gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        pivot_data.plot(kind='bar', ax=ax, color={'RECEITA': 'green', 'DESPESA': 'red'})
        
        # Configurações do gráfico
        ax.set_title("Receitas e Despesas por Mês/Ano", fontsize=14)
        ax.set_xlabel("Mês/Ano", fontsize=12)
        ax.set_ylabel("Total (R$)", fontsize=12)
        ax.legend(title="Tipo de Conta", fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Exibindo o gráfico no Streamlit
        x.pyplot(fig)
    else:
        x.write("Nenhum dado encontrado.")
