"""
coletor da tabela mensal de abate sob inspeção federal (sif), por espécie, categoria e uf;
fonte: mapa/pga - sigsif (porta de dados abertos do ministério da agricultura);
licença da fonte: cc by 4.0;
arquivo salvo sem transformação em raw/abate_bovinos_sif_raw.csv e metadados em
raw/abate_bovinos_sif_metadata.csv;
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests

kRAIZ_DADOS = Path(__file__).resolve().parents[1]
kRAW_DIR = kRAIZ_DADOS / "raw"

kARQUIVO_RAW = kRAW_DIR / "abate_bovinos_sif_raw.csv"
kMETADATA = kRAW_DIR / "abate_bovinos_sif_metadata.csv"

kURL_SERIE = (
    "https://dados.agricultura.gov.br/dataset/062166e3-b515-4274-8e7d-68aadd64b820/"
    "resource/341dc717-4716-42ab-b189-c8d7a9d2a1ba/download/sigsifrelatorioabates.csv"
)

kHEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "*/*",
}


def baixar_csv(destino: Path, url: str = kURL_SERIE, timeout: int = 120) -> None:
    resposta = requests.get(url, headers=kHEADERS, timeout=timeout)
    resposta.raise_for_status()
    destino.write_bytes(resposta.content)


def ler_arquivo(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho, sep=";", dtype=str)
    df["MES_ANO"] = pd.to_datetime(df["MES_ANO"], format="%m/%Y")
    return df


def registrar_metadados(arquivo: Path, df: pd.DataFrame, primeira_coluna: str) -> None:
    registro = {
        "arquivo": arquivo.name,
        "data_download": date.today().isoformat(),
        "fonte": "MAPA/PGA - SIGSIF (abate mensal)",
        "serie": "Abate de bovinos por mes (SIF)",
        "coluna": primeira_coluna,
        "licenca": "CC-BY 4.0",
        "url": kURL_SERIE,
        "linhas": int(df.shape[0]),
        "data_inicio": df["MES_ANO"].min().strftime("%d/%m/%Y"),
        "data_fim": df["MES_ANO"].max().strftime("%d/%m/%Y"),
        "status": "ok",
        "registrado_em": datetime.now().isoformat(timespec="seconds"),
    }
    bloco = pd.DataFrame([registro])
    if kMETADATA.exists():
        historico = pd.read_csv(kMETADATA)
        bloco = pd.concat([historico, bloco], ignore_index=True)
    bloco.to_csv(kMETADATA, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="baixa tabela mensal de abate sif (bovinos)")
    parser.add_argument("--force", action="store_true", help="rebaixa mesmo se o arquivo existir")
    args = parser.parse_args()

    kRAW_DIR.mkdir(parents=True, exist_ok=True)

    if kARQUIVO_RAW.exists() and not args.force:
        print(f"ja existe: {kARQUIVO_RAW.name} (use --force para rebaixar)")
        df = ler_arquivo(kARQUIVO_RAW)
    else:
        baixar_csv(kARQUIVO_RAW)
        df = ler_arquivo(kARQUIVO_RAW)

    primeira_coluna = "MES_ANO"
    print(f"arquivo: {kARQUIVO_RAW.name}")
    print(f"linhas: {df.shape[0]}")
    print(f"inicio: {df['MES_ANO'].min():%d/%m/%Y}")
    print(f"fim:    {df['MES_ANO'].max():%d/%m/%Y}")

    registrar_metadados(kARQUIVO_RAW, df, primeira_coluna)
    print(f"metadados: {kMETADATA}")


if __name__ == "__main__":
    main()