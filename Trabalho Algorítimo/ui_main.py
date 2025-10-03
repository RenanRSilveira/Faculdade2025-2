"""
Módulo ui_main
--------------
Interface principal (Tkinter + abas).
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import repository as repo
from ui_dialogs import ProdutoDialog, PessoaDialog
from tkcalendar import DateEntry


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

        self.notebook.add(self.frame_relatorios, text="Relatórios")

        # Setup
        self.setup_produtos()
        self.setup_clientes()
        self.setup_fornecedores()
        self.setup_vendas()
        self.setup_relatorios()

    # ---------------- Produtos ----------------
    def setup_produtos(self):
        """Monta a aba Produtos"""

        # Frame de botões
        frame_botoes = ttk.Frame(self.frame_produtos)
        frame_botoes.pack(fill="x", pady=5)

        ttk.Button(frame_botoes, text="Adicionar", takefocus=False, command=self.add_produto).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Atualizar", takefocus=False, command=self.load_produtos).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Deletar", takefocus=False, command=self.del_produto).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Editar", takefocus=False, command=self.edit_produto).pack(side="left", padx=5)


        # Treeview
        colunas = ("id_produto","nome","categoria","preco","quantidade","fornecedor","estoque_minimo")
        self.tree_prod = ttk.Treeview(self.frame_produtos, columns=colunas, show="headings")
        for c in colunas:
            self.tree_prod.heading(c, text=c.upper())
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
            nome, cat, preco, qtd, forn, est_min = dlg.result

            # Verifica se o produto já existe com o mesmo fornecedor
            prod_existente = repo.buscar_produto_por_nome_fornecedor(nome, forn)

            if prod_existente:
                # Atualiza a quantidade
                repo.atualizar_quantidade_produto(prod_existente["id_produto"], qtd)
                messagebox.showinfo(
                    "Atualizado", 
                    f"A quantidade do produto '{nome}' (Fornecedor {forn}) foi aumentada em {qtd}."
                )
            else:
                # Insere novo produto
                repo.inserir_produto(nome, cat, preco, qtd, forn, est_min)
                messagebox.showinfo("Sucesso", f"Produto '{nome}' adicionado.")

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


    # ---------------- Clientes ----------------
    def setup_clientes(self):
        # --- Frame de botões ---
        frame_botoes = ttk.Frame(self.frame_clientes)
        frame_botoes.pack(fill="x", pady=5)

        ttk.Button(frame_botoes, text="Adicionar", takefocus=False, command=self.add_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Editar", takefocus=False, command=self.edit_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Excluir", takefocus=False, command=self.del_cliente).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Atualizar", takefocus=False, command=self.atualizar_clientes).pack(side="left", padx=5)

        # --- Treeview de clientes ---


        colunas = ("ID", "Nome", "Telefone", "Email", "Endereço")
        self.tree_clientes = ttk.Treeview(self.frame_clientes, columns=colunas, show="headings")

        for col in colunas:
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=150)

        self.tree_clientes.pack(fill="both", expand=True)

        # Botões
        frame_btn = ttk.Frame(self.frame_clientes)
        frame_btn.pack(fill="x", pady=5)

        ttk.Button(frame_btn, text="Adicionar", command=self.add_cliente).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="Editar", command=self.edit_cliente).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="Excluir", command=self.del_cliente).pack(side="left", padx=5)

        # Preenche tabela
        self.atualizar_clientes()
        self.tree_clientes.focus_set()



    def atualizar_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)

        for c in repo.listar_clientes():
            endereco_fmt = f"{c['rua']}, {c['numero']} - {c['bairro']}, {c['cidade']}/{c['estado']} - {c['cep']}"
            self.tree_clientes.insert(
                "", "end",
                values=(c["id_cliente"], c["nome"], c["telefone"], c["email"], endereco_fmt)
            )



    def load_clientes(self):
        for i in self.tree_cli.get_children(): self.tree_cli.delete(i)
        for c in repo.listar_clientes():
            self.tree_cli.insert("", "end", values=(c["id_cliente"],c["nome"],c["telefone"],c["email"]))

    def add_cliente(self):
        dlg = PessoaDialog(self.root, title="Novo Cliente")
        self.root.wait_window(dlg.top)

        if dlg.result:
            nome, tel, email, id_endereco = dlg.result
            repo.inserir_cliente(nome, tel, email, id_endereco)
            self.atualizar_clientes()


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
            self.atualizar_clientes()


    def del_cliente(self):
        sel = self.tree_clientes.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return

        item = self.tree_clientes.item(sel[0])
        id_cliente = item["values"][0]

        if messagebox.askyesno("Confirmar", f"Excluir cliente {id_cliente}?"):
            repo.excluir_cliente(id_cliente)
            self.atualizar_clientes()


    # ---------------- Fornecedores ----------------
    def setup_fornecedores(self):
            # --- Frame de botões ---
        frame_botoes = ttk.Frame(self.frame_fornecedores)
        frame_botoes.pack(fill="x", pady=5)

        ttk.Button(frame_botoes, text="Adicionar", takefocus=False, command=self.add_fornecedor).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Editar", takefocus=False, command=self.edit_fornecedor).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Excluir", takefocus=False, command=self.del_fornecedor).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Atualizar", takefocus=False, command=self.atualizar_fornecedores).pack(side="left", padx=5)

        # --- Treeview de fornecedores ---
        colunas = ("ID", "Nome", "Telefone", "Email", "Endereço")
        self.tree_fornecedores = ttk.Treeview(self.frame_fornecedores, columns=colunas, show="headings")

        for col in colunas:
            self.tree_fornecedores.heading(col, text=col)
            self.tree_fornecedores.column(col, width=150)

        self.tree_fornecedores.pack(fill="both", expand=True)

        # Botões
        frame_btn = ttk.Frame(self.frame_fornecedores)
        frame_btn.pack(fill="x", pady=5)

        ttk.Button(frame_btn, text="Adicionar", command=self.add_fornecedor, takefocus=False).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="Editar", command=self.edit_fornecedor, takefocus=False).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="Excluir", command=self.del_fornecedor, takefocus=False).pack(side="left", padx=5)

        # Preenche tabela
        self.atualizar_fornecedores()
       



    def atualizar_fornecedores(self):
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


    def load_fornecedores(self):
        for i in self.tree_fornecedores.get_children():
            self.tree_fornecedores.delete(i)

        fornecedores = repo.listar_fornecedores()
        for f in fornecedores:
            endereco_fmt = (
                f"{f['rua']}, {f['numero']} - {f['bairro']}, "
                f"{f['cidade']}/{f['estado']} - {f['cep']}"
                if f["rua"] else ""
            )
            self.tree_fornecedores.insert(
                "", "end",
                values=(f["id_fornecedor"], f["nome"], f["telefone"], f["email"], endereco_fmt)
            )

    def add_fornecedor(self):
        dlg = PessoaDialog(self.root, title="Novo Fornecedor")
        self.root.wait_window(dlg.top)

        if dlg.result:
            nome, tel, email, id_endereco = dlg.result
            repo.inserir_fornecedor(nome, tel, email, id_endereco)
            self.atualizar_fornecedores()


    def del_fornecedor(self):
        """Deleta fornecedor selecionado da tabela e do banco"""
        sel = self.tree_fornecedores.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para deletar.")
            return

        item = self.tree_fornecedores.item(sel[0])
        id_forn = item["values"][0]

        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o fornecedor {id_forn}?"):
            repo.deletar_fornecedor(id_forn)
            self.load_fornecedores()


    # ---------------- Vendas ----------------
    def setup_vendas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Vendas")

        # Treeview principal (vendas)
        colunas = ("id_venda", "id_cliente", "cliente", "valor_total", "data_venda")
        self.tree_vend = ttk.Treeview(frame, columns=colunas, show="headings", height=8)

        for c in colunas:
            self.tree_vend.heading(c, text=c.upper())

        self.tree_vend.pack(fill="both", expand=True, pady=5)

        # Quando selecionar uma venda, carrega os itens
        self.tree_vend.bind("<<TreeviewSelect>>", self.on_venda_select)



        # Treeview secundária (itens da venda)
        colunas_itens = ("id_produto", "produto", "quantidade", "preco_unitario", "subtotal")
        self.tree_itens = ttk.Treeview(frame, columns=colunas_itens, show="headings", height=5)

        self.tree_itens.heading("id_produto", text="ID PRODUTO")
        self.tree_itens.heading("produto", text="PRODUTO")
        self.tree_itens.heading("quantidade", text="QTD")
        self.tree_itens.heading("preco_unitario", text="PREÇO UNIT.")
        self.tree_itens.heading("subtotal", text="SUBTOTAL")

        self.tree_itens.pack(fill="both", expand=True, pady=5)

        # Botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(pady=5)

        ttk.Button(frame_botoes, text="Adicionar", takefocus=False, command=self.add_venda).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Atualizar", takefocus=False, command=self.load_vendas).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Deletar", takefocus=False, command=self.del_venda).pack(side="left", padx=5)

        self.frame_vendas = frame
        self.load_vendas()


    def on_venda_select(self, event):
        """
        Quando o usuário seleciona uma venda, exibe os itens dessa venda na tree_itens.
        """
        # limpa tree_itens
        for i in self.tree_itens.get_children():
            self.tree_itens.delete(i)

        selected = self.tree_vend.selection()  
        if not selected:
            return

        venda_id = self.tree_vend.item(selected[0])["values"][0]
        itens = repo.listar_itens_venda(venda_id)

        for it in itens:
            self.tree_itens.insert(
                "",
                "end",
                values=(
                    it["id_produto"],
                    it["produto"],
                    it["quantidade"],
                    f"{it['preco_unitario']:.2f}",
                    f"{it['subtotal']:.2f}"
                )
            )


    def registrar_venda(self):
        clientes=repo.listar_clientes()
        if not clientes:
            messagebox.showwarning("Atenção","Cadastre ao menos um cliente")
            return
        escolha=simpledialog.askinteger("Venda","ID do cliente:\n"+ "\n".join(f"{c['id_cliente']} - {c['nome']}" for c in clientes))
        if not escolha: return
        itens=[]
        while True:
            produtos=repo.listar_produtos()
            if not produtos: break
            pid=simpledialog.askinteger("Produto","ID do produto (cancelar p/ terminar):\n"+ "\n".join(f"{p['id_produto']} - {p['nome']} (estoque {p['quantidade']})" for p in produtos))
            if not pid: break
            qtd=simpledialog.askinteger("Qtd","Quantidade:",minvalue=1)
            prod=next((p for p in produtos if p["id_produto"]==pid),None)
            if not prod or qtd>prod["quantidade"]:
                messagebox.showerror("Erro","Produto inválido ou estoque insuficiente")
                continue
            itens.append({"id_produto":pid,"quantidade":qtd,"preco_unit":float(prod["preco"]),"subtotal":float(prod["preco"])*qtd})
        if itens:
            vid=repo.registrar_venda(escolha,itens)
            messagebox.showinfo("Sucesso",f"Venda registrada ID {vid}")

    def add_venda(self):
        """
        Abre um diálogo para registrar uma nova venda com múltiplos produtos.
        """
        dlg = tk.Toplevel(self.root)
        dlg.title("Adicionar Venda")

        # Seleção de cliente
        tk.Label(dlg, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        clientes = repo.listar_clientes()
        cb_cliente = ttk.Combobox(dlg, values=[f"{c['id_cliente']} - {c['nome']}" for c in clientes])
        cb_cliente.grid(row=0, column=1, padx=5, pady=5, columnspan=3, sticky="ew")

        # Tree para itens da venda
        colunas = ("id_produto", "produto", "quantidade", "preco_unit", "subtotal")
        tree_itens = ttk.Treeview(dlg, columns=colunas, show="headings", height=5)
        for c in colunas:
            tree_itens.heading(c, text=c.upper())
        tree_itens.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Seleção de produto
        tk.Label(dlg, text="Produto:").grid(row=2, column=0, padx=5, pady=5)
        produtos = repo.listar_produtos()
        cb_produto = ttk.Combobox(dlg, values=[f"{p['id_produto']} - {p['nome']} ({p['quantidade']} em estoque)" for p in produtos], width=50)
        cb_produto.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(dlg, text="Quantidade:").grid(row=2, column=2, padx=5, pady=5)
        entry_qtd = tk.Entry(dlg)
        entry_qtd.grid(row=2, column=3, padx=5, pady=5)

        # Função para adicionar item na tree
        def add_item():
            valor_cb = cb_produto.get()
            if not valor_cb or not entry_qtd.get().isdigit():
                messagebox.showerror("Erro", "Selecione um produto e informe a quantidade.")
                return

            # Extrai o ID do produto do combobox
            id_produto = int(valor_cb.split(" - ")[0])
            qtd = int(entry_qtd.get())

            # 🔎 Busca direto pelo ID (mais seguro que pelo nome)
            produto = repo.buscar_produto_por_id(id_produto)
            if not produto:
                messagebox.showerror("Erro", f"O produto ID {id_produto} não foi encontrado.")
                return

            nome_produto = produto["nome"]
            estoque_disponivel = produto["quantidade"]

            # Valida quantidade
            if qtd <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que zero.")
                return

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
            tree_itens.insert(
                "", "end",
                values=(id_produto, nome_produto, qtd, f"{preco:.2f}", f"{subtotal:.2f}")
            )

            # limpa campos
            entry_qtd.delete(0, tk.END)
            cb_produto.set("")

        ttk.Button(dlg, text="Adicionar Item", command=add_item).grid(row=3, column=0, columnspan=4, pady=5)

        # Função para salvar venda
        def salvar_venda():
            # Desabilita o botão imediatamente para evitar clique duplo
            btn_salvar.config(state="disabled")

            if not cb_cliente.get():
                messagebox.showerror("Erro", "Selecione um cliente.")
                btn_salvar.config(state="normal")
                return
            id_cliente = int(cb_cliente.get().split(" - ")[0])

            itens = []
            total = 0
            for it in tree_itens.get_children():
                vals = tree_itens.item(it)["values"]
                id_produto, _, qtd, preco, subtotal = vals
                itens.append((id_produto, int(qtd), float(preco)))
                total += float(subtotal)

            if not itens:
                messagebox.showerror("Erro", "Adicione ao menos um produto.")
                btn_salvar.config(state="normal")
                return

            try:
                repo.inserir_venda(id_cliente, itens)

                resumo = "\n".join([f"Produto {idp} - Qtd {q} - R$ {p:.2f}" for idp, q, p in itens])
                messagebox.showinfo(
                    "Sucesso",
                    f"Venda registrada!\n\nCliente: {cb_cliente.get()}\nTotal: R$ {total:.2f}\n\nItens:\n{resumo}"
                )

                self.load_vendas()
                dlg.destroy()

            except ValueError as e:
                # 🚨 Aqui cai quando não há estoque suficiente
                messagebox.showerror("Erro de estoque", str(e))
                btn_salvar.config(state="normal")  # reabilita botão para tentar de novo

        # Botão de salvar (precisa da referência para desabilitar no clique)
        btn_salvar = ttk.Button(dlg, text="Salvar Venda", command=salvar_venda)
        btn_salvar.grid(row=4, column=0, columnspan=4, pady=10)


            
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




    def consultar_vendas(self):
        self.txt_vendas.delete("1.0","end")
        for v in repo.listar_vendas():
            self.txt_vendas.insert("end",f"Venda {v['id_venda']} - {v['data_venda']} - Cliente: {v['cliente']} - Total: {v['valor_total']}\n")
            for it in repo.listar_itens_venda(v["id_venda"]):
                self.txt_vendas.insert("end",f"   {it['nome']} x{it['quantidade']} @ {it['preco_unitario']} = {it['subtotal']}\n")
            self.txt_vendas.insert("end","-"*50+"\n")

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


    # ---------------- Relatórios ----------------
    def setup_relatorios(self):
        """Monta a aba Relatórios com botões padronizados sem foco."""

        frame_botoes = ttk.Frame(self.frame_relatorios)
        frame_botoes.pack(pady=5)

        largura_padrao = 25  # largura fixa dos botões

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
        data_inicio, data_fim = self.pedir_datas()
        if not data_inicio or not data_fim:
            return

        rows = repo.historico_vendas_por_periodo(data_inicio, data_fim)
        self.txt_rel.config(state="normal")
        self.txt_rel.delete("1.0", "end")

        if not rows:
            self.txt_rel.insert("end", "Nenhuma venda encontrada nesse período.\n")
        else:
            for r in rows:
                self.txt_rel.insert(
                    "end",
                    f"Venda {r['id_venda']} | Cliente: {r['cliente']} | "
                    f"Total: R$ {r['valor_total']:.2f} | Data: {r['data_venda']}\n"
                )
        self.txt_rel.config(state="disabled")

    def pedir_datas(self):
        """Abre uma janela com calendário para escolher data inicial e final."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Selecionar Período")

        tk.Label(dlg, text="Data inicial:").grid(row=0, column=0, padx=5, pady=5)
        cal_inicio = DateEntry(dlg, date_pattern="yyyy-mm-dd")
        cal_inicio.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dlg, text="Data final:").grid(row=1, column=0, padx=5, pady=5)
        cal_fim = DateEntry(dlg, date_pattern="yyyy-mm-dd")
        cal_fim.grid(row=1, column=1, padx=5, pady=5)

        result = {}

        def confirmar():
            result["inicio"] = cal_inicio.get_date().strftime("%Y-%m-%d")
            result["fim"] = cal_fim.get_date().strftime("%Y-%m-%d")
            dlg.destroy()

        ttk.Button(dlg, text="OK", command=confirmar).grid(row=2, column=0, columnspan=2, pady=10)

        dlg.transient(self.root)
        dlg.grab_set()
        self.root.wait_window(dlg)

        return result.get("inicio"), result.get("fim")



    def report_estoque_baixo(self):
        self.txt_rel.config(state="normal")   # habilita para edição
        self.txt_rel.delete("1.0", "end")
        rows = [p for p in repo.listar_produtos() if p["quantidade"] <= p["estoque_minimo"]]
        if not rows:
            self.txt_rel.insert("end", "Nenhum produto com estoque baixo\n")
        else:
            for r in rows:
                self.txt_rel.insert("end", f"{r['id_produto']} - {r['nome']} | Qtd {r['quantidade']} | Min {r['estoque_minimo']}\n")
        self.txt_rel.config(state="disabled")  # trava novamente

    def edit_produto(self):
        """Edita nome e/ou preço do produto selecionado."""
        sel = self.tree_prod.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return

        item = self.tree_prod.item(sel[0])
        id_produto, nome_atual, categoria, preco_atual, qtd, forn, est_min = item["values"]

        # Pergunta novos valores
        novo_nome = simpledialog.askstring(
            "Editar Produto",
            f"Nome atual: {nome_atual}\nDigite o novo nome (ou deixe em branco):",
        parent=self.root  # ✅ mantém a janela principal em foco
        )
        self.root.focus_force()

        
        novo_preco_str = simpledialog.askstring(
            "Editar Produto",
            f"Preço atual: {preco_atual}\nDigite o novo preço (ou deixe em branco):",
        parent=self.root  # ✅ mantém a janela principal em foco
        )
        self.root.focus_force()

        # Se usuário deixou em branco → mantém os valores atuais
        if not novo_nome:
            novo_nome = nome_atual

        if not novo_preco_str:
            novo_preco = preco_atual
        else:
            try:
                novo_preco = float(novo_preco_str)
            except ValueError:
                messagebox.showerror("Erro", "Preço inválido.")
                return

        # Atualiza no banco
        repo.atualizar_produto(id_produto, nome=novo_nome, preco=novo_preco)

        messagebox.showinfo("Sucesso", f"Produto {id_produto} atualizado.")
        self.load_produtos()


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
            self.atualizar_fornecedores()
