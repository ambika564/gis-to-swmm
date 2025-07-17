# table.py
import pandas as pd
from gis_to_swmm.definitions import Junction, Conduit
from typing import List

def parse_junctions(junction_table):
    junctions = []
    nrows = junction_table.df.shape[0]

    for i in range(1, nrows):  # Skip header if needed
        x = float(junction_table.get(i, 0))
        y = float(junction_table.get(i, 1))
        name = junction_table.get(i, 2)
        is_open = int(junction_table.get(i, 6)) == 1
        invert = float(junction_table.get(i, 4))
        junctions.append(Junction(name=name, x=x, y=y, is_open=is_open, invert_elev=invert))
    
    return junctions

def load_table(path):
    return Table(path)

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

    def load_junctions(path) -> List[Junction]:
        df = pd.read_csv(path)
        return [
            Junction(row['name'], row['x'], row['y'], row['is_open'], row['invert'])
            for _, row in df.iterrows()
        ]

    def load_conduits(path) -> List[Conduit]:
        df = pd.read_csv(path)
        return [
            Conduit(row['name'], row['from_node'], row['to_node'], row['length'], row['roughness'])
            for _, row in df.iterrows()
        ]
    
    def write_to_stream(self, stream):
        # Write headers
        stream.write("\t".join(self.df.columns) + "\n")
        
        for _, row in self.df.iterrows():
            line = "\t".join(str(val) for val in row)
            stream.write(line + "\n")




