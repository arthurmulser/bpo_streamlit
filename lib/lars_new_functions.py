from functools import lru_cache
import yfinance as yf
import streamlit as st # keep this for st.warning, can be removed if moved to pure backend;

@lru_cache(maxsize=100)
def get_current_price(nome_patrimonio: str, bolsa_valores: str):
    """
    busca o preço atual e a moeda de um ativo no yahoo finance.
    adiciona o sufixo '.sa' para ações da b3.
    args:
        nome_patrimonio (str): o símbolo do patrimônio (e.g., 'itsa4', 'aapl').
        bolsa_valores (str): a bolsa onde o ativo é negociado (e.g., 'b3', 'nasdaq').
    returns:
        tuple[float, str] or none: uma tupla contendo o preço atual e a moeda (e.g., (50.25, 'brl')),
                                     ou none se não for possível obtê-lo.
    """
    if not isinstance(nome_patrimonio, str) or not nome_patrimonio:
        # st.warning(f"nome do patrimônio inválido: {nome_patrimonio}");
        return None
    if not isinstance(bolsa_valores, str) or not bolsa_valores:
        # st.warning(f"bolsa de valores inválida para {nome_patrimonio}: {bolsa_valores}");
        return None

    ticker_symbol = nome_patrimonio.upper() # ensure uppercase;
    ticker_symbol = ticker_symbol.replace('.', '-') # replace dot with hyphen for class shares;
    if bolsa_valores.upper() == 'B3':
        if not ticker_symbol.endswith('.SA'):
            ticker_symbol = f"{ticker_symbol}.SA"

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        price = None
        currency = info.get('currency', None)

        if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
            price = info['regularMarketPrice']
        elif 'currentPrice' in info and info['currentPrice'] is not None:
            price = info['currentPrice']
        
        # fallback para o histórico se o preço atual não estiver no 'info';
        if price is None:
            todays_data = ticker.history(period='1d')
            if not todays_data.empty:
                price = todays_data['Close'].iloc[-1]

        if price is not None and currency is not None:
            return price, currency.upper()
        else:
            return None

    except Exception as e:
        return None