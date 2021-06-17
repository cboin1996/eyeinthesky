import logging
import os, sys
import tkinter as tk

from src.windows import home
from src import initializer
from src.io import files
from src import config

def run():
    base_ip = "http://10.14.164.18/api/fleet/v1/"
    log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    base_path = sys.path[0]
    initializer.log_init(base_path, log_format)
    initializer.launch(config.required_dirs)
            
    window = tk.Tk()        

    home_window = home.Home(base_ip, base_path)
    home_window.open(window)

    window.mainloop()
if __name__=="__main__":
    run()