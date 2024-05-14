menu = """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

while True:

    opcao = input(menu)

    if opcao == "d":
        deposito = float(input("Digite o valor a ser depositado: "))
        if deposito > 0:
            saldo += deposito
            extrato += f"C R${deposito:.2f}\n"
            print("Depósito realizado com sucesso!")
        else:
            print("Valor inválido. O valor do depósito deve ser positivo.")

    elif opcao == "s":
        if numero_saques < LIMITE_SAQUES:
            saque = float(input("Digite o valor a ser sacado: "))
            if 0 < saque <= limite and saque <= saldo:
                saldo -= saque
                extrato += f"D R${saque:.2f}\n"
                numero_saques += 1
                print("Saque realizado com sucesso!")
            elif saque > saldo:
                print("Saldo insuficiente.")
            else:
                print("Valor inválido. O valor do saque deve ser menor ou igual a R$500.00.")
        else:
            print("Você atingiu o limite diário de saques.")

    elif opcao == "e":
        print("\n================ EXTRATO ================")
        print("Sem movimentações." if not extrato else extrato)
        print(f"\nSaldo atual: R${saldo:.2f}")
        print("==========================================")

    elif opcao == "q":
        print("bye!!")
        break

    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")