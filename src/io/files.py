import json
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)
def write_json(fp, json_data):
    with open(fp, 'w') as f:
        logger.info(f"Writing json to file at: {fp}")
        json.dump(json_data, f)

def load_json(fp):
    with open(fp, 'r') as f:
        logger.info(f"Reading json from file at: {fp}")
        return json.load(f)

def read_csv(fp_or_buf, index_col=False):
    df = pd.read_csv(fp_or_buf, index_col=False)
    return df

def write_csv(df: pd.DataFrame, fp):
    logger.info(f"Creating csv {fp}")
    df.to_csv(fp)

def write_text(fp, string):
    with open(fp, 'w') as f:
        f.write(string)

def get_filesafe_str(string):
    return string.replace("[", "").replace(":", "").replace("-", "").replace("]", "")

def savefig(fig, fp, dpi=300):
    fig.savefig(fp, dpi=dpi)
    logger.info(f"Saving fig => {fp}")