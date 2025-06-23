

import pytest
import icontract
from b_tree import BTree

@pytest.fixture
def arvore_t2() -> BTree:
    """Retorna uma árvore de ordem t=2 (Árvore 2-3-4) vazia."""
    return BTree(t=2)

@pytest.fixture
def arvore_t3() -> BTree:
    """Retorna uma árvore de ordem t=3 vazia."""
    return BTree(t=3)

class TestBTreeContracts:
    """Agrupa todos os testes relacionados aos contratos da Árvore-B."""

    def test_pre_insert_sucesso(self, arvore_t3: BTree):
        """
        Contrato: "Chave a ser inserida não existe na árvore"
        Caso: SUCESSO. Inserir uma chave nova deve funcionar.
        """
        arvore_t3.insert(10)
        assert arvore_t3.search(10) is not None

    def test_pre_insert_excecao_chave_duplicada(self, arvore_t3: BTree):
        """
        Contrato: "Chave a ser inserida não existe na árvore"
        Caso: EXCEÇÃO. Tentar inserir uma chave duplicada deve falhar.
        """
        arvore_t3.insert(10)
        with pytest.raises(icontract.errors.ViolationError, match="A chave a ser inserida não deve existir"):
            arvore_t3.insert(10)

    def test_pre_delete_sucesso(self, arvore_t3: BTree):
        """
        Contrato: "Chave a ser removida existe na árvore"
        Caso: SUCESSO. Remover uma chave existente deve funcionar.
        """
        arvore_t3.insert(10)
        arvore_t3.delete(10)
        assert arvore_t3.search(10) is None

    def test_pre_delete_excecao_chave_inexistente(self, arvore_t3: BTree):
        """
        Contrato: "Chave a ser removida existe na árvore"
        Caso: EXCEÇÃO. Tentar remover uma chave que não existe deve falhar.
        """
        arvore_t3.insert(10)
        with pytest.raises(icontract.errors.ViolationError, match="A chave a ser removida deve existir"):
            arvore_t3.delete(99)
            
    
    

    def test_post_insert_split_raiz_sucesso(self, arvore_t3: BTree):
        """
        Contratos: Pós-condições de contagem de chaves/filhos e altura.
        Caso: SUCESSO após divisão da raiz. A inserção da 6ª chave em uma
              árvore de t=3 força a divisão da raiz e o aumento da altura.
              Os contratos devem ser mantidos.
        """
        chaves = [10, 20, 30, 40, 50]
        for k in chaves:
            arvore_t3.insert(k)
        
        assert arvore_t3.get_height() == 0
        
        
        arvore_t3.insert(60)
        
        assert arvore_t3.get_height() == 1
        assert arvore_t3.root.keys == [30]

    def test_post_insert_simples_sem_mudar_altura(self, arvore_t3: BTree):
        """
        Contratos: Pós-condições de contagem de chaves/filhos e altura.
        Caso: SUCESSO em inserção simples. A altura NÃO deve mudar.
        """
        arvore_t3.insert(10)
        arvore_t3.insert(20)
        assert arvore_t3.get_height() == 0

    def test_post_delete_merge_diminui_altura(self, arvore_t2: BTree):
        """
        Contratos: Pós-condições de contagem de chaves/filhos e altura.
        Caso: SUCESSO após fusão que diminui a altura da árvore.
        """
        list(map(arvore_t2.insert, [20, 40, 10, 30]))
        
        arvore_t2.delete(40)
        assert arvore_t2.get_height() == 1
        arvore_t2.delete(10)
        
        assert arvore_t2.get_height() == 0
        assert arvore_t2.root.keys == [20, 30]

    def test_post_delete_emprestimo_sem_mudar_altura(self, arvore_t2: BTree):
        """
        Contratos: Pós-condições de contagem de chaves/filhos e altura.
        Caso: SUCESSO após "pegar emprestado", sem alterar a altura.
        """
        list(map(arvore_t2.insert, [10, 20, 30, 40]))
        
        assert arvore_t2.get_height() == 1
        
        arvore_t2.delete(10) 
        
        assert arvore_t2.get_height() == 1
        assert arvore_t2.root.keys == [30]

    def test_post_excecao_nao_deve_acontecer_em_operacao_valida(self, arvore_t3: BTree):
        """
        Contratos: Pós-condições de contagem de chaves/filhos e altura.
        Caso: Um teste genérico para garantir que uma sequência complexa de
              operações válidas não viola nenhuma pós-condição.
        """
        try:
            for i in range(1, 21):
                arvore_t3.insert(i * 10)
            for i in range(5, 15):
                arvore_t3.delete(i * 10)
        except icontract.errors.ViolationError as e:
            pytest.fail(f"Uma pós-condição foi violada inesperadamente: {e}")

    
    def test_invariantes_sucesso_apos_operacoes(self, arvore_t3: BTree):
        """
        Contratos: Invariantes de folhas no mesmo nível e chaves ordenadas.
        Caso: SUCESSO. Após várias operações, a árvore deve permanecer válida.
        """
        try:
            list(map(arvore_t3.insert, [10, 20, 5, 15, 30, 25]))
            arvore_t3.delete(10)
            list(map(arvore_t3.insert, [8, 9, 7]))
        except icontract.errors.ViolationError as e:
            pytest.fail(f"Uma invariante foi violada inesperadamente: {e}")

    def test_invariante_excecao_chaves_desordenadas(self, arvore_t3: BTree):
        """
        Contratos: Invariantes de chaves ordenadas.
        Caso: EXCEÇÃO. Se quebrarmos a ordenação manualmente, a próxima operação
              deve detectar a violação da invariante.
        """
        arvore_t3.insert(10)
        arvore_t3.insert(20)
        
        
        arvore_t3.root.keys = [20, 10]
        
        with pytest.raises(icontract.errors.ViolationError, match="Verifica as invariantes"):
            arvore_t3.search(10)

    def test_invariante_excecao_folhas_niveis_diferentes(self, arvore_t3: BTree):
        """
        Contratos: Invariantes de folhas no mesmo nível.
        Caso: EXCEÇÃO. Se quebrarmos o balanceamento manualmente, a invariante
              deve ser violada.
        """
        list(map(arvore_t3.insert, [10, 20, 30, 40, 50, 60]))
        
        
        arvore_t3.root.children.pop(0) 

        with pytest.raises(icontract.errors.ViolationError, match="Verifica as invariantes"):
            arvore_t3.search(10)
            
    def test_cenario_complexo_insert_e_delete(self, arvore_t3: BTree):
        """Teste de cenário misto para garantir robustez e validade dos contratos."""
        chaves_inserir = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45]
        chaves_remover = [50, 40, 60]
        
        try:
            for k in chaves_inserir:
                arvore_t3.insert(k)
            
            for k in chaves_remover:
                arvore_t3.delete(k)
        except icontract.errors.ViolationError as e:
            pytest.fail(f"Contrato violado em cenário complexo: {e}")
            
        assert arvore_t3.search(30) is not None
        assert arvore_t3.search(50) is None

    def test_arvore_vazia_apos_remocao_total(self, arvore_t3: BTree):
        """Garante que a árvore fica em um estado válido (vazio) após remover todos os elementos."""
        chaves = [10, 20, 30]
        for k in chaves:
            arvore_t3.insert(k)
        
        for k in chaves:
            arvore_t3.delete(k)
        
        assert not arvore_t3.root.keys
        assert arvore_t3.root.leaf
        assert arvore_t3.get_height() == 0