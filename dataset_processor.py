import sys
from os import walk
from typing import List, Tuple
import pandas as pd


def find_csvs(path : str) -> List[pd.DataFrame]:
    file_list = [x[2] for x in walk(path)]
    print(file_list)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError('Not enough arguments')
    print(sys.argv[1])
    data_list = find_csvs(sys.argv[1])