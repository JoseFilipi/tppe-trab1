# FGA0242 - Técnicas de Programação para Plataformas Emergentes
# Trabalho Prático 1: Implementação da Árvore-B com Design by Contracts
#
# Aluno:

import icontract
from typing import List, Optional, Tuple
from collections import deque

# -----------------------------------------------------------------------------
# 1. Classe BTreeNode (Sem alterações)
# -----------------------------------------------------------------------------
class BTreeNode:
    def __init__(self, leaf: bool = False):
        self.leaf, self.keys, self.children = leaf, [], []

# -----------------------------------------------------------------------------
# 2. Classe BTree
# -----------------------------------------------------------------------------

def _check_node_key_count(node: BTreeNode, t: int, is_root: bool) -> bool:
    if not node.keys and is_root and node.leaf: return True
    min_keys = 1 if is_root else t - 1
    max_keys = 2 * t - 1
    return min_keys <= len(node.keys) <= max_keys

def _check_node_child_count(node: BTreeNode, t: int, is_root: bool) -> bool:
    if node.leaf: return len(node.children) == 0
    if len(node.children) != len(node.keys) + 1: return False
    min_children = 2 if is_root else t
    max_children = 2 * t
    return min_children <= len(node.children) <= max_children

def _check_keys_sorted(keys: List[int]) -> bool:
    return all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1))

@icontract.invariant(
    lambda self: self._check_all_invariants() and self._check_postcondition_hack(),
    description="Verifica as invariantes e as pós-condições simuladas da Árvore-B"
)
class BTree:
    def __init__(self, t: int):
        if t < 2: raise ValueError("A ordem 't' da Árvore-B deve ser no mínimo 2.")
        self.root = BTreeNode(leaf=True)
        self.t = t
        self._op_in_progress = None
        self._state_before_op = {}

    def _check_postcondition_hack(self) -> bool:
        if not self._op_in_progress:
            return True
        op_name, state = self._op_in_progress, self._state_before_op
        self._op_in_progress, self._state_before_op = None, {}

        if op_name == 'insert':
            if not (not (state["root_keys_len"] == 2 * self.t - 1) or self.get_height() == state["height"] + 1):
                return False
        elif op_name == 'delete':
            if not (not (state["root_keys_len"] == 1 and not state["root_is_leaf"]) or self.get_height() == state["height"] - 1):
                return False
        return True

    @icontract.require(lambda self, k: self.search(k) is None)
    @icontract.ensure(lambda self: self._check_structural_postconditions())
    def insert(self, k: int):
        self._op_in_progress = 'insert'
        self._state_before_op = {"height": self.get_height(), "root_keys_len": len(self.root.keys)}
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode()
            self.root = new_root
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, k)
        else:
            self._insert_non_full(root, k)

    @icontract.require(lambda self, k: self.search(k) is not None)
    @icontract.ensure(lambda self: self._check_structural_postconditions())
    def delete(self, k: int):
        self._op_in_progress = 'delete'
        self._state_before_op = {
            "height": self.get_height(),
            "root_keys_len": len(self.root.keys),
            "root_is_leaf": self.root.leaf
        }
        self._delete_recursive(self.root, k)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _check_all_invariants(self) -> bool:
        if not self.root: return True
        leaf_depths = self._get_all_leaf_depths()
        if len(set(leaf_depths)) > 1: return False
        return self._check_node_properties_recursively(self.root)

    def _get_all_leaf_depths(self) -> List[int]:
        if not self.root or (not self.root.keys and self.root.leaf): return [0]
        depths, q = [], deque([(self.root, 0)])
        while q:
            node, depth = q.popleft()
            if node.leaf: depths.append(depth)
            for child in node.children: q.append((child, depth + 1))
        return depths

    def _check_node_properties_recursively(self, node: BTreeNode) -> bool:
        if not _check_keys_sorted(node.keys): return False
        if not node.leaf:
            for i in range(len(node.keys)):
                for key_in_left_subtree in self._get_all_keys(node.children[i]):
                    if key_in_left_subtree >= node.keys[i]: return False
                for key_in_right_subtree in self._get_all_keys(node.children[i+1]):
                    if key_in_right_subtree <= node.keys[i]: return False
            for child in node.children:
                if not self._check_node_properties_recursively(child): return False
        return True
    
    def _check_structural_postconditions(self) -> bool:
        if not self.root: return True
        q = deque([(self.root, True)])
        while q:
            node, is_root = q.popleft()
            if not _check_node_key_count(node, self.t, is_root): return False
            if not _check_node_child_count(node, self.t, is_root): return False
            for child in node.children: q.append((child, False))
        return True

    def search(self, k: int) -> Optional[Tuple[BTreeNode, int]]:
        return self._search_recursive(self.root, k)

    def _search_recursive(self, x: BTreeNode, k: int) -> Optional[Tuple[BTreeNode, int]]:
        i = 0
        while i < len(x.keys) and k > x.keys[i]: i += 1
        if i < len(x.keys) and k == x.keys[i]: return (x, i)
        if x.leaf: return None
        return self._search_recursive(x.children[i], k)

    def _insert_non_full(self, x: BTreeNode, k: int):
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append(0)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:
            while i >= 0 and k < x.keys[i]: i -= 1
            i += 1
            if len(x.children[i].keys) == 2 * self.t - 1:
                self._split_child(x, i)
                if k > x.keys[i]: i += 1
            self._insert_non_full(x.children[i], k)

    def _split_child(self, x: BTreeNode, i: int):
        t = self.t
        y = x.children[i]
        z = BTreeNode(leaf=y.leaf)
        
        x.children.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t:]
        y.keys = y.keys[:t - 1]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

    def _delete_recursive(self, x: BTreeNode, k: int):
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i]: i += 1
        if i < len(x.keys) and x.keys[i] == k:
            if x.leaf: x.keys.pop(i)
            else: self._delete_from_internal_node(x, i)
        else:
            if x.leaf: return
            child_idx = i
            if len(x.children[child_idx].keys) < t:
                self._fill_child(x, child_idx)
            if child_idx > len(x.keys):
                self._delete_recursive(x.children[child_idx - 1], k)
            else:
                self._delete_recursive(x.children[child_idx], k)

    def _delete_from_internal_node(self, x: BTreeNode, i: int):
        t, k = self.t, x.keys[i]
        if len(x.children[i].keys) >= t:
            pred = self._get_predecessor(x.children[i])
            x.keys[i] = pred
            self._delete_recursive(x.children[i], pred)
        elif len(x.children[i+1].keys) >= t:
            succ = self._get_successor(x.children[i+1])
            x.keys[i] = succ
            self._delete_recursive(x.children[i+1], succ)
        else:
            self._merge_children(x, i)
            self._delete_recursive(x.children[i], k)
            
    def _fill_child(self, x: BTreeNode, i: int):
        t = self.t
        if i != 0 and len(x.children[i - 1].keys) >= t: self._borrow_from_prev(x, i)
        elif i != len(x.keys) and len(x.children[i + 1].keys) >= t: self._borrow_from_next(x, i)
        else:
            if i != len(x.keys): self._merge_children(x, i)
            else: self._merge_children(x, i - 1)

    def _borrow_from_prev(self, x: BTreeNode, i: int):
        child, sibling = x.children[i], x.children[i - 1]
        child.keys.insert(0, x.keys[i - 1])
        x.keys[i - 1] = sibling.keys.pop()
        if not child.leaf: child.children.insert(0, sibling.children.pop())

    def _borrow_from_next(self, x: BTreeNode, i: int):
        child, sibling = x.children[i], x.children[i + 1]
        child.keys.append(x.keys[i])
        x.keys[i] = sibling.keys.pop(0)
        if not child.leaf: child.children.append(sibling.children.pop(0))

    def _merge_children(self, x: BTreeNode, i: int):
        child, sibling = x.children[i], x.children[i + 1]
        child.keys.append(x.keys.pop(i))
        child.keys.extend(sibling.keys)
        child.children.extend(sibling.children)
        x.children.pop(i + 1)

    def _get_predecessor(self, x: BTreeNode) -> int:
        while not x.leaf: x = x.children[-1]
        return x.keys[-1]

    def _get_successor(self, x: BTreeNode) -> int:
        while not x.leaf: x = x.children[0]
        return x.keys[0]

    def _get_all_keys(self, node: Optional[BTreeNode]) -> List[int]:
        if not node: return []
        keys, q = [], deque([node])
        while q:
            curr = q.popleft()
            keys.extend(curr.keys)
            for child in curr.children: q.append(child)
        return keys
    
    def get_height(self) -> int:
        if not self.root or self.root.leaf: return 0
        h, node = 0, self.root
        while not node.leaf:
            node = node.children[0]
            h += 1
        return h

    def print_tree(self):
        print("--- Árvore-B (t={}) ---".format(self.t))
        if not self.root or not self.root.keys:
            print("Árvore vazia.\n------------------------")
            return
        q, level_nodes = deque([(self.root, 0)]), {}
        while q:
            node, level = q.popleft()
            if level not in level_nodes: level_nodes[level] = []
            level_nodes[level].append(node.keys)
            for child in node.children: q.append((child, level + 1))
        for level, nodes in sorted(level_nodes.items()):
            print(f"Nível {level}: {nodes}")
        print("------------------------")

