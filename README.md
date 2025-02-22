# AntennaCurrentPlotter
Interactive plotting of oscilloscope waveforms from my non-LTI amplifier research

This script provides convenient plots and waveform analysis for a specific set of results common in my graduate research. This convenience comes at the cost of many dependencies:

**plotly**: pretty plots with a better zoom feature than matplotlib

**numpy**: data arrays from csv, math

**scipy**: waveform analysis (mean, rms)

**tkinter**: file selection and symbol rate GUIs

**EngineeringNotation**: formatting math results

**os.path**: printing file name to plot title

**re**: stripping garbage lines that scopes sometimes put at the end of capture files

By default, the script asks you for a csv file and a feature frequency. The first column should be time-axis values and every subsequent column its own waveform at those time points. It then plots 5 feature periods and calculates mean and rms values over 100 periods for each waveform in the file. This requires that there be >100 feature periods within your time-series data. The plotter also attempts to guess the names of each waveform - which is highly specific to my project but it looks nice when they are correct.
