# Ponto de entrada principal

"""

Ponto de entrada principal do sistema da distribuidora.
"""

import tkinter as tk
from ui_main import App

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.geometry("900x600")
    root.mainloop()

"""
PARA TELA MAXIMIZADA: 

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.state('zoomed')  # Janela maximizada
    root.mainloop()
    """