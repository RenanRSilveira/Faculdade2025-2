# Caixas de diálogo (ProdutoDiaLog, PessoaDiaLog, etc.)

"""
Define janelas de diálogo (forms) para adicionar/editar dados.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import repository as repo

class ProdutoDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        top.title("Novo Produto")

        tk.Label(top, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nome = tk.Entry(top)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Categoria:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_cat = tk.Entry(top)
        self.entry_cat.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="Preço:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_preco = tk.Entry(top)
        self.entry_preco.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(top, text="Quantidade:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_qtd = tk.Entry(top)
        self.entry_qtd.grid(row=3, column=1, padx=5, pady=5)

        # 🔹 Combobox com fornecedores
        tk.Label(top, text="Fornecedor:").grid(row=4, column=0, padx=5, pady=5)
        fornecedores = repo.listar_fornecedores()
        self.cb_forn = ttk.Combobox(top, values=[f"{f['id_fornecedor']} - {f['nome']}" for f in fornecedores])
        self.cb_forn.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(top, text="Estoque mínimo:").grid(row=5, column=0, padx=5, pady=5)
        self.entry_est_min = tk.Entry(top)
        self.entry_est_min.grid(row=5, column=1, padx=5, pady=5)

        ttk.Button(top, text="OK", command=self.ok).grid(row=6, column=0, columnspan=2, pady=10)

        self.result = None

    def ok(self):
        try:
            nome = self.entry_nome.get()
            cat = self.entry_cat.get()
            preco = float(self.entry_preco.get())
            qtd = int(self.entry_qtd.get())

            # 🔹 Extrai só o id do fornecedor
            forn = self.cb_forn.get()
            if forn:
                id_forn = int(forn.split(" - ")[0])
            else:
                id_forn = None

            est_min = int(self.entry_est_min.get())
            self.result = (nome, cat, preco, qtd, id_forn, est_min)
            self.top.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Erro", f"Preencha corretamente os campos!\n{e}")


class PessoaDialog:
    def __init__(self, parent, title="Nova Pessoa", pessoa=None):
        """
        Dialog para adicionar/editar Cliente ou Fornecedor.
        Se 'pessoa' for passado, os campos são preenchidos para edição.
        """
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.transient(parent)
        self.top.grab_set()

        # --- Campos principais ---
        ttk.Label(self.top, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.e_nome = ttk.Entry(self.top, width=40)
        self.e_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Telefone:").grid(row=1, column=0, padx=5, pady=5)
        self.e_tel = ttk.Entry(self.top, width=20)
        self.e_tel.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.top, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.e_email = ttk.Entry(self.top, width=30)
        self.e_email.grid(row=2, column=1, sticky="w", columnspan=2, padx=5, pady=5)

        # --- Endereço ---
        ttk.Label(self.top, text="Estado:").grid(row=3, column=0, padx=5, pady=5)
        self.cb_estado = ttk.Combobox(self.top, values=[e["nome"] for e in repo.listar_estados()])
        self.cb_estado.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.top, text="Cidade:").grid(row=4, column=0, padx=5, pady=5)
        self.cb_cidade = ttk.Combobox(self.top)
        self.cb_cidade.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        def carregar_cidades(event=None):
            estado_nome = self.cb_estado.get()
            if estado_nome:
                estado = next((e for e in repo.listar_estados() if e["nome"] == estado_nome), None)
                if estado:
                    cidades = repo.listar_cidades(estado["id_estado"])
                    lista_cidades = [c["nome"] for c in cidades]
                    self.cb_cidade["values"] = lista_cidades

                    # 🔹 Se a cidade atual não está na lista, limpa
                    if self.cb_cidade.get() not in lista_cidades:
                        self.cb_cidade.set("")

        self.cb_estado.bind("<<ComboboxSelected>>", carregar_cidades)

        ttk.Label(self.top, text="Rua:").grid(row=5, column=0, padx=5, pady=5)
        self.e_rua = ttk.Entry(self.top, width=30)
        self.e_rua.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.top, text="Número:").grid(row=6, column=0, padx=5, pady=5)
        self.e_numero = ttk.Entry(self.top, width=10)
        self.e_numero.grid(row=6, column=1, sticky="w",  padx=5, pady=5)

        ttk.Label(self.top, text="Bairro:").grid(row=7, column=0, padx=5, pady=5)
        self.e_bairro = ttk.Entry(self.top, width=20)
        self.e_bairro.grid(row=7, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.top, text="CEP:").grid(row=8, column=0, padx=5, pady=5)
        self.e_cep = ttk.Entry(self.top, width=12)
        self.e_cep.grid(row=8, column=1, sticky="w", padx=5, pady=5)

        # --- Botões ---
        ttk.Button(self.top, text="Salvar", command=self.on_save).grid(row=9, column=0, pady=10)
        ttk.Button(self.top, text="Cancelar", command=self.top.destroy).grid(row=9, column=1, pady=10)

        # --- Preencher se for edição ---
        if pessoa:
            self.e_nome.insert(0, pessoa["nome"])
            self.e_tel.insert(0, pessoa["telefone"])
            self.e_email.insert(0, pessoa["email"])

            if pessoa.get("estado"):
                self.cb_estado.set(pessoa["estado"])
                carregar_cidades()
            if pessoa.get("cidade"):
                self.cb_cidade.set(pessoa["cidade"])
            if pessoa.get("rua"):
                self.e_rua.insert(0, pessoa["rua"])
            if pessoa.get("numero"):
                self.e_numero.insert(0, pessoa["numero"])
            if pessoa.get("bairro"):
                self.e_bairro.insert(0, pessoa["bairro"])
            if pessoa.get("cep"):
                self.e_cep.insert(0, pessoa["cep"])

    def on_save(self):
        nome = self.e_nome.get().strip()
        tel = self.e_tel.get().strip()
        email = self.e_email.get().strip()
        estado_nome = self.cb_estado.get().strip()
        cidade_nome = self.cb_cidade.get().strip()
        rua = self.e_rua.get().strip()
        numero = self.e_numero.get().strip()
        bairro = self.e_bairro.get().strip()
        cep = self.e_cep.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório!")
            return

        # --- Estado ---
        id_estado = None
        if estado_nome:
            estado = next((e for e in repo.listar_estados() if e["nome"] == estado_nome), None)
            if estado:
                id_estado = estado["id_estado"]
            else:
                messagebox.showerror("Erro", "Estado inválido!")
                return

        # --- Cidade ---
        id_cidade = None
        if cidade_nome and id_estado:
            cidade = next((c for c in repo.listar_cidades(id_estado) if c["nome"] == cidade_nome), None)
            if cidade:
                id_cidade = cidade["id_cidade"]
            else:
                # 🔹 Se a cidade não existir, cria no banco
                id_cidade = repo.inserir_cidade(cidade_nome, id_estado)

        # --- Endereço ---
        id_endereco = None
        if rua and id_cidade:
            id_endereco = repo.inserir_endereco(rua, numero, bairro, cep, id_cidade)

        # --- Resultado final ---
        self.result = (nome, tel, email, id_endereco)
        self.top.destroy()

class VendaDialog:
    """Janela para cadastrar venda"""

    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Nova Venda")
        self.result = None

        tk.Label(self.top, text="ID Cliente:").grid(row=0, column=0, sticky="w")
        self.e_cliente = tk.Entry(self.top)
        self.e_cliente.grid(row=0, column=1)

        tk.Label(self.top, text="ID Produto:").grid(row=1, column=0, sticky="w")
        self.e_produto = tk.Entry(self.top)
        self.e_produto.grid(row=1, column=1)

        tk.Label(self.top, text="Quantidade:").grid(row=2, column=0, sticky="w")
        self.e_qtd = tk.Entry(self.top)
        self.e_qtd.grid(row=2, column=1)

        tk.Label(self.top, text="Preço unitário:").grid(row=3, column=0, sticky="w")
        self.e_preco = tk.Entry(self.top)
        self.e_preco.grid(row=3, column=1)

        ttk.Button(self.top, text="Salvar", command=self.on_save).grid(row=4, column=0, columnspan=2, pady=5)

    def on_save(self):
        try:
            id_cliente = int(self.e_cliente.get())
            id_produto = int(self.e_produto.get())
            qtd = int(self.e_qtd.get())
            preco = float(self.e_preco.get())

            # result = (id_cliente, lista_de_itens)
            self.result = (id_cliente, [(id_produto, qtd, preco)])
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Campos inválidos: {e}")
