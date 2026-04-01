import pandas as pd # importar biblioteca pandas;
import matplotlib.pyplot as plt # importar biblioteca matplotlib;
import seaborn as sns # importar biblioteca seaborn;
import os # importar biblioteca os;

caminho_arquivo = os.path.join(os.path.dirname(__file__), "life_expec_alterado.csv") # definir caminho absoluto para o arquivo csv;
df_life_expec = pd.read_csv(caminho_arquivo, sep=";") # ler arquivo csv com separador ponto e virgula;

print(df_life_expec.groupby("Economy_status_Developed")["Life_expectancy"].describe()) # mostrar estatisticas descritivas por status economico;

plt.figure(figsize=(10, 6)) # definir tamanho da figura;
sns.boxplot(data=df_life_expec, x="Economy_status_Developed", y="Life_expectancy") # gerar boxplot bivariado;
plt.title("expectativa de vida por status econômico") # definir titulo do grafico;
plt.xlabel("status econômico (desenvolvido: yes/no)") # definir rotulo do eixo x;
plt.ylabel("expectativa de vida") # definir rotulo do eixo y;
plt.tight_layout() # ajustar layout automaticamente;
plt.show() # exibir o grafico gerado;
