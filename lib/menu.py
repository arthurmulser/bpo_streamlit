#20250313
import matplotlib.pyplot as plt
import streamlit as st

plt.style.use('dark_background')

def menu():
    st.markdown('<h1 class="title">Hello World</h1>', unsafe_allow_html=True)
    
    if st.button("GO TO BPO"):
        st.session_state.tela_atual = "B"
    if st.button("GO TO FIN"):
        st.session_state.tela_atual = "C"
    if st.button("GO TO SC "):
        st.session_state.tela_atual = "D"    