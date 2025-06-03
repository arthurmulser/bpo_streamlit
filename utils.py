#20250603 - testar select do get_total_leite_produzido;
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

def get_db_connection_sc():
    conn_sc = pymysql.connect(
        host='135.148.122.162',
        user='vedvoyager_vedvoyager_bpo_views',
        password='Jordeci1@',
        database='vedvoyager_vedvoyager_prod'
    )
    return conn_sc

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

# utils.py
def get_animais():
    conn = get_db_connection_sc()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        idtb_animais,
        nome,
        sexo,
        data_nascimento,
        idtb_animais_mae,
        nome_mae,
        idtb_ativo
    FROM view_animais
    WHERE idtb_animais_mae > 0
    ORDER BY data_nascimento DESC;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    animais = pd.DataFrame(rows, columns=[
        'idtb_animais',
        'nome',
        'sexo',
        'data_nascimento',
        'idtb_animais_mae',
        'nome_mae',
        'idtb_ativo'
    ])
    
    # Converter data_nascimento para datetime, tratando valores inválidos
    if not animais.empty:
        animais['data_nascimento'] = pd.to_datetime(
            animais['data_nascimento'],
            errors='coerce',  # Converte datas inválidas para NaT (Not a Time)
            format='%Y-%m-%d'
        )
        # Remover linhas com datas inválidas (opcional)
        animais = animais.dropna(subset=['data_nascimento'])
    
    return animais

##
def get_total_leite_produzido(data_inicial, data_final, idtb_animais):
    query = f"""
    SELECT 
        SUM(valor_calculado) AS total_valor_calculado
    FROM
        (SELECT 
            valor,
            dt_evento,
            CASE
                WHEN
                    dt_evento BETWEEN '{data_inicial}' AND '{data_final}'
                        AND MONTH('{data_inicial}') = MONTH('{data_final}')
                        AND YEAR('{data_inicial}') = YEAR('{data_final}')
                THEN
                    DATEDIFF('{data_final}', '{data_inicial}') + 1
                WHEN
                    MONTH(dt_evento) = MONTH('{data_inicial}')
                        AND YEAR(dt_evento) = YEAR('{data_inicial}')
                THEN
                    DATEDIFF(LAST_DAY(dt_evento), '{data_inicial}') + 1
                WHEN
                    MONTH(dt_evento) = MONTH('{data_final}')
                        AND YEAR(dt_evento) = YEAR('{data_final}')
                THEN
                    DAY('{data_final}')
                ELSE DAY(LAST_DAY(dt_evento))
            END AS dias_considerados,
            valor * CASE
                WHEN
                    dt_evento BETWEEN '{data_inicial}' AND '{data_final}'
                        AND MONTH('{data_inicial}') = MONTH('{data_final}')
                        AND YEAR('{data_inicial}') = YEAR('{data_final}')
                THEN
                    DATEDIFF('{data_final}', '{data_inicial}') + 1
                WHEN
                    MONTH(dt_evento) = MONTH('{data_inicial}')
                        AND YEAR(dt_evento) = YEAR('{data_inicial}')
                THEN
                    DATEDIFF(LAST_DAY(dt_evento), '{data_inicial}') + 1
                WHEN
                    MONTH(dt_evento) = MONTH('{data_final}')
                        AND YEAR(dt_evento) = YEAR('{data_final}')
                THEN
                    DAY('{data_final}')
                ELSE DAY(LAST_DAY(dt_evento))
            END AS valor_calculado
        FROM
            view_eventos
        WHERE
            idtb_eventos_tipos = 1
                AND idtb_animais = {idtb_animais}
                AND dt_evento BETWEEN '{data_inicial}' AND '{data_final}') AS subquery;
    """

    conn = get_db_connection_sc()
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return result or 0.0