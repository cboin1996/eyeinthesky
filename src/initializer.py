import os, sys
import logging
from src import config
from src.io import files
from src import util
logger = logging.getLogger(__name__)

def launch(dirs):
    util.generate_dirs(dirs)

def log_init(base_dir, log_format):
    """ Setup logging to file and console """
    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        datefmt="%y-%m-%d %H:%M:%S",
                        filename=os.path.join(base_dir, ".out","out.log"),
                        filemode='w')

    console = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(log_format)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def setup_settings(settings_path, settings: dict):
    if not os.path.exists(settings_path):
        reset_settings(settings_path, settings)

def reset_settings(settings_path, settings: dict):
    files.write_json(settings_path, settings)