import os
from pathlib import Path
import pandas as pd
import streamlit as st
from utils import get_db_connection_lars
import numpy as np
import matplotlib.pyplot as plt

CSV_DIR = Path(__file__).parent.parent / "_csv"
CSV_DIR.mkdir(exist_ok=True)

def fetch_and_save_patrimonios_eventos(path: Path):
    """Busca `patrimonios_eventos` do banco usando `get_db_connection_lars()` e salva em csv."""
    query = "SELECT * FROM patrimonios_eventos;"
    conn = get_db_connection_lars()
    try:
        df = pd.read_sql(query, conn)
        if not df.empty:
            df['dt_evento'] = pd.to_datetime(df['dt_evento'], errors='coerce')
        df.to_csv(path, index=False)
        return df
    finally:
        conn.close()

def load_csv_or_prompt(path: Path, fetch_fn):
    """Carrega csv se existir, caso contrário oferece botão para gerar do db."""
    if path.exists():
        try:
            df = pd.read_csv(path)
            return df
        except Exception as e:
            st.error(f"Erro ao ler {path.name}: {e};")
            return pd.DataFrame()

    st.info(f"Arquivo {path.name} não encontrado, clique no botão para gerar a partir do banco;")
    if st.button(f"Gerar {path.name} a partir do DB;"):
        with st.spinner(f"Gerando {path.name};"):
            df = fetch_fn(path)
        st.success(f"{path.name} gerado e salvo em {path};")
        return df

    return pd.DataFrame()

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

    st.write("### CSV Management;")
    gen_col1, gen_col2 = st.columns(2)
    with gen_col1:
        if st.button("(Re)gerar Patrimônios Eventos CSV;"):
            with st.spinner("Buscando patrimônios eventos do DB e salvando CSV;"):
                df_patrimonios_eventos = fetch_and_save_patrimonios_eventos(patrimonios_eventos_csv)
            st.success(f"Salvo: {patrimonios_eventos_csv};")

    df_patrimonios_eventos = load_csv_or_prompt(patrimonios_eventos_csv, fetch_and_save_patrimonios_eventos)

    if df_patrimonios_eventos.empty:
        st.warning("Nenhum dado de patrimônios eventos disponível, gere o CSV ou verifique o diretório `_csv/`.")
        return

    st.write("### Dados de Patrimônios Eventos")
    st.dataframe(df_patrimonios_eventos)

def plot_compras_por_empresa(df, empresa_col='idtb_empresas', patr_col='idtb_patrimonios',
                             evento_col='evento', save=False, show=True):
    """
    Gera um gráfico de barras por empresa (idtb_empresas). Cada gráfico tem uma barra
    por idtb_patrimonios com: quantidade total de compra, valor total e preço médio.
    Compras são eventos == 'C'.

    Retorna um dict {empresa: matplotlib.figure.Figure}
    """
    # detectar colunas prováveis para quantidade/valor/preço
    def pick_col(cands):
        for c in cands:
            if c in df.columns:
                return c
        return None

    qty_col = pick_col(['quantidade', 'qtde', 'qtd', 'quantity', 'qty'])
    val_col = pick_col(['valor', 'valor_total', 'valor_compra', 'value', 'amount', 'total'])
    price_col = pick_col(['preco', 'preco_unitario', 'preco_medio', 'price', 'unit_price'])

    if qty_col is None and val_col is None:
        raise ValueError("Não foi possível encontrar colunas de quantidade ou valor no DataFrame.")

    # filtrar apenas compras
    dfc = df.copy()
    if evento_col in dfc.columns:
        dfc = dfc[dfc[evento_col] == 'C']
    else:
        # se não existir coluna de evento, assume todo o dataframe é válido
        pass

    # se não houver coluna de preço, vamos calcular a partir de valor/quantidade
    # agregar por empresa + patrimonio
    agg_dict = {}
    if qty_col:
        agg_dict[qty_col] = 'sum'
    if val_col:
        agg_dict[val_col] = 'sum'
    grouped = dfc.groupby([empresa_col, patr_col]).agg(agg_dict).reset_index()

    # normalizar nomes de colunas no agrupado
    if qty_col:
        grouped = grouped.rename(columns={qty_col: 'total_qty'})
    else:
        grouped['total_qty'] = 0
    if val_col:
        grouped = grouped.rename(columns={val_col: 'total_value'})
    else:
        grouped['total_value'] = 0.0

    # calcular preço médio
    grouped['avg_price'] = grouped['total_value'] / grouped['total_qty'].replace({0: np.nan})

    figs = {}
    empresas = grouped[empresa_col].unique()
    for emp in empresas:
        emp_df = grouped[grouped[empresa_col] == emp].sort_values(patr_col)
        pats = emp_df[patr_col].astype(str).tolist()
        x = np.arange(len(pats))
        width = 0.25

        fig, ax = plt.subplots(figsize=(max(6, len(pats) * 0.6), 4))
        ax.bar(x - width, emp_df['total_qty'].fillna(0), width, label='Quantidade')
        ax.bar(x, emp_df['total_value'].fillna(0), width, label='Valor Total')
        ax.bar(x + width, emp_df['avg_price'].fillna(0), width, label='Preço Médio')

        ax.set_xticks(x)
        ax.set_xticklabels(pats, rotation=45, ha='right')
        ax.set_title(f'Compras - Empresa {emp}')
        ax.set_ylabel('Valores')
        ax.legend()
        plt.tight_layout()

        if save:
            fname = f'compras_empresa_{emp}.png'
            fig.savefig(fname, dpi=150)
        if show:
            plt.show()

        figs[emp] = fig

    return figs

