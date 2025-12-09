#20250603 - testar select do get_total_leite_produzido;
import pandas as pd
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection(): #20250608
    conn = pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_DATABASE_BPO')
    )
    return conn

def get_db_connection_lars(): #20251209
    conn_sc = pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_DATABASE_LARS')
    )
    return conn_sc 

def get_db_connection_sc(): #20250608
    conn_sc = pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_DATABASE_SC')
    )
    return conn_sc

def get_realizados_por_empresa(selected_empresa=None): #20250608
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

def get_empresas(): #20250608
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT DISTINCT
        IdEmpresa, Empresa
    FROM
        view_realizados
    GROUP BY IdEmpresa;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    empresas = pd.DataFrame(rows, columns=['IdEmpresa', 'Empresa'])
    return empresas

def get_animais(): #20250608
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
        dt_desmame,
        idtb_ativo
    FROM
        view_animais
    ;
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
        'dt_desmame',
        'idtb_ativo'
    ])
    
    if not animais.empty:
        animais['data_nascimento'] = pd.to_datetime(
            animais['data_nascimento'],
            errors='coerce', 
            format='%Y-%m-%d'
        )
    
    return animais

def get_total_leite_produzido(data_inicial, data_final, idtb_animais): #20250608 - vou substituir isso por um select que retorna a média de produção entre o nascimento e o desmame;
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

def get_media_leite_por_periodo(data_inicial, data_final, idtb_animais): #20250608
    query = """
    SELECT AVG(valor)
    FROM view_eventos
    WHERE idtb_eventos_tipos = 1
      AND idtb_animais = %s
      AND dt_evento BETWEEN %s AND %s
    """
    
    try:
        conn = get_db_connection_sc()
        with conn.cursor() as cursor:
            cursor.execute(query, (idtb_animais, data_inicial, data_final))
            result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    
    except Exception as e:
        print(f"erro ao calcular média: {e}")
        return 0.0
    
    finally:
        if 'conn' in locals() and conn:
            conn.close()


   