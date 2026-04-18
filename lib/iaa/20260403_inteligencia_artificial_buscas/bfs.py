from collections import deque

grafo = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F", "G"],
    "D": ["H", "I"],
    "E": ["J"],
    "F": ["K"],
    "G": [],
    "H": ["L"],
    "I": ["M"],
    "J": ["N"],
    "K": ["O"],
    "L": [],
    "M": [],
    "N": [],
    "O": []
} # dicionário de listas de adjacência;

def bfs(grafo, inicio, no_destino):
    fila = deque([inicio]) # fila;
    visitados = set()

    while fila:
        no = fila.popleft()  # remove o primeiro, aqui está o pulo do gato pois o grafo[no] é montado sempre com o mais a esquerda;

        if no not in visitados:
            print(no)
            visitados.add(no)
            print(f'visitados: {visitados};')

            if no == no_destino:
                return True

            for vizinho in grafo[no]:
                print(f'grafo[no]: {grafo[no]}') # grafo filho do no;
                if vizinho not in visitados:
                    fila.append(vizinho)

    return False


foi_encontrado = bfs(grafo, inicio="A", no_destino="E")

if foi_encontrado:
    print('resultado encontrado;')
else:
    print('resultado não encontrado;')