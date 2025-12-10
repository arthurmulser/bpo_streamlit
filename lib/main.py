#20250313
import streamlit as st
from dotenv import load_dotenv
from bpo import bpo
from fin import fin
from menu import menu
from sc import sc
from sc_new import sc_new
from lars_new import lars_new

load_dotenv()

st.markdown(
    """
    <style>
        html, body, [class*="css"] {           
            font-size: 15px; /* tamanho da tela */  
        }
        .title {    
            text-align: left;
        }
        .stSelectbox label, .stSelectbox div {
            font-family: "Courier New", monospace !important;
            
        }
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            font-family: "Courier New", monospace !important;
        }
        
    </style>
    """,
    unsafe_allow_html=True,
)
if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "A"
if st.session_state.tela_atual == "A":
    menu()
elif st.session_state.tela_atual == "B":
    bpo()
elif st.session_state.tela_atual == "C":
    fin()
elif st.session_state.tela_atual == "D":
    sc()
elif st.session_state.tela_atual == "E":
    sc_new()
elif st.session_state.tela_atual == "F":
    lars_new()    