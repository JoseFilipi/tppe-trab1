# FGA0242 - Técnicas de Programação para Plataformas Emergentes
# Trabalho Prático 1: Implementação da Árvore-B com Design by Contracts


import icontract
from typing import List, Optional, Tuple
from collections import deque

# -----------------------------------------------------------------------------
# 1. Classe BTreeNode
#    Representa um nó na Árvore-B.
# -----------------------------------------------------------------------------
class BTreeNode:
    """
    Um nó em uma Árvore-B.

    Atributos:
        leaf (bool): True se o nó for uma folha, False caso contrário.
        keys (List[int]): A lista de chaves armazenadas no nó.
        children (List[BTreeNode]): A lista de nós filhos.
    """
    def __init__(self, leaf: bool = False):
        """Inicializa um novo nó da Árvore-B."""
        self.leaf, self.keys, self.children = leaf, [], []

# -----------------------------------------------------------------------------
# 2. Classe BTree
#    Implementa a estrutura de dados Árvore-B e suas operações.
# -----------------------------------------------------------------------------

# --- Funções Auxiliares para Contratos ---
# Estas funções são usadas pelos decoradores do `icontract` para verificar
# as propriedades da Árvore-B.

def _check_node_key_count(node: BTreeNode, t: int, is_root: bool) -> bool:
    """Verifica se o número de chaves em um nó está dentro dos limites da Árvore-B."""
    # A raiz pode estar vazia (árvore vazia) ou ter de 1 a 2t-1 chaves.
    # Nós internos devem ter entre t-1 e 2t-1 chaves.
    if not node.keys and is_root and node.leaf: return True # Árvore vazia
    min_keys = 1 if is_root else t - 1
    max_keys = 2 * t - 1
    return min_keys <= len(node.keys) <= max_keys

def _check_node_child_count(node: BTreeNode, t: int, is_root: bool) -> bool:
    """Verifica se o número de filhos de um nó está correto."""
    if node.leaf:
        return len(node.children) == 0 # Nós folha não têm filhos.
    # Um nó interno deve ter len(keys) + 1 filhos.
    if len(node.children) != len(node.keys) + 1:
        return False
    # A raiz pode ter de 2 a 2t filhos se não for folha.
    # Nós internos devem ter de t a 2t filhos.
    min_children = 2 if is_root else t
    max_children = 2 * t
    return min_children <= len(node.children) <= max_children

def _check_keys_sorted(keys: List[int]) -> bool:
    """Verifica se as chaves em uma lista estão ordenadas crescentemente."""
    return all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1))

