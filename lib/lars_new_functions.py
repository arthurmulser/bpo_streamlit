from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st # keep this for st.warning, can be removed if moved to pure backend;
import pandas as pd
import math


def get_current_price(nome_patrimonio: str, bolsa_valores: str, data_fim: datetime = None):
    """
    busca o preço de um ativo no yahoo finance.
    se uma data for fornecida, busca o preço de fechamento para essa data.
    caso contrário, busca o preço atual.
    adiciona o sufixo '.sa' para ações da b3.
    args:
        nome_patrimonio (str): o símbolo do patrimônio (e.g., 'itsa4', 'aapl').
        bolsa_valores (str): a bolsa onde o ativo é negociado (e.g., 'b3', 'nasdaq').
        data (datetime, optional): a data para a qual o preço deve ser buscado. defaults to none (preço atual).
    returns:
        tuple[float, str] or none: uma tupla contendo o preço e a moeda (e.g., (50.25, 'brl')),
                                     ou none se não for possível obtê-lo.
    """
    if not isinstance(nome_patrimonio, str) or not nome_patrimonio:
        # st.warning(f"nome do patrimônio inválido: {nome_patrimonio}");
        return None
    if not isinstance(bolsa_valores, str) or not bolsa_valores:
        # st.warning(f"bolsa de valores inválida para {nome_patrimonio}: {bolsa_valores}");
        return None

    is_historical = data_fim is not None
    if data_fim is None:
        data_fim = datetime.now()

    ticker_symbol = nome_patrimonio.upper() # ensure uppercase;
    ticker_symbol = ticker_symbol.replace('.', '-') # replace dot with hyphen for class shares;
    if bolsa_valores.upper() == 'B3':
        if not ticker_symbol.endswith('.SA'):
            ticker_symbol = f"{ticker_symbol}.SA"

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        currency = info.get('currency', None)
        price = None

        # se não for busca histórica, tenta obter o preço atual primeiro;
        if not is_historical:
            if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                price = info['regularMarketPrice']
            elif 'currentPrice' in info and info['currentPrice'] is not None:
                price = info['currentPrice']
            
            if price is not None and currency is not None:
                return price, currency.upper()

        # para busca histórica ou como fallback para o preço atual;
        end_date = data_fim
        start_date = end_date - timedelta(days=7)
        
        hist = ticker.history(start=start_date, end=end_date)
        
        if not hist.empty:
            price = hist['Close'].iloc[-1]

        if price is not None and currency is not None:
            return price, currency.upper()
        
        return None

    except Exception as e:
        # st.warning(f"erro ao buscar preço para {nome_patrimonio}: {e}");
        return None

def calculate_patrimonio_with_splits(df_events, data_fim: datetime = None):
    """
    calcula a quantidade total e o valor total de um patrimônio até uma data específica.
    se nenhuma data for fornecida, considera todos os eventos até a data atual.
    """
    if data_fim is None:
        data_fim = datetime.now()

    # converte a coluna 'dt_evento' para datetime para garantir a comparação correta;
    df_events['dt_evento'] = pd.to_datetime(df_events['dt_evento'])

    # filtra os eventos para incluir apenas aqueles até a data especificada;
    df_filtered = df_events[df_events['dt_evento'] <= data_fim].copy()
    
    if df_filtered.empty:
        return pd.Series({'quantidade': 0, 'valor_convertido': 0})

    df_filtered = df_filtered.sort_values(by='dt_evento')
    
    total_quantity = 0
    total_value = 0
    
    # pega o valor de use_decimal do primeiro evento;
    use_decimal = df_filtered['use_decimal'].iloc[0]
    
    for _, row in df_filtered.iterrows():
        event_type = row['evento']
        quantity = row['quantidade']
        value = row['valor_convertido']

        if event_type == 'C':  # compra;
            total_quantity += quantity
            total_value += value
        elif event_type == 'B':  # bonificação;
            total_quantity += quantity
            if use_decimal == 2:
                total_quantity = math.floor(total_quantity)
        elif event_type == 'D':  # desdobramento;
            if total_quantity > 0:
                total_quantity *= quantity
                if use_decimal == 2:
                    total_quantity = math.floor(total_quantity)
        elif event_type == 'G':  # grupamento;
            if total_quantity > 0:
                total_quantity /= quantity
                if use_decimal == 2:
                    total_quantity = math.floor(total_quantity)
    
    return pd.Series({'quantidade': total_quantity, 'valor_convertido': total_value})
