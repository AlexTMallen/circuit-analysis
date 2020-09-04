import numpy as np


# uses a multigraph setup to connect a set of wires
# nodes: a set of wires
# edges: a set of components
# inpt: a mapping from each component to its input wire (arbitray)
# outpt: a mapping from each component to its output wire (the one thats not "input")
# connectedTo: a mapping from each wire to the terminals of edges it's connected to

# ALGO TO FIND CURRENTS
# (1) look for connected components like series/parallel and construct a simplified circuit (recursively?)
# (2) formulate len(components) linearly independent equations:
#		(a) find INDEPENDENT loops and apply Kirchoff's voltage law
#		(b) apply Kirchoff's current law to independent junctions
# (3) solve matrix equation


class Terminal:
    wire = None
    component = None

    def __init__(self, wire, component):
        self.wire = wire
        self.component = component

    def __repr__(self):
        term = " input" if self.component.inpt == self else " output"
        return self.component.__repr__() + term


class Component:
    inpt = None
    outpt = None
    simplified_comp = None
    current = 0
    name = "unnamed component"

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
        raise Exception("terminal needs to be in component")


class Resistor(Component):
    resistance = 0

    def __init__(self, resistance, name, inpt_wire=None, outpt_wire=None):
        self.resistance = resistance
        self.name = name
        self.inpt = Terminal(inpt_wire, self)
        self.outpt = Terminal(outpt_wire, self)


class Capacitor(Component):
    capacitance = 1

    def __init__(self, capacitance, inpt_wire=None, outpt_wire=None):
        self.capacitance = capacitance
        self.inpt = Terminal(inpt_wire, self)
        self.outpt = Terminal(outpt_wire, self)


class Battery(Component):
    emf = 0

    def __init__(self, emf, name, inpt_wire=None, outpt_wire=None):
        self.emf = emf
        self.name = name
        self.inpt = Terminal(inpt_wire, self)
        self.outpt = Terminal(outpt_wire, self)



class Wire:
    voltage = 0

    def __init__(self, name):
        self.name = name
        self.connected_to = []

    def set_connected_to(self, components):
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


def main():
    wires = [Wire("w0"), Wire("w1"), Wire("w2")]
    battery = Battery(3, "b", inpt_wire=wires[2], outpt_wire=wires[0])
    r0 = Resistor(10, "r0", inpt_wire=wires[0], outpt_wire=wires[1])
    r1 = Resistor(5, "r1", inpt_wire=wires[0], outpt_wire=wires[2])
    r2 = Resistor(1, "r2", inpt_wire=wires[1], outpt_wire=wires[2])

    components = [battery, r0, r1, r2]
    for wire in wires:
        wire.set_connected_to(components)

    voltages, currents = analyze(wires, components)
    print("currents:", currents)
    print("voltages:", voltages)

    # s, p = get_series_parallel([battery, r1], wires)


def get_series_parallel(components, wires):
    # doesn't work yet / isn't necessary
    # find series and parallel TODO
    series_s = []
    parallels = []
    for comp in components:
        # Series
        series = []
        end = comp
        while len(end) == 2 and all(type(c) == type(comp) for c in end.outpt.wire.connected_to):
            series.append(end)
            temp = end.outpt.wire.connected_to.copy()
            temp.remove(end)
            end = temp[0]

        start = comp
        while len(start) == 2 and all(type(c) == type(comp) for c in start.inpt.wire.connected_to):
            if (start != comp):
                series.insert(0, start)
            temp = start.outpt.wire.connected_to.copy()
            temp.remove(start)
            start = temp[0]

        if series not in series_s:
            series_s.append(series)

    # # Parallel
    # out_connected_to = set(comp.outpt.wire.connected_to)
    # parallel = set(t for t in out_connected_to if t.component.inpt.wire == comp.inpt.wire and type(comp) == type(t.component))

    # in_connected_to = set(comp.inpt.wire.connected_to)
    # parallel.union(set(c for c in in_connected_to if c.outpt.wire == comp.outpt.wire and type(comp) == type(c)))
    # if parallel not in parallels:
    # 	parallels.append(parallel)

    print("parallels:", parallels)
    print("series:", series_s)
    return series_s, parallels


