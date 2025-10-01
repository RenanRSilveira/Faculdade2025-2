# Funções auxiliadres (formatações, validações)

"""

Funções auxiliares de formatação e validação.
"""

def formatar_preco(valor):
    """
    Formata um número como moeda brasileira.

    Parameters
    ----------
    valor : float

    Returns
    -------
    str
        Valor formatado, ex: "R$ 10,50".
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
