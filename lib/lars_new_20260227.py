from pathlib import Path
import pandas as pd
import streamlit as st
from lars_new_files import functions 

# define the path to the csv file;
CSV_DIR = Path(__file__).parent / "_csv"
CSV_DIR.mkdir(exist_ok=True)
PATRIMONIOS_EVENTOS_CSV = CSV_DIR / "view_patrimonios_eventos.csv"

def lars_new_20260227():
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown("""
            <h1 class="title">LARS_NEW_20260227 - CSV</h1>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("<-"):
            st.session_state.tela_atual = "A"

    st.write("### csv management;")

    df_display = None; # initialize df_display;

    # regeneration button;
    if st.button("(re)gerar patrimônios eventos csv;"):
        try:
            with st.spinner("buscando patrimônios eventos do db e salvando csv;"):
                # this function saves the csv and should ideally return the dataframe;
                functions.fetch_and_save_patrimonios_eventos(PATRIMONIOS_EVENTOS_CSV)
            st.success(f"salvo: {PATRIMONIOS_EVENTOS_CSV};")
            # force a rerun to reflect the new data and apply filters;
            st.rerun() 
        except ImportError:
            st.error("módulo 'functions' não encontrado;")
        except Exception as e:
            st.error(f"erro ao gerar csv: {e}")

    # load data and apply filters;
    # try to load the csv if it exists;
    if PATRIMONIOS_EVENTOS_CSV.exists():
        try:
            df = pd.read_csv(PATRIMONIOS_EVENTOS_CSV)
            
            st.write("### filtros;")
            
            # get unique company names for the selectbox;
            if 'nome_empresa' in df.columns:
                unique_empresas = df['nome_empresa'].unique()
                
                # add selectbox for company name;
                selected_empresa = st.selectbox(
                    "selecione a empresa:",
                    ['todas'] + sorted(list(unique_empresas)) # add 'all' option and sort;
                )
    
            else:
                st.warning("a coluna 'nome_empresa' não foi encontrada no csv;")
                df_display = df.copy() # display all if column missing;
        except Exception as e:
            st.error(f"erro ao carregar ou filtrar csv: {e};")
            df_display = None # ensure it's none if loading fails;
    else:
        st.info("nenhum arquivo csv encontrado;")

if __name__ == "__main__":
    lars_new_20260227()
