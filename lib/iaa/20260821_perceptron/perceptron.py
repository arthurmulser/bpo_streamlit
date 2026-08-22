from pathlib import Path

import pandas as pd

# dataset com nota, frequencia e situacao final dos alunos;
csv_path = Path(__file__).parent / "alunos_notas_e_freq.csv"


class Perceptron:
    def __init__(self, n_inputs, learning_rate=0.01, n_epochs=100):
        # 1. inicializar pesos e bias com zeros;
        self.weights = [0.0] * n_inputs
        self.bias = 0.0
        self.learning_rate = learning_rate
        self.n_epochs = n_epochs

    @staticmethod
    def activation(x):
        # 2. funcao degrau: retorna 1 se soma ponderada >= 0, senao 0;
        return 1 if x >= 0 else 0

    def predict(self, inputs):
        # 3. propagacao: soma ponderada das entradas + bias;
        weighted_sum = sum(w * xi for w, xi in zip(self.weights, inputs)) + self.bias
        return self.activation(weighted_sum)

    def fit(self, x, y):
        # 4. treinamento pela regra do perceptron;
        errors_per_epoch = []
        for epoch in range(1, self.n_epochs + 1):
            errors = 0
            for xi, target in zip(x, y):
                prediction = self.predict(xi)
                update = self.learning_rate * (target - prediction)
                self.weights = [w + update * feature for w, feature in zip(self.weights, xi)]
                self.bias += update
                errors += int(update != 0.0)
            errors_per_epoch.append(errors)
            print(f"epoca {epoch}: {errors} erros")
            # convergiu quando nenhuma atualizacao foi necessaria;
            if errors == 0:
                break
        return errors_per_epoch


def main():
    # entradas: nota e frequencia; saida esperada: passou;
    df = pd.read_csv(csv_path)
    x = df[["nota", "frequencia"]].values.tolist()
    y = df["passou"].values

    perceptron = Perceptron(n_inputs=len(x[0]), learning_rate=0.001, n_epochs=100)
    errors = perceptron.fit(x, y)

    print("=" * 80)
    print("perceptron simples - aprovacao de alunos")
    print("=" * 80)
    print(f"epocas executadas: {len(errors)}")
    print(f"erros na ultima epoca: {errors[-1]}")
    print(f"pesos finais: {[round(float(w), 4) for w in perceptron.weights]}")
    print(f"bias final:   {perceptron.bias:.4f}")
    print("=" * 80)


if __name__ == '__main__':
    main()
