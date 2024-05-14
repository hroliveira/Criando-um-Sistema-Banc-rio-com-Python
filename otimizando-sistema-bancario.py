import textwrap
from enum import Enum

class MenuOption(Enum):
    DEPOSITAR = '1'
    SACAR = '2'
    EXTRATO = '3'
    NOVA_CONTA = '4'
    LISTAR_CONTAS = '5'
    NOVO_USUARIO = '6'
    SAIR = '0'

class Banco:
    def __init__(self):
        self.LIMITE_SAQUES = 3
        self.AGENCIA = "0001"
        self.saldo = 0
        self.limite = 500
        self.extrato = ""
        self.numero_saques = 0
        self.usuarios = []
        self.contas = []

    def menu(self):
        menu = textwrap.dedent("""
        ================ MENU ================
        [1]\tDepositar
        [2]\tSacar
        [3]\tExtrato
        [4]\tNova conta
        [5]\tListar contas
        [6]\tNovo usuário
        [0]\tSair
        => """)
        return input(menu)

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.extrato += f"C:\tR$ {valor:.2f}\n"
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n$$$ Operação falhou! O valor informado é inválido. $$$")

    def sacar(self, valor):
        excedeu_saldo = valor > self.saldo
        excedeu_limite = valor > self.limite
        excedeu_saques = self.numero_saques >= self.LIMITE_SAQUES

        if excedeu_saldo:
            print("\n$$$ Operação falhou! Você não tem saldo suficiente. $$$")

        elif excedeu_limite:
            print("\n$$$ Operação falhou! O valor do saque excede o limite. $$$")

        elif excedeu_saques:
            print("\n$$$ Operação falhou! Número máximo de saques excedido. $$$")

        elif valor > 0:
            self.saldo -= valor
            self.extrato += f"D:\t\t-R$ {valor:.2f}\n"
            self.numero_saques += 1
            print("\n=== Saque realizado com sucesso! ===")

        else:
            print("\n$$$ Operação falhou! O valor informado é inválido. $$$")

    def exibir_extrato(self):
        print("\n================ EXTRATO ================")
        print("Não foram realizadas movimentações." if not self.extrato else self.extrato)
        print(f"\nSaldo:\t\tR$ {self.saldo:.2f}")
        print("==========================================")


    def criar_usuario(self):
        cpf = input("Informe o CPF (somente número): ")
        usuario = self.filtrar_usuario(cpf)

        if usuario:
            print("\n$$$ Já existe usuário com esse CPF! $$$")
            return

        nome = input("Informe o nome completo: ")
        data_nascimento = input("Informe a data de nascimento (DD-MM-AAAA): ")
        endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

        self.usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco})

        print("=== Usuário criado com sucesso! ===")

    def filtrar_usuario(self, cpf):
        usuarios_filtrados = [usuario for usuario in self.usuarios if usuario["cpf"] == cpf]
        return usuarios_filtrados[0] if usuarios_filtrados else None

    def criar_conta(self):
        cpf = input("Informe o CPF do usuário: ")
        usuario = self.filtrar_usuario(cpf)

        if usuario:
            print("\n=== Conta criada com sucesso! ===")
            self.contas.append({"agencia": self.AGENCIA, "numero_conta": len(self.contas) + 1, "usuario": usuario})
        else:
            print("\n$$$ Usuário não encontrado, operação cancelada! $$$")
        

    def listar_contas(self):
        for conta in self.contas:
            linha = f"""\
                Agência:\t{conta['agencia']}
                C/C:\t\t{conta['numero_conta']}
                Titular:\t{conta['usuario']['nome']}
            """
            print("=" * 100)
            print(textwrap.dedent(linha))

    def run(self):
        while True:
            opcao = self.menu()

            if opcao == MenuOption.DEPOSITAR.value:
                valor = float(input("Informe o valor do depósito: "))
                self.depositar(valor)

            elif opcao == MenuOption.SACAR.value:
                valor = float(input("Informe o valor do saque: "))
                self.sacar(valor)

            elif opcao == MenuOption.EXTRATO.value:
                self.exibir_extrato()

            elif opcao == MenuOption.NOVO_USUARIO.value:
                self.criar_usuario()

            elif opcao == MenuOption.NOVA_CONTA.value:
                self.criar_conta()

            elif opcao == MenuOption.LISTAR_CONTAS.value:
                self.listar_contas()

            elif opcao == MenuOption.SAIR.value:
                break

            else:
                print("Operação inválida, por favor selecione novamente a operação desejada.")

if __name__ == "__main__":
    banco = Banco()
    banco.run()
