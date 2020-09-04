from Component import Component
from Terminal import Terminal


class Battery(Component):
    def __init__(self, emf, name, inpt_wire=None, outpt_wire=None):
        self.emf = emf
        Component.__init__(self, name, inpt_wire=inpt_wire, outpt_wire=outpt_wire)

