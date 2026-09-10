from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

kRANDOM_SEED = 42


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def tanh_prime(a):
    return 1 - np.tanh(a) ** 2


class MlpGaussianaCamadas:
    def __init__(self, hidden_sizes, activation='tanh', learning_rate=0.1, momentum=0.9,
                 n_epochs=3000, seed=kRANDOM_SEED):
        # arquitetura: 2 entradas (x1, x2) -> camadas ocultas -> 1 saida (sigmoid);
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.n_epochs = n_epochs
        sizes = [2] + list(hidden_sizes) + [1]
        self.sizes = sizes
        rng = np.random.default_rng(seed)
        # pesos e bias de cada camada com inicializacao xavier;
        self.weights = []
        self.biases = []
        for i in range(len(sizes) - 1):
            fan_in, fan_out = sizes[i], sizes[i + 1]
            self.weights.append(rng.normal(0, np.sqrt(2 / (fan_in + fan_out)), (fan_in, fan_out)))
            self.biases.append(np.zeros(fan_out))
        # velocidades do momentum;
        self.velocities_w = [np.zeros_like(w) for w in self.weights]
        self.velocities_b = [np.zeros_like(b) for b in self.biases]

    def forward(self, x):
        # propagacao: ativacao nao linear nas camadas ocultas e sigmoid na saida;
        acts = [x]
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            z = acts[-1] @ w + b
            if i == len(self.weights) - 1:
                acts.append(sigmoid(z))
            else:
                acts.append(np.tanh(z))
        self.activations = acts
        return acts[-1]

    def predict(self, x):
        return (self.forward(x) >= 0.5).astype(int)

    def backprop(self, x, y):
        # cross-entropy binaria: com sigmoid na saida o gradiente em z ultimo colapsa para (a - y);
        n = len(x)
        dz = (self.activations[-1] - y) / n
        dw_list, db_list = [], []
        for layer in range(len(self.weights) - 1, -1, -1):
            dw = self.activations[layer].T @ dz
            db = dz.sum(axis=0)
            dw_list.append(dw)
            db_list.append(db)
            if layer > 0:
                da = dz @ self.weights[layer].T
                # tanh: derivada em funcao da saida ativada a -> 1 - a^2;
                dz = da * tanh_prime(self.activations[layer])
        return list(reversed(dw_list)), list(reversed(db_list))

    def fit(self, x, y):
        loss_history = []
        for _ in range(self.n_epochs):
            self.forward(x)
            dw_list, db_list = self.backprop(x, y)
            for i in range(len(self.weights)):
                self.velocities_w[i] = self.momentum * self.velocities_w[i] + (1 - self.momentum) * dw_list[i]
                self.velocities_b[i] = self.momentum * self.velocities_b[i] + (1 - self.momentum) * db_list[i]
                self.weights[i] -= self.learning_rate * self.velocities_w[i]
                self.biases[i] -= self.learning_rate * self.velocities_b[i]
            loss = -np.mean(y * np.log(self.activations[-1] + 1e-12)
                            + (1 - y) * np.log(1 - self.activations[-1] + 1e-12))
            loss_history.append(float(loss))
        return loss_history

    def score(self, x, y):
        return float(np.mean(self.predict(x).ravel() == y.ravel()))


def make_gaussian_data(n_samples=400):
    # duas distribuicoes gaussianas bem separadas (como o playground);
    rng = np.random.default_rng(kRANDOM_SEED)
    n = n_samples // 2
    c0 = rng.normal([-1.5, -1.5], 0.8, (n, 2))
    c1 = rng.normal([1.5, 1.5], 0.8, (n, 2))
    x = np.vstack([c0, c1])
    y = np.array([0] * n + [1] * n)
    return x, y


def make_circles_data(n_samples=400):
    # padrao complexo: anel ao redor do centro (ruido gaussiano nos raios);
    rng = np.random.default_rng(kRANDOM_SEED)
    n = n_samples // 2
    # classe 0: circulo interno;
    theta0 = rng.uniform(0, 2 * np.pi, n)
    x0 = np.c_[0.5 * np.cos(theta0), 0.5 * np.sin(theta0)] + rng.normal(0, 0.1, (n, 2))
    # classe 1: anel externo;
    theta1 = rng.uniform(0, 2 * np.pi, n)
    x1 = np.c_[2.0 * np.cos(theta1), 2.0 * np.sin(theta1)] + rng.normal(0, 0.1, (n, 2))
    x = np.vstack([x0, x1])
    y = np.array([0] * n + [1] * n)
    return x, y


def train_test_split(x, y, test_size=0.3, seed=kRANDOM_SEED):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(x))
    n_test = int(test_size * len(x))
    test_idx, train_idx = idx[:n_test], idx[n_test:]
    return x[train_idx], x[test_idx], y[train_idx], y[test_idx]


