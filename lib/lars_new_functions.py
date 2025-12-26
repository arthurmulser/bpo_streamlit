from functools import lru_cache
import yfinance as yf
import streamlit as st # keep this for st.warning, can be removed if moved to pure backend;

@lru_cache(maxsize=100)
def get_current_price(nome_patrimonio: str, bolsa_valores: str):
    """
    busca o preço atual de um ativo no yahoo finance com base no nome do patrimônio e na bolsa de valores.
    adiciona o sufixo '.sa' para ações da b3.
    args:
        nome_patrimonio (str): o nome ou símbolo do patrimônio (e.g., 'itsa4', 'aapl').
        bolsa_valores (str): a bolsa de valores onde o ativo é negociado (e.g., 'b3', 'nasdaq').
    Returns:
        float: o preço atual do ativo, ou none se não for possível obtê-lo.
    """
    if not isinstance(nome_patrimonio, str) or not nome_patrimonio:
        st.warning(f"nome do patrimônio inválido: {nome_patrimonio}")
        return None
    if not isinstance(bolsa_valores, str) or not bolsa_valores:
        st.warning(f"bolsa de valores inválida para {nome_patrimonio}: {bolsa_valores}")
        return None

    ticker_symbol = nome_patrimonio.upper() # ensure uppercase;
    if bolsa_valores.upper() == 'B3':
        if not ticker_symbol.endswith('.SA'): # avoid double suffix;
            ticker_symbol = f"{ticker_symbol}.SA"

    try:
        ticker = yf.Ticker(ticker_symbol)
        # tenta pegar o preço de mercado regular, que é o mais atual;
        info = ticker.info
        if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
            return info['regularMarketPrice']
        elif 'currentPrice' in info and info['currentPrice'] is not None:
            return info['currentPrice']
        else:
            # se não conseguir o preço de mercado, tenta o último preço de fechamento do dia;
            todays_data = ticker.history(period='1d')
            if not todays_data.empty:
                return todays_data['Close'].iloc[-1]
            else:
                st.warning(f"não foi possível obter o preço atual para {ticker_symbol}, a resposta da api pode estar vazia ou o ticker pode ser inválido.")
                return None
    except Exception as e:
        
        return None
