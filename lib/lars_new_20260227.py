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
            
            ###
            if 'nome_empresa' in df.columns:
                unique_nome_empresa = df['nome_empresa'].unique()
                
                selected_nome_empresa = st.selectbox(
                    "selecione nome_empresa:",
                    ['---'] + sorted(list(unique_nome_empresa)) 
                )
            ###
            if 'standard_currency' in df.columns:
                unique_standard_currency = df['standard_currency'].unique()
                
                selected_standard_currency = st.selectbox(
                    "selecione standard_currency:",
                    ['---'] + sorted(list(unique_standard_currency)) 
                )    
            ###
            if 'bolsa_valores' in df.columns:
                unique_bolsa_valores = df['bolsa_valores'].unique()
                
                selected_bolsa_valores = st.selectbox(
                    "selecione bolsa_valores:",
                    ['---'] + sorted(list(unique_bolsa_valores)) 
                )    
            ### 
            if 'broker' in df.columns:
                unique_broker = df['broker'].unique()
                
                selected_broker = st.selectbox(
                    "selecione broker:",
                    ['---'] + sorted(list(unique_broker)) 
                )       
            ###

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
