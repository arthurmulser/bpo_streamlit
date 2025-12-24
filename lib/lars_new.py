import os
from pathlib import Path
import pandas as pd
import streamlit as st
from utils import get_db_connection_lars
import numpy as np
import matplotlib.pyplot as plt

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


def display_patrimonio_por_empresa(csv_path: Path):
    """exibe os patrimônios por empresa com gráfico e tabela."""
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

    empresas = df['nome_empresa'].dropna().unique()
    empresa_selecionada = st.selectbox("empresa:", options=empresas)

    if empresa_selecionada:
        df_empresa = df[df['nome_empresa'] == empresa_selecionada].copy()

        if df_empresa.empty:
            st.info("nenhum dado de patrimônio encontrado para esta empresa.")
            return

        # garante que as colunas 'valor' e 'quantidade' são numéricas;
        df_empresa['valor'] = pd.to_numeric(df_empresa['valor'], errors='coerce')
        df_empresa['quantidade'] = pd.to_numeric(df_empresa['quantidade'], errors='coerce')
        df_empresa.dropna(subset=['valor', 'quantidade'], inplace=True)
        
        # calcula o preço médio ponderado e a quantidade total;
        df_empresa['valor_total'] = df_empresa['valor'] * df_empresa['quantidade']
        
        agg_funcs = {
            'quantidade': ('quantidade', 'sum'),
            'valor_total': ('valor_total', 'sum')
        }
        
        patrimonio_agg = df_empresa.groupby('nome_patrimonio').agg(**agg_funcs).reset_index()

        # evita divisão por zero;
        patrimonio_agg['preco_medio'] = np.where(
            patrimonio_agg['quantidade'] != 0, 
            patrimonio_agg['valor_total'] / patrimonio_agg['quantidade'], 
            0
        )

        st.write(f"Patrimônios de: **{empresa_selecionada}**")

        # gráfico de barras horizontais;
        if not patrimonio_agg.empty:
            fig, ax = plt.subplots(figsize=(10, len(patrimonio_agg) * 0.5)) # adjust figure size dynamically;
            bars = ax.barh(patrimonio_agg['nome_patrimonio'], patrimonio_agg['valor_total'], color='skyblue')
            ax.set_xlabel('Valor Total')
            ax.set_title(f'Valor Total de Patrimônios por Empresa ({empresa_selecionada})')
            ax.xaxis.set_major_formatter(plt.FormatStrFormatter('R$ %.2f')) # format x-axis as currency;

            # adicionar a quantidade em branco sobre cada barra;
            for bar, quantidade in zip(bars, patrimonio_agg['quantidade']):
                ax.text(bar.get_width(), bar.get_y() + bar.get_height()/2, 
                        f'{int(quantidade)}', 
                        va='center', ha='left', color='white', fontsize=9, 
                        bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.2'))

            plt.tight_layout()
            st.pyplot(fig)

            # tabela de dados;
            st.dataframe(patrimonio_agg[['nome_patrimonio', 'quantidade', 'preco_medio']].rename(columns={
                'nome_patrimonio': 'Patrimônio',
                'quantidade': 'Quantidade Total',
                'preco_medio': 'Preço Médio'
            }))
        else:
            st.info("não há dados de patrimônio suficientes para exibir.")



if __name__ == "__main__":
    lars_new()
