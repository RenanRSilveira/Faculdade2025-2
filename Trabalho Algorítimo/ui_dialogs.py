# Caixas de diálogo (ProdutoDiaLog, PessoaDiaLog, etc.)

"""
Define janelas de diálogo (forms) para adicionar/editar dados.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import repository as repo
from tkcalendar import DateEntry

# region Modal Produto
class ProdutoDialog:
    def __init__(self, parent, produto = None):
        """
        Dialog para adicionar/editar Produto.
        Se 'produto' for passado, os campos são preenchidos para edição.
        """
        self.top = tk.Toplevel(parent)
        if (produto):
            self.top.title("Editar Produto")
        else:
            self.top.title("Novo Produto")
        
        self.result = None
        self.top.transient(parent) #Deixa a janela sempre na frente e minimiza junto com a janela principal (parent).
        self.top.grab_set() #Bloqueia a interação com outras janelas da aplicação enquanto essa tiver aberta.

        tk.Label(self.top, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nome = tk.Entry(self.top)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Categoria:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_cat = tk.Entry(self.top)
        self.entry_cat.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Preço:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_preco = tk.Entry(self.top)
        self.entry_preco.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Quantidade:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_qtd = tk.Entry(self.top)
        self.entry_qtd.grid(row=3, column=1, padx=5, pady=5)


        tk.Label(self.top, text="Fornecedor:").grid(row=4, column=0, padx=5, pady=5)

        self.valores_cb_forn = []
        for item in repo.listar_fornecedores():
            self.valores_cb_forn.append({"id": item["id_fornecedor"],
                                    "nome": item["nome"]})

        self.cb_forn = ttk.Combobox(self.top, values=[item["nome"] for item in self.valores_cb_forn], state="readonly")
        self.cb_forn.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Estoque mínimo:").grid(row=5, column=0, padx=5, pady=5)
        self.entry_est_min = tk.Entry(self.top)
        self.entry_est_min.grid(row=5, column=1, padx=5, pady=5)

        ttk.Button(self.top, text="Salvar", command=self.ok).grid(row=6, column=0, columnspan=2, pady=10)

        #Se for edição, preenche os campos
        if produto:
            self.entry_nome.insert(0, produto["nome"])
            self.entry_cat.insert(0, produto["categoria"])
            self.entry_preco.insert(0, produto["preco"])
            self.entry_qtd.insert(0, produto["quantidade"])
            self.entry_est_min.insert(0, produto["estoque_minimo"])

            if produto.get("id_fornecedor"):
                forn = repo.buscar_fornecedor(produto["id_fornecedor"])
                self.cb_forn.set(forn["nome"])
            else:
                self.cb_forn.set("")

    def ok(self):
        try:
            nome = self.entry_nome.get().strip()
            if not nome:
                raise ValueError("Insira o nome!")
            
            cat = self.entry_cat.get().strip()
            if not cat:
                raise ValueError("Insira a categoria!")
            
            if self.cb_forn.get():
                #Extrai só o id do fornecedor
                id_forn = next((item["id"] for item in self.valores_cb_forn if item["nome"] == self.cb_forn.get()), None)
            else:
                raise ValueError("Selecione um fornecedor!")
            
            #Validação de preço
            valor = self.entry_preco.get().strip()
            if not valor:
                raise ValueError("Insira o preço!")
            try:
                preco = float(valor)
            except:
                raise ValueError("Insira um preço válido!")
            if preco <= 0:
                raise ValueError("O preço deve ser maior que zero!")
                
            #Validação de quantidade
            valor = self.entry_qtd.get().strip()
            if not valor:
                raise ValueError("Insira a quantidade!")
            try:
                qtd = int(valor)
            except:
                raise ValueError("Insira uma quantidade válida!")
            if qtd <= 0:
                raise ValueError("A quantidade deve ser maior que zero!")
                
            #Validação de estoque mínimo
            valor = self.entry_est_min.get().strip()
            if not valor:
                raise ValueError("Insira o estoque mínimo!")
            try:
                est_min = int(valor)
            except:
                raise ValueError("Insira um estoque mínimo válido!")
            if est_min <= 0:
                raise ValueError("O estoque mínimo deve ser maior que zero!")
            
            self.result = (nome, cat, preco, qtd, id_forn, est_min)
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Preencha corretamente os campos!\n{e}")
#end region

# region Modal Pessoa
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

        # Campos principais
        ttk.Label(self.top, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.e_nome = ttk.Entry(self.top, width=40)
        self.e_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.top, text="Telefone:").grid(row=1, column=0, padx=5, pady=5)
        self.e_tel = ttk.Entry(self.top, width=20)
        self.e_tel.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.top, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.e_email = ttk.Entry(self.top, width=30)
        self.e_email.grid(row=2, column=1, sticky="w", columnspan=2, padx=5, pady=5)

        # Endereço
        self.valores_cb_estado = []
        for e in repo.listar_estados():
            self.valores_cb_estado.append({"id": e["id_estado"], "nome": e["nome"]})
        
        ttk.Label(self.top, text="Estado:").grid(row=3, column=0, padx=5, pady=5)
        self.cb_estado = ttk.Combobox(self.top, values=[e["nome"] for e in self.valores_cb_estado], state="readonly")
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

                    #Se a cidade atual não está na lista, limpa
                    if self.cb_cidade.get() not in lista_cidades:
                        self.cb_cidade.set("")

        self.cb_estado.bind("<<ComboboxSelected>>", carregar_cidades)

        ttk.Label(self.top, text="Logradouro:").grid(row=5, column=0, padx=5, pady=5)
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

        # Botões
        ttk.Button(self.top, text="Salvar", command=self.on_save).grid(row=9, column=0, pady=10)
        ttk.Button(self.top, text="Cancelar", command=self.top.destroy).grid(row=9, column=1, pady=10)

        # Preenche se for edição
        self.id_endereco = None
        if pessoa:
            self.e_nome.insert(0, pessoa["nome"])
            self.e_tel.insert(0, pessoa["telefone"])
            self.e_email.insert(0, pessoa["email"])
            self.id_endereco = pessoa["id_endereco"]
            self.cb_estado.set(pessoa["estado"])
            carregar_cidades()
            self.cb_cidade.set(pessoa["cidade"])
            self.e_rua.insert(0, pessoa["rua"])
            self.e_numero.insert(0, pessoa["numero"])
            self.e_bairro.insert(0, pessoa["bairro"])
            self.e_cep.insert(0, pessoa["cep"])

    def on_save(self):
        try:
            nome = self.e_nome.get().strip()
            if not nome:
                raise ValueError("Insira o nome!")
            
            email = self.e_email.get().strip()
            if not email:
                raise ValueError("Insira o email!")
            
            rua = self.e_rua.get().strip()
            if not rua:
                raise ValueError("Insira a rua!")
            
            bairro = self.e_bairro.get().strip()
            if not bairro:
                raise ValueError("Insira o bairro!")
            
            #Validação de numero
            valor = self.e_numero.get().strip()
            if not valor:
                raise ValueError("Insira o número!")
            try:
                numero = int(valor)
            except:
                raise ValueError("Insira um número válido!")
            if numero < 0:
                raise ValueError("O número deve ser positivo!")
            
            #Validacao de telefone
            tel = self.e_tel.get().strip()
            if (not tel.isdigit()) or (len(tel) > 11 or len(tel) < 10):
                raise ValueError("Insira um telefone válido!")
            
            #Validação de CEP
            cep = self.e_cep.get().strip()
            if (not cep.isdigit()) or len(cep) != 8:
                raise ValueError("Insira um CEP válido!")
            
            #Validação de estado
            estado_nome = self.cb_estado.get()
            if not estado_nome:
                raise ValueError("Selecione um estado!")
            else:
                #Seleciona o id_estado a partir do nome
                id_estado = next((e["id"] for e in self.valores_cb_estado if e["nome"] == estado_nome), None)
                #Validação de cidade
                cidade_nome = self.cb_cidade.get().strip()
                if not cidade_nome:
                    raise ValueError("Selecione ou insira uma cidade!")
                else: #Se estado e cidade forem válidos
                    cidade = next((c for c in repo.listar_cidades(id_estado) if c["nome"] == cidade_nome), None)
                    if cidade:
                        id_cidade = cidade["id_cidade"]
                    else:
                        # Se a cidade não existir, cria no banco
                        id_cidade = repo.inserir_cidade(cidade_nome, id_estado)

        except Exception as e:
            messagebox.showerror("Erro", f"Preencha corretamente os campos!\n{e}")
            return

        # Atualizando ou criando o endereço
        if self.id_endereco:
            repo.atualizar_endereco(self.id_endereco, rua, numero, bairro, cep, id_cidade)
        else:
            self.id_endereco = repo.inserir_endereco(rua, numero, bairro, cep, id_cidade)

        # Resultado final
        self.result = (nome, tel, email, self.id_endereco)
        self.top.destroy()
#end region

# region Modal Venda
class VendaDialog:
    """Janela para cadastrar venda"""
    def __init__(self, parent):
        
        self.top = tk.Toplevel(parent)
        self.top.title("Adicionar Venda")
        self.result = None
        self.top.transient(parent) #Deixa a janela sempre na frente e minimiza junto com a janela principal (parent).
        self.top.grab_set() #Bloqueia a interação com outras janelas da aplicação enquanto essa tiver aberta.

        # Seleção de cliente
        tk.Label(self.top, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        clientes = repo.listar_clientes()
        self.cb_cliente = ttk.Combobox(self.top, values=[f"{c['id_cliente']} - {c['nome']}" for c in clientes], state="readonly")
        self.cb_cliente.grid(row=0, column=1, padx=5, pady=5, columnspan=3, sticky="ew")


        # Tree para itens da venda
        colunas = ("ID", "Produto", "Quantidade", "Preço Unitário", "Subtotal")
        self.tree_itens = ttk.Treeview(self.top, columns=colunas, show="headings", height=5)
        
        for col in colunas:
            self.tree_itens.heading(col, text=col)
            self.tree_itens.column(col, width=150)

        self.tree_itens.grid(row=1, column=0, columnspan=4, padx=5, pady=5)


        # Seleção de produto
        tk.Label(self.top, text="Produto:").grid(row=2, column=0, padx=5, pady=5)
        produtos = repo.listar_produtos()
        self.cb_produto = ttk.Combobox(self.top, values=[f"{p['id_produto']} - {p['nome']} ({p['quantidade']} em estoque)" for p in produtos], width=50, state="readonly")
        self.cb_produto.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Quantidade:").grid(row=2, column=2, padx=5, pady=5)
        self.entry_qtd = tk.Entry(self.top)
        self.entry_qtd.grid(row=2, column=3, padx=5, pady=5)


        ttk.Button(self.top, text="Adicionar Item", command=self.add_item).grid(row=3, column=0, columnspan=4, pady=5)

        # Botão de salvar (precisa da referência para desabilitar no clique)
        self.btn_salvar = ttk.Button(self.top, text="Salvar Venda", command=self.salvar_venda)
        self.btn_salvar.grid(row=4, column=0, columnspan=4, pady=10)


        # Função para adicionar item na tree
    def add_item(self):
        try:
            #Verifica se um produto foi selecionado
            if self.cb_produto.get():
                valor_cb = self.cb_produto.get()
                id_produto = int(valor_cb.split(" - ")[0])
            else:
                raise ValueError("Selecione um produto!")
            
            #Validação de quantidade
            valor = self.entry_qtd.get()
            if not valor:
                raise ValueError("Insira a quantidade!")
            
            try:
                qtd = int(valor)
            except:
                raise ValueError("Insira uma quantidade válida!")
            
            if qtd <= 0:
                raise ValueError("A quantidade deve ser maior que zero!")

        except Exception as e:
            messagebox.showerror("Erro", f"Preencha corretamente os campos!\n{e}")
            return

        # Busca direto pelo ID (mais seguro que pelo nome)
        produto = repo.buscar_produto(id_produto)
        nome_produto = produto["nome"]
        estoque_disponivel = produto["quantidade"]

        # Valida quantidade disponível
        if qtd > estoque_disponivel:
            messagebox.showerror(
                "Estoque insuficiente",
                f"O produto '{nome_produto}' possui apenas {estoque_disponivel} em estoque.\n"
                f"Você tentou adicionar {qtd}."
            )
            return

        # Se passou na validação, insere na tree
        preco = repo.get_preco_produto(id_produto)
        subtotal = qtd * preco
        self.tree_itens.insert(
            "", "end",
            values=(id_produto, nome_produto, qtd, f"{preco:.2f}", f"{subtotal:.2f}")
        )

        # Limpa os campos para uma nova inserção
        self.entry_qtd.delete(0, "end")
        self.cb_produto.set("")


    # Função para salvar venda
    def salvar_venda(self):
        # Desabilita o botão imediatamente para evitar clique duplo
        self.btn_salvar.config(state="disabled")

        if not self.cb_cliente.get():
            messagebox.showerror("Erro", "Selecione um cliente.")
            self.btn_salvar.config(state="normal")
            return
        
        id_cliente = int(self.cb_cliente.get().split(" - ")[0])

        itens = []
        for it in self.tree_itens.get_children():
            vals = self.tree_itens.item(it)["values"]
            id_produto, _, qtd, preco, subtotal = vals
            itens.append((id_produto, int(qtd), float(preco)))

        if not itens:
            messagebox.showerror("Erro", "Adicione ao menos um produto.")
            self.btn_salvar.config(state="normal")
            return

        self.result = (id_cliente, itens)
        self.top.destroy()
#endregion

# region Modal Período Datas
class PeriodoDataDialog:
    def __init__(self, parent):
        """Abre uma janela com calendário para escolher data inicial e final."""
        self.top = tk.Toplevel(parent)
        self.top.title("Selecionar Período")

        self.top.transient(parent) #Deixa a janela sempre na frente e minimiza junto com a janela principal (parent).
        self.top.grab_set() #Bloqueia a interação com outras janelas da aplicação enquanto essa tiver aberta.
        
        self.result = {}

        tk.Label(self.top, text="Data inicial:").grid(row=0, column=0, padx=5, pady=5)
        self.cal_inicio = DateEntry(self.top, date_pattern="dd-mm-yyyy", firstweekday="sunday", locale="pt_BR", state="readonly")
        self.cal_inicio.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Data final:").grid(row=1, column=0, padx=5, pady=5)
        self.cal_fim = DateEntry(self.top, date_pattern="dd-mm-yyyy", firstweekday="sunday", locale="pt_BR", state="readonly")
        self.cal_fim.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.top, text="OK", command=self.confirmar).grid(row=2, column=0, columnspan=2, pady=10)

    def confirmar(self):
        self.result["data_inicio"] = self.cal_inicio.get_date().strftime("%Y-%m-%d")
        self.result["data_fim"] = self.cal_fim.get_date().strftime("%Y-%m-%d")
        self.top.destroy()
        return self.result
#endregion