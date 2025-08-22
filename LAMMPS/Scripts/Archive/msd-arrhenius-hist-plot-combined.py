import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt

system_folders = ["Ni", "NiFe", "NiFeCr"]

indices = np.arange(1, 6)
temperatures = [700, 800, 900, 1000, 1100]
runtime = 5000  # ps
k = 8.6173E-5
ea_factor = [1 / (k * t) for t in temperatures]

def getParameterFromFile(filename, n_atom_consituent):
    with open(filename, "r") as f:
        next(f) # skip header line
        parameter = []
        for line in f:
            line = line.strip()
            if line != '':
                if n_atom_consituent != None:
                    msd = float(line)
                    sd = msd * n_atom_consituent
                    parameter.append(sd)
                else:
                    pe = float(line)
                    parameter.append(pe)

    return parameter

def getFitParams(x, y):
    x = sm.add_constant(x)
    fit = sm.OLS(y, x).fit()
    return fit.params

def getFitFromArray(arr):
    return getFitParams(np.arange(len(arr)), arr)

def plotPE(pe_slice, of):
    fig, ax = plt.subplots()

    y = np.array(pe_slice)
    x = np.arange(len(y))

    ax.plot(x, y, 'b.')

    ax.set_xlabel("Time [ps]")
    ax.set_ylabel("Potential Energy [eV]")
    ax.grid()
    fig.savefig(of)
    plt.close()

    return

def plotPEEnsemble(system_name, pe):    # lol
    for t, temp in enumerate(temperatures):
        of = f"Plots/{system_name}/1_pe_{temp}.png"
        plotPE(pe[1, t], of)

    return

def plotPEFits(system_name, pe_fit_avg):
    fig, ax = plt.subplots()

    for t, temp in enumerate(temperatures):
        b, m = pe_fit_avg[t]
        x = np.arange(runtime)
        y = m * x + b

        ax.plot(x, y, '-')
        ax.text(x[-1], y[-1], f"T={temp}", va='top', ha='center', fontsize=8)

    ax.set_xlabel("Temperature [K]")
    ax.set_ylabel("Potential Energy [eV]")
    ax.grid()

    of = f"Plots/{system_name}/pe-fit.png"
    fig.savefig(of)
    plt.close()

def getPlotStyle(elem):
    if elem == "Ni":
        return 'g'
    elif elem == "Fe":
        return 'r'
    elif elem == "Cr":
        return 'b'
    else:
        return 'k'

def plotElementSD(sd_slice, of, elements):
    fig, ax = plt.subplots()

    for e, elem in enumerate(elements):
        style = getPlotStyle(elem)

        y = np.array(sd_slice[e])
        x = np.arange(len(y))

        ax.plot(x, y, style, label=elem)

    ax.set_xlabel("Time [ps]")
    ax.set_ylabel("Squared Displacement $[Å^2]$")
    ax.legend()
    ax.grid()
    fig.savefig(of)
    plt.close()

    return

def plotSDEnsemble(system_name, sd, elements):

    for t, temp in enumerate(temperatures):
        of = f"Plots/{system_name}/1_msd_{temp}.png"
        plotElementSD(sd[1, t], of, elements)

    return

def plotSDElementContribution(system_name, sd_percent_contributions_avg, elements):
    fig, ax = plt.subplots()

    x = temperatures

    for e, elem in enumerate(elements):
        style = getPlotStyle(elem)

        y = sd_percent_contributions_avg[:, e]

        ax.plot(x, y, style, label=elem)

    ax.set_xlabel("Temperature [K]")
    ax.set_xticks(temperatures)
    ax.set_ylabel("Displacement Percent Contribution [%]")
    ax.legend()
    ax.grid()

    of = f"Plots/{system_name}/sd-element-contributions.png"
    fig.savefig(of)
    plt.close()

    return

def plotArrheniusHistogram(system_name, arrhenius):
    fig, ax = plt.subplots()

    ax.hist(arrhenius[:, 1])

    ax.set_xlabel("Activation Energy [eV]")
    ax.set_ylabel("Count")

    of = f"Plots/{system_name}/arrhenius-histogram.png"
    fig.savefig(of)
    plt.close()

    return

def plotArrheniusAverage(system_name, ea_factor, lnd_total_avg, arrhenius):
    fig, ax1 = plt.subplots()

    x = np.array(ea_factor)
    y = np.array(lnd_total_avg)

    ax1.plot(x, y, 'o')

    b, m = arrhenius

    y = m * x + b

    ax1.plot(x, y, 'k--')

    ax1.set_xlabel("$1/k_bT$ $[eV^{-1}]$")
    ax1.set_ylabel("$ln(D)$ $[Å^2 ps^{-1}]$")
    ax1.grid()

    def inv_kT_to_T(x):
        return 1 / (x * k)

    def T_to_inv_kT(T):
        return 1 / (T * k)

    ax2 = ax1.secondary_xaxis('top', functions=(inv_kT_to_T, T_to_inv_kT))
    ax2.set_xlabel("Temperature [K]")
    ax2.set_xticks(temperatures)

    of = f"Plots/{system_name}/arrhenius.png"
    fig.savefig(of)
    plt.close()

    return

