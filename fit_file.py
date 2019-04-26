import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

class fit_file:

    # initialize object of class data
    # precondition: data is already aligned (or set to zero)
    def __init__(self, time, data):
        self.time = []
        self.data = []

        for t in time:
            self.time.append(t)
        for d in data:
            self.data.append(d)

        self.time = np.array(self.time)
        self.data = np.array(self.data)

        indexorder = np.argsort(self.time)
        self.time = self.time[indexorder]
        self.data = self.data[indexorder]

        self.cftime = []
        self.cfdata = []

        self.theortime = []
        self.theordata = []

        self.chargeuptime = []
        self.chargeupdata = []

        self.decaytime = []
        self.decaydata = []

        self.ssmean = 0

        self.fig = plt.figure(1)

    # sort the standard fit and theoretical fit data and time so that it is in chronological order
    def sort(self):
        if(len(self.cftime) > 0):
            indexorder = np.argsort(self.cftime)
            self.cftime = self.cftime[indexorder]
            self.cfdata = self.cfdata[indexorder]
        if(len(self.theortime) > 0):
            indexorder = np.argsort(self.theortime)
            self.theortime = self.theortime[indexorder]
            self.theordata = self.theordata[indexorder]

    # function to find the max threshold which is 2 times the standard deviation of the steady state
    # flow subtracted from the mean of the steady state flow
    # params: min is the time value for when to start recording steady state flow values
    #         max is the time value for when to stop recording steady state flow values
    # returns: threshold value
    def threshold(self, min, max):
        thresholdarray = []
        for i in range(len(self.data)):
            if ((self.time[i] > min) and (self.time[i] < max)):
                thresholdarray.append(self.data[i])

        thresholdarray = np.array(thresholdarray)
        stddev = np.std(thresholdarray)
        mean = np.mean(thresholdarray)
        self.ssmean = mean

        print("mean:", mean)
        print("stddev:", stddev)

        threshold = mean - (2*stddev)
        print("threshold:", threshold)
        return threshold

    # filter into cf data and time with min and max, convert to nparray and call sort
    # stops collecting data after run reaches steady state flow
    # params: min is the lower threshold for collecting the cf data
    #         max is the upper threshold for collecting the cf data
    #         method is the threshold value, i.e. time means the cutoff values are time values
    #                                             data means the cutoff values are data
    #         fit is the type of curve fit - linear, logarithmic, or quadratic
    def standard_collect(self, min, max, method, fit):
        count = 0
        for i in range(len(self.data)):
            if (method == "data"):
                if ((self.data[i] > min) and (self.data[i] < max)):
                    self.cftime.append(self.time[i])
                    self.cfdata.append(self.data[i])
                if (self.data[i] > max):
                    count = count + 1
                    if (count > 20):
                        break
            if (method == "time"):
                if ((self.time[i] > min) and (self.time[i] < max)):
                    self.cftime.append(self.time[i])
                    self.cfdata.append(self.data[i])

        self.cftime = np.array(self.cftime)
        self.cfdata = np.array(self.cfdata)

        self.sort()

    # filter into theor data and time with 0.01 min (for log function) and threshold max,
    # convert to nparray and call sort
    # stops collecting data after run reaches steady state flow
    def theoretical_collect(self, min, max):
        count = 0
        threshold = self.threshold(min, max)
        for i in range(len(self.data)):
            if ((self.time[i] > 0.01) and (self.data[i] < threshold)):
                self.theortime.append(self.time[i])
                self.theordata.append(self.data[i])
            if (self.data[i] > threshold):
                count = count + 1
                # removes influence of outliers
                if (count > 10):
                    break

        self.theortime = np.array(self.theortime)
        self.theordata = np.array(self.theordata)

        self.sort()

    # plots the chosen fit (linear, log or quadratic) and residuals on a figure consisting of two frames
    # params: min is the lower threshold for collecting the cf data
    #         max is the upper threshold for collecting the cf data
    #         method is the threshold value type, i.e. time means the cutoff values are time values
    #                                             data means the cutoff values are data
    #         fit is the type of curve fit - linear, logarithmic, or quadratic
    #         syringe is the type of syringe: plastic or glass
    #         flowrate is the steady state flowrate (3, 6, or 9 ml/min)
    def standard_fit(self, min, max, method, fit, syringe, flowrate):
        self.standard_collect(min, max, method, fit)

        frame1 = self.fig.add_axes((.1,.3,.8,.6))
        frame1.plot(self.time, self.data, "m.", markersize =1)

        # fit functions for different fits
        if (fit == "linear"):
            def fit_func(x, a, b):
                return a*x + b

            params = curve_fit(fit_func, self.cftime, self.cfdata)
            [a, b] = params[0]

            labelcf = str(round(a,4))+"x+"+str(round(b,4))
            frame1.plot(self.cftime, a*(self.cftime)+b, "b-", markersize=1, label=labelcf)

        if (fit == "logarithmic"):
            def fit_func(x, a, b):
                return a+b*np.log(x)

            params = curve_fit(fit_func, self.cftime, self.cfdata)
            [a, b] = params[0]

            labelcf = str(round(a,4))+"+"+str(round(b,4))+"log(x)"
            frame1.plot(self.cftime, a+b*np.log(self.cftime), "b-", markersize=1, label=labelcf)

        if (fit == "quadratic"):
            def fit_func(x, a, b, c):
                return (a*x*x)+(b*x)+c

            params = curve_fit(fit_func, self.cftime, self.cfdata)
            [a, b, c] = params[0]

            labelcf = str(round(a,4))+"x^2+"+str(round(b,4))+"x+"+str(round(c,4))
            frame1.plot(self.cftime, (a*self.cftime*self.cftime)+(b*self.cftime)+c, "b-", markersize=1, label=labelcf)

        frame1.set_xticklabels([])
        frame1.grid()

        # ***** plot residuals *****
        if (fit == "quadratic"):
            difference = fit_func(self.cftime, a, b, c) - self.cfdata
        else:
            difference = fit_func(self.cftime, a, b) - self.cfdata

        frame2 = self.fig.add_axes((.1,.1,.8,.2))
        frame2.set_xlim(-0.5, 10.5)
        labelres = "Residuals"
        frame2.plot(self.cftime, difference, 'oc', markersize = 1, label = labelres)
        frame2.grid()

        frame1.set_ylabel("Flow (ml/min)")
        frame2.set_xlabel("Time (seconds)")
        frame1.set_title("Flow through "+syringe+" syringe approaching "+flowrate+"ml/min")

        frame1.legend(loc='lower right')
        frame2.legend(loc='upper right')

    # plots the theoretical fit (equation with log and linear components: alog(bx)+cx+d) and residuals on a figure consisting of two frames
    # params: min is the time value for when to start recording steady state flow values (used for threshold function)
    #         max is the time value for when to stop recording steady state flow values (used for threshold function)
    #         format is the colour and marker for regular plot
    #         formatfit is the colour and marker for theoretically fitted plot
    #         syringe is the type of syringe: plastic or glass
    #         flowrate is the steady state flowrate (3, 6, or 9 ml/min)
    def theoretical_fit(self, min, max, format, formatfit, syringe, flowrate):
        self.theoretical_collect(min, max)

        frame1 = self.fig.add_axes((.1,.3,.8,.6))
        frame1.plot(self.time, self.data, format, marker = '.', linestyle = "None", markersize =1)

        def fit_func(x, a, b, c, d):
            return a*np.log(b*x)+c*x+d

        params = curve_fit(fit_func, self.theortime, self.theordata)
        [a, b, c, d] = params[0]

        labeltheor = str(round(a,4))+"log("+str(round(b,4))+"x)+"+str(round(c,4))+"x+"+str(round(d,4))
        frame1.plot(self.theortime, a*np.log(b*(self.theortime))+c*(self.theortime)+d, formatfit, markersize=1)

        difference = fit_func(self.theortime, a, b, c, d) - self.theordata

        frame2 = self.fig.add_axes((.1,.1,.8,.2))
        frame2.set_xlim(-0.5, 35.5)
        frame2.set_ylim(-3, 3)
        frame1.set_ylim(0, 10)
        frame1.set_xlim(-0.5, 35.5)

        frame2.plot(self.theortime, difference, 'ok', markersize = 0.5)
        frame2.grid(False)
        frame1.grid(True)
        #frame1.legend(loc='lower right')
        frame1.set_ylabel("Flow (ml/min)")
        frame2.set_xlabel("Time (seconds)")
        frame1.set_title("Flow through "+syringe+" syringe approaching "+flowrate)


    # same as theoretical_fit but without residuals plotted
    def theoretical_fit_wo_res(self, min, max, format, formatfit, syringe, flowrate):
        self.theoretical_collect(min, max)

        frame1 = self.fig.add_axes((.1,.1,.8,.8))
        frame1.plot(self.time, self.data, format , markersize =1)

        def fit_func(x, a, b, c, d):
            return a*np.log(b*x)+c*x+d

        params = curve_fit(fit_func, self.theortime, self.theordata)
        [a, b, c, d] = params[0]

        #labeltheor = str(round(a,4))+"log("+str(round(b,4))+"x)+"+str(round(c,4))+"x+"+str(round(d,4))
        frame1.plot(self.theortime, a*np.log(b*(self.theortime))+c*(self.theortime)+d, formatfit, markersize=1)

        frame1.set_ylim(0, 20)
        frame1.set_xlim(-0.5, 20.5)
        frame1.grid(True)
        #frame1.legend(loc='lower right')
        frame1.set_ylabel("Flow (ml/min)")
        frame1.set_xlabel("Time (seconds)")
        frame1.set_title("Flow through "+syringe+" syringe approaching "+flowrate)

    # regular plotting without any curve fitting
    # params: xlim is the righthand xlimit.. adjustable because different runs go for different periods of time
    #         format is the colour and marker for plot
    #         syringe is the type of syringe: plastic or glass
    #         flowrate is the steady state flowrate (3, 6, or 9 ml/min)
    def data_plot(self, xlim, format, syringe, flowrate):
        frame1 = self.fig.add_axes((.1,.1,.8,.8))
        frame1.plot(self.time, self.data, format, markersize =1)
        frame1.set_ylim(0, 20)
        frame1.set_xlim(-0.5, xlim)
        frame1.grid(True)
        frame1.set_ylabel("Flow (ml/min)")
        frame1.set_xlabel("Time (seconds)")
        frame1.set_title("Flow through "+syringe+" syringe approaching "+flowrate)

    # collecting data to be put into the curve fitting arrays for the ramp up portion of the graphs
    # params: min is the time value for when to start recording steady state flow values (used for threshold function)
    #         max is the time value for when to stop recording steady state flow values (used for threshold function)
    def charging_up_collect(self, min, max):
        count = 0
        threshold = self.threshold(min, max)
        for i in range(len(self.data)):
            if ((self.time[i] > 0) and (self.data[i] < threshold)):
                self.chargeuptime.append(self.time[i])
                self.chargeupdata.append(self.data[i])
            if (self.data[i] > threshold):
                # the shape of the graph of a charging capacitor follows a curve with a plateau
                # in order to capture part of the plateau so that the fit better describes the curve
                # I've included 50 data points along the flat
                if (count < 50):
                    self.chargeuptime.append(self.time[i])
                    self.chargeupdata.append(self.data[i])
                else:
                    break
                count = count + 1

        self.chargeuptime = np.array(self.chargeuptime)
        self.chargeupdata = np.array(self.chargeupdata)

        self.sort()

    # provides a curve fit to the ramp up of the flow
    # need to change the position of the charging label manually
    def charging_up_fit(self, min, max, formatfit):
        self.charging_up_collect(min, max)

        def fit_func(x, a, b, c):
            return a*(1-np.exp(-(x/b)))+c

        params = curve_fit(fit_func, self.chargeuptime, self.chargeupdata)
        [a, b, c] = params[0]

        frame1 = self.fig.add_axes((.1,.1,.8,.8))
        frame1.plot(self.chargeuptime, (a*(1-np.exp(-(self.chargeuptime/b)))+c), formatfit , markersize=1)

        labelcharging = str(round(a,2))+"(1-e^(-x/"+str(round(b,2))+"))+"+str(round(c,2))
        frame1.annotate(labelcharging, xy=(0.4,1), xytext=(1.4,1.2), arrowprops=dict(facecolor='k', width = 0.2, headwidth = 5, headlength = 5))
        labelsteady = "Steady state flow: "+ str(round(self.ssmean,2))+" ml/min"
        frame1.annotate(labelsteady, xy=(5,7))
        labeltime = "from "+str(round(min,1))+" to "+str(round(max,1))+" seconds"
        frame1.annotate(labeltime, xy=(5,6.7))

