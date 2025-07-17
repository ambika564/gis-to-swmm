# table.py
import pandas as pd

class Table:
    def __init__(self, path: str):
        self.df = pd.read_csv(path)

    def get(self, row: int, col: int):
        return self.df.iloc[row, col]

    def get_column(self, col: str):
        return self.df[col].tolist()

    def shape(self):
        return self.df.shape

    def print(self):
        print(self.df)
