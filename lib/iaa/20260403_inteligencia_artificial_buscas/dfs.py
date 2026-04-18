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

'''
A (nível 1)
├── B (nível 2)
│   ├── D (nível 3)
│   │   ├── H (nível 4)
│   │   │   └── L (nível 5)
│   │   └── I (nível 4)
│   │       └── M (nível 5)
│   └── E (nível 3)
│       └── J (nível 4)
│           └── N (nível 5)
└── C (nível 2)
    ├── F (nível 3)
    │   └── K (nível 4)
    │       └── O (nível 5)
    └── G (nível 3)
'''

def dfs(grafo, no, visitados=None, no_destino=""):
    if visitados is None:
        visitados = set() # conjunto;

    print(no)
    visitados.add(no)
    print(f'visitados: {visitados};')

    if no == no_destino:
        return True
    
    else:
        for vizinho in grafo[no]:
            print(f'grafo[no]: {grafo[no]}') # grafo filho do no;
            if vizinho not in visitados:
                if dfs(grafo, vizinho, visitados, no_destino):
                    return True
  
    return False        

foi_encontrado = dfs(grafo, no="A", visitados=None, no_destino="E")

if foi_encontrado:
    print('resultado encontrado;')    
else:
    print('resultado não encontrado;')  
