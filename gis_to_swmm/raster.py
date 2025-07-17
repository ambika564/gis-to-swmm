# raster.py
import rasterio
import numpy as np
from dataclasses import dataclass

@dataclass
class Raster:
    array: np.ndarray
    transform: rasterio.Affine
    crs: str
    nodata: float
    width: int
    height: int
    resolution: float
    bounds: tuple

    @classmethod
    def from_file(cls, path: str):
        with rasterio.open(path) as src:
            array = src.read(1).astype(float)
            nodata = src.nodata if src.nodata is not None else np.nan
            array[array == nodata] = np.nan
            return cls(
                array=array,
                transform=src.transform,
                crs=src.crs.to_string() if src.crs else "",
                nodata=nodata,
                width=src.width,
                height=src.height,
                resolution=src.res[0],
                bounds=src.bounds
            )

    def get_value_at(self, row: int, col: int) -> float:
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.array[row, col]
        return np.nan

    def get_coords(self, row: int, col: int):
        x, y = rasterio.transform.xy(self.transform, row, col, offset='center')
        return x, y
