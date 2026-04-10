import numpy as np # biblioteca numpy;
import matplotlib.pyplot as plt # biblioteca matplotlib;

kA = 0 # coeficiente a;
kB = 7 # coeficiente b;

def plotCurve(): # método para plotar;
    x_range = np.linspace(-3, 30, 1000) # faixa de x;
    y_squared = x_range**3 + kA * x_range + kB # equação da curva;

    mask_valid = y_squared >= 0 # máscara de validação;
    x_valid = x_range[mask_valid] # x válidos;
    y_positive = np.sqrt(y_squared[mask_valid]) # y positivos;
    y_negative = -y_positive # y negativos;

    plt.figure(figsize=(8, 6)) # configurar figura;
    plt.axis('equal') # mesma escala nos eixos;
    plt.plot(x_valid, y_positive, color='orange', label='y² = x³ + 7') # plotar parte superior;
    plt.plot(x_valid, y_negative, color='orange') # plotar parte inferior;
    
    plt.axhline(0, color='black', linewidth=0.5) # linha horizontal;
    plt.axvline(0, color='black', linewidth=0.5) # linha vertical;
    plt.grid(True, linestyle='--', alpha=0.7) # grade do gráfico;
    plt.title('curva elíptica secp256k1') # título;
    plt.xlabel('x') # label x;
    plt.ylabel('y') # label y;
    plt.legend() # legenda;
    plt.show() # exibir;

if __name__ == "__main__": # execução principal;
    plotCurve() # chamar função;
