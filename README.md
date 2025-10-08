# bpo_streamlit

Pequeno guia para configurar e rodar este projeto localmente.

## Requisitos
- Python 3.8+ instalado
- PowerShell (Windows) ou um shell Unix (bash, zsh)

## Setup (recomendado)
1. Abrir terminal na pasta do projeto:
```powershell
cd C:\_Projects\bpo_streamlit
```

2. Criar e ativar o ambiente virtual (Windows PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
Se houver bloqueio de execução de scripts, rode:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

(Unix / WSL):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instalar dependências:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## Rodar a aplicação (Streamlit)
```powershell
streamlit run .\sc_new.py
```
ou para a app principal:
```powershell
streamlit run .\main.py
```

## Gerar CSVs sem UI (teste rápido)
Crie `test_generate_csvs.py` com:
```python
from sc_new import fetch_and_save_view_animais, fetch_and_save_view_eventos
from pathlib import Path
p = Path('_csv'); p.mkdir(exist_ok=True)
fetch_and_save_view_animais(p / 'view_animais.csv')
fetch_and_save_view_eventos(p / 'view_eventos.csv')
print('CSVs gerados')
```
Execute:
```powershell
python .\test_generate_csvs.py
```
> Essas funções tentam conectar ao banco usando as credenciais em `utils.py`. Se não tiver acesso ao DB, crie manualmente os CSVs conforme as colunas esperadas.

## Arquivos CSV esperados (exemplo das colunas)
- `_csv/view_animais.csv`:
  - idtb_animais,nome,sexo,data_nascimento,idtb_animais_mae,nome_mae,dt_desmame,idtb_ativo

- `_csv/view_eventos.csv`:
  - idtb_eventos,idtb_animais,idtb_eventos_tipos,dt_evento,valor

## Pacotes que você pode desinstalar globalmente (fora do venv)
Se você instalou pacotes globalmente no sistema Python e quer manter o ambiente limpo, pode desinstalar estes pacotes do Python global pois o projeto usa o `venv` local:

- streamlit
- pandas
- plotly
- pymysql
- matplotlib
- yfinance
- python-dotenv
- mysql-connector-python
- langchain-groq

Use (fora do venv):
```powershell
pip uninstall streamlit pandas plotly pymysql matplotlib yfinance python-dotenv mysql-connector-python langchain-groq
```

> Atenção: só desinstale globalmente se você tiver certeza de que outros projetos não dependem desses pacotes fora do `venv`.

## Notas
- `.gitignore` já ignora `_csv/`, `__pycache__/`, `.env`, `debug.log` e `venv/`.
- Após instalar dependências no `venv`, recomendo travar versões com:
```powershell
pip freeze > requirements.txt
```

Se quiser, eu adiciono `test_generate_csvs.py` ao repositório e travo as versões no `requirements.txt` atual.
