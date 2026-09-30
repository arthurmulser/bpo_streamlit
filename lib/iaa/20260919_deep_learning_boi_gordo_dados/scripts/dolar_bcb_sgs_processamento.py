"""
agrega semanalmente a serie diaria do dolar americano do bcb sgs;

regras (mesmo contrato do boi gordo cepea 20260919, secao 5):
- grade iso (segunda a domingo);
- cotacao de fechamento = ultima observacao disponivel na semana;
- cotacao media = media das observacoes diarias da semana;
- a cotacao de um dia e conhecida no proprio dia, entao a semana nao carrega
  informacao futura;
- nenhuma imputacao: semanas sem observacao ficam fora da base;
- saida: processed/dolar_bcb_sgs_processed.csv;
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

kRAIZ_DADOS = Path(__file__).resolve().parents[1]
kARQUIVO_RAW = kRAIZ_DADOS / "raw" / "dolar_bcb_sgs_raw.csv"
kPROCESSED = kRAIZ_DADOS / "processed"

kSAIDA = kPROCESSED / "dolar_bcb_sgs_processed.csv"
kMETADATA = kPROCESSED / "dolar_bcb_sgs_metadata.csv"

kCASAS_MOEDA = 4


def carregar_ultima_serie_raw() -> pd.DataFrame:
    if not kARQUIVO_RAW.exists():
        sys.exit("arquivo raw nao encontrado: raw/dolar_bcb_sgs_raw.csv")
    df = pd.read_csv(kARQUIVO_RAW, dtype=str)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["dolar_brl_usd"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna(subset=["dolar_brl_usd"])
    df = df.drop_duplicates(subset=["data"])
    return df.sort_values("data").reset_index(drop=True)


def agregar_semanal(df_diario: pd.DataFrame) -> pd.DataFrame:
    iso = df_diario["data"].dt.isocalendar()
    df_diario["ano_iso"] = iso["year"].astype(int)
    df_diario["semana_iso"] = iso["week"].astype(int)
    chave = ["ano_iso", "semana_iso"]

    primeiro_dia = df_diario["data"] - pd.to_timedelta(df_diario["data"].dt.dayofweek, unit="D")
    df_diario["data_semana_inicio"] = primeiro_dia.dt.normalize()
    df_diario["data_semana_fim"] = primeiro_dia.dt.normalize() + pd.to_timedelta(6, unit="D")

    grupos = df_diario.groupby(chave, sort=True)
    semanal = pd.DataFrame(
        {
            "data_semana_inicio": grupos["data_semana_inicio"].first(),
            "data_semana_fim": grupos["data_semana_fim"].first(),
            "dolar_brl_usd_fechamento": grupos["dolar_brl_usd"].last(),
            "dolar_brl_usd_medio": grupos["dolar_brl_usd"].mean(),
            "n_obs": grupos["dolar_brl_usd"].count(),
        }
    ).reset_index()

    semanal["serie"] = (
        semanal["ano_iso"].astype(str) + "-W" + semanal["semana_iso"].astype(str).str.zfill(2)
    )
    semanal["dolar_brl_usd_fechamento"] = semanal["dolar_brl_usd_fechamento"].round(kCASAS_MOEDA)
    semanal["dolar_brl_usd_medio"] = semanal["dolar_brl_usd_medio"].round(kCASAS_MOEDA)

    ordem = [
        "serie",
        "data_semana_inicio",
        "data_semana_fim",
        "dolar_brl_usd_fechamento",
        "dolar_brl_usd_medio",
        "n_obs",
        "ano_iso",
        "semana_iso",
    ]
    return semanal[ordem].reset_index(drop=True)


def registrar_metadados(arquivo: Path, df: pd.DataFrame, arquivo_fonte: Path) -> None:
    registro = {
        "arquivo": arquivo.name,
        "fonte": "Banco Central do Brasil - SGS (serie 1)",
        "arquivo_fonte": arquivo_fonte.name,
        "gerado_em": date.today().isoformat(),
        "periodicidade": "semanal ISO",
        "regra_fechamento": "ultima observacao diaria disponivel na semana",
        "regra_media": "media das observacoes diarias da semana",
        "unidade": "BRL por USD",
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
    diario = carregar_ultima_serie_raw()
    semanal = agregar_semanal(diario)
    semanal.to_csv(kSAIDA, index=False)

    registrar_metadados(kSAIDA, semanal, kARQUIVO_RAW)

    print(f"origem:  {kARQUIVO_RAW.name} ({len(diario)} dias)")
    print(f"saida:   {kSAIDA}")
    print(f"semanas: {semanal.shape[0]}")
    print(f"inicio:  {semanal['data_semana_inicio'].min():%d/%m/%Y}")
    print(f"fim:     {semanal['data_semana_fim'].max():%d/%m/%Y}")


if __name__ == "__main__":
    main()
