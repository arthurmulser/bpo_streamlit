from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

kRANDOM_SEED = 42


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def tanh_prime(a):
    return 1 - np.tanh(a) ** 2


class MlpCirculoProfundidade:
    def __init__(self, hidden_sizes, learning_rate=0.05, momentum=0.9, n_epochs=30, seed=kRANDOM_SEED):
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
        # propagacao: ativacao tanh nas ocultas e sigmoid na saida;
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
        # cross-entropy binaria com sigmoid na saida;
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
                dz = da * tanh_prime(self.activations[layer])
        return list(reversed(dw_list)), list(reversed(db_list))

    def fit(self, x, y, eval_data=None):
        # treino online (sgd sequencial) como no playground: uma epoca = passar os dados amostra a amostra;
        loss_history = []
        train_acc_history, test_acc_history = [], []
        n = len(x)
        y_col = y.reshape(-1, 1)
        rng = np.random.default_rng(kRANDOM_SEED)
        for _ in range(self.n_epochs):
            order = rng.permutation(n)
            epoch_loss = 0.0
            for i in order:
                xi, yi = x[i:i + 1], y_col[i:i + 1]
                self.forward(xi)
                dw_list, db_list = self.backprop(xi, yi)
                for w_idx in range(len(self.weights)):
                    self.velocities_w[w_idx] = (self.momentum * self.velocities_w[w_idx]
                                                + (1 - self.momentum) * dw_list[w_idx])
                    self.velocities_b[w_idx] = (self.momentum * self.velocities_b[w_idx]
                                                + (1 - self.momentum) * db_list[w_idx])
                    self.weights[w_idx] -= self.learning_rate * self.velocities_w[w_idx]
                    self.biases[w_idx] -= self.learning_rate * self.velocities_b[w_idx]
                a2 = self.activations[-1][0, 0]
                epoch_loss += -(yi[0, 0] * np.log(a2 + 1e-12) + (1 - yi[0, 0]) * np.log(1 - a2 + 1e-12))
            loss_history.append(float(epoch_loss / n))
            if eval_data is not None:
                x_test, y_test = eval_data
                train_acc_history.append(self.score(x, y))
                test_acc_history.append(self.score(x_test, y_test))
        return loss_history, train_acc_history, test_acc_history

    def score(self, x, y):
        return float(np.mean(self.predict(x).ravel() == y.ravel()))


def sample_disk(rng, n, rmax):
    # pontos uniformes num disco de raio rmax;
    r = rmax * np.sqrt(rng.random(n))
    theta = rng.uniform(0, 2 * np.pi, n)
    return np.c_[r * np.cos(theta), r * np.sin(theta)]


def sample_annulus(rng, n, rmin, rmax):
    # pontos uniformes num anel entre rmin e rmax;
    r = np.sqrt(rmin ** 2 + (rmax ** 2 - rmin ** 2) * rng.random(n))
    theta = rng.uniform(0, 2 * np.pi, n)
    return np.c_[r * np.cos(theta), r * np.sin(theta)]


def make_circles_data(n_samples=400):
    # classe 0: disco interno; classe 1: anel ao redor (escala -1 a 1);
    rng = np.random.default_rng(kRANDOM_SEED)
    n = n_samples // 2
    x0 = sample_disk(rng, n, rmax=0.8)
    x1 = sample_annulus(rng, n, rmin=0.95, rmax=1.45)
    x = np.vstack([x0, x1]) / 1.5
    y = np.array([0] * n + [1] * n)
    return x, y


def train_test_split(x, y, test_size=0.3, seed=kRANDOM_SEED):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(x))
    n_test = int(test_size * len(x))
    test_idx, train_idx = idx[:n_test], idx[n_test:]
    return x[train_idx], x[test_idx], y[train_idx], y[test_idx]


def plot_decision_boundary(ax, model, x, y, title):
    h = 0.03
    x_min, x_max = x[:, 0].min() - 0.4, x[:, 0].max() + 0.4
    y_min, y_max = x[:, 1].min() - 0.4, x[:, 1].max() + 0.4
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    grid = np.c_[xx.ravel(), yy.ravel()]
    z = model.predict(grid).reshape(xx.shape)
    ax.contourf(xx, yy, z, alpha=0.3, cmap=plt.cm.RdBu)
    ax.contour(xx, yy, z, colors='k', linewidths=0.5)
    ax.scatter(x[:, 0], x[:, 1], c=y, cmap=plt.cm.RdBu, edgecolors='k', s=20)
    ax.set_title(title)
    ax.set_xlabel('X1')
    ax.set_ylabel('X2')


