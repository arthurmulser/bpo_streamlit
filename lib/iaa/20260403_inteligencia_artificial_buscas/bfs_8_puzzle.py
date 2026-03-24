import os
from collections import deque

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def get_neighbors(state):
    neighbors = []
    r, c = find_zero(state)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_state = [row[:] for row in state]
            new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
            neighbors.append(new_state)
    return neighbors

def print_layer(layer_num, states, f): # função modificada para aceitar um objeto de arquivo (f);
    f.write(f"\n--- camada {layer_num} ({len(states)} estados) ---\n")
    for state in states:
        for row in state:
            f.write(str(row) + "\n")
        f.write("-" * 10 + "\n")

def solve_8_puzzle(start_state):
    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    queue = deque([(start_state, 0)])
    visited = {str(start_state)}
    
    current_level = 0
    states_in_current_level = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.abspath(os.path.join(current_dir, "..", "solutions"))
    file_path = os.path.join(target_dir, "bfs_8_puzzle_solve")

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    with open(file_path, "w", encoding="utf-8") as f: #  abre o arquivo para escrita;
        f.write("iniciando busca por largura (bfs)...\n")
        print("processando... verifique o arquivo solve.txt ao finalizar;")

        while queue:
            state, level = queue.popleft()
            
            if level > current_level:
                print_layer(current_level, states_in_current_level, f)
                current_level = level
                states_in_current_level = []
            
            states_in_current_level.append(state)

            if state == goal_state:
                print_layer(level, states_in_current_level, f)
                f.write(f"\nsolucao encontrada no nivel: {level};\n")
                print(f"salva em solve.txt;")
                return
            
            for neighbor in get_neighbors(state):
                if str(neighbor) not in visited:
                    visited.add(str(neighbor))
                    queue.append((neighbor, level + 1))

initial_board = [ # estado inicial;
    [0, 8, 7],
    [6, 5, 4],
    [3, 2, 1]
]

solve_8_puzzle(initial_board)

