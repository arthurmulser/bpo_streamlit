import pandas as pd # importar biblioteca pandas;
import matplotlib.pyplot as plt # importar biblioteca matplotlib;
import seaborn as sns # importar biblioteca seaborn;
import os # importar biblioteca os;

caminho_arquivo = os.path.join(os.path.dirname(__file__), "life_expec_alterado.csv") # definir caminho absoluto para o arquivo csv;
df_life_expec = pd.read_csv(caminho_arquivo, sep=";") # ler arquivo csv com separador ponto e virgula;

correlacao = df_life_expec["Schooling"].corr(df_life_expec["Life_expectancy"]) # calcular correlacao de pearson entre escolaridade e expectativa de vida;
print(f"coeficiente de correlação de pearson: {correlacao:.4f}") # mostrar valor da correlacao no terminal;

plt.figure(figsize=(10, 6)) # definir tamanho da figura;
sns.regplot(data=df_life_expec, x="Schooling", y="Life_expectancy", scatter_kws={"alpha":0.3}, line_kws={"color":"red"}) # gerar grafico de dispersao com linha de regressao;
plt.title(f"relação entre escolaridade e expectativa de vida (r = {correlacao:.2f})") # definir titulo do grafico com valor de r;
plt.xlabel("anos de escolaridade") # definir rotulo do eixo x;
plt.ylabel("expectativa de vida") # definir rotulo do eixo y;
plt.grid(True, linestyle="--", alpha=0.6) # adicionar grade ao grafico;
plt.tight_layout() # ajustar layout automaticamente;
plt.show() # exibir o grafico gerado;
