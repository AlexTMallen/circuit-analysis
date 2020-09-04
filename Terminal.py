class Terminal:
    def __init__(self, wire, component):
        self.wire = wire
        self.component = component

    def __repr__(self):
        term = " input" if self.component.inpt == self else " output"
        return self.component.__repr__() + term
