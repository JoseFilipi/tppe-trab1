from b_tree import BTree
import icontract

# Códigos ANSI para cores no terminal
RESET, BOLD, RED, GREEN, YELLOW, BLUE, CYAN = "\033[0m", "\033[1m", "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[96m"

def run():
    """Função principal que executa a interface de linha de comando."""
    print(f"{BOLD}{CYAN}Iniciando a demonstração da Árvore-B.{RESET}")

    while True:
        try:
            t_input = input(f"{BOLD}{YELLOW}Digite a ordem 't' da Árvore-B (valor mínimo: 2): {RESET}")
            t = int(t_input)
            if t >= 2: break
            else: print(f"{RED}Erro: A ordem 't' deve ser um número inteiro maior ou igual a 2.{RESET}")
        except ValueError:
            print(f"{RED}Erro: Entrada inválida. Por favor, digite um número inteiro.{RESET}")

    b_tree = BTree(t=t)
    print(f"{GREEN}Árvore-B de ordem t={t} criada com sucesso!{RESET}")
    
    def menu():
        """Exibe o menu de opções para o usuário."""
        print(f"\n{BOLD}{BLUE}--- MENU ÁRVORE-B (t={b_tree.t}) ---{RESET}")
        print(f"{YELLOW}1. Inserir chave(s){RESET}\n{YELLOW}2. Remover chave(s){RESET}\n{YELLOW}3. Buscar chave{RESET}\n{YELLOW}4. Exibir árvore{RESET}\n{YELLOW}5. Sair{RESET}\n")
        return input(f"{BOLD}Escolha uma opção: {RESET}")

    while True:
        opcao = menu()
        if opcao == '1':
            try:
                chave_input = input(f"{BOLD}Digite a(s) chave(s) a inserir (separadas por espaço): {RESET}")
                chaves = [int(item) for item in chave_input.split()]
                for chave in chaves:
                    if b_tree.search(chave) is not None:
                        print(f"{YELLOW}Chave {chave} já existe. Ignorando.{RESET}")
                        continue
                    b_tree.insert(chave)
                    print(f"{GREEN}Chave {chave} inserida com sucesso.{RESET}")
            except ValueError: print(f"{RED}Entrada inválida. Digite apenas números inteiros separados por espaço.{RESET}")
            except icontract.errors.ViolationError as e: print(f"{RED}Erro de contrato ao inserir: {e}{RESET}")
        
        elif opcao == '2':
            try:
                chave_input = input(f"{BOLD}Digite a(s) chave(s) a remover (separadas por espaço): {RESET}")
                chaves = [int(item) for item in chave_input.split()]
                for chave in chaves:
                    if b_tree.search(chave) is None:
                        print(f"{YELLOW}Chave {chave} não existe. Ignorando.{RESET}")
                        continue
                    b_tree.delete(chave)
                    print(f"{GREEN}Chave {chave} removida com sucesso.{RESET}")
            except ValueError: print(f"{RED}Entrada inválida. Digite apenas números inteiros separados por espaço.{RESET}")
            except icontract.errors.ViolationError as e: print(f"{RED}Erro de contrato ao remover: {e}{RESET}")

        elif opcao == '3':
            try:
                chave = int(input(f"{BOLD}Digite a chave a buscar: {RESET}"))
                if b_tree.search(chave): print(f"{GREEN}Chave {chave} encontrada na árvore.{RESET}")
                else: print(f"{YELLOW}Chave {chave} NÃO encontrada na árvore.{RESET}")
            except ValueError: print(f"{RED}Entrada inválida. Digite um número inteiro.{RESET}")

        elif opcao == '4':
            print(f"{CYAN}", end=""); b_tree.print_tree(); print(f"{RESET}", end="")

        elif opcao == '5':
            print(f"{BOLD}{BLUE}Saindo...{RESET}"); break
            
        else:
            print(f"{RED}Opção inválida. Tente novamente.{RESET}")

if __name__ == "__main__":
    run()