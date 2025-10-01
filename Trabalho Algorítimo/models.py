# Classes de entidades (Produtos, Cliente, Fornecedor, Venda, etc)

"""

Contém classes que representam entidades do sistema (Produto, Cliente, Fornecedor, Venda).
"""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Produto:
    """Entidade Produto da distribuidora."""
    id_produto: int = None
    nome: str = ""
    categoria: str = ""
    preco: float = 0.0
    quantidade: int = 0
    id_fornecedor: int = None
    estoque_minimo: int = 1

@dataclass
class Cliente:
    """Entidade Cliente que compra produtos."""
    id_cliente: int = None
    nome: str = ""
    telefone: str = ""
    endereco: str = ""
    email: str = ""

@dataclass
class Fornecedor:
    """Entidade Fornecedor que fornece produtos."""
    id_fornecedor: int = None
    nome: str = ""
    telefone: str = ""
    endereco: str = ""
    email: str = ""

@dataclass
class Venda:
    """Entidade Venda realizada para um cliente."""
    id_venda: int = None
    id_cliente: int = None
    data_venda: datetime = None
    valor_total: float = 0.0
