"""
Módulo ui_main
--------------
Interface principal (Tkinter + abas).
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import repository as repo
from ui_dialogs import ProdutoDialog, PessoaDialog, VendaDialog, PeriodoDataDialog


class App:
    """Classe principal da aplicação."""

    def __init__(self, root):
        self.root = root
        self.root.title("Distribuidora - Sistema")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Abas
        self.frame_produtos = ttk.Frame(self.notebook)
        self.frame_clientes = ttk.Frame(self.notebook)
        self.frame_fornecedores = ttk.Frame(self.notebook)
        self.frame_vendas = ttk.Frame(self.notebook)
        self.frame_relatorios = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_produtos, text="Produtos")
        self.notebook.add(self.frame_clientes, text="Clientes")
        self.notebook.add(self.frame_fornecedores, text="Fornecedores")
        self.notebook.add(self.frame_vendas, text="Vendas")
        self.notebook.add(self.frame_relatorios, text="Relatórios")

        # Setup
        self.setup_produtos()
        self.setup_clientes()
        self.setup_fornecedores()
        self.setup_vendas()
        self.setup_relatorios()

    # region Produtos
    def setup_produtos(self):
        """Monta a aba Produtos"""

        # Frame de botões
        frame_botoes = ttk.Frame(self.frame_produtos)
        frame_botoes.pack(fill="x", pady=5)

        ttk.Button(frame_botoes, text="Adicionar", takefocus=False, command=self.add_produto).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Editar", takefocus=False, command=self.edit_produto).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Excluir", takefocus=False, command=self.del_produto).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Atualizar", takefocus=False, command=self.load_produtos).pack(side="left", padx=5)


        # Treeview
        colunas = ("ID","Nome","Categoria","Preço","Quantidade","Fornecedor","Estoque Mínimo")
        self.tree_prod = ttk.Treeview(self.frame_produtos, columns=colunas, show="headings")

        for col in colunas:
            self.tree_prod.heading(col, text=col)
            self.tree_prod.column(col, width=150)

        self.tree_prod.pack(fill="both", expand=True)

        self.load_produtos()


    def load_produtos(self):
        for i in self.tree_prod.get_children(): self.tree_prod.delete(i)
        for p in repo.listar_produtos():
            self.tree_prod.insert("", "end", values=(p["id_produto"],p["nome"],p["categoria"],
                                                     p["preco"],p["quantidade"],p["fornecedor"],p["estoque_minimo"]))

    def add_produto(self):
        dlg = ProdutoDialog(self.root)
        self.root.wait_window(dlg.top)
        if dlg.result:
            #Captura as informações vindas do modal de adição de produto
            nome, cat, preco, qtd, forn, est_min = dlg.result

            # Insere novo produto
            repo.inserir_produto(nome, cat, preco, qtd, forn, est_min)
            messagebox.showinfo("Sucesso", f"Produto '{nome}' adicionado.")

            #Atualiza a tree de produtos
            self.load_produtos()

    def del_produto(self):
        """Deleta produto selecionado da tabela e do banco"""
        sel = self.tree_prod.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto para deletar.")
            return

        item = self.tree_prod.item(sel[0])
        id_prod = item["values"][0]

        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o produto {id_prod}?"):
            repo.deletar_produto(id_prod)
            self.load_produtos()
    
    def edit_produto(self):
        """Edita o produto selecionado."""
        sel = self.tree_prod.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return

        item = self.tree_prod.item(sel[0])
        id_produto = item["values"][0]
        produto = repo.buscar_produto(id_produto)

        dlg = ProdutoDialog(self.root, produto)
        self.root.wait_window(dlg.top)

        if dlg.result:
            nome, cat, preco, qtd, forn, est_min = dlg.result
            repo.atualizar_produto(id_produto, nome, cat, preco, qtd, forn, est_min)
            messagebox.showinfo("Sucesso", f"Produto {id_produto} atualizado!")
            self.load_produtos()
    #endregion


    # region Clientes
    def setup_clientes(self):
        # Frame de botões
        frame_botoes = ttk.Frame(self.frame_clientes)
        frame_botoes.pack(fill="x", pady=5)

        ttk.Button(frame_botoes, text="Adicionar", takefocus=False, command=self.add_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Editar", takefocus=False, command=self.edit_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Excluir", takefocus=False, command=self.del_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Atualizar", takefocus=False, command=self.load_clientes).pack(side="left", padx=5)

        # Treeview de clientes
        colunas = ("ID", "Nome", "Telefone", "Email", "Endereço")
        self.tree_clientes = ttk.Treeview(self.frame_clientes, columns=colunas, show="headings")

        for col in colunas:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=150)

        self.tree_clientes.pack(fill="both", expand=True)

        self.load_clientes()
        self.tree_clientes.focus_set()


    def load_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)

        for c in repo.listar_clientes():
            endereco_fmt = f"{c['rua']}, {c['numero']} - {c['bairro']}, {c['cidade']}/{c['estado']} - {c['cep']}"
            self.tree_clientes.insert(
                "", "end",
                values=(c["id_cliente"], c["nome"], c["telefone"], c["email"], endereco_fmt)
            )

    def add_cliente(self):
        dlg = PessoaDialog(self.root, title="Novo Cliente")
        self.root.wait_window(dlg.top)

        if dlg.result:
            nome, tel, email, id_endereco = dlg.result
            repo.inserir_cliente(nome, tel, email, id_endereco)
            messagebox.showinfo("Sucesso", "Cliente adicionado!")
            self.load_clientes()


    def edit_cliente(self):
        sel = self.tree_clientes.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return

        item = self.tree_clientes.item(sel[0])
        id_cliente = item["values"][0]

        cliente = repo.buscar_cliente(id_cliente)
        dlg = PessoaDialog(self.root, title="Editar Cliente", pessoa=cliente)
        self.root.wait_window(dlg.top)

        if dlg.result:
            nome, tel, email, id_endereco = dlg.result
            repo.atualizar_cliente(id_cliente, nome, tel, email, id_endereco)
            messagebox.showinfo("Sucesso", f"Cliente {id_cliente} atualizado!")
            self.load_clientes()


    def del_cliente(self):
        sel = self.tree_clientes.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return

        item = self.tree_clientes.item(sel[0])
        id_cliente = item["values"][0]

        if messagebox.askyesno("Confirmar", f"Excluir cliente {id_cliente}?"):
            repo.deletar_cliente(id_cliente)
            self.load_clientes()
    #endregion

    #region Fornecedores
    def setup_fornecedores(self):
            # Frame de botões
        frame_botoes = ttk.Frame(self.frame_fornecedores)
        frame_botoes.pack(fill="x", pady=5)

        ttk.Button(frame_botoes, text="Adicionar", takefocus=False, command=self.add_fornecedor).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Editar", takefocus=False, command=self.edit_fornecedor).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Excluir", takefocus=False, command=self.del_fornecedor).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Atualizar", takefocus=False, command=self.load_fornecedores).pack(side="left", padx=5)

        # Treeview de fornecedores
        colunas = ("ID", "Nome", "Telefone", "Email", "Endereço")
        self.tree_fornecedores = ttk.Treeview(self.frame_fornecedores, columns=colunas, show="headings")

        for col in colunas:
            self.tree_fornecedores.heading(col, text=col)
            self.tree_fornecedores.column(col, width=150)

        self.tree_fornecedores.pack(fill="both", expand=True)
        self.load_fornecedores()


    def load_fornecedores(self):
        for item in self.tree_fornecedores.get_children():
            self.tree_fornecedores.delete(item)

        for f in repo.listar_fornecedores():
            endereco_fmt = f"{f['rua']}, {f['numero']} - {f['bairro']}, {f['cidade']}/{f['estado']} - {f['cep']}"
            self.tree_fornecedores.insert(
                "", "end",
                values=(f["id_fornecedor"], f["nome"], f["telefone"], f["email"], endereco_fmt)
            )

    
    def del_fornecedor(self):
        """Deleta fornecedor selecionado."""
        sel = self.tree_fornecedores.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para deletar.")
            return
        item = self.tree_fornecedores.item(sel[0])
        id_forn = item["values"][0]

        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o fornecedor {id_forn}?"):
            repo.deletar_fornecedor(id_forn)
            self.load_fornecedores()


    def add_fornecedor(self):
        dlg = PessoaDialog(self.root, title="Novo Fornecedor")
        self.root.wait_window(dlg.top)

        if dlg.result:
            nome, tel, email, id_endereco = dlg.result
            repo.inserir_fornecedor(nome, tel, email, id_endereco)
            messagebox.showinfo("Sucesso", "Fornecedor atualizado!")
            self.load_fornecedores()


    def edit_fornecedor(self):
        sel = self.tree_fornecedores.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para editar.")
            return

        item = self.tree_fornecedores.item(sel[0])
        id_fornecedor = item["values"][0]

        fornecedor = repo.buscar_fornecedor(id_fornecedor)
        dlg = PessoaDialog(self.root, title="Editar Fornecedor", pessoa=fornecedor)
        self.root.wait_window(dlg.top)

        if dlg.result:
            nome, tel, email, id_endereco = dlg.result
            repo.atualizar_fornecedor(id_fornecedor, nome, tel, email, id_endereco)
            messagebox.showinfo("Sucesso", f"Fornecedor {id_fornecedor} atualizado!")
            self.load_fornecedores()
    #endregion


    # region Vendas
    def setup_vendas(self):
        # Botões
        frame_botoes = ttk.Frame(self.frame_vendas)
        frame_botoes.pack(pady=5)

        ttk.Button(frame_botoes, text="Adicionar", takefocus=False, command=self.add_venda).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Atualizar", takefocus=False, command=self.load_vendas).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Excluir", takefocus=False, command=self.del_venda).pack(side="left", padx=5)


        # Treeview principal (vendas)
        colunas = ("ID Venda", "ID Cliente", "Cliente", "Valor Total", "Data")
        self.tree_vend = ttk.Treeview(self.frame_vendas, columns=colunas, show="headings", height=8)

        for col in colunas:
            self.tree_vend.heading(col, text=col)
            self.tree_vend.column(col, width=150)

        self.tree_vend.pack(fill="both", expand=True, pady=5)
        self.load_vendas()

        # Quando selecionar uma venda, carrega os itens
        self.tree_vend.bind("<<TreeviewSelect>>", self.on_venda_select)


        # Treeview secundária (itens da venda)
        colunas = ("ID", "Produto", "Quantidade", "Preço Unitário", "Subtotal")
        self.tree_itens = ttk.Treeview(self.frame_vendas, columns=colunas, show="headings", height=5)

        for col in colunas:
            self.tree_itens.heading(col, text=col)
            self.tree_itens.column(col, width=150)

        self.tree_itens.pack(fill="both", expand=True, pady=5)


    def on_venda_select(self, event):
        """
        Quando o usuário seleciona uma venda, exibe os itens dessa venda na tree_itens.
        """
        # limpa tree_itens
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)

        selected = self.tree_vend.selection()  
        if not selected:
            return

        venda_id = self.tree_vend.item(selected[0])["values"][0]
        itens = repo.listar_itens_venda(venda_id)

        for it in itens:
            self.tree_itens.insert("","end",values=(
                    it["id_produto"],
                    it["produto"],
                    it["quantidade"],
                    f"{it['preco_unitario']:.2f}",
                    f"{it['subtotal']:.2f}"
                )
            )

    def add_venda(self):
        dlg = VendaDialog(self.root)
        self.root.wait_window(dlg.top)

        if dlg.result:
            id_cliente, itens = dlg.result
            
            try:
                repo.inserir_venda(id_cliente, itens)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao inserir venda!\n{e}")
            
            messagebox.showinfo("Sucesso", "Venda registrada!")
            self.load_vendas()
            self.load_produtos() #Atualiza automaticamente a tree de produtos com o novo estoque
            
    def load_vendas(self):
        for i in self.tree_vend.get_children():
            self.tree_vend.delete(i)

        rows = repo.listar_vendas()
        for v in rows:
            self.tree_vend.insert(
                "",
                "end",
                values=(
                    v["id_venda"],
                    v["id_cliente"],
                    v["cliente"],
                    f"{v['valor_total']:.2f}",
                    v["data_venda"].strftime("%d/%m/%Y %H:%M") if v["data_venda"] else ""
                )
            )

    def del_venda(self):
        """Deleta venda selecionada da tabela e do banco"""
        sel = self.tree_vend.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma venda para deletar.")
            return

        item = self.tree_vend.item(sel[0])
        id_venda = item["values"][0]

        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar a venda {id_venda}?"):
            repo.deletar_venda(id_venda)
            self.load_vendas()
    #endregion

    # region Relatórios
    def setup_relatorios(self):
        """Monta a aba Relatórios com botões padronizados sem foco."""

        frame_botoes = ttk.Frame(self.frame_relatorios)
        frame_botoes.pack(pady=5)

        largura_padrao = 25  #Largura fixa dos botões

        ttk.Button(frame_botoes, text="Estoque baixo", width=largura_padrao,
                takefocus=False, command=self.report_estoque_baixo).pack(pady=5)
        ttk.Button(frame_botoes, text="Histórico por Cliente", width=largura_padrao,
                takefocus=False, command=self.report_vendas_cliente).pack(pady=5)
        ttk.Button(frame_botoes, text="Histórico por Produto", width=largura_padrao,
                takefocus=False, command=self.report_vendas_produto).pack(pady=5)
        ttk.Button(frame_botoes, text="Histórico por Período", width=largura_padrao,
                takefocus=False, command=self.report_vendas_periodo).pack(pady=5)

        # Área de texto somente leitura
        self.txt_rel = tk.Text(self.frame_relatorios, height=20, state="disabled")
        self.txt_rel.pack(fill="both", expand=True)


    def report_estoque_baixo(self):
        self.txt_rel.config(state="normal")   # habilita para edição
        #Exclui todo o texto, começando da primeira linha (inicia em 1) e primeira coluna (inicia em 0) -> "1.0"
        self.txt_rel.delete("1.0", "end")
        rows = [p for p in repo.listar_produtos() if p["quantidade"] <= p["estoque_minimo"]]
        if not rows:
            self.txt_rel.insert("end", "Nenhum produto com estoque baixo\n")
        else:
            for r in rows:
                self.txt_rel.insert("end", f"{r['id_produto']} - {r['nome']} | Qtd {r['quantidade']} | Min {r['estoque_minimo']}\n")
        self.txt_rel.config(state="disabled")  # trava novamente


    def report_vendas_cliente(self):
        clientes = repo.listar_clientes()
        if not clientes:
            messagebox.showwarning("Aviso", "Nenhum cliente cadastrado.")
            return
        escolha = simpledialog.askinteger(
            "Histórico por Cliente",
            "Digite o ID do cliente:\n" + "\n".join(f"{c['id_cliente']} - {c['nome']}" for c in clientes)
        )
        if not escolha:
            return

        rows = repo.historico_vendas_por_cliente(escolha)
        self.txt_rel.config(state="normal")
        self.txt_rel.delete("1.0", "end")
        if not rows:
            self.txt_rel.insert("end", "Nenhuma venda encontrada.\n")
        else:
            self.txt_rel.insert("end", f"Histórico de vendas do Cliente {escolha}:\n\n")
            for r in rows:
                self.txt_rel.insert("end",
                    f"Venda {r['id_venda']} | Data: {r['data_venda']} | Total: R$ {r['valor_total']:.2f}\n"
                    f"   Produto: {r['produto']} x{r['quantidade']} @ {r['preco_unitario']:.2f} = {r['subtotal']:.2f}\n\n"
                )
            total_historico = repo.total_consumido_por_cliente(escolha)["SUM(valor_total)"]
            self.txt_rel.insert("end", f"Total consumido: {total_historico:.2f}\n")
        self.txt_rel.config(state="disabled")

    def report_vendas_produto(self):
        produtos = repo.listar_produtos()
        if not produtos:
            messagebox.showwarning("Aviso", "Nenhum produto cadastrado.")
            return
        escolha = simpledialog.askinteger(
            "Histórico por Produto",
            "Digite o ID do produto:\n" + "\n".join(f"{p['id_produto']} - {p['nome']}" for p in produtos)
        )
        if not escolha:
            return

        rows = repo.historico_vendas_por_produto(escolha)
        self.txt_rel.config(state="normal")
        self.txt_rel.delete("1.0", "end")
        if not rows:
            self.txt_rel.insert("end", "Nenhuma venda encontrada.\n")
        else:
            self.txt_rel.insert("end", f"Histórico de vendas do Produto {escolha}:\n\n")
            for r in rows:
                self.txt_rel.insert("end",
                    f"Venda {r['id_venda']} | Data: {r['data_venda']} | Cliente: {r['cliente']} | Total: R$ {r['valor_total']:.2f}\n"
                    f"   Quantidade: {r['quantidade']} @ {r['preco_unitario']:.2f} = {r['subtotal']:.2f}\n\n"
                )
        self.txt_rel.config(state="disabled")

    def report_vendas_periodo(self):
        dlg = PeriodoDataDialog(self.root)
        self.root.wait_window(dlg.top)
        if dlg.result:
            #Captura as informações vindas do modal de adição de produto
            data_inicio = dlg.result["data_inicio"]
            data_fim = dlg.result["data_fim"]
        else:
            return

        rows = repo.historico_vendas_por_periodo(data_inicio, data_fim)
        self.txt_rel.config(state="normal")
        self.txt_rel.delete("1.0", "end")

        if not rows:
            self.txt_rel.insert("end", "Nenhuma venda encontrada nesse período.\n")
        else:
            total = 0
            for r in rows:
                self.txt_rel.insert(
                    "end",
                    f"Venda {r['id_venda']} | Cliente: {r['cliente']} | "
                    f"Total: R$ {r['valor_total']:.2f} | Data: {r['data_venda']}\n"
                )
                total += r["valor_total"]
            self.txt_rel.insert("end", f"Total faturado no período: R$ {total:.2f}\n")
            
        self.txt_rel.config(state="disabled")

    #endregion


