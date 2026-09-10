from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

kRANDOM_SEED = 42
kACTIVATIONS = {
    'sigmoid': (
        lambda x: 1 / (1 + np.exp(-x)),
        lambda x: (1 / (1 + np.exp(-x))) * (1 - 1 / (1 + np.exp(-x))),
    ),
    'tanh': (np.tanh, lambda x: 1 - np.tanh(x) ** 2),
    'relu': (lambda x: np.maximum(0, x), lambda x: (x > 0).astype(float)),
    'linear': (lambda x: x, lambda x: np.ones_like(x)),
}


class MlpXorAtivacoes:
    def __init__(self, n_hidden=6, activation='tanh', learning_rate=0.1, momentum=0.9, n_epochs=3000, seed=kRANDOM_SEED):
        # camadas: 2 entradas (x1, x2), camada oculta com n_hidden neuronios, 1 saida;
        self.activation = activation
        self.f, self.f_prime = kACTIVATIONS[activation]
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.n_epochs = n_epochs
        rng = np.random.default_rng(seed)
        # inicializacao Xavier para manter a variancia dos gradientes estavel;
        self.w1 = rng.normal(0, np.sqrt(2 / (2 + n_hidden)), (2, n_hidden))
        self.b1 = np.zeros(n_hidden)
        self.w2 = rng.normal(0, np.sqrt(2 / (n_hidden + 1)), (n_hidden, 1))
        self.b2 = np.zeros(1)
        # velocidades do momentum;
        self.vw1 = np.zeros_like(self.w1)
        self.vb1 = np.zeros_like(self.b1)
        self.vw2 = np.zeros_like(self.w2)
        self.vb2 = np.zeros_like(self.b2)

    def forward(self, x):
        # propagacao: entrada -> oculta (ativacao f) -> saida sigmoid;
        self.z1 = x @ self.w1 + self.b1
        self.a1 = self.f(self.z1)
        self.z2 = self.a1 @ self.w2 + self.b2
        self.a2 = kACTIVATIONS['sigmoid'][0](self.z2)
        return self.a2

    def predict(self, x):
        a2 = self.forward(x)
        return (a2 >= 0.5).astype(int)

    def backprop(self, x, y):
        # cross-entropy binaria: com sigmoid na saida o gradiente em z2 colapsa para (a2 - y);
        dz2 = (self.a2 - y) / len(x)
        dw2 = self.a1.T @ dz2
        db2 = np.sum(dz2, axis=0)
        da1 = dz2 @ self.w2.T
        dz1 = da1 * self.f_prime(self.z1)
        dw1 = x.T @ dz1
        db1 = np.sum(dz1, axis=0)
        return dw1, db1, dw2, db2

    def fit(self, x, y):
        loss_history = []
        for _ in range(self.n_epochs):
            self.forward(x)
            dw1, db1, dw2, db2 = self.backprop(x, y)
            # atualizacao com momentum;
            self.vw1 = self.momentum * self.vw1 + (1 - self.momentum) * dw1
            self.vb1 = self.momentum * self.vb1 + (1 - self.momentum) * db1
            self.vw2 = self.momentum * self.vw2 + (1 - self.momentum) * dw2
            self.vb2 = self.momentum * self.vb2 + (1 - self.momentum) * db2
            self.w1 -= self.learning_rate * self.vw1
            self.b1 -= self.learning_rate * self.vb1
            self.w2 -= self.learning_rate * self.vw2
            self.b2 -= self.learning_rate * self.vb2
            # cross-entropy binaria com sigmoid na saida;
            loss = -np.mean(y * np.log(self.a2 + 1e-12) + (1 - y) * np.log(1 - self.a2 + 1e-12))
            loss_history.append(float(loss))
        return loss_history

    def score(self, x, y):
        return float(np.mean(self.predict(x).ravel() == y.ravel()))