def show_compras_streamlit(df, empresa_col='idtb_empresas', patr_col='idtb_patrimonios',
                          evento_col='evento'):
    """
    Integra os gráficos gerados por plot_compras_por_empresa ao Streamlit.
    Exibe selectbox 'Todas' / empresa e renderiza cada figura com st.pyplot,
    além de mostrar a tabela agregada (total_qty, total_value, avg_price).
    """
    if df is None or df.shape[0] == 0:
        st.warning("DataFrame vazio.")
        return

    # detectar colunas de quantidade/valor
    def pick_col(cands):
        for c in cands:
            if c in df.columns:
                return c
        return None

    qty_col = pick_col(['quantidade', 'qtde', 'qtd', 'quantity', 'qty'])
    val_col = pick_col(['valor', 'valor_total', 'valor_compra', 'value', 'amount', 'total'])

    # filtrar compras
    dfc = df.copy()
    if evento_col in dfc.columns:
        dfc = dfc[dfc[evento_col] == 'C']

    # agregar
    agg_dict = {}
    if qty_col:
        agg_dict[qty_col] = 'sum'
    if val_col:
        agg_dict[val_col] = 'sum'
    if not agg_dict:
        st.error("Não foi possível encontrar colunas de quantidade/valor para agregar.")
        return

    grouped = dfc.groupby([empresa_col, patr_col]).agg(agg_dict).reset_index()
    if qty_col:
        grouped = grouped.rename(columns={qty_col: 'total_qty'})
    else:
        grouped['total_qty'] = 0
    if val_col:
        grouped = grouped.rename(columns={val_col: 'total_value'})
    else:
        grouped['total_value'] = 0.0
    grouped['avg_price'] = grouped['total_value'] / grouped['total_qty'].replace({0: np.nan})

    # gerar figuras (não mostrar via plt.show(), apenas retornar figuras)
    figs = plot_compras_por_empresa(df, empresa_col=empresa_col, patr_col=patr_col,
                                   evento_col=evento_col, save=False, show=False)

    empresas = sorted(list(figs.keys()))
    if not empresas:
        st.info("Nenhuma empresa com compras encontradas.")
        return

    empresa_sel = st.selectbox("Empresa", options=["Todas"] + empresas, index=0)

    if empresa_sel == "Todas":
        for emp in empresas:
            st.subheader(f"Empresa {emp}")
            fig = figs[emp]
            st.pyplot(fig)
            plt.close(fig)
            emp_table = grouped[grouped[empresa_col] == emp].reset_index(drop=True)
            st.dataframe(emp_table)
    else:
        st.subheader(f"Empresa {empresa_sel}")
        fig = figs[empresa_sel]
        st.pyplot(fig)
        plt.close(fig)
        st.dataframe(grouped[grouped[empresa_col] == empresa_sel].reset_index(drop=True))

if __name__ == "__main__":
    lars_new()