# **************************** didn't use *********************************
    # # didn't end up using this code because the info it provided was not
    # # that useful.. it most likely needs to be manipulated for each run
    # def decay_collect(self, min, max):
    #     threshold = self.threshold(min, max)
    #
    #     for i in range(len(self.data)):
    #
    #         if ((self.time[i]>max) and (self.data[i] < (threshold-0.2)) and (self.data[i] > 0)):
    #                 self.decaytime.append(self.time[i])
    #                 self.decaydata.append(self.data[i])
    #         else:
    #             continue
    #
    #     self.decaytime = np.array(self.decaytime)
    #     self.decaydata = np.array(self.decaydata)
    #
    #     print(self.decaytime)
    #     print(self.decaydata)
    #
    #     self.sort()
    #
    # # didn't end up using this code because the info it provided was not
    # # that useful.. it most likely needs to be manipulated for each run
    # def decay_fit(self, min, max, formatfit):
    #     self.decay_collect(min, max)
    #
    #     def fit_func(x, a, b, c):
    #         return a*(np.exp(-(x/b)))+c
    #
    #     params = curve_fit(fit_func, self.decaytime, self.decaydata)
    #     [a, b, c] = params[0]
    #
    #     frame1 = self.fig.add_axes((.1,.1,.8,.8))
    #     frame1.plot(self.decaytime, (a*(np.exp(-(self.decaytime/b)))+c), formatfit , markersize=1)
    #
    #     labelcharging = str(round(a,2))+"(e^(-x/"+str(round(b,2))+"))+"+str(round(c,2))
    #     frame1.annotate(labelcharging, xy=(17.5,0.5), xytext=(13,4), arrowprops=dict(facecolor='k', width = 0.2, headwidth = 5, headlength = 5))
