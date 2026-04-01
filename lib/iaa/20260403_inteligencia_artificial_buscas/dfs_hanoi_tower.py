import sys

max_disks = 5 # constante para o limite máximo de discos;

def printState(state):
    for i, peg in enumerate(state):
        print(f"estaca {i+1}: {list(peg)}") # imprime o estado atual das estacas;
    print("-" * 5 + ";")

def getNeighbors(state): # gera todos os movimentos válidos a partir do estado atual;
    neighbors = []
    for from_peg_idx in range(3):
        if not state[from_peg_idx]:
            continue
        
        disk_to_move = state[from_peg_idx][-1]  # o disco que pode ser movido é o último (o de cima);
        
        for to_peg_idx in range(3):
            if from_peg_idx == to_peg_idx:
                continue
            
            if not state[to_peg_idx] or state[to_peg_idx][-1] > disk_to_move: # verifica se o movimento é válido seguindo as regras de hanoi;
                new_state = list(list(peg) for peg in state)
                new_state[from_peg_idx].pop()
                new_state[to_peg_idx].append(disk_to_move)
                neighbors.append(tuple(tuple(peg) for peg in new_state)) # converte de volta para tuplas para ser imutável/hashable;
    return neighbors

def dfsSolve(initial_state, goal_state): # resolve o problema da torre de hanoi usando busca em profundidade;
    stack = [(initial_state, [initial_state])]
    visited = {initial_state}
    
    print("iniciando busca em profundidade (dfs)...;")
    
    while stack:
        current_state, path = stack.pop()
        
        printState(current_state) # imprime a iteração atual;
        
        if current_state == goal_state:
            print(f"solução encontrada com {len(path)-1} movimentos!;")
            return path
        
        for neighbor in reversed(getNeighbors(current_state)): # explora os vizinhos;
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))
    
    print("solução não encontrada!;")
    return None

def main(): # função principal para capturar entradas e executar o algoritmo;
    try:
        num_disks_input = input("digite a quantidade de moedas (max 5): ")
        num_disks = int(num_disks_input)
        
        if num_disks > max_disks:
            print(f"erro: o máximo permitido é {max_disks} moedas.;")
            return

        print("digite a peg (1, 2 ou 3) para cada moeda do maior para o menor;")
        print("exemplo para 3 moedas na estaca 1: 111;")
        pegs_input = input("ordem das moedas: ")
        
        if len(pegs_input) != num_disks:
            print("erro: a quantidade de pegs informada deve ser igual ao número de moedas.;")
            return
        
        initial_pegs = [[], [], []] # inicializa as estacas;
        
        for i, peg_char in enumerate(pegs_input): # distribui as moedas (maior para o menor conforme a entrada);
            peg_idx = int(peg_char) - 1
            if peg_idx < 0 or peg_idx > 2:
                print("erro: as estacas devem ser 1, 2 ou 3.;")
                return
            disk_size = num_disks - i
            initial_pegs[peg_idx].insert(0, disk_size)
        
        for peg in initial_pegs: 
            for j in range(len(peg) - 1):
                if peg[j] < peg[j+1]: # valida se a pilha inicial é válida (menores sobre maiores);
                    print("erro: configuração inicial inválida (moeda menor sob moeda maior).;")
                    return

        initial_state = tuple(tuple(peg) for peg in initial_pegs)
        
        goal_pegs = [[], [], []]
        for i in range(num_disks, 0, -1):
            goal_pegs[2].append(i) # o objetivo é mover tudo para a estaca 3 na ordem correta;
        goal_state = tuple(tuple(peg) for peg in goal_pegs)
        
        dfsSolve(initial_state, goal_state)
        
    except ValueError:
        print("erro: entrada inválida.;")

if __name__ == "__main__":
    main()
