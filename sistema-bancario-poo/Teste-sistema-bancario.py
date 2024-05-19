import unittest
from io import StringIO
from unittest.mock import patch
from sistema_bancario_poo import PessoaFisica, ContaCorrente, depositar, sacar, exibir_extrato, criar_cliente, criar_conta, listar_contas, menu

class TestSistemaBancario(unittest.TestCase):
    def setUp(self):
        self.clientes = []
        self.contas = []

    @patch("builtins.input", side_effect=["nc", "Fulano", "01-01-1980", "12345678900", "Rua A", "q"])
    def test_criar_cliente(self, mock_input):
        criar_cliente(self.clientes)
        self.assertEqual(len(self.clientes), 1)

    @patch("builtins.input", side_effect=["nu", "Fulano", "01-01-1980", "12345678900", "Rua A", "nc", "q"])
    def test_criar_conta(self, mock_input):
        criar_cliente(self.clientes)
        criar_conta(len(self.contas) + 1, self.clientes, self.contas)
        self.assertEqual(len(self.contas), 1)
        self.assertEqual(len(self.clientes[0].contas), 1)

    @patch("builtins.input", side_effect=["nc", "Fulano", "01-01-1980", "12345678900", "Rua A", "d", "12345678900", "1000", "q"])
    def test_depositar(self, mock_input):
        criar_cliente(self.clientes)
        criar_conta(len(self.contas) + 1, self.clientes, self.contas)
        depositar(self.clientes)
        self.assertEqual(self.contas[0].saldo, 1000)

    @patch("builtins.input", side_effect=["nc", "Fulano", "01-01-1980", "12345678900", "Rua A", "d", "12345678900", "1000", "s", "12345678900", "500", "q"])
    def test_sacar(self, mock_input):
        criar_cliente(self.clientes)
        criar_conta(len(self.contas) + 1, self.clientes, self.contas)
        depositar(self.clientes)
        sacar(self.clientes)
        self.assertEqual(self.contas[0].saldo, 500)

    @patch("builtins.input", side_effect=["nc", "Fulano", "01-01-1980", "12345678900", "Rua A", "d", "12345678900", "1000", "s", "12345678900", "500", "e", "12345678900", "q"])
    def test_exibir_extrato(self, mock_input):
        criar_cliente(self.clientes)
        criar_conta(len(self.contas) + 1, self.clientes, self.contas)
        depositar(self.clientes)
        sacar(self.clientes)
        with patch("sys.stdout", new=StringIO()) as fake_out:
            exibir_extrato(self.clientes)
            output = fake_out.getvalue().strip()
        self.assertIn("Extrato", output)
        self.assertIn("Depósito", output)
        self.assertIn("Saque", output)
        self.assertIn("Saldo", output)

    @patch("builtins.input", side_effect=["nc", "Fulano", "01-01-1980", "12345678900", "Rua A", "nc", "q"])
    def test_listar_contas(self, mock_input):
        criar_cliente(self.clientes)
        criar_conta(len(self.contas) + 1, self.clientes, self.contas)
        with patch("sys.stdout", new=StringIO()) as fake_out:
            listar_contas(self.contas)
            output = fake_out.getvalue().strip()
        self.assertIn("Agência", output)
        self.assertIn("C/C", output)
        self.assertIn("Titular", output)

if __name__ == "__main__":
    unittest.main()
