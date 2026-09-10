# Perceptron XOR e Gaussiana

Simula uma perceptron simples (sem camadas ocultas) nas tarefas de classificação **XOR (ou exclusivo)** e **Gaussiana**, como no TensorFlow Playground;

---

## Como rodar

- instale as dependências:
    - `pip install numpy matplotlib`;
- execute o script:
    - `python perceptron_xor_gaussiana.py`;

---

## O que acontece

- **XOR**:
    - a perceptron não consegue resolver o problema (não é linearmente separável), ficando ~37% de acurácia;
- **Gaussiana**:
    - a perceptron resolve perfeitamente (100% de acurácia) em poucas épocas, pois as classes são separáveis por uma reta;

Ao final, um gráfico com as fronteiras de decisão e as curvas de erros por época é salvo em `resultados.png` (na mesma pasta);

---

- formatted with: markdown_formatting_guide_v1.md, date: 20260910;