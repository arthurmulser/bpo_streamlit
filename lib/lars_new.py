import os
from pathlib import Path
import pandas as pd
import streamlit as st
from utils import get_db_connection_lars
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from lars_new_functions import get_current_price
import yfinance as yf
from functools import lru_cache

CSV_DIR = Path(__file__).parent / "_csv"
CSV_DIR.mkdir(exist_ok=True)

def fetch_and_save_patrimonios_eventos(path: Path):
    """Busca `patrimonios_eventos` do banco usando `get_db_connection_lars()` e salva em csv."""
    query = """
    SELECT
        idtb_patrimonios_eventos,
        idtb_patrimonios,
        dt_evento,
        evento,
        quantidade,
        valor,
        idtb_empresas,
        nome_patrimonio,
        bolsa_valores,
        broker,
        standard_currency,
        nome_empresa
    FROM
        patrimonios_eventos;
    """
    conn = get_db_connection_lars()
    try:
        df = pd.read_sql(query, conn)
        if not df.empty:
            df['dt_evento'] = pd.to_datetime(df['dt_evento'], errors='coerce')
        df.to_csv(path, index=False)
        return df
    finally:
        conn.close()



def lars_new():
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown("""
            <h1 class="title">LARS - CSV</h1>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("<-"):
            st.session_state.tela_atual = "A"

    patrimonios_eventos_csv = CSV_DIR / "view_patrimonios_eventos.csv"

    st.write("### csv management;")
    if st.button("(re)gerar patrimônios eventos csv;"):
        with st.spinner("buscando patrimônios eventos do db e salvando csv;"):
            df_patrimonios_eventos = fetch_and_save_patrimonios_eventos(patrimonios_eventos_csv)
        st.success(f"salvo: {patrimonios_eventos_csv};")

    st.markdown("---")
    display_patrimonio_por_empresa(patrimonios_eventos_csv)


@lru_cache(maxsize=10)
def get_exchange_rate(from_currency, to_currency):
    """busca a taxa de câmbio usando o yahoo finance e armazena em cache."""
    if from_currency == to_currency:
        return 1.0
    try:
        ticker = f"{from_currency}{to_currency}=X"
        rate_data = yf.Ticker(ticker)
        rate = rate_data.history(period='1d')['Close'].iloc[0]
        return rate
    except Exception as e:
        st.error(f"não foi possível obter a taxa de câmbio para {from_currency} para {to_currency}: {e}.")
        return None

def display_patrimonio_por_empresa(csv_path: Path):
    """exibe os patrimônios por empresa com conversão de moeda."""
    st.write("### patrimônios por empresa")

    if not csv_path.exists():
        st.warning(f"arquivo csv não encontrado em {csv_path}. por favor, gere o arquivo primeiro.")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"erro ao ler o arquivo csv: {e}")
        return

    if 'nome_empresa' not in df.columns:
        st.error("a coluna 'nome_empresa' não foi encontrada no csv.")
        return

    # adiciona a opção '-selecione-' e ordena as empresas;
    empresa_options = ['-selecione-'] + sorted(df['nome_empresa'].dropna().unique().tolist())
    empresa_selecionada = st.selectbox("empresa:", options=empresa_options)

    if empresa_selecionada and empresa_selecionada != '-selecione-': # verifica se uma empresa válida foi selecionada;
        df_empresa = df[df['nome_empresa'] == empresa_selecionada].copy()

        if df_empresa.empty:
            st.info("nenhum dado de patrimônio encontrado para esta empresa.")
            return

        # adiciona a opção '-selecione-' para as moedas;
        target_currency_options = ['-selecione-', 'BRL', 'USD']
        target_currency = st.selectbox("converter para:", options=target_currency_options)

        if target_currency and target_currency != '-selecione-': # verifica se uma moeda válida foi selecionada;
            # exibe as taxas de conversão utilizadas;
            source_currencies = df_empresa['standard_currency'].dropna().unique()
            for source_curr in source_currencies:
                if source_curr != target_currency:
                    rate = get_exchange_rate(source_curr, target_currency)
                    if rate is not None:
                        st.info(f"cotação {source_curr} para {target_currency}: {rate:.4f}")

            # garante que as colunas 'valor' e 'quantidade' são numéricas;
            df_empresa['valor'] = pd.to_numeric(df_empresa['valor'], errors='coerce')
            df_empresa['quantidade'] = pd.to_numeric(df_empresa['quantidade'], errors='coerce')
            df_empresa.dropna(subset=['valor', 'quantidade', 'standard_currency'], inplace=True)
            
            # calcula o valor total original;
            df_empresa['valor_total'] = df_empresa['valor'] * df_empresa['quantidade']

            # converte a moeda;
            df_empresa['valor_convertido'] = df_empresa.apply(
                lambda row: row['valor_total'] * get_exchange_rate(row['standard_currency'], target_currency)
                if row['standard_currency'] != target_currency else row['valor_total'],
                axis=1
            )
            df_empresa.dropna(subset=['valor_convertido'], inplace=True)

            if df_empresa.empty:
                st.warning("não foi possível converter os valores para a moeda de destino.")
                return

            # agrega os dados após a conversão;
            agg_funcs = {
                'quantidade': ('quantidade', 'sum'),
                'valor_convertido': ('valor_convertido', 'sum')
            }
            patrimonio_agg = df_empresa.groupby('nome_patrimonio').agg(**agg_funcs).reset_index()

            # evita divisão por zero;
            patrimonio_agg['preco_medio_convertido'] = np.where(
                patrimonio_agg['quantidade'] != 0,
                patrimonio_agg['valor_convertido'] / patrimonio_agg['quantidade'],
                0
            )

            # busca o preço atual para cada patrimônio;
            with st.spinner("Buscando cotações atuais..."):
                # cria um mapa de nome_patrimonio para bolsa_valores;
                bolsa_map = df_empresa.drop_duplicates(subset=['nome_patrimonio'])[['nome_patrimonio', 'bolsa_valores']].set_index('nome_patrimonio')
                patrimonio_agg = patrimonio_agg.join(bolsa_map, on='nome_patrimonio')

                # busca o preço atual e sua moeda (retorna uma tupla);
                price_data = patrimonio_agg.apply(
                    lambda row: get_current_price(row['nome_patrimonio'], row['bolsa_valores']) if pd.notna(row['bolsa_valores']) else None,
                    axis=1
                )

                # desempacota a tupla em duas colunas;
                patrimonio_agg[['preco_atual_raw', 'preco_atual_moeda']] = pd.DataFrame(price_data.tolist(), index=patrimonio_agg.index)

                # converte o preço atual para a moeda de destino;
                def convert_price(row):
                    if pd.isna(row['preco_atual_raw']) or pd.isna(row['preco_atual_moeda']):
                        return None
                    if row['preco_atual_moeda'] == target_currency:
                        return row['preco_atual_raw']
                    
                    rate = get_exchange_rate(row['preco_atual_moeda'], target_currency)
                    if rate is None:
                        return None # falha na conversão;
                    return row['preco_atual_raw'] * rate

                patrimonio_agg['preco_atual_convertido'] = patrimonio_agg.apply(convert_price, axis=1)

            st.write(f"Patrimônios de: **{empresa_selecionada}** em **{target_currency}**")

            # gráfico de barras horizontais;
            if not patrimonio_agg.empty:
                fig, ax = plt.subplots(figsize=(10, len(patrimonio_agg) * 0.5))
                bars = ax.barh(patrimonio_agg['nome_patrimonio'], patrimonio_agg['valor_convertido'], color='skyblue')
                
                # custom formatter for currency and integer values;
                def currency_formatter(x, pos):
                    if target_currency == 'BRL':
                        return f"R$ {int(x):,}".replace(",", "X").replace(".", ",").replace("X", ".") # brazilian format;
                    else: # assuming usd;
                        return f"$ {int(x):,}" # standard usd format;

                ax.xaxis.set_major_formatter(mticker.FuncFormatter(currency_formatter))
                
                # set x-axis ticks to be integer multiples of 10, with ~10 divisions;
                max_val = patrimonio_agg['valor_convertido'].max()
                if max_val > 0:
                    # use to try and get around 10 integer ticks, with steps that are 'nice';
                    ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=10, steps=[1, 2, 5, 10], integer=True, prune='lower'))
                    
                    # ensure the upper limit of the axis is a multiple of the step and slightly above max_val;
                    # this ensures roughly 10 divisions and ends on a 'nice' number;
                    locator = ax.xaxis.get_major_locator()
                    ticks = locator.tick_values(ax.get_xlim()[0], max_val * 1.05) # get potential ticks up to 5% above max;
                    if len(ticks) > 1:
                        # find a step based on the generated ticks;
                        step = ticks[1] - ticks[0]
                        upper_bound = np.ceil(max_val / step) * step
                        ax.set_xlim(right=upper_bound)
                    elif max_val > 0: # handle cases where only one tick is generated;
                        ax.set_xlim(right=np.ceil(max_val / 10) * 10) # set upper bound to next multiple of 10;


                ax.set_xlabel(f'Valor Total ({target_currency})')
                ax.set_title(f'Valor Total de Patrimônios por Empresa ({empresa_selecionada})')

                # itera sobre as barras, quantidades e preços atuais para adicionar os textos;
                for bar, quantidade, preco_atual_convertido in zip(bars, patrimonio_agg['quantidade'], patrimonio_agg['preco_atual_convertido']):
                    # texto da quantidade (permanece o mesmo, com um pequeno espaço);
                    ax.text(bar.get_width() * 0.98, bar.get_y() + bar.get_height()/2,
                            f'{int(quantidade)} ',
                            va='center', ha='right', color='white', fontsize=9,
                            bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.2'))

                    # texto do preço atual, à direita da barra;
                    if pd.notna(preco_atual_convertido):
                        # define o formato da moeda com base na moeda de destino;
                        currency_symbol = "R$ " if target_currency == 'BRL' else "$ "
                        
                        # adiciona um pequeno espaço para o texto não ficar colado na barra;
                        padding = ax.get_xlim()[1] * 0.01 
                        
                        ax.text(bar.get_width() + padding, bar.get_y() + bar.get_height()/2,
                                f'| Cotação: {currency_symbol}{preco_atual_convertido:.2f}',
                                va='center', 
                                ha='left', 
                                color='green', 
                                fontsize=10,
                                weight='bold')

                plt.tight_layout()
                st.pyplot(fig)

                # tabela de dados;
                st.dataframe(
                    patrimonio_agg[['nome_patrimonio', 'quantidade', 'preco_medio_convertido', 'preco_atual_convertido']].rename(columns={
                        'nome_patrimonio': 'Patrimônio',
                        'quantidade': 'Quantidade Total',
                        'preco_medio_convertido': f'Preço Médio ({target_currency})',
                        'preco_atual_convertido': f'Preço Atual ({target_currency})'
                    }),
                    column_config={
                        f'Preço Médio ({target_currency})': st.column_config.NumberColumn(
                            format="%.2f"
                        ),
                        f'Preço Atual ({target_currency})': st.column_config.NumberColumn(
                            format="%.2f"
                        )
                    }
                )
            else:
                st.info("não há dados de patrimônio suficientes para exibir.")


if __name__ == "__main__":
    lars_new()
