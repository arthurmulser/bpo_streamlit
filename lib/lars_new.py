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

    st.write("### CSV Management;")
    if st.button("(Re)gerar Patrimônios Eventos CSV;"):
        with st.spinner("Buscando patrimônios eventos do DB e salvando CSV;"):
            df_patrimonios_eventos = fetch_and_save_patrimonios_eventos(patrimonios_eventos_csv)
        st.success(f"Salvo: {patrimonios_eventos_csv};")



if __name__ == "__main__":
    lars_new()
