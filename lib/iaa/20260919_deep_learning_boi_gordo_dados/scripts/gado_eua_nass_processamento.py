"""
transforma a serie mensal de precos de gado nos eua (nass/quickstats) em serie
semanal iso;

regras (programa de dados 20260919, secao 5):
- escolhe o item (short_desc) com a serie mensal contigua mais longa, para nao
  depender de um item unico valido em toda a janela;
- o preco e mantido em dolares por cwt: a conversao para BRL e para o spread
  contra o boi gordo cepea pertencem a etapa de montagem de atributos, que
  depende da serie do dolar;
- o mes corrente e o mes anterior ficam fora do processamento (ainda nao
  divulgados);
- nenhuma informacao futura: o preco do mes M so fica disponivel a partir da
  semana que contem o ultimo dia de M+1, porque o nass divulga o mes na ultima
  semana seguinte;
- semanas seguintes carregam o ultimo preco divulgado (carry-forward);
- saida: processed/gado_eua_nass_processed.csv;
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

kRAIZ_DADOS = Path(__file__).resolve().parents[1]
kARQUIVO_RAW = kRAIZ_DADOS / "raw" / "gado_eua_nass_raw.csv"
kPROCESSED = kRAIZ_DADOS / "processed"

kSAIDA = kPROCESSED / "gado_eua_nass_processed.csv"
kMETADATA = kPROCESSED / "gado_eua_nass_metadata.csv"

kCOLUNA_VALOR = "Value"
kCOLUNA_ITEM = "short_desc"
kCOLUNA_ANO = "year"
kCOLUNA_MES = "begin_code"
kMESES_ATRASO_DIVULGACAO = 1
kTOLERANCIA_LACUNAS = 2
kCASAS_MOEDA = 2

kITEM_PREFERIDO = "CATTLE, GE 500 LBS - PRICE RECEIVED, MEASURED IN $ / CWT"

kITENS_EXCLUIDOS = [
    "PARITY",
    "10 YEAR AVG",
    "ADJUSTED BASE",
    "PCT OF PARITY",
    "INDEX",
    "PRICE PAID",
]


def carregar_preco_mensal() -> tuple[pd.Series, str]:
    if not kARQUIVO_RAW.exists():
        sys.exit("arquivo raw nao encontrado: raw/gado_eua_nass_raw.csv")

    df = pd.read_csv(kARQUIVO_RAW, dtype=str)
    esperadas = [kCOLUNA_ITEM, kCOLUNA_VALOR, kCOLUNA_ANO, kCOLUNA_MES]
    ausentes = [c for c in esperadas if c not in df.columns]
    if ausentes:
        sys.exit(f"colunas esperadas ausentes no raw: {', '.join(ausentes)}")

    df[kCOLUNA_VALOR] = pd.to_numeric(
        df[kCOLUNA_VALOR].astype(str).str.replace(",", "", regex=False), errors="coerce"
    )
    df = df.dropna(subset=[kCOLUNA_VALOR])
    if df.empty:
        sys.exit("nenhum valor numerico no raw de gado dos eua")

    df["mes"] = pd.PeriodIndex(
        df[kCOLUNA_ANO].astype(int).astype(str)
        + "-"
        + df[kCOLUNA_MES].astype(int).astype(str).str.zfill(2),
        freq="M",
    )
    df[kCOLUNA_ITEM] = df[kCOLUNA_ITEM].fillna("(sem item)")

    derivados = df[kCOLUNA_ITEM].str.contains("|".join(kITENS_EXCLUIDOS), case=False)
    if derivados.all():
        sys.exit("todos os itens do raw sao series derivadas, nao ha preco recebido")
    df = df[~derivados]

    escolhidos: list[tuple[str, pd.Series]] = []
    for item, bloco in df.groupby(kCOLUNA_ITEM):
        mensal = bloco.groupby(bloco["mes"])[[kCOLUNA_VALOR]].first()[kCOLUNA_VALOR]
        escolhidos.append((item, mensal.sort_index()))

    def trecho_contiguo(mensal: pd.Series) -> pd.Series:
        partes: list[list[pd.Period]] = []
        for mes in mensal.index:
            if partes and (mes - partes[-1][-1]).n <= kTOLERANCIA_LACUNAS:
                partes[-1].append(mes)
            else:
                partes.append([mes])
        maior = max(partes, key=len)
        return mensal.loc[maior]

    def preferencia(par: tuple[str, pd.Series]) -> tuple[int, int, int]:
        item, mensal = par
        return (
            int(item == kITEM_PREFERIDO),
            len(trecho_contiguo(mensal)),
            int(mensal.notna().sum()),
        )

    melhor_item, melhor_serie = max(escolhidos, key=preferencia)
    return trecho_contiguo(melhor_serie), melhor_item


def agregar_semanal(mensal: pd.Series) -> pd.DataFrame:
    mes_maximo = pd.Timestamp.now().to_period("M") - kMESES_ATRASO_DIVULGACAO
    mensal = mensal[mensal.index <= mes_maximo]
    if mensal.empty:
        sys.exit("nenhum mes fechado apos aplicar o atraso de divulgacao")

    primeira = mensal.index.min().start_time.normalize()
    ultima = mensal.index.max().start_time.normalize()

    semana_inicio = pd.date_range(primeira, ultima, freq="W-MON")
    grade = pd.DataFrame({"data_semana_inicio": semana_inicio})
    grade["data_semana_fim"] = grade["data_semana_inicio"] + pd.to_timedelta(6, unit="D")

    janela = pd.DataFrame(
        {
            "mes_referencia": mensal.index,
            "preco_gado_eua_usd_cwt": mensal.values,
            "data_release": [m + kMESES_ATRASO_DIVULGACAO for m in mensal.index],
        }
    )
    janela["data_release"] = pd.PeriodIndex(janela["data_release"], freq="M").end_time.normalize()
    janela["data_release_fim_semana"] = janela["data_release"] + pd.to_timedelta(
        6 - janela["data_release"].dt.dayofweek, unit="D"
    )

    liberados = grade.merge(
        janela[["data_release_fim_semana", "mes_referencia", "preco_gado_eua_usd_cwt"]],
        left_on="data_semana_fim",
        right_on="data_release_fim_semana",
        how="left",
    )
    liberados["mes_referencia"] = liberados["mes_referencia"].ffill()
    liberados["preco_gado_eua_usd_cwt"] = liberados["preco_gado_eua_usd_cwt"].ffill()

    iso = liberados["data_semana_inicio"].dt.isocalendar()
    liberados["ano_iso"] = iso["year"].astype(int)
    liberados["semana_iso"] = iso["week"].astype(int)
    liberados["serie"] = (
        liberados["ano_iso"].astype(str) + "-W" + liberados["semana_iso"].astype(str).str.zfill(2)
    )

    liberados = liberados.dropna(subset=["preco_gado_eua_usd_cwt"]).copy()
    liberados["preco_gado_eua_usd_cwt"] = liberados["preco_gado_eua_usd_cwt"].round(kCASAS_MOEDA)
    liberados["mes_referencia"] = liberados["mes_referencia"].astype(str)

    ordem = [
        "serie",
        "data_semana_inicio",
        "data_semana_fim",
        "preco_gado_eua_usd_cwt",
        "mes_referencia",
        "ano_iso",
        "semana_iso",
    ]
    return liberados[ordem].reset_index(drop=True)


def registrar_metadados(arquivo: Path, df: pd.DataFrame, arquivo_fonte: Path, item: str) -> None:
    registro = {
        "arquivo": arquivo.name,
        "fonte": "USDA NASS - QuickStats (preco de gado recebido pelo produtor)",
        "arquivo_fonte": arquivo_fonte.name,
        "gerado_em": date.today().isoformat(),
        "item_selecionado": item,
        "periodicidade": "semanal ISO",
        "regra_item": "item com a serie mensal contigua mais longa do raw",
        "regra_divulgacao": (
            f"preco do mes M disponivel na semana que contem o ultimo dia de "
            f"M+{kMESES_ATRASO_DIVULGACAO}"
        ),
        "regra_carry_forward": "semanas seguintes carregam o ultimo preco divulgado",
        "unidade": "USD por cwt (45,3592 kg)",
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
    mensal, item = carregar_preco_mensal()
    semanal = agregar_semanal(mensal)
    semanal.to_csv(kSAIDA, index=False)

    registrar_metadados(kSAIDA, semanal, kARQUIVO_RAW, item)

    print(f"origem:  {kARQUIVO_RAW.name} (item: {item})")
    print(f"meses:   {len(mensal)} fechados")
    print(f"saida:   {kSAIDA}")
    print(f"semanas: {semanal.shape[0]}")
    print(f"inicio:  {semanal['data_semana_inicio'].min():%d/%m/%Y}")
    print(f"fim:     {semanal['data_semana_fim'].max():%d/%m/%Y}")


if __name__ == "__main__":
    main()
