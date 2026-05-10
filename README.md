# bpo_streamlit - Starting the Project

Pequeno guia para configurar e rodar este projeto localmente.

## Requisitos
- Python 3.8+ instalado;
- PowerShell (Windows) ou um shell Unix (bash, zsh);

## Setup (recomendado)

- Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
Se houver bloqueio de execução de scripts, rode:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

- Unix / WSL:
```bash
python3 -m venv venv
source venv/bin/activate
```

- Instalar dependências:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## Rodar a aplicação (Streamlit)
```powershell
streamlit run .\sc_new.py
```
// sc_new;
```powershell
streamlit run .\main.py
```
// main;

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
Essas funções tentam conectar ao banco usando as credenciais em `utils.py`. Se não tiver acesso ao DB, crie manualmente os CSVs conforme as colunas esperadas.

## Arquivos CSV esperados (exemplo das colunas)
- `_csv/view_animais.csv`

- `_csv/view_eventos.csv`


