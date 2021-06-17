import os, sys, shutil
import logging 
import glob
import pandas as pd

logger = logging.getLogger(__name__)

def generate_dirs(dirs):
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            logger.info(f"Creating: {dir_path}")
            os.mkdir(dir_path)

def rm_dirs(dirs):
    for dir_path in dirs:
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            logger.error("Error: %s - %s" % (dir_path, e.strerror))

def browse_dir(root_folder, level=0):
    glob_root = root_folder
    for _ in range(level):
        glob_root = os.path.join(glob_root, "*")
    fnames = glob.glob(glob_root)

    return fnames

def copy_tree(root, out):
    try:
        logger.info(f"Copying files under dir '{root}' to '{out}'")
        shutil.copytree(root, out)
        logger.info(f"Finished Copy.")
        return True

    except Exception as e:
        e.with_traceback
        return False

def get_last_path_name(path):
    return os.path.basename(os.path.normpath(path))

def print_df(df, title=""):
    with pd.option_context("display.max_rows", None,
                        "display.max_columns", None):
        logger.info(f"/--{title}--\\\n{df}")

def get_freq_english(freq):
    if freq == "Y":
        key = "Year"
    if freq == "M":
        key = "Month"
    if freq == "D":
        key = "Day"
    
    return key