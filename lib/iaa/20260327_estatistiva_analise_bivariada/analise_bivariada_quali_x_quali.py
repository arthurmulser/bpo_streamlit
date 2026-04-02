import pandas as pd # importar biblioteca pandas;
import matplotlib.pyplot as plt # importar biblioteca matplotlib;
import seaborn as sns # importar biblioteca seaborn;
import os # importar biblioteca os;

caminho_arquivo = os.path.join(os.path.dirname(__file__), "life_expec_alterado.csv") # definir caminho absoluto para o arquivo csv;
df_life_expec = pd.read_csv(caminho_arquivo, sep=";") # ler arquivo csv com separador ponto e virgula;

tabela_contingencia = pd.crosstab(df_life_expec["Region"], df_life_expec["Economy_status_Developed"]) # criar tabela de contingencia;
print("tabela de Contingência (frequência absoluta):") # imprimir titulo para tabela;
print(tabela_contingencia) # mostrar tabela de frequencia absoluta;

tabela_relativa = pd.crosstab(df_life_expec["Region"], df_life_expec["Economy_status_Developed"], normalize="index") # criar tabela de frequencia relativa por linha;
print("\ntabela de frequência relativa (por região):") # imprimir titulo para tabela relativa;
print(tabela_relativa) # mostrar tabela de frequencia relativa;

tabela_relativa.plot(kind="bar", stacked=True, figsize=(12, 6)) # gerar grafico de barras empilhadas;
plt.title("status econômico por região") # definir titulo do grafico;
plt.xlabel("região") # definir rotulo do eixo x;
plt.ylabel("proporção") # definir rotulo do eixo y;
plt.legend(title="desenvolvido", loc="upper right") # adicionar legenda ao grafico;
plt.xticks(rotation=45) # rotacionar rotulos do eixo x;
plt.tight_layout() # ajustar layout automaticamente;
plt.show() # exibir o grafico gerado;