def make_xor_data(n_per_class=50):
    rng = np.random.default_rng(kRANDOM_SEED)
    noise = 0.02
    # 4 clusters: (0,0), (0,1), (1,0), (1,1);
    c00 = rng.normal([0, 0], noise, (n_per_class, 2))
    c01 = rng.normal([0, 1], noise, (n_per_class, 2))
    c10 = rng.normal([1, 0], noise, (n_per_class, 2))
    c11 = rng.normal([1, 1], noise, (n_per_class, 2))
    x = np.vstack([c00, c01, c10, c11])
    # XOR: 0,0->0 | 0,1->1 | 1,0->1 | 1,1->0;
    y = np.array([0] * n_per_class + [1] * n_per_class + [1] * n_per_class + [0] * n_per_class)
    return x, y


def plot_decision_boundary(ax, model, x, y, title):
    h = 0.02
    x_min, x_max = x[:, 0].min() - 0.3, x[:, 0].max() + 0.3
    y_min, y_max = x[:, 1].min() - 0.3, x[:, 1].max() + 0.3
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    grid = np.c_[xx.ravel(), yy.ravel()]
    z = model.predict(grid).reshape(xx.shape)
    ax.contourf(xx, yy, z, alpha=0.3, cmap=plt.cm.RdBu)
    ax.contour(xx, yy, z, colors='k', linewidths=0.5)
    ax.scatter(x[:, 0], x[:, 1], c=y, cmap=plt.cm.RdBu, edgecolors='k', s=20)
    ax.set_title(title)
    ax.set_xlabel('X1')
    ax.set_ylabel('X2')


def run_experiment(activation, x, y):
    print(f"\n{'-' * 60}\n  ativacao: {activation.upper()}\n{'-' * 60}")

    targets = y.astype(float).reshape(-1, 1)
    model = MlpXorAtivacoes(n_hidden=6, activation=activation)
    loss = model.fit(x, targets)
    acc = model.score(x, y)

    print(f"  epocas: {model.n_epochs}")
    print(f"  loss final: {loss[-1]:.6f}")
    print(f"  acuracia: {acc:.2%}")
    print(f"  resultado: {'RESOLVIDO' if acc >= 0.99 else 'NAO RESOLVIDO'}")
    return model, loss


def main():
    x, y = make_xor_data()

    results = {}
    for activation in ['sigmoid', 'tanh', 'relu', 'linear']:
        model, loss = run_experiment(activation, x, y)
        results[activation] = (model, loss)

    resolvidas = [a for a, (m, _) in results.items() if m.score(x, y) >= 0.99]
    nao_resolvidas = [a for a, (m, _) in results.items() if m.score(x, y) < 0.99]

    print("\n" + "=" * 60)
    print("  RESUMO - XOR com camada oculta de 6 neuronios")
    print("=" * 60)
    print(f"  resolveram o problema: {', '.join(resolvidas).upper()}")
    print(f"  nao resolveram:        {', '.join(nao_resolvidas).upper()}")
    if nao_resolvidas:
        print("  motivo: a ativacao linear composta em varias camadas resulta em")
        print("  uma funcao ainda linear (rede equivalente a uma perceptron simples)")
        print("  e o XOR nao e linearmente separavel;")
    print(f"\n  ativacoes disponiveis no playground: {', '.join(kACTIVATIONS).upper()}")

    # plot das fronteiras e curvas de loss;
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    for col, (activation, (model, loss)) in enumerate(results.items()):
        acc = model.score(x, y)
        plot_decision_boundary(axes[0, col], model, x, y,
                               f"{activation} (acuracia: {acc:.2%})")
        axes[1, col].plot(loss, linewidth=1)
        axes[1, col].set_title(f"{activation} - Loss por Epoca")
        axes[1, col].set_xlabel("Epoca")
        axes[1, col].set_ylabel("Loss")
        axes[1, col].grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = Path(__file__).parent / "resultados_ativacoes.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n  grafico salvo em: {output_path}")
    if plt.get_backend() != 'agg':
        plt.show()


if __name__ == '__main__':
    main()