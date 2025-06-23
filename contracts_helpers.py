from typing import List
from b_tree_node import BTreeNode

def _check_node_key_count(node: BTreeNode, t: int, is_root: bool) -> bool:
    """Verifica se o número de chaves em um nó está dentro dos limites da Árvore-B."""
    if not node.keys and is_root and node.leaf: return True
    min_keys, max_keys = (1 if is_root else t - 1), 2 * t - 1
    return min_keys <= len(node.keys) <= max_keys

def _check_node_child_count(node: BTreeNode, t: int, is_root: bool) -> bool:
    """Verifica se o número de filhos de um nó está correto."""
    if node.leaf: return len(node.children) == 0
    if len(node.children) != len(node.keys) + 1: return False
    min_children, max_children = (2 if is_root else t), 2 * t
    return min_children <= len(node.children) <= max_children

def _check_keys_sorted(keys: List[int]) -> bool:
    """Verifica se as chaves em uma lista estão ordenadas crescentemente."""
    return all(keys[i] <= keys[i + 1] for i in range(len(keys) - 1))