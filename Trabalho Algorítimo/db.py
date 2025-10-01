"""
Responsável pela conexão com o banco de dados MySQL e execução de consultas.
"""

import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    #'password': 'sua_senha',
    'database': 'distribuidora',
    'raise_on_warnings': True
}

def get_conn():
    """
    Cria e retorna uma nova conexão com o banco de dados MySQL.
    
    Returns
    -------
    mysql.connector.connection_cext.CMySQLConnection
        Objeto de conexão.
    """
    return mysql.connector.connect(**DB_CONFIG)

def fetchall(query, params=None):
    """
    Executa uma consulta SELECT e retorna todos os resultados.

    Parameters
    ----------
    query : str
        Comando SQL.
    params : tuple, optional
        Parâmetros da query.

    Returns
    -------
    list[dict]
        Lista de registros em formato dicionário.
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def fetchone(query, params=None):
    """
    Executa uma consulta SQL e retorna apenas uma linha.
    """
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def execute(query, params=None, commit=True):
    """
    Executa uma consulta INSERT, UPDATE ou DELETE no banco.

    Parameters
    ----------
    query : str
        Comando SQL.
    params : tuple, optional
        Parâmetros da query.
    commit : bool, default=True
        Se deve confirmar a transação.

    Returns
    -------
    int
        Último ID inserido (se houver).
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params or ())
    if commit:
        conn.commit()
    lastid = cur.lastrowid
    cur.close()
    conn.close()
    return lastid
