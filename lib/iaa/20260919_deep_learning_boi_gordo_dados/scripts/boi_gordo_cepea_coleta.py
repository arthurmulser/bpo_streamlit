"""
Coletor da série histórica diária do indicador CEPEA/ESALQ boi gordo (à vista).

Fonte: CEPEA/ESALQ - https://cepea.org.br/br/indicador/boi-gordo.aspx
Licença da fonte: CC BY-NC 4.0
Série salva sem transformação em raw/boi_gordo_cepea_raw.xls e metadados em
raw/boi_gordo_cepea_metadata.csv.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime

import pandas as pd
import requests
import xlrd
from pathlib import Path

RAIZ_DADOS = Path(__file__).resolve().parents[1]
RAW_DIR = RAIZ_DADOS / "raw"

ARQUIVO_RAW = RAW_DIR / "boi_gordo_cepea_raw.xls"
METADATA = RAW_DIR / "boi_gordo_cepea_metadata.csv"

URL_SERIE = "https://cepea.org.br/br/indicador/series/boi-gordo.aspx?id=2"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

KWARGS_OPEN = {"ignore_workbook_corruption": True}


def baixar_xls(destino: Path, url: str = URL_SERIE, timeout: int = 120) -> None:
    resposta = requests.get(url, headers=HEADERS, timeout=timeout)
    resposta.raise_for_status()
    destino.write_bytes(resposta.content)


def ler_serie(caminho: Path) -> pd.DataFrame:
    workbook = xlrd.open_workbook(str(caminho), **KWARGS_OPEN)
    planilha = workbook.sheet_by_index(0)
    linhas: list[tuple[str, str, str]] = []
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


def registrar_metadados(
    arquivo: Path,
    df: pd.DataFrame,
    primeira_coluna: str,
) -> None:
    registro = {
        "arquivo": arquivo.name,
        "data_download": date.today().isoformat(),
        "fonte": "CEPEA/ESALQ",
        "serie": "Indicador do Boi Gordo CEPEA/ESALQ",
        "coluna": primeira_coluna,
        "licenca": "CC BY-NC 4.0",
        "url": URL_SERIE,
        "linhas": int(df.shape[0]),
        "data_inicio": df["data"].min().strftime("%d/%m/%Y"),
        "data_fim": df["data"].max().strftime("%d/%m/%Y"),
        "status": "ok",
        "registrado_em": datetime.now().isoformat(timespec="seconds"),
    }
    metadata_path = METADATA
    bloco = pd.DataFrame([registro])
    if metadata_path.exists():
        historico = pd.read_csv(metadata_path)
        bloco = pd.concat([historico, bloco], ignore_index=True)
    bloco.to_csv(metadata_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa serie do boi gordo CEPEA a vista")
    parser.add_argument("--force", action="store_true", help="rebaixa mesmo se o arquivo existir")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    arquivo = ARQUIVO_RAW

    if arquivo.exists() and not args.force:
        print(f"ja existe: {arquivo.name} (use --force para rebaixar)")
        df = ler_serie(arquivo)
    else:
        baixar_xls(arquivo)
        df = ler_serie(arquivo)

    primeira_coluna = "preco_real"
    print(f"arquivo: {arquivo.name}")
    print(f"linhas: {df.shape[0]}")
    print(f"inicio: {df['data'].min():%d/%m/%Y}")
    print(f"fim:    {df['data'].max():%d/%m/%Y}")

    registrar_metadados(arquivo, df, primeira_coluna)
    print(f"metadados: {METADATA}")


if __name__ == "__main__":
    main()