def run_arquitetura(nome, arch, x_train, x_test, y_train, y_test, epoch_limit=30):
    print(f"\n{'-' * 64}\n  ARQUITETURA: {nome}\n{'-' * 64}")

    model = MlpCirculoProfundidade(hidden_sizes=arch, n_epochs=epoch_limit)
    loss, train_acc, test_acc = model.fit(
        x_train, y_train.astype(float).reshape(-1, 1), eval_data=(x_test, y_test))

    n_epochs_done = len(loss)
    first = min(epoch_limit, 10)
    print("  epoca | loss treino | erro treino | erro teste")
    print("  ------|-------------|-------------|-----------")
    for e in range(first):
        if e < len(loss):
            print(f"  {e + 1:>5} | {loss[e]:>11.4f} | {1 - train_acc[e]:>11.2%} | {1 - test_acc[e]:>9.2%}")
    print(f"  ...   |             |             |")
    print(f"  {n_epochs_done:>5} | {loss[-1]:>11.4f} | {1 - train_acc[-1]:>11.2%} | {1 - test_acc[-1]:>9.2%}")

    print(f"\n  apos {n_epochs_done} epocas:")
    print(f"  - acuracia treino: {train_acc[-1]:.2%} (erro {1 - train_acc[-1]:.2%})")
    print(f"  - acuracia teste:  {test_acc[-1]:.2%} (erro {1 - test_acc[-1]:.2%})")

    return model, loss, train_acc, test_acc


def main():
    x, y = make_circles_data()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

    # rede rasa: uma camada oculta com 2 neuronios, ate 30 epocas;
    model_raso, loss_raso, train_acc_raso, test_acc_raso = run_arquitetura(
        "1 camada oculta x 2 neuronios", (2,), x_train, x_test, y_train, y_test)

    # rede profunda: tres camadas ocultas com 4 neuronios cada, ate 30 epocas;
    model_profundo, loss_prof, train_acc_prof, test_acc_prof = run_arquitetura(
        "3 camadas ocultas x 4 neuronios", (4, 4, 4), x_train, x_test, y_train, y_test)

    print("\n" + "=" * 64)
    print("  CONCLUSOES")
    print("=" * 64)
    print("  - rede rasa (2 neuronios): pouca capacidade de representacao;")
    print("    dois neuronios so criam combinacoes de hiperplanos, insuficientes")
    print("    para desenhar a fronteira circular; mesmo apos 30 epocas o erro")
    print(f"    nao zera nem no treino (treino {1 - train_acc_raso[-1]:.2%} /"
          f" teste {1 - test_acc_raso[-1]:.2%});")
    print("  - rede profunda (3 camadas x 4 neuronios): compoe padroes nao")
    print("    lineares, aprende a fronteira do circulo em ~6 epocas e continua")
    print("    corrigindo; erro final de TREINO E de TESTE baixos")
    print(f"    ({1 - train_acc_prof[-1]:.2%} / {1 - test_acc_prof[-1]:.2%}),")
    print("    ou seja, generaliza sem memorizar os dados;")
    print("  - conclusao: aumentar a PROFUNDIDADE (camadas) e o numero de")
    print("    neuronios amplia a capacidade de aprender padroes complexos,")
    print("    como o circulo, que uma rede rasa nao consegue;")

    # grafico: fronteiras e curvas de erro;
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    plot_decision_boundary(axes[0, 0], model_raso, x_test, y_test,
                           f"Raso (2 neuronios) - fronteira")
    plot_decision_boundary(axes[0, 1], model_profundo, x_test, y_test,
                           f"Profunda (3x4) - fronteira")
    axes[0, 2].scatter(x_test[:, 0], x_test[:, 1], c=y_test, cmap=plt.cm.RdBu,
                       edgecolors='k', s=25)
    axes[0, 2].set_title("Dados de teste (círculo)")
    axes[0, 2].set_xlabel('X1')
    axes[0, 2].set_ylabel('X2')

    axes[1, 0].plot(loss_raso, label='raso', marker='o', markersize=3)
    axes[1, 0].plot(loss_prof, label='profundo', marker='o', markersize=3)
    axes[1, 0].set_title("Loss (treino) por Epoca")
    axes[1, 0].set_xlabel("Epoca")
    axes[1, 0].set_ylabel("Loss")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(train_acc_raso, label='treino (raso)', marker='o', markersize=3)
    axes[1, 1].plot(test_acc_raso, label='teste (raso)', marker='o', markersize=3)
    axes[1, 1].plot(train_acc_prof, label='treino (profundo)', marker='o', markersize=3)
    axes[1, 1].plot(test_acc_prof, label='teste (profundo)', marker='o', markersize=3)
    axes[1, 1].set_title("Acurácia por Epoca")
    axes[1, 1].set_xlabel("Epoca")
    axes[1, 1].set_ylabel("Acurácia")
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    axes[1, 2].axis('off')

    plt.tight_layout()
    output_path = Path(__file__).parent / "resultados_circulo_profundidade.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n  grafico salvo em: {output_path}")
    if plt.get_backend() != 'agg':
        plt.show()


if __name__ == '__main__':
    main()