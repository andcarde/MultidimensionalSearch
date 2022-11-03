import sys
from os import walk
from typing import List, Tuple, NoReturn
import pandas as pd
import numpy as np


def find_csvs(path : str) -> List[pd.DataFrame]:
    file_list = []
    for x in walk(path):
        file_list = file_list + x[2]
    return [pd.read_csv(path + '/' + f) for f in file_list]
    
def change_divide_dfs(df_list : List[pd.DataFrame]) -> List[pd.DataFrame]:
    new_dfs = list()
    for df in df_list:
        df = df.drop(['ID'], axis=1)
        df['DT'] = range(len(df['DT'].values))
        divide_df = [df.iloc[i:min(i+48,len(df['DT'].values))] for i in range(0,len(df['DT'].values),48)]
        new_dfs = new_dfs + divide_df

    return new_dfs

def new_csvs(df_list : List[pd.DataFrame], path : str, template_name : str) -> NoReturn:
    for i in range(len(df_list)):
        df_list[i].to_csv(path + '/' + template_name + '_' + str(i) + '.csv')



if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise ValueError('Not enough arguments')
    data_list = find_csvs(sys.argv[1])
    # new_data_list = change_divide_dfs(data_list)
    # new_csvs(new_data_list,sys.argv[2],sys.argv[3])