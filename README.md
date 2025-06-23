# Trabalho Prático 1: Implementação da Árvore-B com Design by Contracts

**Curso:** FGA0242 - Técnicas de Programação para Plataformas Emergentes  

| Aluno          | Matrícula     |
| ------------------------- |:-------------:|
| José Filipi Brito Souza  | 202063346    |
| Renan Rodrigues Lacerda  | 190048191    |
| Guilherme Basílio do Espírito Santo | 160007615   |

## 1. Visão Geral do Projeto

Este trabalho apresenta uma implementação completa e funcional da estrutura de dados **Árvore-B** em Python. O principal objetivo é demonstrar o funcionamento das operações de inserção, remoção e busca, garantindo a corretude e a robustez do código através do paradigma de **Design by Contracts (DbC)**.

Para aplicar o DbC, foi utilizada a biblioteca `icontract`, que permite definir pré-condições, pós-condições e invariantes de forma declarativa, tornando o código mais seguro e auto-documentado.

## 2. Estrutura do Código

O código está organizado em duas classes principais e um bloco de demonstração:

- **`BTreeNode`**: Uma classe simples que representa um nó da Árvore-B. Cada nó contém uma lista de chaves (`keys`), uma lista de filhos (`children`) e um booleano (`leaf`) que indica se é um nó folha.

- **`BTree`**: A classe principal que encapsula toda a lógica da Árvore-B. Ela gerencia o nó raiz (`root`), a ordem da árvore (`t`) e implementa todos os métodos necessários para as operações.

- **Bloco de Demonstração (`if __name__ == "__main__"`)**: Uma interface de linha de comando (CLI) interativa que permite ao usuário testar as funcionalidades da árvore, como inserir, remover, buscar chaves e visualizar a estrutura atual da árvore.

## 3. Conceitos Aplicados

### 3.1. Árvore-B

A Árvore-B é uma estrutura de dados de árvore de busca auto-balanceada, otimizada para sistemas que lidam com grandes volumes de dados, como bancos de dados e sistemas de arquivos. Suas principais características, implementadas neste trabalho, são:

- Mantém os dados sempre ordenados.
- Todas as folhas estão na mesma profundidade.
- O número de chaves e filhos em cada nó obedece a regras estritas definidas pela ordem `t` da árvore.
- As operações de inserção e remoção incluem mecanismos de balanceamento, como a divisão (`split`) de nós cheios e a fusão (`merge`) ou empréstimo (`borrow`) em nós com poucas chaves.

### 3.2. Design by Contracts (DbC)

O Design by Contracts foi aplicado para garantir a corretude do código em tempo de execução. Os seguintes tipos de contratos foram usados:

- **Pré-condições (`@icontract.require`)**: Condições que devem ser verdadeiras *antes* da execução de um método.
  - Ex: Para inserir uma chave, ela não pode já existir na árvore (`search(k) is None`).
  - Ex: Para remover uma chave, ela deve existir na árvore (`search(k) is not None`).

- **Pós-condições (`@icontract.ensure`)**: Condições que devem ser verdadeiras *após* a execução de um método.
  - Ex: Após uma inserção ou remoção, as regras estruturais (número de chaves/filhos por nó) devem continuar válidas.

- **Invariantes (`@icontract.invariant`)**: Condições que devem ser verdadeiras para a instância da classe *sempre* que ela estiver em um estado estável (antes e depois de qualquer chamada de método público).
  - Ex: Todas as folhas devem estar no mesmo nível.
  - Ex: As chaves em cada nó devem estar sempre ordenadas.
  - Ex: Todas as chaves em uma subárvore à esquerda de `chave[i]` devem ser menores que `chave[i]`.

## 4. Funcionalidades

O programa oferece um menu interativo com as seguintes opções:

1.  **Inserir chave**: Adiciona um valor numérico à árvore, realizando o balanceamento se necessário.
2.  **Remover chave**: Exclui um valor existente, garantindo que a árvore permaneça balanceada.
3.  **Buscar chave**: Verifica se uma chave existe na árvore e informa o resultado.
4.  **Exibir árvore**: Imprime uma representação textual da árvore, mostrando as chaves em cada nó, nível por nível.
5.  **Sair**: Encerra o programa.

## 5. Como Executar o Programa

Para executar e testar a implementação, siga os passos abaixo:

1.  **Pré-requisitos**: Certifique-se de ter o Python 3 instalado em seu sistema.

2.  **Instalar Dependências**: O projeto utiliza a biblioteca `icontract`. Instale-a usando o pip:
    ```bash
    pip install icontract
    ```

3.  **Salvar o Código**: Salve o código-fonte fornecido em um arquivo Python, por exemplo, `trabalho_b_tree.py`.

4.  **Executar o Script**: Abra um terminal ou prompt de comando, navegue até o diretório onde você salvou o arquivo e execute o seguinte comando:
    ```bash
    python trabalho_b_tree.py
    ```

5.  **Interagir com o Menu**: O menu interativo será exibido no terminal. Escolha as opções digitando o número correspondente e pressionando Enter. O programa irá validar as entradas e as regras da Árvore-B, exibindo mensagens de sucesso, erro ou violação de contrato.