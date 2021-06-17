import tkinter as tk

class Button(tk.Button):
    def __init__(self, root, display_text, width, height, bg, fg, command):
        tk.Button.__init__(self, root, text=display_text, width=width, height=height, 
                            bg=bg, fg=fg, command=command)
        
    
