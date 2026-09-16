import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt

def executar_modelo_pastesian():
    print("="*60)
    print(" 🍝 PASTESIAN: OTIMIZAÇÃO DE PRODUÇÃO E ESTOQUE (MÉTODO SIMPLEX)")
    print("="*60)
    
    # 1. INTERPRETAÇÃO DO ENUNCIADO
    print("\n[1] INTERPRETAÇÃO DO ENUNCIADO:")
    print(" * Horizonte de planejamento: 4 meses.")
    print(" * Demanda por mês: [M1: 200, M2: 350, M3: 150, M4: 250] lasanhas.")
    print(" * Estoque inicial: 50 lasanhas | Estoque final desejado: 0 lasanhas.")
    print(" * Custos variáveis de produção por mês: [M1: $5.50, M2: $7.20, M3: $8.80, M4: $10.90]")
    print(" * Custos de estocagem entre os meses: [M1->M2: $1.30, M2->M3: $1.95, M3->M4: $2.20]")

    # 2. MODELAGEM MATEMÁTICA (Reduzida para as 4 variáveis de produção X_t)
    print("\n[2] MODELAGEM MATEMÁTICA:")
    print(" * Variáveis de Decisão: X1, X2, X3, X4 (Produção em cada mês).")
    print(" * Função Objetivo (Minimizar Custos Totais de Produção + Estoque):")
    print("   Minimizar Z = 10.95*X1 + 11.35*X2 + 11.00*X3 + 10.90*X4 - 2600")
    print(" * Restrições:")
    print("   1) Atendimento da demanda total: X1 + X2 + X3 + X4 = 900")
    print("   2) Estoque Mês 1 >= 0  =>  X1 >= 150")
    print("   3) Estoque Mês 2 >= 0  =>  X1 + X2 >= 500")
    print("   4) Estocagem Mês 3 >= 0 =>  X1 + X2 + X3 >= 650")
    print("   5) Não-negatividade: X_t >= 0")

    # 3. CONFIGURAÇÃO E RESOLUÇÃO VIA SIMPLEX (SciPy)
    # Coeficientes da Função Objetivo (Minimização)
    c = [10.95, 11.35, 11.00, 10.90]
    
    # Restrições de Inequação (A_ub * x <= b_ub) -> convertidas para (<=) multiplicando por -1
    # -X1 <= -150
    # -X1 - X2 <= -500
    # -X1 - X2 - X3 <= -650
    A_ub = [
        [-1,  0,  0,  0],
        [-1, -1,  0,  0],
        [-1, -1, -1,  0]
    ]
    b_ub = [-150, -500, -650]
    
    # Restrição de Igualdade (A_eq * x == b_eq)
    # X1 + X2 + X3 + X4 = 900
    A_eq = [[1, 1, 1, 1]]
    b_eq = [900]
    
    # Limites das variáveis (X_t >= 0)
    bounds = [(0, None), (0, None), (0, None), (0, None)]
    
    # Executando o Simplex
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='simplex')
    
    if res.success:
        X = res.x
        custo_otimo = res.fun + 2600  # Adicionando a constante fixa de abatimento de estoque inicial
        
        print("\n[3] SOLUÇÃO ÓTIMA ENCONTRADA (MÉTODO SIMPLEX):")
        print(f" * Produção Mês 1 (X1): {X[0]:.2f} unidades")
        print(f" * Produção Mês 2 (X2): {X[1]:.2f} unidades")
        print(f" * Produção Mês 3 (X3): {X[2]:.2f} unidades")
        print(f" * Produção Mês 4 (X4): {X[3]:.2f} unidades")
        print(f" * Custo Total Mínimo: US$ {custo_otimo:.2f}")
        
        # Calculando o estoque mês a mês para exibição e gráfico
        demandas = [200, 350, 150, 250]
        estoque_inicial = 50
        estoques = []
        est_atual = estoque_inicial
        
        print("\n * Plano de Estoque Resultante:")
        for i in range(4):
            est_atual = est_atual + X[i] - demandas[i]
            estoques.append(max(0, est_atual))
            print(f"   - Fim do Mês {i+1}: Estoque = {est_atual:.2f} unidades")

        # 4. GERAÇÃO DE GRÁFICOS
        gerar_graficos(X, demandas, estoques)
    else:
        print("\n[!] O algoritmo não convergiu para uma solução viável:", res.message)

def gerar_graficos(producao, demandas, estoques):
    meses = ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Pastesian - Plano Ótimo de Produção e Estoque', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Produção vs Demanda
    x_pos = np.arange(len(meses))
    largura = 0.35
    
    ax1.bar(x_pos - largura/2, producao, largura, label='Produção Ótima (X)', color='#2b5c8f')
    ax1.bar(x_pos + largura/2, demandas, largura, label='Demanda', color='#e07a5f')
    ax1.set_xlabel('Meses', fontweight='bold')
    ax1.set_ylabel('Quantidade de Lasanhas', fontweight='bold')
    ax1.set_title('Comparativo: Produção x Demanda')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(meses)
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Gráfico 2: Evolução dos Estoques Finais
    ax2.plot(meses, estoques, marker='o', color='#81b29a', linewidth=3, markersize=8, label='Estoque Final')
    ax2.set_xlabel('Meses', fontweight='bold')
    ax2.set_ylabel('Unidades em Estoque', fontweight='bold')
    ax2.set_title('Evolução do Estoque ao Longo dos Meses')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    executar_modelo_pastesian()