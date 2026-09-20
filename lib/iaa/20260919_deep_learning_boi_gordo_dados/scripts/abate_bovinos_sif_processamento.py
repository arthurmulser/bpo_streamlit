"""
transforma o abate mensal sif (bovinos, brasil) em serie semanal iso;
regras (programa de dados 20260919, secao 5):
- soma nacional de machos+femeas das categorias bovinas, por mes de abate;
- somente o trecho contiguo da serie mensal e considerado;
- mes corrente (ainda incompleto) fica fora do processamento;
- nenhuma informacao futura: o total de um mes so fica disponivel na semana
  que contem o ultimo dia daquele mes (divulgacao ao fim do mes);
- semanas seguintes carregam o total do ultimo mes fechado (carry-forward);
- saida: processed/abate_bovinos_sif_processed.csv;
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

kRAIZ_DADOS = Path(__file__).resolve().parents[1]
kARQUIVO_RAW = kRAIZ_DADOS / "raw" / "abate_bovinos_sif_raw.csv"
kPROCESSED = kRAIZ_DADOS / "processed"

kSAIDA = kPROCESSED / "abate_bovinos_sif_processed.csv"
kMETADATA = kPROCESSED / "abate_bovinos_sif_metadata.csv"

kCATEGORIAS_BOVINOS = [
    "Bovino",
    "Vaca",
    "Novilho",
    "Novilha",
    "Novilhao",
    "Novilhona",
    "Novilho Precoce",
    "Novilha Precoce",
    "Novilho Intermediario",
    "Novilha Intermediaria",
    "Touro/Touruno",
    "Vitelo",
    "Bezerro",
    "Garrote",
    "Nonato",
]


def carregar_abate_mensal() -> pd.Series:
    arquivo = kARQUIVO_RAW
    if not arquivo.exists():
        sys.exit("arquivo raw nao encontrado: raw/abate_bovinos_sif_raw.csv")
    df = pd.read_csv(arquivo, sep=";")
    df = df[df["CATEGORIA"].isin(kCATEGORIAS_BOVINOS)].copy()
    df["total"] = df["QTD_MACHO"] + df["QTD_FEMEA"]
    df["MES_ANO"] = pd.to_datetime(df["MES_ANO"], format="%m/%Y")
    mensal = df.groupby(df["MES_ANO"].dt.to_period("M"))["total"].sum().sort_index()

    partes: list[list[pd.Period]] = []
    for mes in mensal.index:
        if partes and (mes - partes[-1][-1]).n == 1:
            partes[-1].append(mes)
        else:
            partes.append([mes])
    trecho = max(partes, key=len)
    mensal = mensal.loc[trecho]

    mes_corrente = pd.Timestamp.now().to_period("M")
    mensal = mensal[mensal.index < mes_corrente]
    return mensal


def agregar_semanal(mensal: pd.Series) -> pd.DataFrame:
    primeira = pd.Period(mensal.index.min(), "M").start_time.normalize()
    ultima = pd.Period(mensal.index.max(), "M").end_time.normalize()

    semana_inicio = pd.date_range(primeira, ultima, freq="W-MON")
    grade = pd.DataFrame({"data_semana_inicio": semana_inicio})
    grade["data_semana_fim"] = grade["data_semana_inicio"] + pd.to_timedelta(6, unit="D")

    janela = pd.DataFrame(
        {
            "mes_referencia": [pd.Period(m, "M") for m in mensal.index],
            "abate_bovinos_cabecas": mensal.values,
            "data_release": [pd.Period(m, "M").end_time.normalize() for m in mensal.index],
        }
    )
    janela["data_release_fim_semana"] = janela["data_release"] + pd.to_timedelta(
        6 - janela["data_release"].dt.dayofweek, unit="D"
    )

    liberados = grade.merge(
        janela[["data_release_fim_semana", "mes_referencia", "abate_bovinos_cabecas"]],
        left_on="data_semana_fim",
        right_on="data_release_fim_semana",
        how="left",
    )
    liberados["mes_referencia"] = liberados["mes_referencia"].ffill()
    liberados["abate_bovinos_cabecas"] = liberados["abate_bovinos_cabecas"].ffill()

    iso = liberados["data_semana_inicio"].dt.isocalendar()
    liberados["ano_iso"] = iso["year"].astype(int)
    liberados["semana_iso"] = iso["week"].astype(int)
    liberados["serie"] = (
        liberados["ano_iso"].astype(str) + "-W" + liberados["semana_iso"].astype(str).str.zfill(2)
    )

    liberados = liberados.dropna(subset=["abate_bovinos_cabecas"])
    liberados["abate_bovinos_cabecas"] = liberados["abate_bovinos_cabecas"].astype(int)
    liberados["mes_referencia"] = liberados["mes_referencia"].astype(str)

    ordem = [
        "serie",
        "data_semana_inicio",
        "data_semana_fim",
        "abate_bovinos_cabecas",
        "mes_referencia",
        "ano_iso",
        "semana_iso",
    ]
    return liberados[ordem].reset_index(drop=True)


def registrar_metadados(arquivo: Path, df: pd.DataFrame, arquivo_fonte: Path) -> None:
    registro = {
        "arquivo": arquivo.name,
        "fonte": "MAPA/PGA - SIGSIF (abate mensal de bovinos)",
        "arquivo_fonte": arquivo_fonte.name,
        "gerado_em": date.today().isoformat(),
        "periodicidade": "semanal ISO",
        "regra_divulgacao": "total mensal disponivel na semana que contem o ultimo dia do mes",
        "regra_carry_forward": "semanas seguintes carregam o total do ultimo mes fechado",
        "abrangencia": "brasil, soma das categorias bovinas de machos e femeas",
        "unidade": "cabecas/mes",
        "linhas": int(df.shape[0]),
        "data_inicio": df["data_semana_inicio"].min().strftime("%d/%m/%Y"),
        "data_fim": df["data_semana_fim"].max().strftime("%d/%m/%Y"),
        "status": "ok",
    }
    bloco = pd.DataFrame([registro])
    if kMETADATA.exists():
        historico = pd.read_csv(kMETADATA)
        bloco = pd.concat([historico, bloco], ignore_index=True)
    bloco.to_csv(kMETADATA, index=False)


def main() -> None:
    kPROCESSED.mkdir(parents=True, exist_ok=True)
    mensal = carregar_abate_mensal()
    semanal = agregar_semanal(mensal)
    semanal.to_csv(kSAIDA, index=False)

    registrar_metadados(kSAIDA, semanal, kARQUIVO_RAW)

    print(f"origem:  {kARQUIVO_RAW.name} ({len(mensal)} meses fechados)")
    print(f"saida:   {kSAIDA}")
    print(f"semanas: {semanal.shape[0]}")
    print(f"inicio:  {semanal['data_semana_inicio'].min():%d/%m/%Y}")
    print(f"fim:     {semanal['data_semana_fim'].max():%d/%m/%Y}")


if __name__ == "__main__":
    main()