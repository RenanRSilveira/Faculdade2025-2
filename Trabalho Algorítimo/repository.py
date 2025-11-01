# Funções do CRUD e operações no banco

"""
Módulo repository
-----------------
CRUD e regras de negócio (interação com o banco).
"""
from db import fetchall, execute, fetchone
from datetime import datetime
import mysql.connector
from db import DB_CONFIG

# region Produto
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

def deletar_produto(id_produto):
    """Remove produto pelo ID."""
    return execute("DELETE FROM produto WHERE id_produto=%s", (id_produto,))

def buscar_produto(id_produto):
    return fetchone("SELECT * FROM produto WHERE id_produto = %s", (id_produto,))

def get_preco_produto(id_produto):
    """
    Retorna o preço de um produto específico.
    """
    row = fetchone("SELECT preco FROM produto WHERE id_produto = %s", (id_produto,))
    return row["preco"] if row else None

def buscar_produto_por_nome_fornecedor(nome, id_fornecedor):
    """
    Retorna um produto pelo nome e fornecedor (ou None se não existir).
    """
    return fetchone(
        "SELECT * FROM produto WHERE nome = %s AND id_fornecedor = %s",
        (nome, id_fornecedor)
    )

def atualizar_produto(id_prod, nome, cat, preco, qtd, forn, est_min):
    """
    Atualiza as informações de um produto.
    """
    query = "UPDATE produto SET nome = %s, categoria=%s, preco = %s, quantidade = %s, id_fornecedor = %s, estoque_minimo = %s WHERE id_produto = %s"
    params = (nome, cat, preco, qtd, forn, est_min, id_prod)
    
    return execute(query, params)
#endregion

# region Venda
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
        # Verifica estoque com bloqueio da linha
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

def deletar_venda(id_venda):
    """Remove venda pelo ID."""
    return execute("DELETE FROM venda WHERE id_venda=%s", (id_venda,))

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

def total_consumido_por_cliente(id_cliente):
    return fetchone("""
        SELECT SUM(valor_total)
        FROM venda v
        WHERE v.id_cliente = %s
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
#endregion

# region Cliente
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

def deletar_cliente(id_cliente):
    """Remove cliente pelo ID."""
    return execute("DELETE FROM cliente WHERE id_cliente=%s", (id_cliente,))

def atualizar_cliente(id_cliente, nome, telefone, email, id_endereco):
    """
    Atualiza os dados de um cliente (nome, telefone, email, endereço).
    """
    query = "UPDATE cliente SET nome = %s, telefone = %s, email = %s, id_endereco = %s WHERE id_cliente = %s"
    params = (nome, telefone, email, id_endereco, id_cliente)
    
    return execute(query, params)

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
#endregion

# region Fornecedor
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

def deletar_fornecedor(id_fornecedor):
    """Remove fornecedor pelo ID."""
    return execute("DELETE FROM fornecedor WHERE id_fornecedor=%s", (id_fornecedor,))

def buscar_fornecedor(id_fornecedor):
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
    """, (id_fornecedor,))

def atualizar_fornecedor(id_fornecedor, nome, telefone, email, id_endereco):
    """
    Atualiza os dados de um fornecedor (nome, telefone, email, endereço).
    """
    query = "UPDATE fornecedor SET nome = %s, telefone = %s, email = %s, id_endereco = %s WHERE id_fornecedor = %s"
    params = (nome, telefone, email, id_endereco, id_fornecedor)

    return execute(query, params)
#endregion

# region Estado
def listar_estados():
    return fetchall("SELECT * FROM estado ORDER BY nome")
#endregion

#region Cidade
def listar_cidades(id_estado):
    return fetchall("SELECT * FROM cidade WHERE id_estado=%s ORDER BY nome", (id_estado,))

def inserir_cidade(nome, id_estado):
    return execute("INSERT INTO cidade (nome, id_estado) VALUES (%s,%s)", (nome, id_estado))
#endregion

#region Endereço
def inserir_endereco(rua, numero, bairro, cep, id_cidade):
    return execute(
        "INSERT INTO endereco (rua, numero, bairro, cep, id_cidade) VALUES (%s,%s,%s,%s,%s)",
        (rua, numero, bairro, cep, id_cidade)
    )

def atualizar_endereco(id_endereco, rua, numero, bairro, cep, id_cidade):
    sql = """
        UPDATE endereco
        SET rua=%s, numero=%s, bairro=%s, cep=%s, id_cidade=%s
        WHERE id_endereco=%s
    """
    execute(sql, (rua, numero, bairro, cep, id_cidade, id_endereco))
#endregion