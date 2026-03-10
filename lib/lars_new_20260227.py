from pathlib import Path
import pandas as pd
import streamlit as st
from lars_new_functions import fetch_and_save_patrimonios_eventos 

CSV_DIR = Path(__file__).parent / "_csv"
CSV_DIR.mkdir(exist_ok=True)

def lars_new_20260227():

    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown("""
            <h1 class="title">LARS - CSV</h1>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("<-"):
            st.session_state.tela_atual = "A"    

    st.write("### csv management;")
    patrimonios_eventos_csv = CSV_DIR / "view_patrimonios_eventos.csv"

    if st.button("(re)gerar patrimônios eventos csv;"):
        with st.spinner("buscando patrimônios eventos do db e salvando csv;"):
            df_patrimonios_eventos = fetch_and_save_patrimonios_eventos(patrimonios_eventos_csv)
        st.success(f"salvo: {patrimonios_eventos_csv};")

if __name__ == "__main__":
    lars_new_20260227()
