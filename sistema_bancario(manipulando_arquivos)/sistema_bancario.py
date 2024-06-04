import csv
# import os
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

# Define the root path and data directory
ROOT_PATH = Path(__file__).parent
DATA_DIR = ROOT_PATH / "dados"

# Ensure the data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Define paths for the log and CSV files
LOG_FILE_PATH = DATA_DIR / "log.txt"
CSV_FILE_PATH = DATA_DIR / "dados_clientes.csv"


class ContaIterador:
    def __init__(self, contas):
        self._contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self._contas[self._index]
            self._index += 1
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
            """
        except IndexError:
            raise StopIteration


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 10:
            print("\nOpa, algo deu errado. Você não pode fazer mais transações hoje.")
            return
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:('{self.nome}','{self.cpf}')>"


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\nOperação falhou! Você não tem saldo suficiente.")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True

        else:
            print("\nOperação falhou! O valor informado é inválido.")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\nOperação falhou! O valor informado é inválido.")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\nOperação falhou! O valor do saque excede o limite.")

        elif excedeu_saques:
            print("\nOperação falhou! Número máximo de saques excedido.")

        else:
            return super().sacar(valor)

        return False

    def __repr__(self):
        return f"""<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"""

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gera_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if (
                tipo_transacao is None
                or transacao["tipo"].lower() == tipo_transacao.lower()
            ):
                yield transacao

    def transacoes_do_dia(self):
        data_atual = datetime.utcnow().date()
        return [
            transacao
            for transacao in self._transacoes
            if datetime.strptime(transacao["data"], "%d-%m-%Y %H:%M:%S").date()
            == data_atual
        ]


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{data_hora}] Função '{func.__name__}' executada com argumentos {args} e {kwargs}. Retornou {resultado}\n"
        with open(LOG_FILE_PATH, "a") as log_file:
            log_file.write(log_entry)
        return resultado

    return envelope


def menu():
    menu = """\n
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova conta
    [5]\tListar contas
    [6]\tNovo usuário
    [0]\tSair
    => """
    return input(textwrap.dedent(menu))


def submenu_extrato():
    submenu = """\n
    ============ EXTRATO ============
    [1]\tDepósitos
    [2]\tSaques
    [3]\tAmbos
    => """
    return input(textwrap.dedent(submenu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\nCliente não possui conta!")
        return

    return cliente.contas[0]


@log_transacao
def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nOps, parece que o cliente não está cadastrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)
    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nOps, parece que o cliente não está cadastrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)
    cliente.realizar_transacao(conta, transacao)


@log_transacao
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nOps, parece que o cliente não está cadastrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    tipo_transacao = submenu_extrato()
    if tipo_transacao == "1":
        tipo_transacao = "Deposito"
    elif tipo_transacao == "2":
        tipo_transacao = "Saque"
    elif tipo_transacao == "3":
        tipo_transacao = None
    else:
        print("\nOpção inválida! Mostrando todas as transações.")
        tipo_transacao = None

    print("\n====================== EXTRATO ======================")
    print(f"Conta: {conta.numero:<23} Titular: {cliente.nome}\n")
    print(f"{'TIPO':<10}{'VALOR':<20}{'DATA/HORA'}")

    extrato = ""
    tem_transacao = False
    for transacao in conta.historico.gera_relatorio(tipo_transacao=tipo_transacao):
        tem_transacao = True
        tipo = "C" if transacao["tipo"] == "Deposito" else "D"
        valor = (
            f"+ R$ {transacao['valor']:.2f}"
            if tipo == "C"
            else f"- R$ {transacao['valor']:.2f}"
        )
        extrato += f"{tipo:<10}{valor:<20}{transacao['data']}\n"

    if not tem_transacao:
        extrato = "Ops, parece que não há nada para ver aqui! Nenhuma movimentação foi registrada.\n"

    print(extrato)
    print(f"SALDO:{conta.saldo:>15.2f}")
    print("=====================================================")


@log_transacao
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print(
            "\nUé, esse CPF já está familiarizado! Já temos um cliente cadastrado com ele."
        )
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade estado): ")

    cliente = PessoaFisica(
        nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco
    )

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


@log_transacao
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print(
            "\nOps, parece que o cliente não está cadastrado no sistema! A conta não pôde ser criada."
        )
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in ContaIterador(contas):
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def salvar_dados(clientes, contas):
    with open(CSV_FILE_PATH, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "cpf",
                "nome",
                "data_nascimento",
                "endereco",
                "conta_numero",
                "conta_agencia",
                "conta_saldo",
            ]
        )
        for cliente in clientes:
            for conta in cliente.contas:
                writer.writerow(
                    [
                        cliente.cpf,
                        cliente.nome,
                        cliente.data_nascimento,
                        cliente.endereco,
                        conta.numero,
                        conta.agencia,
                        conta.saldo,
                    ]
                )


def carregar_dados():
    clientes = []
    contas = []
    try:
        with open(CSV_FILE_PATH, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cliente = filtrar_cliente(row["cpf"], clientes)
                if not cliente:
                    cliente = PessoaFisica(
                        nome=row["nome"],
                        data_nascimento=row["data_nascimento"],
                        cpf=row["cpf"],
                        endereco=row["endereco"],
                    )
                    clientes.append(cliente)
                conta = ContaCorrente(numero=row["conta_numero"], cliente=cliente)
                conta._saldo = float(row["conta_saldo"])
                cliente.contas.append(conta)
                contas.append(conta)
    except FileNotFoundError:
        print("Arquivo de dados não encontrado. Iniciando com dados vazios.")
    return clientes, contas


def main():
    clientes, contas = carregar_dados()

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "5":
            listar_contas(contas)

        elif opcao == "6":
            criar_cliente(clientes)

        elif opcao == "0":
            salvar_dados(clientes, contas)
            break

        else:
            print(
                "\nDesculpe, mas não entendi o que você quis fazer. Por favor, tente novamente."
            )


if __name__ == "__main__":
    main()
