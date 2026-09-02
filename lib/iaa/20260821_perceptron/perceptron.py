from pathlib import Path

import numpy as np
import pandas as pd

# dataset com nota, frequencia e situacao final dos alunos;
csv_path = Path(__file__).parent / "alunos_notas_e_freq.csv"
# semente fixa para reprodutibilidade do embaralhamento;
kRANDOM_SEED = 42


class Perceptron:
    def __init__(self, n_inputs, learning_rate=0.1, n_epochs=100):
        # 1. inicializar pesos e bias com zeros;
        self.weights = np.zeros(n_inputs)
        self.bias = 0.0
        self.learning_rate = learning_rate
        self.n_epochs = n_epochs
        # melhores parametros encontrados (pocket algorithm);
        self.best_weights = self.weights.copy()
        self.best_bias = 0.0
        self.best_errors = np.inf

    @staticmethod
    def activation(x):
        # 2. funcao degrau: retorna 1 se soma ponderada >= 0, senao 0;
        return int(x >= 0)

    def predict(self, inputs):
        # 3. propagacao: soma ponderada das entradas + bias;
        return self.activation(inputs @ self.weights + self.bias)

    def fit(self, x, y):
        # 4. treinamento pela regra do perceptron com embaralhamento por epoca;
        rng = np.random.default_rng(kRANDOM_SEED)
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
            print(
                f"epoca {epoch}: {errors} erros"
                f" | pesos: {np.round(self.weights, 4)}"
                f" | bias: {self.bias:.4f}"
            )
            # guarda os melhores parametros vistos ate agora;
            if errors < self.best_errors:
                self.best_errors = errors
                self.best_weights = self.weights.copy()
                self.best_bias = float(self.bias)
            # convergiu quando nenhuma atualizacao foi necessaria;
            if errors == 0:
                break
        return errors_per_epoch

    def score(self, x, y):
        # acuracia usando os melhores pesos armazenados;
        predictions = (x @ self.best_weights + self.best_bias >= 0).astype(int)
        return float(np.mean(predictions == y))


def main():
    df = pd.read_csv(csv_path)

    # entradas: nota e freq; saida esperada: passou;
    x_raw = df[["nota", "freq"]].to_numpy(float)
    y = df["passou"].to_numpy(float)

    # normalizacao min-max para levar as features para o intervalo [0, 1];
    x_min = x_raw.min(axis=0)
    x_range = x_raw.max(axis=0) - x_min
    x = (x_raw - x_min) / x_range

    perceptron = Perceptron(n_inputs=x.shape[1], learning_rate=0.1, n_epochs=100)
    errors = perceptron.fit(x, y)

    print("=" * 80)
    print("perceptron simples - aprovacao de alunos")
    print("=" * 80)
    print(f"epocas executadas: {len(errors)}")
    print(f"melhor epoca: {errors.index(min(errors)) + 1} ({min(errors)} erros)")
    print(f"acuracia (melhores pesos): {perceptron.score(x, y):.2%}")
    print(f"pesos finais: {np.round(perceptron.weights, 4)}")
    print(f"bias final:   {perceptron.bias:.4f}")
    print("=" * 80)


if __name__ == '__main__':
    main()
