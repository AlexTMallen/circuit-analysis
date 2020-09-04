import numpy as np

from Circuit import Circuit
from Wire import Wire
from Terminal import Terminal
from Component import Component
from Resistor import Resistor
from Battery import Battery

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


def main():
    wires = [Wire("w0"), Wire("w1"), Wire("w2")]
    battery = Battery(3, "b", inpt_wire=wires[2], outpt_wire=wires[0])
    r0 = Resistor(10, "r0", inpt_wire=wires[0], outpt_wire=wires[1])
    r1 = Resistor(5, "r1", inpt_wire=wires[0], outpt_wire=wires[2])
    r2 = Resistor(1, "r2", inpt_wire=wires[1], outpt_wire=wires[2])

    components = [battery, r0, r1, r2]

    circuit = Circuit(wires, components)

    voltages, currents = circuit.analyze()
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


if __name__ == "__main__":
    main()
