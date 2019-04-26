import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from matplotlib.lines import Line2D

import glob

import data_file
import fit_file

# ******************************************** #
flowrate = "18mlmin on Ignite #6"
syringes = "1ml BD, Injekt, and Omnifix"
pathbd = "./data/BD1/18mlmin/*.txt"
pathinjbr = "./data/INJEKT1/18mlmin/*.txt"
pathomnibr = "./data/OMNIFIX1/18mlmin/*.txt"
end = 6
# ******************************************** #

mastertime = [[] for i in range(4)]
masterdata = [[] for i in range(4)]

filesbd = glob.glob(pathbd)
filesinjbr = glob.glob(pathinjbr)
filesomnibr = glob.glob(pathomnibr)

allfiles = [filesbd, filesinjbr, filesomnibr]
formats = ["b.", "g.", "y."]
formatfits = ["b", "g", "y"]

for i in range(len(allfiles)):
    for filename in allfiles[i]:
        file = data_file.data_file(filename,end)
        file.interpolate()
        for j in range(len(file.idata)):
            masterdata[i].append(file.idata[j])
            mastertime[i].append(file.itime[j])

    cf_file = fit_file.fit_file(mastertime[i], masterdata[i])
    cf_file.data_plot(end+0.5, formats[i], syringes, flowrate)

    # cf_file.standard_fit(10, 20, "time", "linear", "5ml BD, Injekt, and Omnifix", flowrate)
    cf_file.theoretical_fit_wo_res(5, 10, formats[i], formatfits[i], "5ml BD, Injekt, and Omnifix", flowrate)

    cf_file.standard_collect(3, 15, "data", "linear")
    def fit_func(x, a, b):
        return a*x + b

    params = curve_fit(fit_func, cf_file.cftime, cf_file.cfdata)
    [a, b] = params[0]

    plt.plot(cf_file.cftime, a*(cf_file.cftime)+b, formatfits[i])

plt.show()
