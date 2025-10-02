import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from utils import get_animais, get_db_connection_sc, get_media_leite_por_periodo

# streamlit run .\sc_new.py --server.port 8501; streamlit run main.py --server.port 8502;

CSV_DIR = Path("_csv")
CSV_DIR.mkdir(exist_ok=True)

def fetch_and_save_view_animais(path: Path):
    """busca `view_animais` do banco usando `get_animais()` e salva em csv;"""
    df = get_animais()
    if not df.empty:  # forçar formatos antes de salvar;
        df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce')
        df['dt_desmame'] = pd.to_datetime(df['dt_desmame'], errors='coerce')
    df.to_csv(path, index=False)
    return df

def fetch_and_save_view_eventos(path: Path):
    """busca `view_eventos` diretamente do banco e salva em csv, verificar sobre essa função no utils;
    """
    query = "SELECT idtb_eventos, idtb_animais, idtb_eventos_tipos, dt_evento, valor FROM view_eventos;"
    conn = get_db_connection_sc()
    try:
        df = pd.read_sql(query, conn)
        if not df.empty:
            df['dt_evento'] = pd.to_datetime(df['dt_evento'], errors='coerce')
        df.to_csv(path, index=False)
        return df
    finally:
        conn.close()

def load_csv_or_prompt(path: Path, fetch_fn):
    """carrega csv se existir, caso contrário oferece botão para gerar do db;"""
    if path.exists():
        try:
            df = pd.read_csv(path)
            return df
        except Exception as e:
            st.error(f"erro ao ler {path.name}: {e};")
            return pd.DataFrame()

    st.info(f"arquivo {path.name} não encontrado, clique no botão para gerar a partir do banco;")
    if st.button(f"gerar {path.name} a partir do db;"):
        with st.spinner(f"gerando {path.name};"):
            df = fetch_fn(path)
        st.success(f"{path.name} gerado e salvo em {path};")
        return df

    return pd.DataFrame()

def sc_new():

    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown("""
            <h1 class="title">SC - CSV</h1>
        """, unsafe_allow_html=True)

    animais_csv = CSV_DIR / "view_animais.csv"
    eventos_csv = CSV_DIR / "view_eventos.csv"

    st.write("### csv management;") # buttons to (re)generate each csv explicitly;
    gen_col1, gen_col2 = st.columns(2)
    with gen_col1:
        if st.button("(re)gerar animais csv;"):
            with st.spinner("buscando animais do db e salvando csv;"):
                df_animais = fetch_and_save_view_animais(animais_csv)
            st.success(f"Salvo: {animais_csv};")
    with gen_col2:
        if st.button("(re)gerar eventos csv;"):
            with st.spinner("buscando eventos do db e salvando csv;"):
                df_eventos = fetch_and_save_view_eventos(eventos_csv)
            st.success(f"salvo: {eventos_csv};")

    df = load_csv_or_prompt(animais_csv, fetch_and_save_view_animais) # carregar os csvs (ou instruir a gerar);
    df_eventos = load_csv_or_prompt(eventos_csv, fetch_and_save_view_eventos)

    if df.empty:
        st.warning("nenhum dado de animais disponível, gere o csv ou verifique o diretório `_csv/`.")
        return

    df["data_nascimento"] = pd.to_datetime(df["data_nascimento"])  # convertendo a coluna de datas para datetime;
    df = df.sort_values(by="data_nascimento").reset_index(drop=True)
    df["cor"] = df["sexo"].map({"F": "F", "M": "M"})

    y_positions = []
    last_date = None
    offset = 0
    for date in df["data_nascimento"]:
        if last_date is not None and (date - last_date).days < 100000:
            offset += 1
        else:
            offset = 0
        y_positions.append(1 + offset)
        last_date = date

    df["ey_pos"] = y_positions

    def define_data_final_para_calculo_do_leite_total(row):
        if pd.notna(row.get('dt_desmame')):
            return row['dt_desmame']
        else:
            data_nascimento = row['data_nascimento']
            data_atual = pd.to_datetime(datetime.now().date())
            diferenca_meses = (data_atual - data_nascimento).days / 30
            if diferenca_meses > 16:
                return data_nascimento
            else:
                return data_atual

    df['data_final_calc'] = df.apply(define_data_final_para_calculo_do_leite_total, axis=1)

    df['data_final_calc'] = pd.to_datetime(df['data_final_calc'], errors='coerce') # garantir que colunas de data são datetime (defensivo contra numpy/strings/misturas);
    df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce')
    
    def calcular_dias_produzindo(row): # substituir valores inválidos por nat e calcular dias apenas quando ambos são datetimes;
        di = row.get('data_final_calc')
        dn = row.get('data_nascimento')
        try:
            if pd.isna(di) or pd.isna(dn):
                return pd.NA
            di_ts = pd.to_datetime(di) # garantir que são timestamps;
            dn_ts = pd.to_datetime(dn)
            return int((di_ts - dn_ts).days)
        except Exception:
            return pd.NA

    df['dias_produzindo_leite'] = df.apply(calcular_dias_produzindo, axis=1)

    if not df_eventos.empty: # calcular média de leite por período usando o csv de eventos se disponível, caso contrário usar a função db;
        df_eventos['dt_evento'] = pd.to_datetime(df_eventos['dt_evento'], errors='coerce') # garantir tipos;

        def media_por_periodo_csv(data_inicial, data_final, idtb_animais):
            mask = (
                (df_eventos['idtb_eventos_tipos'] == 1) &
                (df_eventos['idtb_animais'] == int(idtb_animais)) &
                (df_eventos['dt_evento'] >= pd.to_datetime(data_inicial)) &
                (df_eventos['dt_evento'] <= pd.to_datetime(data_final))
            )
            sub = df_eventos.loc[mask]
            if sub.empty:
                return 0.0
            return float(sub['valor'].mean())

        df["media_leite_periodo"] = df.apply(lambda row: media_por_periodo_csv(
            row['data_nascimento'], row['data_final_calc'], row['idtb_animais_mae']
        ), axis=1)

    else:
        df["media_leite_periodo"] = df.apply(lambda row: get_media_leite_por_periodo(
            data_inicial=row['data_nascimento'],
            data_final=row['data_final_calc'],
            idtb_animais=row['idtb_animais_mae']
        ), axis=1)

    df["total_leite"] = df["media_leite_periodo"] * df["dias_produzindo_leite"]

    # garantir que 'dt_desmame' é datetime antes de formatar;
    df['dt_desmame'] = pd.to_datetime(df['dt_desmame'], errors='coerce')
    df['dt_desmame_formatada'] = df['dt_desmame'].apply(
        lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else "não informado"
    )

    fig = px.scatter(
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
        title="linha do tempo de nascimentos (csv)",
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

if __name__ == "__main__": # para testes locais rápidos;
    sc_new()