def linear_separability(x, y):
    # acuracia de um classificador linear (fisher) nos dados, medindo o quanto
    # as classes estao separaveis linearmente nessa representacao;
    x0, x1 = x[y == 0], x[y == 1]
    m0, m1 = x0.mean(axis=0), x1.mean(axis=0)
    sw = (x0 - m0).T @ (x0 - m0) + (x1 - m1).T @ (x1 - m1)
    sw = sw + 1e-6 * np.eye(x.shape[1])
    w = np.linalg.solve(sw, m1 - m0)
    t = (m0 @ w + m1 @ w) / 2
    acc = 0.5 * (np.mean(x0 @ w < t) + np.mean(x1 @ w > t))
    return acc


def pca_projection(x, n_components=2):
    x_centered = x - x.mean(axis=0)
    _, _, vt = np.linalg.svd(x_centered, full_matrices=False)
    return x_centered @ vt[:n_components].T


def part1_gaussiana():
    print("\n" + "=" * 64)
    print("  PARTE 1 - GAUSSIANA (2 CLUSTERS) COM 30% PARA TESTE")
    print("=" * 64)

    x, y = make_gaussian_data()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

    model = MlpGaussianaCamadas(hidden_sizes=(6,))
    model.fit(x_train, y_train.astype(float).reshape(-1, 1))

    print(f"  dados: {len(x)} amostras (70% treino / 30% teste)")
    print(f"  arquitetura: 2 -> 6 -> 1")
    print(f"  acuracia treino: {model.score(x_train, y_train):.2%}")
    print(f"  acuracia teste:  {model.score(x_test, y_test):.2%}")
    print("  conclusao: dados gaussianos separaveis sao faceis;\n"
          "             o desafio esta nos padroes nao lineares (ver parte 2);")
    return x_train, x_test, y_train, y_test


def part2_melhorar_aprendizado():
    print("\n" + "=" * 64)
    print("  PARTE 2 - COMO MELHORAR O APRENDIZADO (PADRAO COMPLEXO: ANEIS)")
    print("=" * 64)

    x, y = make_circles_data()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

    arquiteturas = [(), (2,), (8,), (12, 6)]
    print("  arquitetura            | acuracia treino | acuracia teste")
    print("  -----------------------|-----------------|---------------")
    for arch in arquiteturas:
        model = MlpGaussianaCamadas(hidden_sizes=arch)
        model.fit(x_train, y_train.astype(float).reshape(-1, 1))
        label = "sem camada oculta" if not arch else " -> ".join(map(str, arch))
        print(f"  {label:<22} | {model.score(x_train, y_train):>13.2%} | {model.score(x_test, y_test):>12.2%}")

    print("  formas de melhorar o aprendizado de padroes complexos:")
    print("  - aumentar a profundidade (mais camadas ocultas);")
    print("  - aumentar o numero de neuronios por camada;")
    print("  - usar ativacoes nao lineares (tanh, relu, sigmoid);")
    print("  - melhorar o otimizador (momentum, adam) e ajustar a taxa;")
    print("  - dispor de mais dados e aplicar regularizacao (dropout, L2);")
    print("  - normalizar as entradas e fazer engenharia de features;")

    return x_train, x_test, y_train, y_test


def part3_camadas():
    print("\n" + "=" * 64)
    print("  PARTE 3 - O QUE CADA CAMADA APRENDE (BAIXA x ALTA)")
    print("=" * 64)

    x, y = make_circles_data()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

    # ultima camada oculta com 2 neuronios para visualizarmos cada amostra em 2d;
    model = MlpGaussianaCamadas(hidden_sizes=(8, 2))
    model.fit(x_train, y_train.astype(float).reshape(-1, 1))

    # representacoes em treino;
    reps = {'camada 0 (entrada)': x_train}
    for layer in range(1, len(model.activations) - 1):
        reps[f'camada oculta {layer}'] = model.activations[layer]

    print("  separabilidade linear de cada camada (acuracia do Fisher):")
    for name, rep in reps.items():
        print(f"  - {name}: {linear_separability(rep, y_train):.2%}")

    fig, axes = plt.subplots(1, len(reps), figsize=(6 * len(reps), 5))
    for ax, (name, rep) in zip(axes, reps.items()):
        rep_2d = rep if rep.shape[1] == 2 else pca_projection(rep)
        ax.scatter(rep_2d[:, 0], rep_2d[:, 1], c=y_train, cmap=plt.cm.RdBu, edgecolors='k', s=25)
        ax.set_title(name)
        ax.set_xlabel('dimensao 1')
        ax.set_ylabel('dimensao 2')

    plt.suptitle("XOR / aneis: representacoes internas por camada")
    plt.tight_layout()
    output_path = Path(__file__).parent / "resultados_camadas.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n  grafico salvo em: {output_path}")

    print("  conclusao: camadas mais baixas aprendem padroes simples\n"
          "  (combinacoes locais/lineares); as camadas superiores combinam\n"
          "  esses padroes e produzem representacoes abstratas e mais\n"
          "  separaveis, logo as UPPER LAYERS aprendem padroes mais complexos;")

    if plt.get_backend() != 'agg':
        plt.show()


def main():
    part1_gaussiana()
    part2_melhorar_aprendizado()
    part3_camadas()


if __name__ == '__main__':
    main()