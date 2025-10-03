# Funções do CRUD e operações no banco

"""
Módulo repository
-----------------
CRUD e regras de negócio (interação com o banco).
"""
from db import fetchall, execute, fetchone
from datetime import datetime

# ---------------- PRODUTOS ----------------
def listar_produtos():
    return fetchall("""
        SELECT p.id_produto, p.nome, p.categoria, p.preco, p.quantidade,
               f.nome AS fornecedor, p.estoque_minimo
        FROM produto p
        LEFT JOIN fornecedor f ON p.id_fornecedor=f.id_fornecedor
        ORDER BY p.nome
    """)

def inserir_produto(nome, cat, preco, qtd, forn_id, estoque_min):
    return execute("""INSERT INTO produto (nome,categoria,preco,quantidade,id_fornecedor,estoque_minimo)
                      VALUES (%s,%s,%s,%s,%s,%s)""",
                   (nome,cat,preco,qtd,forn_id,estoque_min))


import mysql.connector
from db import DB_CONFIG

def inserir_venda(id_cliente, itens):
    """
    Insere uma nova venda com múltiplos produtos e atualiza o estoque.
    Usa transação e SELECT ... FOR UPDATE para evitar concorrência.
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        conn.start_transaction()
        cur = conn.cursor(dictionary=True)

        total = 0
        # 🔒 Verifica estoque com bloqueio da linha
        for id_produto, qtd, preco in itens:
            cur.execute("SELECT quantidade, nome FROM produto WHERE id_produto = %s FOR UPDATE", (id_produto,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Produto {id_produto} não encontrado.")
            if row["quantidade"] < qtd:
                raise ValueError(
                    f"Estoque insuficiente para '{row['nome']}'. "
                    f"Disponível: {row['quantidade']}, solicitado: {qtd}."
                )
            total += qtd * preco

        # Cria a venda
        cur.execute(
            "INSERT INTO venda (id_cliente, valor_total, data_venda) VALUES (%s, %s, NOW())",
            (id_cliente, total)
        )
        venda_id = cur.lastrowid

        # Insere itens e atualiza estoque
        for id_produto, qtd, preco in itens:
            subtotal = qtd * preco
            cur.execute(
                """INSERT INTO produto_venda (id_venda, id_produto, quantidade, preco_unitario, subtotal)
                   VALUES (%s, %s, %s, %s, %s)""",
                (venda_id, id_produto, qtd, preco, subtotal)
            )
            cur.execute(
                "UPDATE produto SET quantidade = quantidade - %s WHERE id_produto = %s",
                (qtd, id_produto)
            )

        conn.commit()
        return venda_id

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

   
def atualizar_quantidade_produto(id_produto, qtd_extra):
    """
    Incrementa a quantidade de um produto já existente no estoque.
    """
    return execute(
        "UPDATE produto SET quantidade = quantidade + %s WHERE id_produto = %s",
        (qtd_extra, id_produto)
    )


def excluir_produto(pid):
    execute("DELETE FROM produto WHERE id_produto=%s", (pid,))

def entrada_produto(pid, qtd, preco_compra):
    execute("INSERT INTO entrada_produto (id_produto,quantidade,preco_compra) VALUES (%s,%s,%s)",
            (pid,qtd,preco_compra))
    execute("UPDATE produto SET quantidade=quantidade+%s WHERE id_produto=%s", (qtd,pid))


# ---------------- CLIENTES ----------------
def listar_clientes():
    sql = """
        SELECT cl.id_cliente, cl.nome, cl.telefone, cl.email,
               e.rua, e.numero, e.bairro, e.cep,
               c.nome AS cidade, est.sigla AS estado
        FROM cliente cl
        JOIN endereco e ON cl.id_endereco = e.id_endereco
        JOIN cidade c ON e.id_cidade = c.id_cidade
        JOIN estado est ON c.id_estado = est.id_estado
    """
    return fetchall(sql)

def inserir_cliente(nome,tel,email,id_endereco=None):
    return execute("INSERT INTO cliente (nome,telefone,email,id_endereco) VALUES (%s,%s,%s,%s)",
                   (nome,tel,email,id_endereco))

def excluir_cliente(cid):
    execute("DELETE FROM cliente WHERE id_cliente=%s",(cid,))


# ---------------- FORNECEDORES ----------------
def listar_fornecedores():
    sql = """
        SELECT f.id_fornecedor, f.nome, f.telefone, f.email,
               e.rua, e.numero, e.bairro, e.cep,
               c.nome AS cidade, est.sigla AS estado
        FROM fornecedor f
        JOIN endereco e ON f.id_endereco = e.id_endereco
        JOIN cidade c ON e.id_cidade = c.id_cidade
        JOIN estado est ON c.id_estado = est.id_estado
    """
    return fetchall(sql)

def inserir_fornecedor(nome,tel,email,id_endereco=None):
    return execute("INSERT INTO fornecedor (nome,telefone,email,id_endereco) VALUES (%s,%s,%s,%s)",
                   (nome,tel,email,id_endereco))

def excluir_fornecedor(fid):
    execute("DELETE FROM fornecedor WHERE id_fornecedor=%s",(fid,))


# ---------------- VENDAS ----------------
def registrar_venda(cliente_id, itens):
    conn = None
    import mysql.connector
    try:
        conn = mysql.connector.connect(**{
            "host":"localhost","user":"seu_usuario","password":"sua_senha","database":"distribuidora"
        })
        cur = conn.cursor()
        valor_total = sum(it['subtotal'] for it in itens)
        cur.execute("INSERT INTO venda (id_cliente,data_venda,valor_total) VALUES (%s,%s,%s)",
                    (cliente_id, datetime.now(), valor_total))
        id_venda = cur.lastrowid
        for it in itens:
            cur.execute("""INSERT INTO produto_venda (id_venda,id_produto,quantidade,preco_unitario,subtotal)
                           VALUES (%s,%s,%s,%s,%s)""",
                        (id_venda,it['id_produto'],it['quantidade'],it['preco_unit'],it['subtotal']))
            cur.execute("UPDATE produto SET quantidade=quantidade-%s WHERE id_produto=%s",
                        (it['quantidade'], it['id_produto']))
        conn.commit()
        return id_venda
    except Exception as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn: conn.close()

def listar_vendas():
    return fetchall("""
        SELECT v.id_venda, v.id_cliente, c.nome AS cliente,
               v.valor_total, v.data_venda
        FROM venda v
        JOIN cliente c ON v.id_cliente = c.id_cliente
        ORDER BY v.data_venda DESC
    """)


def listar_itens_venda(id_venda):
    """
    Retorna todos os itens (produtos) de uma venda específica.
    Inclui subtotal calculado no SQL.
    """
    return fetchall("""
        SELECT 
            pv.id_produto, 
            p.nome AS produto, 
            pv.quantidade, 
            pv.preco_unitario,
            (pv.quantidade * pv.preco_unitario) AS subtotal
        FROM produto_venda pv
        JOIN produto p ON pv.id_produto = p.id_produto
        WHERE pv.id_venda = %s
    """, (id_venda,))


def deletar_cliente(id_cliente):
    """Remove cliente pelo ID."""
    return execute("DELETE FROM cliente WHERE id_cliente=%s", (id_cliente,))

def deletar_fornecedor(id_fornecedor):
    """Remove fornecedor pelo ID."""
    return execute("DELETE FROM fornecedor WHERE id_fornecedor=%s", (id_fornecedor,))

def deletar_produto(id_produto):
    """Remove produto pelo ID."""
    return execute("DELETE FROM produto WHERE id_produto=%s", (id_produto,))

def deletar_venda(id_venda):
    """Remove venda pelo ID."""
    return execute("DELETE FROM venda WHERE id_venda=%s", (id_venda,))

def get_preco_produto(id_produto):
    """
    Retorna o preço de um produto específico.
    """
    row = fetchone("SELECT preco FROM produto WHERE id_produto = %s", (id_produto,))
    return row["preco"] if row else None

def buscar_produto_por_nome(nome):
    """
    Retorna um produto pelo nome exato (ou None se não existir).
    """
    return fetchone("SELECT * FROM produto WHERE nome = %s", (nome,))

def buscar_produto_por_nome_fornecedor(nome, id_fornecedor):
    """
    Retorna um produto pelo nome e fornecedor (ou None se não existir).
    """
    return fetchone(
        "SELECT * FROM produto WHERE nome = %s AND id_fornecedor = %s",
        (nome, id_fornecedor)
    )

def atualizar_produto(id_produto, nome=None, preco=None):
    """
    Atualiza nome e/ou preço de um produto.
    """
    if nome is not None and preco is not None:
        query = "UPDATE produto SET nome = %s, preco = %s WHERE id_produto = %s"
        params = (nome, preco, id_produto)
    elif nome is not None:
        query = "UPDATE produto SET nome = %s WHERE id_produto = %s"
        params = (nome, id_produto)
    elif preco is not None:
        query = "UPDATE produto SET preco = %s WHERE id_produto = %s"
        params = (preco, id_produto)
    else:
        return None  # nada a atualizar
    
    return execute(query, params)

def atualizar_cliente(id_cliente, nome=None, telefone=None, email=None, id_endereco=None):
    """
    Atualiza os dados de um cliente (nome, telefone, email, endereço).
    Só atualiza os campos que não forem None.
    """
    query_parts = []
    params = []

    if nome is not None:
        query_parts.append("nome = %s")
        params.append(nome)
    if telefone is not None:
        query_parts.append("telefone = %s")
        params.append(telefone)
    if email is not None:
        query_parts.append("email = %s")
        params.append(email)
    if id_endereco is not None:
        query_parts.append("id_endereco = %s")
        params.append(id_endereco)

    if not query_parts:
        return None  # nada a atualizar

    params.append(id_cliente)
    query = f"UPDATE cliente SET {', '.join(query_parts)} WHERE id_cliente = %s"
    return execute(query, tuple(params))

def atualizar_fornecedor(id_fornecedor, nome=None, telefone=None, email=None, id_endereco=None):
    """
    Atualiza os dados de um fornecedor (nome, telefone, email, endereço).
    Só atualiza os campos que não forem None.
    """
    query_parts = []
    params = []

    if nome is not None:
        query_parts.append("nome = %s")
        params.append(nome)
    if telefone is not None:
        query_parts.append("telefone = %s")
        params.append(telefone)
    if email is not None:
        query_parts.append("email = %s")
        params.append(email)
    if id_endereco is not None:
        query_parts.append("id_endereco = %s")
        params.append(id_endereco)

    if not query_parts:
        return None  # nada a atualizar

    params.append(id_fornecedor)
    query = f"UPDATE fornecedor SET {', '.join(query_parts)} WHERE id_fornecedor = %s"
    return execute(query, tuple(params))

def historico_vendas_por_cliente(id_cliente):
    return fetchall("""
        SELECT v.id_venda, v.data_venda, v.valor_total,
               p.nome AS produto, pv.quantidade, pv.preco_unitario, pv.subtotal
        FROM venda v
        JOIN produto_venda pv ON v.id_venda = pv.id_venda
        JOIN produto p ON pv.id_produto = p.id_produto
        WHERE v.id_cliente = %s
        ORDER BY v.data_venda DESC
    """, (id_cliente,))

def historico_vendas_por_produto(id_produto):
    return fetchall("""
        SELECT v.id_venda, v.data_venda, v.valor_total,
               c.nome AS cliente, pv.quantidade, pv.preco_unitario, pv.subtotal
        FROM venda v
        JOIN produto_venda pv ON v.id_venda = pv.id_venda
        JOIN cliente c ON v.id_cliente = c.id_cliente
        WHERE pv.id_produto = %s
        ORDER BY v.data_venda DESC
    """, (id_produto,))

def historico_vendas_por_periodo(data_inicio, data_fim):
    return fetchall("""
        SELECT v.id_venda, c.nome AS cliente, v.valor_total, v.data_venda
        FROM venda v
        JOIN cliente c ON v.id_cliente = c.id_cliente
        WHERE v.data_venda BETWEEN %s AND %s
        ORDER BY v.data_venda
    """, (data_inicio, data_fim))


def listar_estados():
    return fetchall("SELECT * FROM estado ORDER BY nome")

def inserir_estado(nome, sigla):
    return execute("INSERT INTO estado (nome, sigla) VALUES (%s,%s)", (nome, sigla))

def buscar_estado_por_nome(nome):
    """Retorna um estado pelo nome (ou None)."""
    return fetchone("SELECT * FROM estado WHERE nome = %s", (nome,))

def get_or_create_estado(nome, sigla=None):
    """
    Retorna id_estado do estado pelo nome.
    - Se existir, retorna o existente.
    - Se não existir, cria pedindo a sigla.
    """
    estado = buscar_estado_por_nome(nome)
    if estado:
        return estado["id_estado"], estado["sigla"]
    
    if not sigla:
        raise ValueError("Sigla é obrigatória para criar novo estado.")
    
    id_estado = execute("INSERT INTO estado (nome, sigla) VALUES (%s, %s)", (nome, sigla))
    return id_estado, sigla


def listar_cidades(id_estado):
    return fetchall("SELECT * FROM cidade WHERE id_estado=%s ORDER BY nome", (id_estado,))

def inserir_cidade(nome, id_estado):
    return execute("INSERT INTO cidade (nome, id_estado) VALUES (%s,%s)", (nome, id_estado))

def listar_enderecos(id_cidade):
    return fetchall("SELECT * FROM endereco WHERE id_cidade=%s ORDER BY rua, numero", (id_cidade,))

def inserir_endereco(rua, numero, bairro, cep, id_cidade):
    return execute(
        "INSERT INTO endereco (rua, numero, bairro, cep, id_cidade) VALUES (%s,%s,%s,%s,%s)",
        (rua, numero, bairro, cep, id_cidade)
    )

def buscar_cidade_por_nome(nome):
    return fetchone("SELECT * FROM cidade WHERE nome = %s", (nome,))

def inserir_cidade(nome, id_estado):
    return execute("INSERT INTO cidade (nome, id_estado) VALUES (%s, %s)", (nome, id_estado))

def buscar_endereco(id_endereco):
    sql = """
        SELECT e.id_endereco, e.rua, e.numero, e.bairro, e.cep,
               c.id_cidade, c.nome AS cidade,
               est.id_estado, est.nome AS estado, est.sigla
        FROM endereco e
        JOIN cidade c ON e.id_cidade = c.id_cidade
        JOIN estado est ON c.id_estado = est.id_estado
        WHERE e.id_endereco = %s
    """
    return fetchone(sql, (id_endereco,))

def atualizar_endereco(id_endereco, rua, numero, bairro, cep, id_cidade):
    sql = """
        UPDATE endereco
        SET rua=%s, numero=%s, bairro=%s, cep=%s, id_cidade=%s
        WHERE id_endereco=%s
    """
    execute(sql, (rua, numero, bairro, cep, id_cidade, id_endereco))

def buscar_cliente(cid):
    return fetchone("""
        SELECT c.id_cliente AS id, c.nome, c.telefone, c.email,
               e.rua, e.numero, e.bairro, e.cep,
               ci.id_cidade, ci.nome AS cidade,
               es.id_estado, es.sigla AS estado
        FROM cliente c
        LEFT JOIN endereco e ON c.id_endereco = e.id_endereco
        LEFT JOIN cidade ci ON e.id_cidade = ci.id_cidade
        LEFT JOIN estado es ON ci.id_estado = es.id_estado
        WHERE c.id_cliente=%s
    """, (cid,))


def buscar_fornecedor(fid):
    return fetchone("""
        SELECT f.id_fornecedor AS id, f.nome, f.telefone, f.email,
               e.rua, e.numero, e.bairro, e.cep,
               ci.id_cidade, ci.nome AS cidade,
               es.id_estado, es.sigla AS estado
        FROM fornecedor f
        LEFT JOIN endereco e ON f.id_endereco = e.id_endereco
        LEFT JOIN cidade ci ON e.id_cidade = ci.id_cidade
        LEFT JOIN estado es ON ci.id_estado = es.id_estado
        WHERE f.id_fornecedor=%s
    """, (fid,))

def buscar_produto_por_id(id_produto):
    return fetchone("SELECT * FROM produto WHERE id_produto = %s", (id_produto,))
