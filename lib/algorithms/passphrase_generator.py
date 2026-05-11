def passphrase_generator(n):

    '''
    o algoritmo recebe um número inteiro positivo n, calcula o resto da divisão de n + 1 por 7 para determinar um índice inicial em uma lista fixa de 7 strings (s0 a s6), seleciona sequencialmente três strings a partir desse índice (com recomeço circular ao atingir o final da lista) e retorna uma string concatenando todas as 7 strings originais separadas por pontos, seguidas pelas três strings selecionadas e pelo valor de n, também separados por pontos (formando uma passphrase única baseada no número de entrada);
    '''    

    s = [
        "s0", "s1", "s2", "s3", 
        "s4", "s5", "s6"
    ] # strings previamente conhecidas;
    
    indice_extra_0 = (n + 1) % len(s)
    indice_extra_1 = (indice_extra_0 + 1) % len(s)
    indice_extra_2 = (indice_extra_1 + 1) % len(s)

    s_selecionada_0 = s[indice_extra_0]
    s_selecionada_1 = s[indice_extra_1]
    s_selecionada_2 = s[indice_extra_2]
    
    cadeia_principal = ".".join(s) + "." + s_selecionada_0 + "." + s_selecionada_1 + "." + s_selecionada_2 + "." + str(n)
    
    return cadeia_principal

try:
    entrada_n = int(input("digite o valor de n (inteiro positivo): "))
    
    if entrada_n < 0:
        print("erro: o sistema não aceita números negativos;")
    else:
        resultado = passphrase_generator(entrada_n)
        print("-" * 30)
        print(f"resultado: {resultado};")
        print("-" * 30)
    
except ValueError:
    print("por favor, insira apenas números inteiros;")