def main():

    for system_idx, system_name in enumerate(system_folders):

        if system_name == "Ni":
            elements = ["Ni"]
            n_atom = {'Ni': 2049}
        elif system_name == "NiFe":
            elements = ["Ni", "Fe"]
            n_atom = {'Ni': 756, 'Fe': 1293}
        elif system_name == "NiFeCr":
            elements = ["Ni", "Fe", "Cr"]
            n_atom = {'Ni': 1511, 'Fe': 218, 'Cr': 320}

        pe                              = np.empty((len(indices), len(temperatures))                    , dtype=object)
        pe_fit                          = np.empty((len(indices), len(temperatures), 2)                 , dtype=float)
        pe_fit_avg                      = np.empty((len(temperatures), 2)                               , dtype=float)
        sd                              = np.empty((len(indices), len(temperatures), len(elements))     , dtype=object)
        sd_total                        = np.empty((len(indices), len(temperatures))                    , dtype=object)
        sd_percent_contributions        = np.empty((len(indices), len(temperatures), len(elements))     , dtype=object)
        sd_percent_contributions_avg    = np.empty((len(temperatures), len(elements))                   , dtype=object)
        d                               = np.empty((len(indices), len(temperatures), len(elements), 2)  , dtype=float)
        d_total                         = np.empty((len(indices), len(temperatures), 2)                 , dtype=float)
        lnd_total                       = np.empty((len(indices), len(temperatures), 2)                 , dtype=float)
        d_total_avg                     = np.empty((len(temperatures), 2)                               , dtype=float)
        lnd_total_avg                   = np.empty((len(temperatures), 2)                               , dtype=float)
        arrhenius                       = np.empty((len(indices), 2)                                    , dtype=float)
        arrhenius_avg                   = np.empty((2)                                                  , dtype=float)

        for i, idx in enumerate(indices):
            for t, temp in enumerate(temperatures):

                f = f"{system_name}/{idx}_pe_{temp}.txt"
                pe[i, t] = getParameterFromFile(f, None)

                pe_fit[i, t] = getFitFromArray(pe[i, t])

                for e, elem in enumerate(elements):

                    f = f"{system_name}/{idx}_msd_{elements[e]}_{temp}.txt"
                    sd[i, t, e] = getParameterFromFile(f, n_atom[elem])

                    d[i, t, e] = getFitFromArray(sd[i, t, e])

                sd_total[i, t] = np.sum(np.stack(sd[i, t, :]), axis=0)

                for e, elem in enumerate(elements):
                    sd_slice = sd[i, t, e]
                    sd_slice_total = sd_total[i, t]

                    sd_percent_contributions[i, t, e] = sd_slice[-1] / sd_slice_total[-1] * 100

                d_total[i, t] = getFitFromArray(sd_total[i, t])

                lnd_total[i, t] = np.log(d_total[i, t])

        for t, temp in enumerate(temperatures):
            pe_fit_avg[t] = np.mean(pe_fit[:, t, :], axis=0)

            d_total_avg[t] =  np.mean(d_total[:, t, :], axis=0)

            lnd_total_avg[t] = np.log(d_total_avg[t])

            sd_percent_contributions_avg[t] = np.mean(sd_percent_contributions[:, t, :], axis=0)

        for i, idx in enumerate(indices):
            arrhenius[i] = getFitParams(ea_factor, lnd_total[i, :, 1])

        arrhenius_avg = getFitParams(ea_factor, lnd_total_avg[:, 1])

        print(f"Plotting {system_name} PE ensemble...")

        plotPEEnsemble(system_name, pe)

        print(f"Plotting {system_name} PE fits per runtime...")

        plotPEFits(system_name, pe_fit_avg)

        print(f"Plotting {system_name} SD ensemble...")

        plotSDEnsemble(system_name, sd, elements)

        print(f"Plotting {system_name} element contributions...")

        plotSDElementContribution(system_name, sd_percent_contributions_avg, elements)

        print(f"Plotting {system_name} Arrhenius histogram...")

        plotArrheniusHistogram(system_name, arrhenius)

        print(f"{system_name} Arrhenius parameters: Ea = {abs(arrhenius_avg[1])} (eV), D0 = {arrhenius_avg[0]}.")

        print(f"Generating {system_name} Arrhenius plots.")

        plotArrheniusAverage(system_name, ea_factor, lnd_total_avg[:, 1], arrhenius_avg)

        print(f"{system_name} finished ")

    return

main()
