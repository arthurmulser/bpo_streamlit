import heapq # importar biblioteca para fila de prioridade;

grafo = { # grafo de 5 camadas para busca de custo uniforme;
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

def ucs(grafo, inicio, objetivo):
    fila_prioridade = [(0, inicio, [inicio])] # composta por uma tupla;
    visitados = set()

    while fila_prioridade: # enquanto houver nos na fila;
        custo_atual, no_atual, caminho = heapq.heappop(fila_prioridade) # extrair no de menor custo (um heap é uma árvore binária com uma propriedade especial: o pai sempre é menor que os filhos);

        if no_atual == objetivo:
            return custo_atual, caminho # retornar custo e caminho;

        if no_atual not in visitados: # processar nó se ainda não visitado;
            visitados.add(no_atual) # marcar nó como visitado;

            for vizinho, custo_vizinho in grafo.get(no_atual, []): # percorrer vizinhos;
                if vizinho not in visitados: # verificar se o vizinho ja foi visitado;
                    novo_custo = custo_atual + custo_vizinho # calcular novo custo;
                    novo_caminho = caminho + [vizinho] # construir novo caminho;
                    heapq.heappush(fila_prioridade, (novo_custo, vizinho, novo_caminho)) # adicionar na fila;
                    print(f"fila: {fila_prioridade}") # exibir caminho;

    return float('inf'), [] # infinito se não encontrar;

if __name__ == "__main__": # bloco principal;
    resultado_custo, resultado_caminho = ucs(grafo, 'A', 'JJ') # executar busca;
    print(f"custo: {resultado_custo}") # exibir custo;
    print(f"caminho: {resultado_caminho}") # exibir caminho;
