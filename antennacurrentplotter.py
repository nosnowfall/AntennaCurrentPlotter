import logging
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
from scipy import integrate
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from flame_mods.EngineeringNotation import *
from os import path as ospath
import re

def testfunc(xin:np.ndarray)->list[float]:
    """
    test function for verifying integrator
    """
    return [np.sin(2*np.pi*10E6*xx) for xx in xin]

def skip_blanks(filein):
    for line in filein:
        if not re.match(b'.+,.+', line):
            continue
        yield line
        
def rms(y:np.ndarray,x:np.ndarray) -> float:
    """
    Calculate the RMS of sampled function y(x)
    """
    y2 = np.square(y)
    dx = x[-1] - x[0]
    rmsval = np.sqrt(integrate.trapezoid(y2, x)/dx)
    return rmsval

def mean(y:np.ndarray,x:np.ndarray) -> float:
    """
    Calculate the mean of sampled function y(x)
    """
    dx = x[-1] - x[0]
    meanval = integrate.trapezoid(y,x)/dx
    return meanval

def main():
    # choose a file for analysis
    root = tk.Tk()
    root.withdraw() # we only want to draw the pop-up dialogs
    filename = filedialog.askopenfilename(title='Select Waveform Data', filetypes=[('csv','.csv')])
    fsym = simpledialog.askinteger("Symbol Rate", "please enter symbol rate (kHz)", initialvalue=400, minvalue=100, maxvalue=3010) * 1000
    root.destroy() # prevents Windows from crashing

    logging.info(f'analyzing {ospath.basename(filename)}')
    infile = open(filename, 'rb')
    skipper = skip_blanks(infile)
    wfm = np.genfromtxt(skipper, delimiter=',', unpack=True, autostrip=True)
    # try: # sometimes the csv has a space after comma
    #     wfm = np.loadtxt(filename, delimiter=',', unpack=True)
    # except ValueError:
    #     wfm = np.genfromtxt(filename, delimiter=', ', unpack=True) # loadtxt doesn't support multi-char delimiter
    t = wfm[0]
    waves = wfm[1:]
    infile.close()

    # get some info about the sample
    dt = t[-1] - t[0]
    # fsam = len(wfm[0]) / dx # alternate sample rate calc
    fsam = 1/(t[1] - t[0])
    logging.info(f'recovered {engf(len(t))} samples at {sif(fsam, "S/s")} over {sif(dt,"s")}')
    fcar = 10.6625*10**6 # assuming NIWC test data

    # set limits on analysis to about 5 symbols
    sam_per_car = int(fsam / fcar)
    sam_per_sym = int(fsam / fsym)
    minsam = 0
    maxsam = int(5*fsam/fsym)
    location = int(len(t) / 2) # bias to middle of plot
    
    logging.info(f'{len(waves)} {"waveforms" if len(waves)>1 else "waveform"}, expecting {sif(fcar,"Hz")} carrier and {sif(fsym,"Hz")} symbol rate')
    
    # do math on 100 symbols for each waveform
    subtitles = [f'Trace {n}' for n in range(1, len(waves)+1)]
    for num, wave in enumerate(waves, 1):
        valrms = rms(wave[minsam:20*maxsam], t[minsam:20*maxsam])
        valmean = mean(wave[minsam:20*maxsam], t[minsam:20*maxsam])
        logging.info(f'Waveform {num}: RMS {engf(valrms)}, MEAN {engf(valmean)}')

        # some wicked naming schemes
        if abs(valmean) <= 0.2:
            subtitles[num-1] = 'RF Current'
        elif 4.5 <= valmean <= 5.5:
            subtitles[num-1] = '5v Logic Rail'
        elif 5.5 <= valmean: 
            subtitles[num-1] = 'Bias Voltage'


    # plotting
    fig = make_subplots(rows=len(waves), cols=1, y_title='volts, amps', x_title='seconds', subplot_titles=subtitles)
    for num, wave in enumerate(waves, 1):
        fig.add_trace(go.Scatter(x=t[minsam:maxsam], y=wave[minsam:maxsam]), row=num, col=1)
    fig.update_layout(title_text=f'{ospath.basename(filename)}')
    fig.show()

    return None

if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        encoding = 'utf-8'
    )
    logging.debug('Logging initialized')
    try:
        main()
    except Exception as e:
        logging.warning(f'Execution failed with error: {repr(e)}')
        exit()