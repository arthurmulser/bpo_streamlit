#20250313
import pandas as pd
import pymysql

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