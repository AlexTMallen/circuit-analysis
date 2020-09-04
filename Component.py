from Terminal import Terminal


class Component:
    inpt = None
    outpt = None
    simplified_comp = None
    current = 0
    name = "unnamed component"

    def __init__(self, name, inpt_wire=None, outpt_wire=None):
        self.name = name
        self.inpt = Terminal(inpt_wire, self)
        self.outpt = Terminal(outpt_wire, self)

    def __repr__(self):
        return self.name

    def get_adjacent_terminals(self, terminal):
        adj_terms = []
        for terminal in self.get_other_terminal(terminal).wire.connected_to:
            if terminal.component != self:
                adj_terms.append(terminal)
        return adj_terms

    def get_other_terminal(self, terminal):
        comp = terminal.component
        if comp == self:
            if comp.inpt == terminal:
                return comp.outpt
            return comp.inpt
        raise Exception("terminal must be in component")

