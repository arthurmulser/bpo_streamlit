import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
from utils import get_animais, get_media_leite_por_periodo

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
    
    df["data_nascimento"] = pd.to_datetime(df["data_nascimento"]) # convertendo a coluna de datas para datetime;

    df = df.sort_values(by="data_nascimento").reset_index(drop=True) # ordenando os dados pela data de nascimento;

    df["cor"] = df["sexo"].map({"F": "F", "M": "M"}) # criando coluna de cores (rosa para fêmeas, azul para machos);

    y_positions = [] # criando deslocamento no eixo y para evitar sobreposição;
    last_date = None
    offset = 0  # deslocamento inicial;

    for date in df["data_nascimento"]:
        if last_date is not None and (date - last_date).days < 100000:
            offset += 1 
        else:
            offset = 0  # reseta o deslocamento se houver espaço suficiente;
        y_positions.append(1 + offset)
        last_date = date

    df["ey_pos"] = y_positions  # adiciona ao dataframe;

    def define_data_final_para_calculo_do_leite_total(row):
        if pd.notna(row['dt_desmame']):
            return row['dt_desmame']
        else:
            data_nascimento = row['data_nascimento']

            data_atual = pd.to_datetime(datetime.now().date())  
            
            diferenca_meses = (data_atual - data_nascimento).days / 30
            
            if diferenca_meses > 16: # se não houver sido lançado a data de desmame;
                return data_nascimento  
            else:
                return data_atual  

    df['data_final_calc'] = df.apply(define_data_final_para_calculo_do_leite_total, axis=1)

    df['dias_produzindo_leite'] = (df['data_final_calc'] - df['data_nascimento']).dt.days

    df["media_leite_periodo"] = df.apply(lambda row: get_media_leite_por_periodo(
        data_inicial=row['data_nascimento'],
        data_final=row['data_final_calc'],
        idtb_animais=row['idtb_animais_mae']
    ), axis=1)

    df["total_leite"] = df["media_leite_periodo"] * df["dias_produzindo_leite"]

    df['dt_desmame_formatada'] = df['dt_desmame'].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else "não informado"
    )

    fig = px.scatter( # criando o gráfico de linha do tempo;
        df,
        x="data_nascimento",
        y="ey_pos",
        color="sexo",
        hover_name="nome",
        hover_data={
            "data_nascimento": "|%d/%m/%Y",  
            "dt_desmame_formatada": True,
            "dias_produzindo_leite": True,  
            "media_leite_periodo": ":.2f",   
            "total_leite": ":.2f",     
            "nome_mae": True,
            "idtb_animais_mae": True,            
            "ey_pos": True              
        },
        labels={
            "data_nascimento": "dt_nas",
            "dt_desmame_formatada": "dt_des",
            "media_leite_periodo": "av_lit",
            "dias_produzindo_leite": "di_ple",
            "total_leite": "pd_tot",
            "idtb_animais_mae": "id_mae",
            "nome_mae": "no_mae"
        },
        title="linha do tempo de nascimentos",
    )

    fig.update_traces(
        text="oi",  
        textposition="top center",                            
        textfont=dict(size=10, color="black")                
    )

    fig.update_traces(marker=dict(size=10))  
    fig.update_yaxes(
        title="quantidade de nascimentos",
        tickmode="linear",
        dtick=1,  
        ticks="outside",
        showgrid=True  
    )

    fig.update_xaxes(title="data de nascimento")
    
    st.plotly_chart(fig, use_container_width=True)
