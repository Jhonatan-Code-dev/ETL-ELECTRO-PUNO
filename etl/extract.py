import pandas as pd
import csv
import chardet
from .settings import COLUMNS


def load_csv(file_path):
    with open(file_path, "rb") as f:
        enc = chardet.detect(f.read())["encoding"]

    with open(file_path, encoding=enc) as f:
        sample = f.read(2048)
        sep = csv.Sniffer().sniff(sample, delimiters=";,").delimiter

    df = pd.read_csv(
        file_path,
        sep=sep,
        header=0,
        encoding=enc,
        dtype=str,
        low_memory=False
    )

    if len(df.columns) == len(COLUMNS):
        df.columns = COLUMNS

    return df
