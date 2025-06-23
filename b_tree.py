import icontract
from typing import List, Optional, Tuple, Dict, Any
from collections import deque
from b_tree_node import BTreeNode
from contracts_helpers import _check_node_key_count, _check_node_child_count, _check_keys_sorted

@icontract.invariant(lambda self: self._check_all_invariants(), description="Verifica as invariantes da Árvore-B")
class BTree:
    def __init__(self, t: int):
        if t < 2: raise ValueError("A ordem 't' da Árvore-B deve ser no mínimo 2.")
        self.root, self.t = BTreeNode(leaf=True), t

    @icontract.require(lambda self, k: self.search(k) is None, "A chave a ser inserida não deve existir na árvore.")
    @icontract.ensure(
        lambda self, result: (self._check_structural_postconditions() and (not (result["root_keys_len"] == 2 * self.t - 1) or self.get_height() == result["height"] + 1)),
        description="A estrutura e a altura da árvore devem ser válidas após a inserção."
    )
    def insert(self, k: int) -> Dict[str, Any]:
        old_state = {"height": self.get_height(), "root_keys_len": len(self.root.keys)}
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode()
            self.root = new_root
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, k)
        else:
            self._insert_non_full(root, k)
        return old_state

    @icontract.require(lambda self, k: self.search(k) is not None, "A chave a ser removida deve existir na árvore.")
    @icontract.ensure(
        lambda self, result: (
            self._check_structural_postconditions() and
            self.get_height() in [result['height'], result['height'] - 1] and
            (self.get_height() != result['height'] - 1 or (result["root_keys_len"] == 1 and not result["root_is_leaf"]))
        ),
        description="A estrutura e a altura da árvore devem ser válidas após a remoção."
    )
    def delete(self, k: int) -> Dict[str, Any]:
        old_state = {"height": self.get_height(), "root_keys_len": len(self.root.keys), "root_is_leaf": self.root.leaf}
        self._delete_recursive(self.root, k)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]
        return old_state
    
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
            while i >= 0 and k < x.keys[i]: x.keys[i + 1], i = x.keys[i], i - 1
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
        z.keys, y.keys = y.keys[t:], y.keys[:t - 1]
        if not y.leaf:
            z.children, y.children = y.children[t:], y.children[:t]

    def _delete_recursive(self, x: BTreeNode, k: int):
        t, i = self.t, 0
        while i < len(x.keys) and k > x.keys[i]: i += 1
        if i < len(x.keys) and x.keys[i] == k:
            if x.leaf: x.keys.pop(i)
            else: self._delete_from_internal_node(x, i)
        else:
            if x.leaf: return
            child_idx = i
            is_last_child = (child_idx == len(x.children) - 1)
            if len(x.children[child_idx].keys) < t:
                self._fill_child(x, child_idx)
            if is_last_child and child_idx > len(x.keys):
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
        if i != 0 and len(x.children[i - 1].keys) >= self.t: self._borrow_from_prev(x, i)
        elif i != len(x.keys) and len(x.children[i + 1].keys) >= self.t: self._borrow_from_next(x, i)
        elif i != len(x.keys): self._merge_children(x, i)
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
        print(f"--- Estrutura da Árvore (t={self.t}) ---")
        if not self.root or not self.root.keys:
            print("Árvore vazia.")
            print("---------------------------------")
            return
        self._print_recursive(self.root, "", True, is_root=True)
        print("---------------------------------")
        
    def _print_recursive(self, node: BTreeNode, prefix: str, is_last: bool, is_root: bool = False):
        if is_root:
            print(str(node.keys))
        else:
            print(prefix + ("└── " if is_last else "├── ") + str(node.keys))
        if not node.leaf:
            child_prefix = prefix + ("    " if is_last else "│   ")
            num_children = len(node.children)
            for i, child in enumerate(node.children):
                self._print_recursive(child, child_prefix, i == num_children - 1)