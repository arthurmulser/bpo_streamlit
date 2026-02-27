#20250313
import matplotlib.pyplot as plt
import streamlit as st
from lars_new_20260227 import lars_new_20260227


plt.style.use('dark_background')

def menu():
    st.markdown('<h1 class="title">Hello World</h1>', unsafe_allow_html=True)
    
    if st.button("GO TO BPO"):
        st.session_state.tela_atual = "B"
    if st.button("GO TO FIN"):
        st.session_state.tela_atual = "C"
    if st.button("GO TO SC "):
        st.session_state.tela_atual = "D"    

    st.markdown("---")
    
    st.markdown('<h1 class="title">Módulos Novos</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3) 
    with col1:
        if st.button("SC_NEW 📈"):
            st.session_state.tela_atual = "E" 
    with col2:
        if st.button("LARS_NEW 📊"):
            st.session_state.tela_atual = "F" 
    with col3: # new column for the new button;
        if st.button("LARS_NEW_20260227 🧪"): # new button;
            st.session_state.tela_atual = "G" # new screen state;
    st.markdown("---")
