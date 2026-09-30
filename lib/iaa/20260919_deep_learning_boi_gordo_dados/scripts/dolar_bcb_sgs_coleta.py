"""
coletor da serie diaria da taxa de cambio do dolar americano (venda) do sistema
de series temporais do banco central do brasil (sgs);

fonte: banco central do brasil - sgs, serie 1 (dolar americano, livre, venda);
licenca da fonte: dados abertos do bcb, uso livre;
serie salva sem transformacao em raw/dolar_bcb_sgs_raw.csv e metadados em
raw/dolar_bcb_sgs_metadata.csv;
observacao: a api aceita no maximo 10 anos por consulta em serie diaria, por isso
a coleta e feita ano a ano;
"""

from __future__ import annotations

import argparse
import time
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests

kRAIZ_DADOS = Path(__file__).resolve().parents[1]
kRAW_DIR = kRAIZ_DADOS / "raw"

kARQUIVO_RAW = kRAW_DIR / "dolar_bcb_sgs_raw.csv"
kMETADATA = kRAW_DIR / "dolar_bcb_sgs_metadata.csv"

kURL_SERIE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"
kSERIE_SGS = 1
kANO_INICIO = 1997
kPAUSA_SEGUNDOS = 0.4
kTIMEOUT = 60

kHEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def montar_url(ano: int) -> str:
    return (
        f"{kURL_SERIE}?formato=json"
        f"&dataInicial=01/01/{ano}"
        f"&dataFinal=31/12/{ano}"
    )


def baixar_ano(ano: int, timeout: int = kTIMEOUT) -> list[dict]:
    resposta = requests.get(montar_url(ano), headers=kHEADERS, timeout=timeout)
    resposta.raise_for_status()
    try:
        return resposta.json()
    except ValueError:
        return []


def baixar_serie(anos: range, timeout: int = kTIMEOUT) -> pd.DataFrame:
    registros: list[dict] = []
    for ano in anos:
        linhas = baixar_ano(ano, timeout=timeout)
        print(f"  {ano}: {len(linhas)} registros")
        registros.extend(linhas)
        if ano != anos[-1]:
            time.sleep(kPAUSA_SEGUNDOS)
    return pd.DataFrame(registros, columns=["data", "valor"])


def ler_arquivo(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho, dtype=str)


def registrar_metadados(arquivo: Path, df: pd.DataFrame, primeira_coluna: str) -> None:
    datas = pd.to_datetime(df["data"], format="%d/%m/%Y")
    registro = {
        "arquivo": arquivo.name,
        "data_download": date.today().isoformat(),
        "fonte": "Banco Central do Brasil - SGS (serie 1)",
        "serie": "Taxa de cambio - Livre - Dolar americano (venda) - diario",
        "coluna": primeira_coluna,
        "licenca": "dados abertos do bcb, uso livre com atribuicao",
        "url": kURL_SERIE,
        "linhas": int(df.shape[0]),
        "data_inicio": datas.min().strftime("%d/%m/%Y"),
        "data_fim": datas.max().strftime("%d/%m/%Y"),
        "status": "ok",
        "registrado_em": datetime.now().isoformat(timespec="seconds"),
    }
    bloco = pd.DataFrame([registro])
    if kMETADATA.exists():
        historico = pd.read_csv(kMETADATA)
        bloco = pd.concat([historico, bloco], ignore_index=True)
    bloco.to_csv(kMETADATA, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="baixa serie diaria do dolar (bcb sgs 1)")
    parser.add_argument("--force", action="store_true", help="rebaixa mesmo se o arquivo existir")
    args = parser.parse_args()

    kRAW_DIR.mkdir(parents=True, exist_ok=True)

    if kARQUIVO_RAW.exists() and not args.force:
        print(f"ja existe: {kARQUIVO_RAW.name} (use --force para rebaixar)")
        df = ler_arquivo(kARQUIVO_RAW)
    else:
        print(f"baixando serie {kSERIE_SGS} de {kANO_INICIO} ate {date.today().year}")
        df = baixar_serie(range(kANO_INICIO, date.today().year + 1))
        df.to_csv(kARQUIVO_RAW, index=False)

    primeira_coluna = "data"
    datas = pd.to_datetime(df["data"], format="%d/%m/%Y")
    print(f"arquivo: {kARQUIVO_RAW.name}")
    print(f"linhas: {df.shape[0]}")
    print(f"inicio: {datas.min():%d/%m/%Y}")
    print(f"fim:    {datas.max():%d/%m/%Y}")

    registrar_metadados(kARQUIVO_RAW, df, primeira_coluna)
    print(f"metadados: {kMETADATA}")


if __name__ == "__main__":
    main()
