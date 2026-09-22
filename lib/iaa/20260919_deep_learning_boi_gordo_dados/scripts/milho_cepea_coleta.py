"""
coletor da série histórica diária do indicador cepea/esalq milho (à vista);

fonte: cepea/esalq - https://cepea.org.br/br/indicador/milho.aspx;
licença da fonte: cc by-nc 4.0;
série salva sem transformação em raw/milho_cepea_raw.xls e metadados em
raw/milho_cepea_metadata.csv;
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests
import xlrd

kRAIZ_DADOS = Path(__file__).resolve().parents[1]
kRAW_DIR = kRAIZ_DADOS / "raw"

kARQUIVO_RAW = kRAW_DIR / "milho_cepea_raw.xls"
kMETADATA = kRAW_DIR / "milho_cepea_metadata.csv"

kURL_SERIE = "https://cepea.org.br/br/indicador/series/milho.aspx?id=77"

kHEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

kKWARGS_OPEN = {"ignore_workbook_corruption": True}


def baixar_xls(destino: Path, url: str = kURL_SERIE, timeout: int = 120) -> None:
    resposta = requests.get(url, headers=kHEADERS, timeout=timeout)
    resposta.raise_for_status()
    destino.write_bytes(resposta.content)


def ler_serie(caminho: Path) -> pd.DataFrame:
    workbook = xlrd.open_workbook(str(caminho), **kKWARGS_OPEN)
    planilha = workbook.sheet_by_index(0)
    linhas: list[tuple[str, str]] = []
    for r in range(planilha.nrows):
        if planilha.cell_value(r, 0) == "Data":
            data_header = r
            break
    else:
        raise ValueError("header de dados nao encontrado no arquivo")
    for r in range(data_header + 1, planilha.nrows):
        data = str(planilha.cell_value(r, 0)).strip()
        valor_real = planilha.cell_value(r, 1)
        if not data:
            continue
        linhas.append((data, valor_real))
    df = pd.DataFrame(linhas, columns=["data", "preco_real"])
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["preco_real"] = pd.to_numeric(df["preco_real"], errors="coerce")
    df = df.dropna(subset=["preco_real"])
    df = df.drop_duplicates(subset=["data"])
    df = df.sort_values("data").reset_index(drop=True)
    return df


def registrar_metadados(arquivo: Path, df: pd.DataFrame, primeira_coluna: str) -> None:
    registro = {
        "arquivo": arquivo.name,
        "data_download": date.today().isoformat(),
        "fonte": "CEPEA/ESALQ",
        "serie": "Indicador do Milho CEPEA/ESALQ",
        "coluna": primeira_coluna,
        "licenca": "CC BY-NC 4.0",
        "url": kURL_SERIE,
        "linhas": int(df.shape[0]),
        "data_inicio": df["data"].min().strftime("%d/%m/%Y"),
        "data_fim": df["data"].max().strftime("%d/%m/%Y"),
        "status": "ok",
        "registrado_em": datetime.now().isoformat(timespec="seconds"),
    }
    bloco = pd.DataFrame([registro])
    if kMETADATA.exists():
        historico = pd.read_csv(kMETADATA)
        bloco = pd.concat([historico, bloco], ignore_index=True)
    bloco.to_csv(kMETADATA, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="baixa serie do milho cepea a vista")
    parser.add_argument("--force", action="store_true", help="rebaixa mesmo se o arquivo existir")
    args = parser.parse_args()

    kRAW_DIR.mkdir(parents=True, exist_ok=True)

    if kARQUIVO_RAW.exists() and not args.force:
        print(f"ja existe: {kARQUIVO_RAW.name} (use --force para rebaixar)")
        df = ler_serie(kARQUIVO_RAW)
    else:
        baixar_xls(kARQUIVO_RAW)
        df = ler_serie(kARQUIVO_RAW)

    primeira_coluna = "preco_real"
    print(f"arquivo: {kARQUIVO_RAW.name}")
    print(f"linhas: {df.shape[0]}")
    print(f"inicio: {df['data'].min():%d/%m/%Y}")
    print(f"fim:    {df['data'].max():%d/%m/%Y}")

    registrar_metadados(kARQUIVO_RAW, df, primeira_coluna)
    print(f"metadados: {kMETADATA}")


if __name__ == "__main__":
    main()