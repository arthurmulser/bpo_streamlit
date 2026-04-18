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