def analyze(wires, components):
    """
    find the currents and voltages of the given circuit
    :param wires:
    :param components:
    :return:
    """
    # matrix to find currents
    # initialized only for the junction equations since there is an unkown amount of loop equaitons appended later
    M = [np.zeros(len(components)) for _ in range(len(
        wires) - 1)]
    # current through each component where inpt->outpt is positive
    currents = np.zeros(len(components))

    component_to_index = dict()
    for i, comp in enumerate(components):
        component_to_index[comp] = i

    x = 0
    # find junctions for the first len(wires) - 1 rows of M
    for wire in wires:
        # sum of incoming currents through all components connected to wire must equal 0 (for components where the input terminal is connected to wire, incoming current = -component.current)
        for terminal in wire.connected_to:
            comp = terminal.component
            y = component_to_index[comp]
            M[x][y] += 1 if comp.outpt == terminal else -1

        if not all(M[x] == 0):
            x += 1
        if x == len(wires) - 1:
            break

    loops = find_loops(components)

    # finding equations for each loop
    n = len(components)
    rhs_vals = [0] * (len(wires) - 1)
    for loop in loops:
        # make an equation based on resistors/capacitors in this loop
        lhs_vector = np.zeros(n)
        isBattery = False
        for term in loop:
            comp = term.component
            # find direction of comp relative to loop
            # if same then dir == 1 else -1
            direc = 1 if term == comp.outpt == "output" else -1

            if type(comp) == Battery:
                isBattery = True
                rhs_vals.append(-direc * comp.emf)  # assumes only one battery
            if type(comp) == Resistor:
                y = component_to_index[comp]
                lhs_vector[y] = -direc * comp.resistance
        if not isBattery:
            rhs_vals.append(0)

        M.append(lhs_vector)

    rhs = np.array(rhs_vals)
    M = np.array(M)
    print(M)
    print(rhs)

    currents, errors, rank, singular_values = np.linalg.lstsq(M, rhs, rcond=None)
    for i, comp in enumerate(components):
        comp.current = currents[i]

    if not all(errors == 0):
        print("No solution found: errors:", errors)

    voltages = find_voltages(wires, components)

    return voltages, currents


def find_voltages(wires, components):
    """
    uses DFS to search for all wires and compute their absolute voltage based on relative voltage
    :param components:
    :return: voltages (also updates the voltage attribute of the wires)
    """
    # TODO: assumes components[0] is the one and only battery
    wire = components[0].inpt.wire
    wire.voltage = 0
    stack = [(w, out_t, wire) for out_t, w in wire.get_adjacent_wires()]
    visited = {wire}

    while stack:
        current_wire, out_terminal, prev_wire = stack.pop()

        comp = out_terminal.component
        direc = 1 if out_terminal == comp.outpt else -1
        if type(comp) == Battery:
            current_wire.voltage = prev_wire.voltage + direc * comp.emf
        elif type(comp) == Resistor:
            current_wire.voltage = prev_wire.voltage - direc * comp.resistance * comp.current

        for new_out_terminal, new_wire in current_wire.get_adjacent_wires():
            if new_wire not in visited:
                stack.append((new_wire, out_terminal, current_wire))
                visited.add(new_wire)

    voltages = []
    for wire in wires:
        voltages.append(wire.voltage)

    return np.array(voltages)


def find_loops(components):
    """
    uses DFS to find start_c again, starting from start_c. Once it finds it, it backtracks to find the loop discovered
    it does this for all start_c in components to ensure enough independent loops are created
    :param components:
    :return: loops
    """
    # find loops to apply Kirchoff's voltage law
    loops = []
    for start_c in components:
        loop = []  # terminals
        stack = [start_c.outpt]
        visited = {start_c}
        backtrack = dict()

        while stack:
            current_t = stack.pop()
            current_c = current_t.component

            for neigh_term in current_c.get_adjacent_terminals(current_t):
                neigh_comp = neigh_term.component
                if neigh_comp not in visited:
                    stack.append(neigh_term)
                    backtrack[neigh_term] = current_t
                    visited.add(neigh_comp)
                if neigh_term == start_c.outpt:
                    term = current_t
                    loop.append(term)
                    while term != start_c.outpt:
                        term = backtrack[term]
                        loop.append(term)
                    stack = None
                    break
        loops.append(loop)

    return loops


if __name__ == "__main__":
    main()
