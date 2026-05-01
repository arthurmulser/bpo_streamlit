import heapq # importar biblioteca para fila de prioridade;

grafo = { # grafo de 5 camadas;
    'A': [('B', 2), ('C', 5)], # camada 1;
    'B': [('D', 4), ('E', 1)], # camada 2;
    'C': [('E', 6), ('F', 3)], # camada 2;
    'D': [('G', 7), ('H', 2)], # camada 3;
    'E': [('H', 5), ('I', 3)], # camada 3;
    'F': [('I', 1), ('J', 8)], # camada 3;
    'G': [('K', 3)], # camada 4;
    'H': [('L', 4)], # camada 4;
    'I': [('M', 2)], # camada 4;
    'J': [('N', 6), ('O', 5)], # camada 4;
    'K': [], # camada 5;
    'L': [], # camada 5;
    'M': [], # camada 5;
    'N': [], # camada 5;
    'O': []  # camada 5;
}

heuristica = { # valores heuristicos para o objetivo m;
    'A': 8, # estimativa para a;
    'B': 6, # estimativa para b;
    'C': 6, # estimativa para c;
    'D': 4, # estimativa para d;
    'E': 5, # estimativa para e;
    'F': 3, # estimativa para f;
    'G': 5, # estimativa para g;
    'H': 3, # estimativa para h;
    'I': 2, # estimativa para i;
    'J': 4, # estimativa para j;
    'K': 6, # estimativa para k;
    'L': 4, # estimativa para l;
    'M': 0, # estimativa para m;
    'N': 6, # estimativa para n;
    'O': 7  # estimativa para o;
}

def aStarSearch(grafo, heuristica, inicio, objetivo):
    fila_prioridade = [(heuristica[inicio], 0, inicio, [inicio])]
    custos_acumulados = {inicio: 0} # dicionario de menores custos g;

    while fila_prioridade: # processar fila;
        f, g, no_atual, caminho = heapq.heappop(fila_prioridade) # extrair elemento de menor f;
        print(f"elemento extraído: (f={f}, g={g}, nó='{no_atual}', caminho={caminho})")

        if no_atual == objetivo: # checar objetivo;
            return g, caminho # retornar custo g e trajeto;

        for vizinho, custo_vizinho in grafo.get(no_atual, []): # iterar vizinhos;
            novo_custo_g = g + custo_vizinho # calcular custo g acumulado;
            if vizinho not in custos_acumulados or novo_custo_g < custos_acumulados[vizinho]: # verificar se eh melhor caminho;
                custos_acumulados[vizinho] = novo_custo_g # atualizar custo g;
                f_total = novo_custo_g + heuristica.get(vizinho, 0) # calcular f = g + h;
                heapq.heappush(fila_prioridade, (f_total, novo_custo_g, vizinho, caminho + [vizinho])) # inserir na fila;

    return float('inf'), [] # retornar vazio se nao encontrar;

if __name__ == "__main__": # ponto de entrada;
    resultado_custo, resultado_caminho = aStarSearch(grafo, heuristica, 'A', 'M') # executar busca;
    print(f"custo: {resultado_custo}") # mostrar custo;
    print(f"caminho: {resultado_caminho}") # mostrar caminho;
