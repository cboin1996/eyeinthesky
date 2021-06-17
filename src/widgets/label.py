import tkinter as tk 

class Label(tk.Label):
    def __init__(self, root, txt):
        tk.Label.__init__(self, root, text=txt)