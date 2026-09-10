# MLP no TensorFlow Playground

Simulações baseadas nos experimentos do TensorFlow Playground (http://playground.tensorflow.org) em tarefas de classificação com entradas **X1** e **X2**;

---

## Como rodar

- instale as dependências:
    - `pip install numpy matplotlib`;
- execute um dos casos abaixo;

---

## Casos e arquivos

| Caso | Arquivo | Descrição |
| :--- | :--- | :--- |
| **Caso 1** | `perceptron_xor_gaussiana.py` | Perceptron simples (sem camadas ocultas) nas tarefas **XOR** e **Gaussiana**; mostra que ela só resolve o que é linearmente separável; |
| **Caso 2** | `mlp_xor_ativacoes.py` | MLP com camada oculta de **6 neurônios** no problema **XOR**; compara as ativações **sigmoid**, **tanh**, **relu** e **linear**; apenas a linear não resolve, pois rede linear composta continua linear; |
| **Caso 3** | `mlp_gaussiana_camadas.py` | Classificação com dados gaussianos (**30% para teste**); mostra como melhorar o aprendizado de padrões complexos (profundidade, neurônios, regularização) e o que cada camada aprende; |
| **Caso 4** | `mlp_circulo_profundidade.py` | Dados do tipo **círculo** (disco e anel) com **30 épocas**: rede rasa (**1 camada x 2 neurônios**) não consegue desenhar a fronteira circular; rede **3 camadas x 4 neurônios** resolve com erro de teste ~1%; |
| **Caso 5** | `mlp_espiral_profundidade.py` | Dados em **espiral** com **100 épocas**: observa-se que a rede **3 camadas x 4 neurônios** quase resolve a espiral (erro de teste ~2%); com **16 neurônios por camada** o erro cai para ~1%; sem overfitting relevante; |

---

## O que acontece em cada caso

- **Caso 1**:
    - XOR:
        - não resolvido (~37% de acurácia), pois não é linearmente separável;
    - Gaussiana:
        - resolvido (100% de acurácia), pois as classes são separáveis por uma reta;
- **Caso 2**:
    - com a camada oculta, **sigmoid**, **tanh** e **relu** resolvem o XOR (100%);
    - **linear** não resolve (~52%): a composição de funções lineares é linear, logo a rede equivale a uma perceptron simples;
- **Caso 3**:
    - dados gaussianos separáveis: ~100% de acurácia no treino e no teste;
    - padrões complexos (anéis): sem camada oculta ~68% no teste; com profundidade e mais neurônios chega a 100%;
    - **upper layers** aprendem os padrões mais complexos, pois combinam os padrões simples das camadas mais baixas e produzem representações mais abstratas e separáveis;
- **Caso 4**:
    - rede rasa (1 camada x 2 neurônios): erro de treino ~21% e de teste ~22% após 30 épocas; não aprende a fronteira circular mesmo no treino (capacidade insuficiente);
    - rede profunda (3 camadas x 4 neurônios): reduz o erro a ~1% no treino e ~1% no teste, generalizando bem;
    - conclusão: adicionar **profundidade** e **neurônios** amplia a capacidade de aprender padrões complexos (círculo), que a rede rasa não consegue;
- **Caso 5**:
    - rede **3 camadas x 4 neurônios** após 100 épocas: o grande salto de aprendizado acontece nas primeiras ~10 épocas e o erro de teste termina em ~2%;
    - rede **3 camadas x 16 neurônios**: com a mesma profundidade, o erro de teste cai para ~1% (largura maior generaliza um pouco melhor);
    - não há overfitting relevante (treino e teste terminam próximos), ou seja, a espiral foi realmente modelada;

---

- formatted with: markdown_formatting_guide_v1.md, date: 20260910;