@icontract.invariant(
    lambda self: self._check_all_invariants() and self._check_postcondition_hack(),
    description="Verifica as invariantes e as pós-condições simuladas da Árvore-B"
)
class BTree:
    """
    Implementação da Árvore-B com Design by Contracts.

    Atributos:
        root (BTreeNode): O nó raiz da árvore.
        t (int): A ordem (grau mínimo) da árvore.
    """
    def __init__(self, t: int):
        """
        Inicializa a Árvore-B.

        Args:
            t (int): A ordem da árvore, que deve ser no mínimo 2.
        
        Raises:
            ValueError: Se 't' for menor que 2.
        """
        if t < 2:
            raise ValueError("A ordem 't' da Árvore-B deve ser no mínimo 2.")
        self.root = BTreeNode(leaf=True)
        self.t = t
        # Atributos para simular pós-condições usando a invariante
        self._op_in_progress = None
        self._state_before_op = {}

    def _check_postcondition_hack(self) -> bool:
        """
        Simula a verificação de pós-condições usando o mecanismo de invariantes.
        A invariante é verificada no final de cada método público. Esta função
        compara o estado atual com o estado salvo antes da operação.
        """
        if not self._op_in_progress:
            return True # Nenhuma operação em andamento.

        op_name, state = self._op_in_progress, self._state_before_op
        # Limpa o estado para a próxima verificação de invariante.
        self._op_in_progress, self._state_before_op = None, {}

        # Pós-condição para inserção: a altura aumenta em 1 se a raiz estava cheia.
        if op_name == 'insert':
            if not (not (state["root_keys_len"] == 2 * self.t - 1) or self.get_height() == state["height"] + 1):
                return False
        # Pós-condição para remoção: a altura diminui em 1 se a raiz ficou vazia e não era folha.
        elif op_name == 'delete':
            if not (not (state["root_keys_len"] == 1 and not state["root_is_leaf"]) or self.get_height() == state["height"] - 1):
                return False
        return True

    @icontract.require(lambda self, k: self.search(k) is None, "A chave a ser inserida não deve existir na árvore.")
    @icontract.ensure(lambda self: self._check_structural_postconditions(), "A estrutura da árvore deve ser válida após a inserção.")
    def insert(self, k: int):
        """
        Insere uma chave na Árvore-B.

        Args:
            k (int): A chave a ser inserida.
        """
        # Salva o estado para a verificação da pós-condição.
        self._op_in_progress = 'insert'
        self._state_before_op = {"height": self.get_height(), "root_keys_len": len(self.root.keys)}
        
        root = self.root
        # Se a raiz estiver cheia, a árvore cresce em altura.
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode()
            self.root = new_root
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, k)
        else:
            self._insert_non_full(root, k)

    @icontract.require(lambda self, k: self.search(k) is not None, "A chave a ser removida deve existir na árvore.")
    @icontract.ensure(lambda self: self._check_structural_postconditions(), "A estrutura da árvore deve ser válida após a remoção.")
    def delete(self, k: int):
        """
        Remove uma chave da Árvore-B.

        Args:
            k (int): A chave a ser removida.
        """
        # Salva o estado para a verificação da pós-condição.
        self._op_in_progress = 'delete'
        self._state_before_op = {
            "height": self.get_height(),
            "root_keys_len": len(self.root.keys),
            "root_is_leaf": self.root.leaf
        }
        
        self._delete_recursive(self.root, k)

        # Se a raiz ficar sem chaves após a remoção e não for uma folha,
        # a altura da árvore diminui.
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _check_all_invariants(self) -> bool:
        """Verifica todas as invariantes da Árvore-B."""
        if not self.root: return True
        # Invariante 1: Todas as folhas devem estar na mesma profundidade.
        leaf_depths = self._get_all_leaf_depths()
        if len(set(leaf_depths)) > 1:
            return False
        # Invariante 2: Propriedades dos nós (chaves ordenadas, particionamento).
        return self._check_node_properties_recursively(self.root)

    def _get_all_leaf_depths(self) -> List[int]:
        """Retorna uma lista com as profundidades de todas as folhas (usando BFS)."""
        if not self.root or (not self.root.keys and self.root.leaf): return [0]
        depths, q = [], deque([(self.root, 0)])
        while q:
            node, depth = q.popleft()
            if node.leaf:
                depths.append(depth)
            for child in node.children:
                q.append((child, depth + 1))
        return depths

    def _check_node_properties_recursively(self, node: BTreeNode) -> bool:
        """Verifica recursivamente as propriedades de cada nó."""
        # Propriedade 1: Chaves dentro de um nó devem estar ordenadas.
        if not _check_keys_sorted(node.keys): return False
        
        if not node.leaf:
            # Propriedade 2: Chaves na subárvore à esquerda de uma chave[i] devem ser menores que chave[i].
            # Chaves na subárvore à direita devem ser maiores.
            for i in range(len(node.keys)):
                for key_in_left_subtree in self._get_all_keys(node.children[i]):
                    if key_in_left_subtree >= node.keys[i]: return False
                for key_in_right_subtree in self._get_all_keys(node.children[i+1]):
                    if key_in_right_subtree <= node.keys[i]: return False
            
            # Verifica as propriedades para todos os filhos.
            for child in node.children:
                if not self._check_node_properties_recursively(child): return False
        return True
    
    def _check_structural_postconditions(self) -> bool:
        """Verifica as regras estruturais (contagem de chaves/filhos) para todos os nós."""
        if not self.root: return True
        q = deque([(self.root, True)]) # Fila com (nó, é_raiz_flag)
        while q:
            node, is_root = q.popleft()
            if not _check_node_key_count(node, self.t, is_root): return False
            if not _check_node_child_count(node, self.t, is_root): return False
            for child in node.children:
                q.append((child, False))
        return True

    def search(self, k: int) -> Optional[Tuple[BTreeNode, int]]:
        """
        Busca por uma chave na Árvore-B.

        Args:
            k (int): A chave a ser procurada.

        Returns:
            Optional[Tuple[BTreeNode, int]]: Uma tupla (nó, índice) se a chave for encontrada,
                                             None caso contrário.
        """
        return self._search_recursive(self.root, k)

    def _search_recursive(self, x: BTreeNode, k: int) -> Optional[Tuple[BTreeNode, int]]:
        """Função auxiliar recursiva para a busca."""
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if i < len(x.keys) and k == x.keys[i]:
            return (x, i)
        if x.leaf:
            return None
        return self._search_recursive(x.children[i], k)

    def _insert_non_full(self, x: BTreeNode, k: int):
        """Insere uma chave 'k' em um nó 'x' que não está cheio."""
        i = len(x.keys) - 1
        if x.leaf:
            # Insere a chave na posição correta em um nó folha.
            x.keys.append(0) # Espaço temporário
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:
            # Encontra o filho correto para descer na árvore.
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            # Se o filho estiver cheio, divide-o.
            if len(x.children[i].keys) == 2 * self.t - 1:
                self._split_child(x, i)
                # Decide em qual dos novos filhos a chave deve ser inserida.
                if k > x.keys[i]:
                    i += 1
            self._insert_non_full(x.children[i], k)

    def _split_child(self, x: BTreeNode, i: int):
        """
        Divide um filho cheio 'y' do nó 'x'.

        Args:
            x (BTreeNode): O nó pai (que não está cheio).
            i (int): O índice do filho cheio em x.children.
        """
        t = self.t
        y = x.children[i]
        z = BTreeNode(leaf=y.leaf)
        
        # Move a chave mediana de 'y' para 'x'.
        x.children.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        
        # Move as chaves e filhos maiores de 'y' para o novo nó 'z'.
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

    def _delete_recursive(self, x: BTreeNode, k: int):
        """Função recursiva para remover uma chave."""
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i]: i += 1

        # Caso 1: A chave está no nó 'x'.
        if i < len(x.keys) and x.keys[i] == k:
            if x.leaf:
                x.keys.pop(i) # Remove de um nó folha.
            else:
                self._delete_from_internal_node(x, i) # Remove de um nó interno.
        # Caso 2: A chave não está em 'x', desce para o filho apropriado.
        else:
            if x.leaf:
                return # Chave não encontrada.
            
            child_idx = i
            # Se o filho tem poucas chaves (underflow), corrige antes de descer.
            if len(x.children[child_idx].keys) < t:
                self._fill_child(x, child_idx)
            
            # Após o ajuste, o filho pode ter sido mesclado, ajustando o índice.
            if child_idx > len(x.keys):
                self._delete_recursive(x.children[child_idx - 1], k)
            else:
                self._delete_recursive(x.children[child_idx], k)

    def _delete_from_internal_node(self, x: BTreeNode, i: int):
        """Trata a remoção de uma chave de um nó interno."""
        t, k = self.t, x.keys[i]

        # Caso 2a: O filho esquerdo (predecessor) tem chaves suficientes.
        if len(x.children[i].keys) >= t:
            pred = self._get_predecessor(x.children[i])
            x.keys[i] = pred
            self._delete_recursive(x.children[i], pred)
        # Caso 2b: O filho direito (sucessor) tem chaves suficientes.
        elif len(x.children[i+1].keys) >= t:
            succ = self._get_successor(x.children[i+1])
            x.keys[i] = succ
            self._delete_recursive(x.children[i+1], succ)
        # Caso 2c: Ambos os filhos têm o mínimo de chaves. Mescla os dois.
        else:
            self._merge_children(x, i)
            self._delete_recursive(x.children[i], k)
            
    def _fill_child(self, x: BTreeNode, i: int):
        """
        Garante que o filho x.children[i] tenha pelo menos 't' chaves.
        Isso é feito pegando emprestado de um irmão ou mesclando.
        """
        t = self.t
        # Tenta pegar emprestado do irmão esquerdo.
        if i != 0 and len(x.children[i - 1].keys) >= t:
            self._borrow_from_prev(x, i)
        # Tenta pegar emprestado do irmão direito.
        elif i != len(x.keys) and len(x.children[i + 1].keys) >= t:
            self._borrow_from_next(x, i)
        # Se não puder emprestar, mescla com um irmão.
        else:
            if i != len(x.keys):
                self._merge_children(x, i)
            else:
                self._merge_children(x, i - 1)

    def _borrow_from_prev(self, x: BTreeNode, i: int):
        """Pega uma chave emprestada do irmão esquerdo."""
        child, sibling = x.children[i], x.children[i - 1]
        # A chave do pai desce para o filho, a chave do irmão sobe para o pai.
        child.keys.insert(0, x.keys[i - 1])
        x.keys[i - 1] = sibling.keys.pop()
        # Move o filho correspondente do irmão, se não for folha.
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

    def _borrow_from_next(self, x: BTreeNode, i: int):
        """Pega uma chave emprestada do irmão direito."""
        child, sibling = x.children[i], x.children[i + 1]
        # A chave do pai desce para o filho, a chave do irmão sobe para o pai.
        child.keys.append(x.keys[i])
        x.keys[i] = sibling.keys.pop(0)
        # Move o filho correspondente do irmão, se não for folha.
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    def _merge_children(self, x: BTreeNode, i: int):
        """
        Mescla o filho x.children[i] com seu irmão direito x.children[i+1].
        A chave correspondente do pai desce para o nó mesclado.
        """
        child, sibling = x.children[i], x.children[i + 1]
        
        # A chave do pai desce para o filho esquerdo.
        child.keys.append(x.keys.pop(i))
        # As chaves e filhos do irmão direito são movidos para o filho esquerdo.
        child.keys.extend(sibling.keys)
        child.children.extend(sibling.children)
        
        # Remove o irmão direito da lista de filhos do pai.
        x.children.pop(i + 1)

    def _get_predecessor(self, x: BTreeNode) -> int:
        """Encontra a chave predecessora (maior chave na subárvore esquerda)."""
        while not x.leaf:
            x = x.children[-1]
        return x.keys[-1]

    def _get_successor(self, x: BTreeNode) -> int:
        """Encontra a chave sucessora (menor chave na subárvore direita)."""
        while not x.leaf:
            x = x.children[0]
        return x.keys[0]

    def _get_all_keys(self, node: Optional[BTreeNode]) -> List[int]:
        """Retorna todas as chaves em uma subárvore (usado para verificação de invariantes)."""
        if not node: return []
        keys, q = [], deque([node])
        while q:
            curr = q.popleft()
            keys.extend(curr.keys)
            for child in curr.children:
                q.append(child)
        return keys
    
    def get_height(self) -> int:
        """Calcula a altura da árvore."""
        if not self.root or self.root.leaf: return 0
        h, node = 0, self.root
        while not node.leaf:
            node = node.children[0]
            h += 1
        return h

    def print_tree(self):
        """Imprime a árvore nível por nível para visualização."""
        print("--- Árvore-B (t={}) ---".format(self.t))
        if not self.root or not self.root.keys:
            print("Árvore vazia.\n------------------------")
            return
        
        q = deque([(self.root, 0)]) # Fila para BFS: (nó, nível)
        level_nodes = {} # Dicionário para agrupar nós por nível
        
        while q:
            node, level = q.popleft()
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node.keys)
            for child in node.children:
                q.append((child, level + 1))
        
        # Imprime os níveis ordenadamente.
        for level, nodes in sorted(level_nodes.items()):
            print(f"Nível {level}: {nodes}")
        print("------------------------")

