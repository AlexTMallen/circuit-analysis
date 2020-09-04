class Wire:
    voltage = 0

    def __init__(self, name):
        self.name = name

    def set_connected_to(self, components):
        self.connected_to = []
        for comp in components:
            if comp.inpt.wire == self:
                self.connected_to.append(comp.inpt)
            if comp.outpt.wire == self:
                self.connected_to.append(comp.outpt)

    def get_adjacent_wires(self):
        adj_wires = []
        for terminal in self.connected_to:
            comp = terminal.component
            adj_wires.append((comp.outpt, comp.outpt.wire) if comp.inpt == terminal else (comp.inpt, comp.inpt.wire))
        return adj_wires

    def __repr__(self):
        return self.name

