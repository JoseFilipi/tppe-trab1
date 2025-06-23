class BTreeNode:
    """
    Um nó em uma Árvore-B.

    Atributos:
        leaf (bool): True se o nó for uma folha, False caso contrário.
        keys (list[int]): A lista de chaves armazenadas no nó.
        children (list[BTreeNode]): A lista de nós filhos.
    """
    def __init__(self, leaf: bool = False):
        """Inicializa um novo nó da Árvore-B."""
        self.leaf, self.keys, self.children = leaf, [], []