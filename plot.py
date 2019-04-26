import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from matplotlib.lines import Line2D

import glob

import data_file
import fit_file

# ******************************************** #
path = "./data/INJEKT5/3mlmin/*.txt"
flowrate = "3mlmin on Ignite #6"
syringe = "Braun Injekt 5ml"
end = 85
format = "g."
# ******************************************** #

mastertime = [[] for i in range(4)]
masterdata = [[] for i in range(4)]

files = glob.glob(path)

for i in range(4):
    for name in files:
        file = data_file.data_file(name, end)
        file.interpolate()

        for j in range(len(file.idata)):
            masterdata[i].append(file.idata[j])
            mastertime[i].append(file.itime[j])

    cf_file = fit_file.fit_file(mastertime[i], masterdata[i])
    # # cf_file.theoretical_fit_wo_res(2, 10, 'b.', 'c', syringe, flowrate)

    cf_file.data_plot(end+0.5, format, syringe, flowrate)
    # cf_file.charging_up_fit(4, 8, 'k')

    # cf_file.decay_fit(2, 4, 'k')
    cf_file.standard_collect(5, 15, "data","linear")

plt.show()
