from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


class PerceptronXorGaussiana:
    def __init__(self, n_inputs, learning_rate=0.1, n_epochs=100):
        self.weights = np.zeros(n_inputs)
        self.bias = 0.0
        self.learning_rate = learning_rate
        self.n_epochs = n_epochs
        self.best_weights = self.weights.copy()
        self.best_bias = 0.0
        self.best_errors = np.inf

    @staticmethod
    def activation(x):
        return int(x >= 0)

    def predict(self, inputs):
        return self.activation(inputs @ self.weights + self.bias)

    def fit(self, x, y):
        rng = np.random.default_rng(42)
        errors_per_epoch = []
        for epoch in range(1, self.n_epochs + 1):
            order = rng.permutation(len(x))
            errors = 0
            for xi, target in zip(x[order], y[order]):
                prediction = self.predict(xi)
                update = self.learning_rate * (target - prediction)
                self.weights += update * xi
                self.bias += update
                errors += int(update != 0.0)
            errors_per_epoch.append(errors)
            if errors < self.best_errors:
                self.best_errors = errors
                self.best_weights = self.weights.copy()
                self.best_bias = float(self.bias)
            if errors == 0:
                break
        return errors_per_epoch

    def score(self, x, y):
        predictions = (x @ self.best_weights + self.best_bias >= 0).astype(int)
        return float(np.mean(predictions == y))


def make_xor_data(n_per_class=50):
    rng = np.random.default_rng(42)
    noise = 0.02
    # 4 clusters: (0,0), (0,1), (1,0), (1,1);
    c00 = rng.normal([0, 0], noise, (n_per_class, 2))
    c01 = rng.normal([0, 1], noise, (n_per_class, 2))
    c10 = rng.normal([1, 0], noise, (n_per_class, 2))
    c11 = rng.normal([1, 1], noise, (n_per_class, 2))
    x = np.vstack([c00, c01, c10, c11])
    # xor: 0,0->0 | 0,1->1 | 1,0->1 | 1,1->0;
    y = np.array([0]*n_per_class + [1]*n_per_class + [1]*n_per_class + [0]*n_per_class)
    return x, y


def make_gaussian_data(n_per_class=100, pos_class_label=1.0):
    rng = np.random.default_rng(42)
    # two linearly separable clusters (sem overlap);
    c0 = rng.normal([-1.5, -1.5], 0.4, (n_per_class, 2))
    c1 = rng.normal([1.5, 1.5], 0.4, (n_per_class, 2))
    x = np.vstack([c0, c1])
    y = np.array([0]*n_per_class + [1]*n_per_class)
    return x, y


def plot_decision_boundary(ax, perceptron, x, y, title):
    h = 0.02
    x_min, x_max = x[:, 0].min() - 0.5, x[:, 0].max() + 0.5
    y_min, y_max = x[:, 1].min() - 0.5, x[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    grid = np.c_[xx.ravel(), yy.ravel()]
    Z = np.array([perceptron.predict(pt) for pt in grid])
    Z = Z.reshape(xx.shape)

    ax.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.RdBu)
    ax.contour(xx, yy, Z, colors='k', linewidths=0.5)
    scatter = ax.scatter(x[:, 0], x[:, 1], c=y, cmap=plt.cm.RdBu, edgecolors='k', s=20)
    ax.set_title(title)
    ax.set_xlabel('X1')
    ax.set_ylabel('X2')
    return scatter


def run_experiment(name, x, y):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    model = PerceptronXorGaussiana(n_inputs=2, learning_rate=0.1, n_epochs=100)
    errors = model.fit(x, y)

    acc = model.score(x, y)
    print(f"  epocas executadas: {len(errors)}")
    print(f"  melhor epoca: {errors.index(min(errors))+1} ({min(errors)} erros)")
    print(f"  acuracia final: {acc:.2%}")
    print(f"  pesos: {np.round(model.weights, 4)}")
    print(f"  bias:  {model.bias:.4f}")
    print(f"  resultado: {'RESOLVIDO' if acc >= 0.99 else 'NAO RESOLVIDO'}")

    return model, errors


def main():
    # --- xor ---;
    x_xor, y_xor = make_xor_data(n_per_class=50)
    model_xor, errors_xor = run_experiment("XOR (OU EXCLUSIVO)", x_xor, y_xor)

    # --- gaussiana ---;
    x_gauss, y_gauss = make_gaussian_data(n_per_class=100)
    model_gauss, errors_gauss = run_experiment("GAUSSIANA", x_gauss, y_gauss)

    # --- plot ---;
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    plot_decision_boundary(axes[0, 0], model_xor, x_xor, y_xor,
                           f"XOR - Fronteira (acuracia: {model_xor.score(x_xor, y_xor):.2%})")
    axes[0, 1].plot(errors_xor, 'o-', markersize=3)
    axes[0, 1].set_title("XOR - Erros por Epoca")
    axes[0, 1].set_xlabel("Epoca")
    axes[0, 1].set_ylabel("Erros")
    axes[0, 1].grid(True, alpha=0.3)

    plot_decision_boundary(axes[1, 0], model_gauss, x_gauss, y_gauss,
                           f"Gaussiana - Fronteira (acuracia: {model_gauss.score(x_gauss, y_gauss):.2%})")
    axes[1, 1].plot(errors_gauss, 'o-', markersize=3)
    axes[1, 1].set_title("Gaussiana - Erros por Epoca")
    axes[1, 1].set_xlabel("Epoca")
    axes[1, 1].set_ylabel("Erros")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = Path(__file__).parent / "resultados.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n  grafico salvo em: {output_path}")
    if plt.get_backend() != 'agg':
        plt.show()


if __name__ == '__main__':
    main()
