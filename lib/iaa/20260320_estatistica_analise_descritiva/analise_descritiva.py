
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

# 1. carregar dados;
try:
    df = pd.read_csv('infant_deaths.csv')
except FileNotFoundError:
    print("erro: O arquivo 'infant_deaths.csv' não foi encontrado na pasta atual.")
    exit()

# 2. garantir que a coluna 'infant_deaths' seja tratada como número;
# (o 'coerce' transforma qualquer texto perdido em nan, que removemos depois);
df['infant_deaths'] = pd.to_numeric(df['infant_deaths'], errors='coerce')
df = df.dropna(subset=['infant_deaths'])

# exibir informações básicas;
print("=" * 80)
print("análise descritiva - infant_deaths")
print("=" * 80)
print(f"\nvariável analisada: {df.columns[0]}")
print(f"número de observações válidas: {df.shape[0]}\n")

data = df['infant_deaths']

print(f"{'=' * 80}")
print(f"média:                            {data.mean():.4f}")
print(f"desvio padrão:                    {data.std():.4f}")
print(f"mínimo:                           {data.min():.4f}")
print(f"q1 (1º quartil):                  {data.quantile(0.25):.4f}")
print(f"q2 (mediana/2º quartil):          {data.quantile(0.50):.4f}")
print(f"q3 (3º quartil):                  {data.quantile(0.75):.4f}")
print(f"máximo:                           {data.max():.4f}")
print(f"amplitude:                        {data.max() - data.min():.4f}")
print(f"distância interquartílica (iqr):  {data.quantile(0.75) - data.quantile(0.25):.4f}")

cv = (data.std() / data.mean() * 100) if data.mean() != 0 else 0
print(f"coeficiente de variação:          {cv:.4f}%")

moda = data.mode()
print(f"moda:                             {moda[0] if not moda.empty else 'sem moda'}")

print(f"assimetria (skewness):            {stats.skew(data):.4f}")

print(f"curtose:                          {stats.kurtosis(data):.4f}")
print("=" * 80) 

fig, (ax_hist, ax_box) = plt.subplots(1, 2, figsize=(12, 5))

# 1. histograma;
ax_hist.hist(data, bins=15, color='skyblue', edgecolor='black', alpha=0.7)
ax_hist.set_title('histograma de infant_deaths')
ax_hist.set_xlabel('mortes')
ax_hist.set_ylabel('frequência')
ax_hist.grid(axis='y', linestyle='--', alpha=0.7)

# 2. boxplot;
ax_box.boxplot(data, patch_artist=True, boxprops=dict(facecolor='lightgreen'))
ax_box.set_title('boxplot de infant_deaths')
ax_box.set_ylabel('valores')
ax_box.set_xticklabels(['dados'])
ax_box.grid(axis='y', linestyle='--', alpha=0.7)

# ajustar layout para não sobrepor;
plt.tight_layout()

# exibir os gráficos na tela;
print("\nexibindo gráficos... feche a janela da imagem para encerrar o script.")
plt.show()