# -----------------------------------------------------------------------------
# Bloco de Demonstração
# Oferece uma interface de linha de comando para interagir com a Árvore-B.
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Códigos ANSI para cores no terminal, melhorando a legibilidade.
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

    print(f"{BOLD}{CYAN}Iniciando a demonstração da Árvore-B.{RESET}")
    # Define a ordem 't' da árvore. t=3 significa que cada nó pode ter entre 2 e 5 chaves.
    t = 3 
    b_tree = BTree(t=t)
    
    def menu():
        """Exibe o menu de opções para o usuário."""
        print(f"\n{BOLD}{BLUE}--- MENU ÁRVORE-B ---{RESET}")
        print(f"{YELLOW}1. Inserir chave{RESET}")
        print(f"{YELLOW}2. Remover chave{RESET}")
        print(f"{YELLOW}3. Buscar chave{RESET}")
        print(f"{YELLOW}4. Exibir árvore{RESET}")
        print(f"{YELLOW}5. Sair{RESET}\n")
        return input(f"{BOLD}Escolha uma opção: {RESET}")

    # Loop principal do programa.
    while True:
        opcao = menu()
        if opcao == '1':
            try:
                chave = int(input(f"{BOLD}Digite a chave a inserir: {RESET}"))
                # Pré-condição verificada manualmente para dar feedback amigável ao usuário.
                # O contrato `icontract` também fará essa verificação.
                if b_tree.search(chave) is not None:
                    print(f"{YELLOW}Chave {chave} já existe na árvore. Não é possível inserir duplicatas.{RESET}")
                else:
                    b_tree.insert(chave)
                    print(f"{GREEN}Chave {chave} inserida com sucesso.{RESET}")
            except ValueError:
                print(f"{RED}Entrada inválida. Digite um número inteiro.{RESET}")
            # Captura e exibe violações de contrato detectadas pelo `icontract`.
            except icontract.errors.ViolationError as e:
                print(f"{RED}Erro de contrato ao inserir: {e}{RESET}")
        
        elif opcao == '2':
            try:
                chave = int(input(f"{BOLD}Digite a chave a remover: {RESET}"))
                # Pré-condição verificada manualmente para feedback.
                if b_tree.search(chave) is None:
                    print(f"{YELLOW}Chave {chave} não existe na árvore. Nada a remover.{RESET}")
                else:
                    b_tree.delete(chave)
                    print(f"{GREEN}Chave {chave} removida com sucesso.{RESET}")
            except ValueError:
                print(f"{RED}Entrada inválida. Digite um número inteiro.{RESET}")
            except icontract.errors.ViolationError as e:
                print(f"{RED}Erro de contrato ao remover: {e}{RESET}")

        elif opcao == '3':
            try:
                chave = int(input(f"{BOLD}Digite a chave a buscar: {RESET}"))
                resultado = b_tree.search(chave)
                if resultado:
                    print(f"{GREEN}Chave {chave} encontrada na árvore.{RESET}")
                else:
                    print(f"{YELLOW}Chave {chave} NÃO encontrada na árvore.{RESET}")
            except ValueError:
                print(f"{RED}Entrada inválida. Digite um número inteiro.{RESET}")

        elif opcao == '4':
            print(f"{CYAN}", end="")
            b_tree.print_tree()
            print(f"{RESET}", end="")

        elif opcao == '5':
            print(f"{BOLD}{BLUE}Saindo...{RESET}")
            break
        
        else:
            print(f"{RED}Opção inválida. Tente novamente.{RESET}")