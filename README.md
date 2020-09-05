# circuit-analysis
This tool allows you to define any RC circuit simply by defining which wires are connected to which ends of which components, then it will do all the rest of the work for you. 
- It uses Kirchhoff's Junction Law and Kirchhoff's Voltage Law to generate a set of simulataneous linear equations in the form of a matrix which is used to solve for  the current through each component. 
  - Kirchhoff's Voltage Law loops are found using a Depth First Search over the components until the starting component is found again, at which point the shortest loop leading back to the start is backtracked.
  - Kirchoff's Loop Law equations are simply found by looking at the components (and their directions) attatched to each wire and setting their net current to 0A.
- It then finds the voltage of each wire by setting a 0V wire and using the voltage change across each component to set the voltages of its neighboring wires using a search (arbitrarily depth first) over the wires.
