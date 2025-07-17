# definitions.py

LANDUSE = {
    "ROOF_CONNECTED": 10,
    "ROOF_UNCONNECTED": 20,
    "BUILT_AREA": 30,
    "NATURAL_AREA": 60,
    "LANDUSE_NONE": 0
}

class Junction:
    def __init__(self, name, x, y, is_open=True, invert_elev=0.0):
        self.name = name
        self.x = x
        self.y = y
        self.is_open = is_open
        self.invert_elev = invert_elev

class Conduit:
    def __init__(self, name, from_node, to_node, length, roughness):
        self.name = name
        self.from_node = from_node
        self.to_node = to_node
        self.length = length
        self.roughness = roughness

