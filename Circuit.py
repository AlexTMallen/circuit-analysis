import numpy as np

from Battery import Battery
from Resistor import Resistor

class Circuit:
    def __init__(self, wires, components):
        self.wires = wires
        self.components = components
        for wire in wires:
            wire.set_connected_to(components)

    def analyze(self):
        """
        find the currents and voltages of the given circuit
        :param wires:
        :param components:
        :return:
        """
        # matrix to find currents
        # initialized only for the junction equations since there is an unkown amount of loop equaitons appended later
        M = [np.zeros(len(self.components)) for _ in range(len(
            self.wires) - 1)]
        # current through each component where inpt->outpt is positive
        currents = np.zeros(len(self.components))

        component_to_index = dict()
        for i, comp in enumerate(self.components):
            component_to_index[comp] = i

        x = 0
        # find junctions for the first len(wires) - 1 rows of M
        for wire in self.wires:
            # sum of incoming currents through all components connected to wire must equal 0 (for components where the input terminal is connected to wire, incoming current = -component.current)
            for terminal in wire.connected_to:
                comp = terminal.component
                y = component_to_index[comp]
                M[x][y] += 1 if comp.outpt == terminal else -1

            if not all(M[x] == 0):
                x += 1
            if x == len(self.wires) - 1:
                break

        loops = self._find_loops()

        # finding equations for each loop
        n = len(self.components)
        rhs_vals = [0] * (len(self.wires) - 1)
        for loop in loops:
            # make an equation based on resistors/capacitors in this loop
            lhs_vector = np.zeros(n)
            isBattery = False
            for term in loop:
                comp = term.component
                # find direction of comp relative to loop
                # if same then dir == 1 else -1
                direc = 1 if term == comp.outpt else -1

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
        for i, comp in enumerate(self.components):
            comp.current = currents[i]

        if not all(errors == 0):
            print("No solution found: errors:", errors)

        voltages = self._find_voltages()

        return voltages, currents

    def _find_voltages(self):
        """
        precon: each resistor has a current set
        uses DFS to search for all wires and compute their absolute voltage based on relative voltage
        :return: voltages (also updates the voltage attribute of the wires)
        """
        # TODO: assumes components[0] is the one and only battery
        wire = self.components[0].inpt.wire
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
        for wire in self.wires:
            voltages.append(wire.voltage)

        return np.array(voltages)

    def _find_loops(self):
        """
        uses DFS to find start_c again, starting from start_c. Once it finds it, it backtracks to find the loop discovered
        it does this for all start_c in components to ensure enough independent loops are created
        :param components:
        :return: loops
        """
        # find loops to apply Kirchoff's voltage law
        loops = []
        for start_c in self.components:
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
