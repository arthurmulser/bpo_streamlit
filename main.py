import streamlit as x
import pymysql
import pandas as pd
import matplotlib.pyplot as plt

x.markdown(
    """
    <style>
        html, body, [class*="css"] {           
            font-size: 15px; /* tamanho da tela */  
        }
        .title {    
            text-align: left;
        }
        .stSelectbox label, .stSelectbox div {
            font-family: "Courier New", monospace !important;
            
        }
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            font-family: "Courier New", monospace !important;
        }
        
    </style>
    """,
    unsafe_allow_html=True,
)

plt.style.use('dark_background')

def get_db_connection():
    conn = pymysql.connect(
        host='135.148.122.162',
        user='vedvoyager_vedvoyager_bpo_views',
        password='Jordeci1@',
        database='vedvoyager_bpo'
    )
    return conn

def get_data_from_db(selected_empresa=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        YEAR(DataPagamento) AS Ano,
        MONTH(DataPagamento) AS Mes,
        TipoConta,
        SUM(Valor) AS Total
    FROM view_realizados 
    WHERE Empresa = %s
    GROUP BY YEAR(DataPagamento), MONTH(DataPagamento), TipoConta
    ORDER BY YEAR(DataPagamento), MONTH(DataPagamento);
    """
    
    cursor.execute(query, (selected_empresa,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(rows, columns=['Ano', 'Mes', 'TipoConta', 'Total'])
    df['Mes_Ano'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mes'].astype(str) + '-01')
    df = df.sort_values(by='Mes_Ano')
    df['Mes_Ano'] = df['Mes_Ano'].dt.strftime('%Y/%m')
    
    return df

def get_empresas():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT DISTINCT IdEmpresa, Empresa 
    FROM view_realizados
    GROUP BY IdEmpresa;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    empresas = pd.DataFrame(rows, columns=['IdEmpresa', 'Empresa'])
    return empresas

x.markdown('<h1 class="title">Receitas/Despesas</h1>', unsafe_allow_html=True)

empresas_df = get_empresas()

empresa_selecionada = x.selectbox(
    "Empresa:",
    options=empresas_df['Empresa'].tolist(),
    index=0
)

if not empresas_df.empty:
    empresa_id = empresas_df.loc[empresas_df['Empresa'] == empresa_selecionada, 'IdEmpresa'].values[0]
else:
    empresa_id = None

data = get_data_from_db(selected_empresa=empresa_selecionada)

if not data.empty:
    
    pivot_data = data.pivot(index='Mes_Ano', columns='TipoConta', values='Total')
    pivot_data = pivot_data.fillna(0)

    
    fig, ax = plt.subplots(figsize=(17, 8))
    pivot_data.plot(
        kind='bar',
        ax=ax,
        color={'RECEITA': 'white', 'DESPESA': 'gray'}
    )
    
    ax.set_title("Receitas e Despesas por Mês/Ano", fontsize=14, color='white')
    ax.set_xlabel("Mês/Ano", fontsize=12, color='white')
    ax.set_ylabel("Total (R$)", fontsize=12, color='white')
    ax.legend(title="Tipo de Conta", fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7, color='white')
    ax.tick_params(colors='white')

    x.pyplot(fig)
else:
    x.write(
        "<p style='color: white; text-align: center;'>Nenhum dado encontrado.</p>",
        unsafe_allow_html=True,
    )
