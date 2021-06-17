import tkinter as tk

class Entry(tk.Entry):
    def __init__(self, root, width, bg, fg, textvariable):
        tk.Entry.__init__(self, root, width=width, 
                            bg=bg, fg=fg, textvariable=textvariable)