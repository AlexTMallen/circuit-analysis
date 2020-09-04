from Component import Component
from Terminal import Terminal


class Resistor(Component):
    def __init__(self, resistance, name, inpt_wire=None, outpt_wire=None):
        self.resistance = resistance
        Component.__init__(self, name, inpt_wire=inpt_wire, outpt_wire=outpt_wire)


