import tkinter as tk

class Frame(tk.Frame):
    def __init__(self, root_window, height, bg, side):
        tk.Frame.__init__(self,root_window,bg=bg)

