"""
coletor da serie mensal de precos recebidos pelo produtor de gado de corte nos
eua (usda nass - quickstats), nacional, em dolares por quintal (cwt);

fonte: usda nass - quickstats, portal de dados abertos usda;
licenca da fonte: dominio publico;
serie salva sem transformacao em raw/gado_eua_nass_raw.csv e metadados em
raw/gado_eua_nass_metadata.csv;
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

kRAIZ_DADOS = Path(__file__).resolve().parents[1]
kRAW_DIR = kRAIZ_DADOS / "raw"

kARQUIVO_RAW = kRAW_DIR / "gado_eua_nass_raw.csv"
kMETADATA = kRAW_DIR / "gado_eua_nass_metadata.csv"

kURL_SERIE = "https://quickstats.nass.usda.gov/api/api_GET/"
kURL_CONTAGEM = "https://quickstats.nass.usda.gov/api/get_counts"
kURL_CADASTRO = "https://quickstats.nass.usda.gov/api"
kVARIAVEL_CHAVE = "QUICKSTATS_API_KEY"

kPARAMETROS = {
    "commodity_desc": "CATTLE",
    "statisticcat_desc": "PRICE RECEIVED",
    "unit_desc": "$ / CWT",
    "freq_desc": "MONTHLY",
    "state_name": "US TOTAL",
}

kCAMPOS_DOMINIO = [
    "short_desc",
    "class_desc",
    "unit_desc",
    "statisticcat_desc",
    "freq_desc",
    "domain_desc",
    "state_name",
    "reference_period_desc",
]

kANO_INICIO = 1997
kROW_COUNT = 50000
kPAUSA_SEGUNDOS = 0.4
kTIMEOUT = 120
kTENTATIVAS = 3

kHEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def obter_chave() -> str:
    load_dotenv()
    chave = os.getenv(kVARIAVEL_CHAVE)
    if not chave:
        sys.exit(
            f"chave de api ausente: defina {kVARIAVEL_CHAVE} no .env "
            f"(cadastro gratuito em {kURL_CADASTRO})"
        )
    return chave


def consultar(
    chave: str, ano: int, timeout: int = kTIMEOUT, amplitude: bool = False
) -> list[dict]:
    parametros = {
        "key": chave,
        "year": str(ano),
        "row_count": str(kROW_COUNT),
        "format": "JSON",
        "commodity_desc": kPARAMETROS["commodity_desc"],
    }
    if not amplitude:
        parametros.update(kPARAMETROS)
    for tentativa in range(1, kTENTATIVAS + 1):
        try:
            resposta = requests.get(
                kURL_SERIE, params=parametros, headers=kHEADERS, timeout=timeout
            )
        except requests.RequestException as erro:
            print(f"  {ano}: tentativa {tentativa} falhou ({type(erro).__name__})")
            time.sleep(2 * tentativa)
            continue
        if resposta.status_code == 401:
            sys.exit(
                "chave de api recusada pelo quickstats (401): "
                f"confira {kVARIAVEL_CHAVE} no .env"
            )
        try:
            resposta.raise_for_status()
        except requests.HTTPError as erro:
            print(f"  {ano}: tentativa {tentativa} falhou (http {erro.response.status_code})")
            time.sleep(2 * tentativa)
            continue
        try:
            corpo = resposta.json()
        except ValueError:
            print(f"  {ano}: tentativa {tentativa} devolveu corpo invalido")
            corpo = {}
        if "error" in corpo or "message" in corpo:
            sys.exit(f"quickstats recusou a consulta: {resposta.text[:300]}")
        dados = corpo.get("data") or []
        if not dados and tentativa < kTENTATIVAS:
            time.sleep(2 * tentativa)
            continue
        return dados
    return []


def consultar_contagem(chave: str, ano: int, timeout: int = kTIMEOUT) -> int | str:
    """
    a contagem sai antes da serie: o quickstats recusa com http 413 quando a
    resposta Passaria do limite de 50.000 registros;
    """
    try:
        resposta = requests.get(
            kURL_CONTAGEM,
            params={"key": chave, "year": str(ano), "commodity_desc": kPARAMETROS["commodity_desc"]},
            headers=kHEADERS,
            timeout=timeout,
        )
        resposta.raise_for_status()
        return int(resposta.json()["count"])
    except (requests.RequestException, ValueError, KeyError, TypeError) as erro:
        return f"indisponivel ({type(erro).__name__})"


def baixar_serie(chave: str, anos: range) -> pd.DataFrame:
    registros: list[dict] = []
    for ano in anos:
        linhas = consultar(chave, ano)
        print(f"  {ano}: {len(linhas)} registros")
        if len(linhas) >= kROW_COUNT:
            print(f"  {ano}: atendeu o limite de {kROW_COUNT} linhas, filtro amplo demais")
        registros.extend(linhas)
        if ano != anos[-1]:
            time.sleep(kPAUSA_SEGUNDOS)
    if not registros:
        return pd.DataFrame()
    return pd.DataFrame(registros)


def relatar_dominio(chave: str) -> None:
    ano = date.today().year - 1
    contagem = consultar_contagem(chave, ano)
    print(f"ano de referencia: {ano}")
    print(f"registros de gado no ano (sem filtro de preco): {contagem}")
    linhas = consultar(chave, ano, amplitude=True)
    if not linhas:
        print("quickstats nao devolveu nenhum registro de gado para o ano consultado")
        return
    df = pd.DataFrame(linhas)
    disponiveis = [c for c in kCAMPOS_DOMINIO if c in df.columns]
    print("valores disponiveis no quickstats para bovinos:")
    for coluna in disponiveis:
        valores = sorted(v for v in df[coluna].dropna().unique() if str(v).strip())
        amostra = ", ".join(valores[:25])
        if len(valores) > 25:
            amostra += f", ... (+{len(valores) - 25})"
        print(f"  {coluna}: {amostra}")


def ler_arquivo(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho, dtype=str)


def extrair_mes(df: pd.DataFrame) -> pd.Series:
    """
    o quickstats nao manda o mes em um campo `month`: ele vem em `begin_code`
    (01 a 12) e em `reference_period_desc` (JAN a DEZ);
    """
    ano = df["year"].astype(int).astype(str)
    mes = df["begin_code"].astype(int).astype(str).str.zfill(2)
    return pd.PeriodIndex(ano + "-" + mes, freq="M")


def registrar_metadados(arquivo: Path, df: pd.DataFrame, primeira_coluna: str) -> None:
    datas = extrair_mes(df).to_timestamp()
    registro = {
        "arquivo": arquivo.name,
        "data_download": date.today().isoformat(),
        "fonte": "USDA NASS - QuickStats",
        "serie": "Cattle - Price Received - US TOTAL - monthly - $ / CWT",
        "coluna": primeira_coluna,
        "licenca": "dominio publico (usda nass)",
        "url": kURL_SERIE,
        "linhas": int(df.shape[0]),
        "data_inicio": datas.min().strftime("%m/%Y"),
        "data_fim": datas.max().strftime("%m/%Y"),
        "status": "ok",
        "registrado_em": datetime.now().isoformat(timespec="seconds"),
    }
    bloco = pd.DataFrame([registro])
    if kMETADATA.exists():
        historico = pd.read_csv(kMETADATA)
        bloco = pd.concat([historico, bloco], ignore_index=True)
    bloco.to_csv(kMETADATA, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="baixa precos de gado nos eua (usda nass quickstats)"
    )
    parser.add_argument("--force", action="store_true", help="rebaixa mesmo se o arquivo existir")
    parser.add_argument(
        "--dominio",
        action="store_true",
        help="lista os valores aceitos pelo quickstats e sai (diagnostico de filtro)",
    )
    args = parser.parse_args()

    kRAW_DIR.mkdir(parents=True, exist_ok=True)
    chave = obter_chave()

    if args.dominio:
        relatar_dominio(chave)
        return

    if kARQUIVO_RAW.exists() and not args.force:
        print(f"ja existe: {kARQUIVO_RAW.name} (use --force para rebaixar)")
        df = ler_arquivo(kARQUIVO_RAW)
    else:
        print(f"baixando precos de gado de {kANO_INICIO} ate {date.today().year}")
        df = baixar_serie(chave, range(kANO_INICIO, date.today().year + 1))
        if df.empty:
            print("nenhum registro devolvido com o filtro atual:")
            relatar_dominio(chave)
            return
        df.to_csv(kARQUIVO_RAW, index=False)

    primeira_coluna = "year"
    datas = extrair_mes(df).to_timestamp()
    print(f"arquivo: {kARQUIVO_RAW.name}")
    print(f"linhas: {df.shape[0]}")
    print(f"itens:  {df['short_desc'].nunique() if 'short_desc' in df.columns else '-'}")
    print(f"inicio: {datas.min():%m/%Y}")
    print(f"fim:    {datas.max():%m/%Y}")

    registrar_metadados(kARQUIVO_RAW, df, primeira_coluna)
    print(f"metadados: {kMETADATA}")


if __name__ == "__main__":
    main()
