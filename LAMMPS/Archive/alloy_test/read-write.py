'''

s

'''

from ase.io import read, write
import numpy as np

#read last configuration of trajmd.xyz
atoms = read('trajmd.xyz', index=-1)

#add cell information to the atoms object
cell = np.array([[35.2, 0, 0], [0,35.2,0], [0,0,35.2]])
atoms.set_cell(cell)

#add pbc information to the atoms object
atoms.set_pbc(True)

#Write to file
write('last_config_of_traj.xyz', atoms)
