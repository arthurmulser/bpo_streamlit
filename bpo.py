#20250313
import matplotlib.pyplot as plt
import streamlit as st
from utils import get_empresas, get_data_from_db

def bpo():
    col1, col2 = st.columns([4, 1])  
    
    with col1:
        st.markdown(
            """
            <h1 class="title">
                BPO
            </h1>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if st.button("<-"):
            st.session_state.tela_atual = "A"  

    empresas_df = get_empresas()
    empresa_selecionada = st.selectbox(
        "Empresa:",
        options=empresas_df['Empresa'].tolist(),
        index=0
    )

    if not empresas_df.empty:
        empresa_id = empresas_df.loc[empresas_df['Empresa'] == empresa_selecionada, 'IdEmpresa'].values[0]
    else:
        empresa_id = None

    data = get_data_from_db(selected_empresa=empresa_selecionada)

    if not data.empty:
        pivot_data = data.pivot(index='Mes_Ano', columns='TipoConta', values='Total')
        pivot_data = pivot_data.fillna(0)

        fig, ax = plt.subplots(figsize=(17, 8))
        pivot_data.plot(
            kind='bar',
            ax=ax,
            color={'RECEITA': 'white', 'DESPESA': 'gray'}
        )
        
        ax.set_title("Receitas e Despesas por Mês/Ano", fontsize=14, color='white')
        ax.set_xlabel("Mês/Ano", fontsize=12, color='white')
        ax.set_ylabel("Total (R$)", fontsize=12, color='white')
        ax.legend(title="Tipo de Conta", fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7, color='white')
        ax.tick_params(colors='white')

        st.pyplot(fig)
    else:
        st.write(
            "<p style='color: white; text-align: center;'>Nenhum dado encontrado.</p>",
            unsafe_allow_html=True,
        )