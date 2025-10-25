# Documentação da Lógica - Views Animais e Eventos

## Tipos de Eventos (`idtb_eventos_tipos`)

A seguir estão os tipos de eventos e seus IDs correspondentes.

| ID  | Descrição                     |
| --- | ----------------------------- |
| 1   | Produção Diária de Leite      |
| 2   | Desmamou Bezerro              |
| 3   | Venda de Animal               |
| 4   | Vacinação Contra Brucelose    |

## Lógica do Período Produtivo da Mãe

O período produtivo de uma vaca mãe é determinado pelo ciclo de vida de suas crias.

### Início do Período Produtivo
- O período produtivo de uma mãe **começa** na data de nascimento de sua cria.
- O nascimento de um bezerro sinaliza que a mãe começou a produzir leite.

### Fim do Período Produtivo
- O período produtivo de uma mãe **termina** quando sua cria é desmamada.
- O evento "Desmamou Bezerro" (ID 2) para uma cria indica o fim da lactação da mãe associada a essa cria.

### Caso de Exceção: Sobreposição de Crias
- **Cenário:** Uma mãe dá à luz a uma nova cria *antes* que a cria anterior tenha um evento de desmame registrado (Evento ID 2).
- **Consequência:** O período produtivo se torna ambíguo e o cálculo da produção de leite para essa mãe torna-se impossível de determinar com precisão.
- **Ação no Sistema:** A interface deve indicar visualmente essa inconsistência. Ela deve sinalizar que o cálculo não é possível e informar o motivo: "Falta documentar o desmame do filho anterior."

## Lógica de Cálculo da Produção de Leite

A produção de leite é calculada individualmente para cada animal, mês a mês. A interface pode então agregar esses dados conforme necessário.

### Gatilho e Valor Base
- A base para o cálculo é a **média dos valores** de todos os eventos de "Produção Diária de Leite" (ID 1) registrados para uma vaca dentro de um determinado mês.
- Se não houver eventos de produção no mês, a produção para aquele mês é zero.

### Cálculo dos Dias Produtivos no Mês
O número de dias produtivos dentro de um mês é ajustado com base nos eventos de nascimento e desmame da cria associada.

1.  **Cenário Padrão:** Se a lactação da mãe já havia começado antes do início do mês e terminou depois do fim do mês, o número de dias produtivos é simplesmente o **número total de dias no mês**.

2.  **Mês do Nascimento:** Se a cria nasceu durante o mês em questão, os dias produtivos são contados a partir da **data de nascimento** até o último dia do mês.

3.  **Mês do Desmame:** Se a cria foi desmamada durante o mês, os dias produtivos são contados desde o **primeiro dia do mês** até o **dia anterior à data do desmame**.

4.  **Nascimento e Desmame no Mesmo Mês:** Se a cria nasceu e foi desmamada dentro do mesmo mês, os dias produtivos são o intervalo entre a **data de nascimento** e o **dia anterior ao desmame**.

### Fórmula Final
A produção total de leite de uma vaca em um determinado mês é:

`Produção Mensal = (Média dos valores dos eventos de produção no mês) * (Número de dias produtivos no mês)`
