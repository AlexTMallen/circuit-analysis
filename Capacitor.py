from Terminal import Terminal


# TODO not implemented into circuit yet
class Capacitor(Component):
    capacitance = 1

    def __init__(self, capacitance, inpt_wire=None, outpt_wire=None):
        self.capacitance = capacitance
        self.inpt = Terminal(inpt_wire, self)
        self.outpt = Terminal(outpt_wire, self)

