"""
Agrega semanalmente a serie diaria do boi gordo CEPEA (a vista).

Regras (programa de dados 20260919, secao 5):
- grade ISO (segunda a domingo);
- preco de fechamento = ultima observacao disponivel na semana;
- preco medio = media das observacoes diarias da semana;
- nenhuma informacao futura entra nos calculos da semana t;

Saida: processed/boi_gordo_cepea_processed.csv
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import xlrd

RAIZ_DADOS = Path(__file__).resolve().parents[1]
ARQUIVO_RAW = RAIZ_DADOS / "raw" / "boi_gordo_cepea_raw.xls"
PROCESSED = RAIZ_DADOS / "processed"

SAIDA = PROCESSED / "boi_gordo_cepea_processed.csv"
METADATA = PROCESSED / "boi_gordo_cepea_metadata.csv"

KWARGS_OPEN = {"ignore_workbook_corruption": True}


def carregar_ultima_serie_raw() -> pd.DataFrame:
    arquivo = ARQUIVO_RAW
    if not arquivo.exists():
        sys.exit("arquivo raw nao encontrado: raw/boi_gordo_cepea_raw.xls")
    workbook = xlrd.open_workbook(str(arquivo), **KWARGS_OPEN)
    planilha = workbook.sheet_by_index(0)
    registros = []
    for r in range(planilha.nrows):
        if planilha.cell_value(r, 0) == "Data":
            inicio = r
            break
    else:
        sys.exit("header de dados nao encontrado")
    for r in range(inicio + 1, planilha.nrows):
        data = str(planilha.cell_value(r, 0)).strip()
        preco = planilha.cell_value(r, 1)
        if not data:
            continue
        registros.append((data, preco))
    df = pd.DataFrame(registros, columns=["data", "preco_avista"])
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["preco_avista"] = pd.to_numeric(df["preco_avista"], errors="coerce")
    df = df.dropna(subset=["preco_avista"]).sort_values("data")
    return df.reset_index(drop=True)


def agregar_semanal(df_diario: pd.DataFrame) -> pd.DataFrame:
    iso = df_diario["data"].dt.isocalendar()
    df_diario["ano_iso"] = iso["year"].astype(int)
    df_diario["semana_iso"] = iso["week"].astype(int)
    chave = ["ano_iso", "semana_iso"]

    primeiro_dia = df_diario["data"] - pd.to_timedelta(df_diario["data"].dt.dayofweek, unit="D")
    ultimo_dia = primeiro_dia + pd.to_timedelta(6, unit="D")
    df_diario["data_semana_inicio"] = primeiro_dia.dt.normalize()
    df_diario["data_semana_fim"] = ultimo_dia.dt.normalize()

    grupos = df_diario.groupby(chave, sort=True)
    semanal = pd.DataFrame(
        {
            "data_semana_inicio": grupos["data_semana_inicio"].first(),
            "data_semana_fim": grupos["data_semana_fim"].first(),
            "preco_avista_fechamento": grupos["preco_avista"].last(),
            "preco_avista_medio": grupos["preco_avista"].mean(),
            "n_obs": grupos["preco_avista"].count(),
        }
    ).reset_index()

    semanal["serie"] = (
        semanal["ano_iso"].astype(str) + "-W" + semanal["semana_iso"].astype(str).str.zfill(2)
    )
    ordem = ["serie", "data_semana_inicio", "data_semana_fim", "preco_avista_fechamento", "preco_avista_medio", "n_obs", "ano_iso", "semana_iso"]
    semanal["preco_avista_fechamento"] = semanal["preco_avista_fechamento"].round(2)
    semanal["preco_avista_medio"] = semanal["preco_avista_medio"].round(4)
    return semanal[ordem]


def registrar_metadados(arquivo: Path, df: pd.DataFrame, arquivo_fonte: Path) -> None:
    registro = {
        "arquivo": arquivo.name,
        "fonte": "CEPEA/ESALQ - Indicador do Boi Gordo (a vista)",
        "arquivo_fonte": arquivo_fonte.name,
        "gerado_em": date.today().isoformat(),
        "periodicidade": "semanal ISO",
        "regra_fechamento": "ultima observacao diaria disponivel na semana",
        "regra_media": "media das observacoes diarias da semana",
        "unidade": "R$/arroba de 15 kg",
        "linhas": int(df.shape[0]),
        "data_inicio": df["data_semana_inicio"].min().strftime("%d/%m/%Y"),
        "data_fim": df["data_semana_fim"].max().strftime("%d/%m/%Y"),
        "status": "ok",
    }
    metadata_path = METADATA
    bloco = pd.DataFrame([registro])
    if metadata_path.exists():
        historico = pd.read_csv(metadata_path)
        bloco = pd.concat([historico, bloco], ignore_index=True)
    bloco.to_csv(metadata_path, index=False)


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    diario = carregar_ultima_serie_raw()
    semanal = agregar_semanal(diario)
    saida = SAIDA
    semanal.to_csv(saida, index=False)

    arquivo_fonte = ARQUIVO_RAW
    registrar_metadados(saida, semanal, arquivo_fonte)

    print(f"origem:  {arquivo_fonte.name} ({len(diario)} dias)")
    print(f"saida:   {saida}")
    print(f"semanas: {semanal.shape[0]}")
    print(f"inicio:  {semanal['data_semana_inicio'].min():%d/%m/%Y}")
    print(f"fim:     {semanal['data_semana_fim'].max():%d/%m/%Y}")


if __name__ == "__main__":
    main()