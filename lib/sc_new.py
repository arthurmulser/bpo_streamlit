import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from utils import get_animais, get_db_connection_sc, get_media_leite_por_periodo

# streamlit run .\sc_new.py --server.port 8501; streamlit run main.py --server.port 8502;

CSV_DIR = Path(__file__).parent.parent / "_csv"
CSV_DIR.mkdir(exist_ok=True)

COLOR_INACTIVE = '#B0B0B0'  # Cor para mães inativas no gráfico
COLOR_ACTIVE = '#1f77b4'    # Cor para mães ativas no gráfico (azul padrão Plotly)

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
    ### ### ###
    st.markdown("### Linha de tempo dos nascimentos")
    st.plotly_chart(fig, use_container_width=True, key="timeline_chart")

    st.markdown("### Produção Total de Leite por Mãe")

    if df_eventos.empty: # verifique se o dataframe de eventos está carregado;
        st.warning("Arquivo de eventos não carregado. O cálculo da produção de leite não pode ser realizado.")
        df_prod_total = pd.DataFrame({'animal': [], 'producao': [], 'ativa': []})
        production_per_month = {}
    else:
        df_eventos['dt_evento'] = pd.to_datetime(df_eventos['dt_evento'])
        
        total_production_per_mother = {}
        production_per_month = {}
        
        df['idtb_animais_mae'] = pd.to_numeric(df['idtb_animais_mae'], errors='coerce')
        df_eventos['idtb_animais'] = pd.to_numeric(df_eventos['idtb_animais'], errors='coerce')

        unique_mother_ids = df['idtb_animais_mae'].dropna().unique()

        for mother_id in unique_mother_ids:
            mother_total_production = 0
            calves_df = df[df['idtb_animais_mae'] == mother_id]
            mother_name = calves_df['nome_mae'].iloc[0]

            for _, calf in calves_df.iterrows():
                lactation_start = pd.to_datetime(calf['data_nascimento'])
                lactation_end = pd.to_datetime(calf['data_final_calc'])

                if pd.isna(lactation_start) or pd.isna(lactation_end):
                    continue

                for month_start in pd.date_range(start=lactation_start.to_period('M').to_timestamp(), end=lactation_end, freq='MS'):
                    month_end = month_start + pd.offsets.MonthEnd(0)
                    effective_start = max(month_start, lactation_start)
                    effective_end = min(month_end, lactation_end - pd.Timedelta(days=1))
                    
                    if effective_start > effective_end:
                        continue

                    month_events = df_eventos[
                        (df_eventos['idtb_animais'] == mother_id) &
                        (df_eventos['idtb_eventos_tipos'] == 1) &
                        (df_eventos['dt_evento'] >= effective_start) &
                        (df_eventos['dt_evento'] <= effective_end)
                    ]
                    
                    monthly_production = 0
                    if not month_events.empty:
                        monthly_avg = month_events['valor'].mean()
                        productive_days = (effective_end - effective_start).days + 1
                        monthly_production = monthly_avg * productive_days
                    
                    mother_total_production += monthly_production
                    
                    if monthly_production > 0:
                        month_key = month_start.strftime('%Y-%m')
                        production_per_month[month_key] = production_per_month.get(month_key, 0) + monthly_production
            
            total_production_per_mother[mother_name] = mother_total_production

        df_prod_total = pd.DataFrame(list(total_production_per_mother.items()), columns=['animal', 'producao']) # cria o dataframe de produção;
        df_prod_total['producao'] = df_prod_total['producao'].round()

        df_status = df[['nome', 'idtb_ativo']].copy() # cria um dataframe separado para o status de atividade;
        df_status.rename(columns={'nome': 'animal'}, inplace=True)
        df_status['idtb_ativo_raw'] = pd.to_numeric(df_status['idtb_ativo'], errors='coerce').fillna(0)
        df_status['ativa'] = df_status['idtb_ativo_raw'].astype(int) == 1
        df_status = df_status[['animal', 'ativa', 'idtb_ativo_raw']].drop_duplicates()

        df_prod_total = pd.merge(df_prod_total, df_status, on='animal', how='left') # junta a informação de status no dataframe de produção;
        df_prod_total['ativa'].fillna(False, inplace=True)
        df_prod_total['idtb_ativo_raw'].fillna(0, inplace=True)

        df_prod_total['status_cor'] = df_prod_total['ativa'].apply(lambda x: 'Ativa' if x else 'Inativa') # cria a coluna de cor e a nova label para o eixo x;
        df_prod_total['animal_label'] = df_prod_total['animal'] + " (Ativo: " + df_prod_total['idtb_ativo_raw'].astype(int).astype(str) + ")"
        df_prod_total = df_prod_total.sort_values('producao', ascending=False)

    if not df_prod_total.empty: # gráfico 1: produção por mãe;
        fig_prod_total = px.bar(
            df_prod_total,
            x='animal_label',
            y='producao',
            title='Produção Total de Leite por Mãe',
            labels={'animal_label': 'Mãe (Status Ativo)', 'producao': 'Produção Total de Leite (Litros)', 'status_cor': 'Status'},
            text='producao',
            color='status_cor',
            color_discrete_map={
                'Ativa': COLOR_ACTIVE,
                'Inativa': COLOR_INACTIVE
            }
        )
        fig_prod_total.update_traces(texttemplate='%{text:.0f} L', textposition='outside')
        fig_prod_total.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_prod_total, use_container_width=True, key="prod_total_chart")
    else:
        st.write("Nenhum dado de produção de mãe encontrado para exibir o gráfico.")

    st.markdown("### Produção de Leite por Mês") # gráfico 2: produção por mês;
    if not production_per_month:
        st.write("Nenhum dado de produção mensal encontrado para exibir o gráfico.")
    else:
        first_event_month = min(production_per_month.keys()) # garante que a faixa de meses vai do primeiro evento até o mês atual;
        last_month = pd.Timestamp.now().strftime('%Y-%m')
        all_months_range = pd.date_range(start=first_event_month, end=last_month, freq='MS').strftime('%Y-%m')
        
        full_monthly_data = {month: round(production_per_month.get(month, 0)) for month in all_months_range} # preenche os meses sem produção com 0;

        df_monthly_prod = pd.DataFrame({
            'mes': list(full_monthly_data.keys()),
            'producao_mensal': list(full_monthly_data.values())
        })

        fig_monthly_prod = px.bar(
            df_monthly_prod,
            x='mes',
            y='producao_mensal',
            title='Produção Total de Leite por Mês (Todas as Vacas)',
            labels={'mes': 'Mês', 'producao_mensal': 'Produção Total (Litros)'},
            text='producao_mensal'
        )
        fig_monthly_prod.update_traces(texttemplate='%{text:.0f} L', textposition='outside')
        fig_monthly_prod.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_monthly_prod, use_container_width=True, key="monthly_prod_chart")

if __name__ == "__main__": # para testes locais rápidos;
    sc_new()
