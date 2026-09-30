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
import sys
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
kPAUSA_SEGUNDOS = 1.0
kTIMEOUT = 60
kTENTATIVAS = 4
kESPERA_INICIAL_SEGUNDOS = 2
kMINIMO_OBS_POR_ANO = 200

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
    """
    consulta um ano com repeticao: o bcb devolve 502 e resposta vazia de forma
    intermitente, e um ano vazio aceito em silencio vira lacuna na serie;
    """
    for tentativa in range(1, kTENTATIVAS + 1):
        try:
            resposta = requests.get(montar_url(ano), headers=kHEADERS, timeout=timeout)
            resposta.raise_for_status()
            linhas = resposta.json()
        except (requests.RequestException, ValueError) as erro:
            print(f"  {ano}: tentativa {tentativa} falhou ({type(erro).__name__})")
            linhas = []
        else:
            if linhas:
                return linhas
            print(f"  {ano}: tentativa {tentativa} devolveu resposta vazia")
        if tentativa < kTENTATIVAS:
            time.sleep(kESPERA_INICIAL_SEGUNDOS * tentativa)
    sys.exit(
        f"ano {ano} nao pode ser baixado apos {kTENTATIVAS} tentativas; "
        "a api do bcb esta instavel, rode novamente"
    )


def baixar_serie(anos: range, timeout: int = kTIMEOUT) -> pd.DataFrame:
    registros: list[dict] = []
    anos_vazios: list[int] = []
    for ano in anos:
        linhas = baixar_ano(ano, timeout=timeout)
        print(f"  {ano}: {len(linhas)} registros")
        if not linhas:
            anos_vazios.append(ano)
        registros.extend(linhas)
        if ano != anos[-1]:
            time.sleep(kPAUSA_SEGUNDOS)
    if anos_vazios:
        sys.exit(f"anos sem registro: {anos_vazios}; nada foi gravado")
    return pd.DataFrame(registros, columns=["data", "valor"])


def ler_arquivo(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho, dtype=str)


def validar_cobertura(df: pd.DataFrame) -> None:
    """
    um ano fechado de cotacao diaria tem cerca de 250 observacoes uteis; ano com
    menos disso indica resposta truncada do bcb e nao deve chegar ao raw;
    """
    ano_atual = date.today().year
    datas = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    if datas.isna().any():
        sys.exit("data invalida no raw do dolar")
    contagem = datas.dt.year.value_counts()
    esperados = range(kANO_INICIO, ano_atual + 1)
    faltando = [ano for ano in esperados if ano not in contagem.index]
    if faltando:
        sys.exit(f"anos ausentes no raw do dolar: {faltando}")
    minimo = 1 if ano_atual == max(esperados) else kMINIMO_OBS_POR_ANO
    suspensos = {
        ano: int(contagem[ano]) for ano in esperados if contagem[ano] < minimo
    }
    if suspensos:
        sys.exit(f"anos com cobertura insuficiente: {suspensos}; nada foi gravado")


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
        validar_cobertura(df)
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