# Bloco de demonstração
if __name__ == "__main__":
    # Códigos ANSI para cores
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

    print(f"{BOLD}{CYAN}Iniciando a demonstração da Árvore-B.{RESET}")
    t = 3
    b_tree = BTree(t=t)
    
    def menu():
        print(f"\n{BOLD}{BLUE}--- MENU ÁRVORE-B ---{RESET}")
        print(f"{YELLOW}1. Inserir chave{RESET}")
        print(f"{YELLOW}2. Remover chave{RESET}")
        print(f"{YELLOW}3. Buscar chave{RESET}")
        print(f"{YELLOW}4. Exibir árvore{RESET}")
        print(f"{YELLOW}5. Sair{RESET}\n")
        return input(f"{BOLD}Escolha uma opção: {RESET}")

    while True:
        opcao = menu()
        if opcao == '1':
            try:
                chave = int(input(f"{BOLD}Digite a chave a inserir: {RESET}"))
                if b_tree.search(chave) is not None:
                    print(f"{YELLOW}Chave {chave} já existe na árvore. Não é possível inserir duplicatas.{RESET}")
                else:
                    b_tree.insert(chave)
                    print(f"{GREEN}Chave {chave} inserida com sucesso.{RESET}")
            except ValueError:
                print(f"{RED}Entrada inválida. Digite um número inteiro.{RESET}")
            except icontract.errors.ViolationError as e:
                print(f"{RED}Erro de contrato ao inserir: {e}{RESET}")
        elif opcao == '2':
            try:
                chave = int(input(f"{BOLD}Digite a chave a remover: {RESET}"))
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