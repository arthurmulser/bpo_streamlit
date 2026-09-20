"""
ativador central das coletas e processamentos da frente de dados;

uso:
    python main_dados.py                       # coleta + processamento de todas as fontes;
    python main_dados.py --coleta              # apenas coletas;
    python main_dados.py --processamento       # apenas processamentos;
    python main_dados.py --fonte leite_sidra   # apenas uma fonte;
    python main_dados.py --force               # rebaixa mesmo se o arquivo existir;
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

kRAIZ_DADOS = Path(__file__).resolve().parent
kSCRIPTS = kRAIZ_DADOS / "scripts"

kFONTES = ["abate_bovinos_sif", "boi_gordo_cepea"]

kETAPAS_PADRAO = ["coleta", "processamento"]


def executar_fonte(fonte: str, etapas: list[str], force: bool) -> None:
    for etapa in etapas:
        script = kSCRIPTS / f"{fonte}_{etapa}.py"
        if not script.exists():
            sys.exit(f"script nao encontrado: {script}")
        comando = [sys.executable, str(script)]
        if etapa == "coleta" and force:
            comando.append("--force")
        print(f"=== [{fonte}] {etapa} ===")
        subprocess.run(comando, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="ativador central das coletas e processamentos de dados")
    parser.add_argument("--fonte", default=None, help="nome da fonte a executar (padrao: todas)")
    parser.add_argument("--coleta", action="store_true", help="executa apenas as coletas")
    parser.add_argument("--processamento", action="store_true", help="executa apenas os processamentos")
    parser.add_argument("--force", action="store_true", help="rebaixa mesmo se o arquivo existir")
    args = parser.parse_args()

    fontes = [args.fonte] if args.fonte else kFONTES
    if args.fonte and args.fonte not in kFONTES:
        sys.exit(f"fonte desconhecida: {args.fonte} (disponiveis: {', '.join(kFONTES)})")

    if args.coleta and not args.processamento:
        etapas = ["coleta"]
    elif args.processamento and not args.coleta:
        etapas = ["processamento"]
    else:
        etapas = kETAPAS_PADRAO

    for fonte in fontes:
        executar_fonte(fonte, etapas, args.force)


if __name__ == "__main__":
    main()