# cell.py
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Cell:
    name: str = "empty"
    center_x: float = 0.0
    center_y: float = 0.0
    elevation: float = 0.0
    flowdir: int = -1
    cell_size: float = 0.0
    slope: float = 0.0
    area: float = 0.0
    flow_width: float = 0.0
    landuse: int = 0
    outlet_x: float = 0.0
    outlet_y: float = 0.0
    outlet_id: int = -1
    subcatchment_id: int = -1
    outlet: str = "*"
    raingage: str = "r1"
    imperv: str = "25.0"
    snow_pack: str = ""
    N_Imperv: str = "0.01"
    N_Perv: str = "0.1"
    S_Imperv: str = "0.05"
    S_Perv: str = "0.05"
    PctZero: str = "0.0"
    RouteTo: str = "OUTLET"
    PctRouted: str = "100.0"
    Suction: str = "3.5"
    HydCon: str = "0.5"
    IMDmax: str = "0.25"
    is_sink: int = 0
    num_elements: int = 0
    has_inlet: int = 0
    elev_nodata: float = 0.0
    tag: str = "None"
    inlet_ids: List[int] = field(default_factory=list)
    neighbor_indices: List[int] = field(default_factory=lambda: [-1] * 8)
    neighbor_distances: List[float] = field(default_factory=lambda: [0.0] * 8)
    
    outlet: str = "*"                         # name of the outlet node or subcatchment
    outlet_id: int = -1                       # index of the outlet (cell or junction)
    outlet_coord: Tuple[float, float] = (0.0, 0.0)  # coordinates of the outlet
    is_sink: int = 0              # 0=routed, 1=sink, 2=forced (e.g., roof to junction)

