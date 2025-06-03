import pandas as pd
import plotly.express as px
import streamlit as st
from utils import get_animais, get_total_leite_produzido

def sc():
    col1, col2 = st.columns([4, 1])  

    st.markdown("## Born")

    with col1:
        st.markdown(
            """
            <h1 class="title">
                SC
            </h1>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if st.button("<-"):
            st.session_state.tela_atual = "A" 
            
    df = get_animais()
    
    # convertendo a coluna de datas para datetime
    df["data_nascimento"] = pd.to_datetime(df["data_nascimento"])

    # ordenando os dados pela data de nascimento
    df = df.sort_values(by="data_nascimento").reset_index(drop=True)

    # criando coluna de cores (rosa para Fêmeas, azul para Machos)
    df["cor"] = df["sexo"].map({"F": "F", "M": "M"})

    # criando deslocamento no eixo Y para evitar sobreposição
    y_positions = []
    last_date = None
    offset = 0  # deslocamento inicial

    for date in df["data_nascimento"]:
        if last_date is not None and (date - last_date).days < 100000:
            offset += 1 
        else:
            offset = 0  # reseta o deslocamento se houver espaço suficiente
        y_positions.append(1 + offset)
        last_date = date

    df["y_position"] = y_positions  # adiciona ao dataframe

    df["total_leite"] = df.apply(lambda row: get_total_leite_produzido(
        data_inicial='2024-12-13',
        data_final='2025-04-30',
        idtb_animais=row['idtb_animais_mae']  # Usando o ID da mãe
    ), axis=1)

    # criando o gráfico de linha do tempo
    fig = px.scatter(
        df,
        x="data_nascimento",
        y="y_position",
        color="cor",
        hover_name="nome",
        hover_data={
            "data_nascimento": "|%d/%m/%Y",  # Formatação da data
            "total_leite": ":.2f",           # Total de leite com 2 casas decimais
            "nome_mae": True,
            "idtb_animais_mae": True,            
            "y_position": True              
        },
        labels={
            "data_nascimento": "Data de Nascimento",
            "total_leite": "Produção Total de Leite (L)",
            "idtb_animais_mae": "ID da Mãe",
            "nome_mae": "Nome da Mãe"
        },
        title="Linha do Tempo de Nascimentos",
    )

    fig.update_traces(
        text="oi",  # Formata o valor
        textposition="top center",                            # Posiciona acima do ponto
        textfont=dict(size=10, color="black")                # Estilo do texto (opcional)
    )

    # melhorando layout do gráfico
    fig.update_traces(marker=dict(size=10))  # define tamanho dos pontos
    fig.update_yaxes(
        title="Quantidade de Nascimentos",
        tickmode="linear",
        dtick=1,  # 1 em 1 nascimento
        ticks="outside",
        showgrid=True  # pode ser True pra facilitar leitura
    )



    fig.update_xaxes(title="Data de Nascimento")
    
    # exibir no streamlit
    st.plotly_chart(fig, use_container_width=True)
