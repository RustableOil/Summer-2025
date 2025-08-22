"""
By providing MSD values measured every 1 ps in plaintext, the following will happen:

1. A regression analysis is performed to obtain diffusion coefficient from MSD for a temperature

2. Repeat step 1 for the other temperatures and store the diffusion coefficients in a list

3. Perform a regression analysis on ln(D) vs. 1/kT

4. Extract E_a and D_0 from linear fit

Contraints:

- nAtoms should be constant over every system

"""

import glob
import re
import statsmodels.api as sm
import math
import numpy as np

nRun = 100
nAtoms = 2049
k = 8.6173E-5
T = np.array([700.0, 800.0, 900.0, 1000.0, 1100.0])
ea_factor = 1 / (k * T)

systems = ["Ni", "NiFe", "NiFeCr"]  # names for folders storing system msd files

def extractTemp(filename):
    match = re.search(r"_(\d+)", filename)
    return int(match.group(1)) if match else -1

def getMSDFit(filename):
    filename = "".join(filename)
    with open(filename, 'r') as f:

        for skipline in range(2):
            next(f)

        msd_list = []
        for line in f:
            newline = line.strip().split()
            msd_list = np.append(msd_list, float(newline[1]))

        msd = np.array(msd_list)

    f.close()

    ps = np.linspace(0, len(msd) - 1, len(msd))
    ps = sm.add_constant(ps)

    x = ps
    y = msd

    results = sm.OLS(y, x).fit()
    print(filename, end="")
    print(results.params)
    return results.params

def getSystemDiffusion(filenames):

    systemMSDParams = []

    for filename in filenames:
        params = getMSDFit(filename)
        systemMSDParams.append(params)

    return np.array(systemMSDParams)

def getEAandD0(params):

    params = np.array(params)

    D_values = params[:,1]

    D_values *= nAtoms

    lnD = np.log(D_values)

    x = ea_factor
    y = lnD

    x = sm.add_constant(x)
    results = sm.OLS(y, x).fit()
    return results.params


for sys_name in systems:

    of = "./system_d0_ea_" + sys_name + ".txt"  # output file

    with open(of, 'w') as f:
        f.write(str(nRun) + "\n")
    f.close()

    with open(of, 'a') as f:

        for I in range(nRun):

            wildcard_filename_combined = "./" + sys_name + "/" + str(I+1) + "_msd_*.txt"
            filenames = glob.glob(wildcard_filename_combined)
            print(filenames)
            filenames.sort(key = extractTemp)
            msd_params = getSystemDiffusion(filenames)
            diff_temp_regr = getEAandD0(msd_params)
            d0 = diff_temp_regr[0]
            ea = diff_temp_regr[1]
            params_out = [sys_name, str(d0), str(ea)]
            f.write(" ".join(params_out) + "\n")

    f.close()




