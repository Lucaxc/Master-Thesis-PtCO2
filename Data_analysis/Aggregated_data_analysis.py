'''
------------------------------------------------------------------------------------------
                        PYTHON SCRIPT FOR DATAFRAME ANALYSIS

Author: Luca Colombo, MSc Student in Biomedical Engineering - Technologies for Electronics

This script is used to perform statistical analysis on data retrieved from script named
<Dataframe_Analysis>.

\Parameters:
    @param <filename.csv>: at the beginning of the script change the file name to
            associate the running of the script with the desired CSV file. It includes
            processing both for PCB device data and Sentec device data
    @param <subject_id>: subject that has to be considered in the exponential fitting 
            part of the script.
------------------------------------------------------------------------------------------
'''

from functools import partial
from pickle import FALSE, TRUE
from re import sub
from turtle import color
from unittest.mock import patch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
from sklearn import preprocessing
from sklearn import metrics
from scipy import stats
import math
import scipy

# Importing dataframe
print("-------------------------------------------------------------------------")
print("------------------------------- New run ---------------------------------")
print("-------------------------------------------------------------------------")

subject_id = 1

'''
---------------------------------------------------------------------------------
DATAFRAME IMPORT

In the following section dataframes are imported and prepared for data analysis.
Dataframes to be considered are separately for lobe and forearm.
Merge dataset is used for statistical analysis in a related script
---------------------------------------------------------------------------------
'''
df_pcb = pd.read_csv('CO2_df_10_median_P.csv', sep=";")
df_sentec = pd.read_csv('Sentec_df_10_median_P.csv', sep=";")
print("\n\nDataframe PCB with START:")
print(df_pcb)

# Rebreathing index identification
index_start_rebreathing = df_pcb[df_pcb["28_01P"] == "START"].index.values
print("\nIndex start rebreathing: ")
print(index_start_rebreathing)

# Baseline array extraction
baseline_arr_PCB = []
baseline_arr_sentec = []
for i in range(0, len(df_pcb.columns), 1):
    baseline_arr_PCB.append(
        round(float(df_pcb.iloc[index_start_rebreathing-1, i].values), 2))
    baseline_arr_sentec.append(
        round(float(df_sentec.iloc[index_start_rebreathing-1, i].values), 2))

print("\n\nBaseline array PCB: ")
print(baseline_arr_PCB)
print("\n\nBaseline array Sentec: ")
print(baseline_arr_sentec)

# START row removal
df_pcb = df_pcb.drop(index_start_rebreathing, axis=0)
df_pcb = df_pcb.reset_index()
df_sentec = df_sentec.drop(index_start_rebreathing, axis=0)
df_sentec = df_sentec.reset_index()
#print("\n\nDataframe PCB without START row:")
# print(df_pcb)

# Removing Rows with NaN
df_pcb = df_pcb.dropna()
df_sentec = df_sentec.dropna()
offset = df_pcb.iloc[0, 0]
offset = int(offset)
print("\n\nOffset is: %s" % offset)

df_pcb.pop('index')
df_sentec.pop('index')
df_pcb = df_pcb.reset_index(drop=TRUE)
df_sentec = df_sentec.reset_index(drop=TRUE)
#print("\n\nDataframe PCB without NaN rows:")
# print(df_pcb)
# print(type(df["28_01"][0]))


'''
---------------------------------------------------------------------------------
DATA MERGE

In the following section dataframes are merged
---------------------------------------------------------------------------------
'''
# Summing values row by row
Data_matrix = []
Data_matrix_sentec = []
Data_matrix_no_offset = []
Data_matrix_no_offset_sentec = []
rows = len(df_pcb.index)
columns = len(df_pcb.columns)
# print(columns)

for i in range(0, len(df_pcb.columns), 1):
    append = df_pcb.iloc[:, i].values
    Data_matrix.append(append)
    Data_matrix_sentec.append(df_sentec.iloc[:, i].values)
print("\n\nData matrix PCB: ")
print(Data_matrix)
# print("\n\nData matrix Sentec: ")
# print(Data_matrix_sentec)

# Generation of arrays corresponding to columns, subtraction of the baseline and deltas computation
Data_matrix_no_offset = Data_matrix
Data_matrix_no_offset_sentec = Data_matrix_sentec
delta_matrix_pcb = []
delta_matrix_pcb_normalized = []
delta_matrix_sentec = []
delta_matrix_sentec_normalized = []
print("\n\n")
print(Data_matrix_no_offset[0])
print("\n\nColumns of data matrix: ")
print(len(Data_matrix_no_offset))  # numbers of columns
delta_PCB = []
delta_sentec = []
support_PCB = []
support_PCB_normalized = []
support_sentec = []
support_sentec_normalized = []
for i in range(0, len(Data_matrix_no_offset), 1):
    # support.append(Data_matrix_no_offset[i].astype(float))

    # conversion of data_matrix column into array of float
    support_PCB = Data_matrix_no_offset[i].astype(float)

    # baseline subrtaction from array
    support_PCB = support_PCB - baseline_arr_PCB[i]

    # Data normalization
    support_PCB_normalized = (support_PCB/baseline_arr_PCB[i]) * 100
    delta_matrix_pcb.append(support_PCB)
    delta_matrix_pcb_normalized.append(support_PCB_normalized)
    # print(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]))
    # Array of delta values from start rebreathing to maximum
    delta_PCB.append(
        round(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]), 2))
    support_sentec = Data_matrix_no_offset_sentec[i].astype(float)

    # baseline subrtaction from array
    support_sentec = support_sentec - baseline_arr_sentec[i]
    support_sentec_normalized = (support_sentec/baseline_arr_sentec[i]) * 100
    delta_matrix_sentec.append(support_sentec)
    delta_matrix_sentec_normalized.append(support_sentec_normalized)
    # print(support_sentec)
    # print(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]))
    delta_sentec.append(
        round(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]), 2))

print("\n\n------------------------------------------------------------------------------------")
print("\n\nMatrix of delta PCB:")
print(delta_matrix_pcb)
'''
print("\n\nMatrix of delta Sentec:")
print(delta_matrix_sentec)
print("\n\n------------------------------------------------------------------------------------")
print("\n\nMatrix of normalized delta PCB:")
print(delta_matrix_pcb_normalized)
print("\n\nMatrix of normalized delta Sentec:")
print(delta_matrix_sentec_normalized)
print("\n\n------------------------------------------------------------------------------------")
print("PCB Delta values from baseline: ")
print(delta_PCB)
print("\nSentec Delta values from baseline: ")
print(delta_sentec)
print("------------------------------------------------------------------------------------")
'''
# Generation of a unique array for aggregated analysis
arr_sum_device = []
arr_sum_sentec = []
arr_sum_device_delta = []
arr_sum_sentec_delta = []
arr_sum_device_normalized = []
arr_sum_sentec_normalized = []
partial_total_device = 0
partial_total_sentec = 0
partial_total_device_delta = 0
partial_total_sentec_delta = 0
partial_total_device_normalized = 0
partial_total_sentec_normalized = 0

for j in range(0, rows, 1):
    for i in range(0, columns, 1):
        partial_total_device += round(float(Data_matrix[i][j]), 2)
        partial_total_sentec += round(float(Data_matrix_sentec[i][j]), 2)
        partial_total_device_delta += round(float(delta_matrix_pcb[i][j]), 2)
        partial_total_sentec_delta += round(
            float(delta_matrix_sentec[i][j]), 2)
        partial_total_device_normalized += round(
            float(delta_matrix_pcb_normalized[i][j]), 2)
        partial_total_sentec_normalized += round(
            float(delta_matrix_sentec_normalized[i][j]), 2)

    # print(Data_matrix[i][j])
    arr_sum_device.append(round(partial_total_device/columns, 2))
    arr_sum_sentec.append(round(partial_total_sentec/columns, 2))
    arr_sum_device_delta.append(round(partial_total_device_delta/columns, 2))
    arr_sum_sentec_delta.append(round(partial_total_sentec_delta/columns, 2))
    arr_sum_device_normalized.append(round(partial_total_device_normalized, 2))
    arr_sum_sentec_normalized.append(round(partial_total_sentec_normalized, 2))
    partial_total_device = 0
    partial_total_sentec = 0
    partial_total_device_delta = 0
    partial_total_sentec_delta = 0
    partial_total_device_normalized = 0
    partial_total_sentec_normalized = 0

'''
print("\n\nArray of the sum:")
print(arr_sum_device)
print(arr_sum_sentec)

print("\n\nArray of the delta sum:")
print(arr_sum_device_delta)
print(arr_sum_sentec_delta)

print("\n\nArray of the normalized sum:")
print(arr_sum_device_normalized)
print(arr_sum_sentec_normalized)

print("\n\nNumber of array elements:")
print(len(arr_sum_device))
print(len(arr_sum_sentec))

print("\n\nNumber of array elements delta:")
print(len(arr_sum_device_delta))
print(len(arr_sum_sentec_delta))

print("\n\nNumber of array elements normalized:")
print(len(arr_sum_device_normalized))
print(len(arr_sum_sentec_normalized))
'''

# Plot with mean values (no standard deviation)
plt.figure(0)
y1 = arr_sum_sentec
x1 = range(0, len(arr_sum_sentec), 1)
plt.title("MEDIAN VALUES - Sentec Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Median values', 'Start rebreathing',
           'End rebreathing'], loc="upper left")

plt.figure(1)
y1 = arr_sum_sentec_delta
x1 = range(0, len(arr_sum_sentec_delta), 1)
plt.title("DELTA MEDIAN VALUES - Sentec Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Median values', 'Start rebreathing',
           'End rebreathing'], loc="upper left")

plt.figure(2)
y1 = arr_sum_device_delta
x1 = range(0, len(arr_sum_device_delta), 1)
plt.title("DELTA MEDIAN VALUES - PCB Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Median values', 'Start rebreathing',
           'End rebreathing'], loc="upper left")


plt.figure(3)
y1 = arr_sum_device
x1 = range(0, len(arr_sum_device), 1)
plt.title("MEDIAN VALUES - PCB Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Median values', 'Start rebreathing',
           'End rebreathing'], loc="upper left")

plt.figure(4)
y1 = arr_sum_device_normalized
x1 = range(0, len(arr_sum_device_normalized), 1)
plt.title("NORMALIZED VALUES - PCB Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Median values', 'Start rebreathing',
           'End rebreathing'], loc="upper left")

plt.figure(5)
y1 = arr_sum_device_normalized
x1 = range(0, len(arr_sum_device_normalized), 1)
plt.title("NORMALIZED VALUES - PCB Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Median values', 'Start rebreathing',
           'End rebreathing'], loc="upper left")

# Standard deviation computation
arr_row = []
std_arr = []
count = 0
for j in range(0, rows, 1):
    for i in range(0, columns, 1):
        arr_row.append(round(float(Data_matrix[i][j]), 2))
    std_arr.append(round(stat.stdev(arr_row), 2))
    count += 1
    # print("Standard Deviation of sample %s is % s " % (count, std_arr[j]))
    arr_row = []
    # print(arr_row)

# Mean standard deviation
total_std = 0
average_std = 0
for i in range(0, len(std_arr), 1):
    total_std += std_arr[i]
average_std = round(float(total_std/len(std_arr)), 2)
print("\n\nAverage std: %s" % average_std)

# Plot with standard deviation
plt.figure(6)
plt.title("Mean values and Standard deviation - PCB Device Forearm data")
plt.errorbar(x1, y1, std_arr, color='blue',
             fmt='-*', ecolor="red", elinewidth=0.5)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.text(30, 1010, "Average Standard Deviation = %s ppm" %
         average_std, fontsize=7)
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Start rebreathing', 'End rebreathing',
           'Average values and std'], loc="upper left")

# Plot with couples of delta values - for correlation
plt.figure(7)
plt.title("Sentec - PCB device correlation analysis")
plt.xlabel('Sentec measured CO2 [mmHg]')
plt.ylabel('PCB device measured [ppm]')
plt.plot(delta_sentec, delta_PCB, 'o', color="blue")


'''
---------------------------------------------------------------------------------
BOXPLOT

In the following section boxplots of PCB device data are generated

BOXPLOT PATCH ARTIST
plt.boxplot(data[:,:3], positions=[1,2,3], notch=True, patch_artist=True,
            boxprops=dict(facecolor=c, color=c),
            capprops=dict(color=c),
            whiskerprops=dict(color=c),
            flierprops=dict(color=c, markeredgecolor=c),
            medianprops=dict(color=c),
            )
---------------------------------------------------------------------------------
'''
# Device variables
partial_data_for_boxplot = []
partial_data_for_boxplot_delta = []
partial_data_for_boxplot_normalized = []
data_for_boxplot = []
data_for_boxplot_delta = []
data_for_boxplot_normalized = []

# Sentec Variables
S_partial_data_for_boxplot = []
S_partial_data_for_boxplot_delta = []
S_partial_data_for_boxplot_normalized = []
S_data_for_boxplot = []
S_data_for_boxplot_delta = []
S_data_for_boxplot_normalized = []

for j in range(0, rows, 1):
    for i in range(0, columns, 1):
        partial_data_for_boxplot.append(round(float(Data_matrix[i][j]), 2))
        partial_data_for_boxplot_delta.append(
            round(float(delta_matrix_pcb[i][j]), 2))
        partial_data_for_boxplot_normalized.append(
            round(float(delta_matrix_pcb_normalized[i][j]), 2))
        S_partial_data_for_boxplot.append(
            round(float(Data_matrix_sentec[i][j]), 2))
        S_partial_data_for_boxplot_delta.append(
            round(float(delta_matrix_sentec[i][j]), 2))
        S_partial_data_for_boxplot_normalized.append(
            round(float(delta_matrix_sentec_normalized[i][j]), 2))

    data_for_boxplot.append(partial_data_for_boxplot)
    data_for_boxplot_delta.append(partial_data_for_boxplot_delta)
    data_for_boxplot_normalized.append(partial_data_for_boxplot_normalized)
    # print(partial_data_for_boxplot_delta)
    partial_data_for_boxplot = []
    partial_data_for_boxplot_delta = []
    partial_data_for_boxplot_normalized = []

    S_data_for_boxplot.append(S_partial_data_for_boxplot)
    S_data_for_boxplot_delta.append(S_partial_data_for_boxplot_delta)
    S_data_for_boxplot_normalized.append(S_partial_data_for_boxplot_normalized)
    # print(S_partial_data_for_boxplot_delta)
    S_partial_data_for_boxplot = []
    S_partial_data_for_boxplot_delta = []
    S_partial_data_for_boxplot_normalized = []


#print("\n\nData for boxplot (dataframe's rows extracted):")
# print(data_for_boxplot)

plt.figure(8)
plt.title("PCB Device Forearm boxplot")
plt.xlabel('Sample number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
plt.boxplot(data_for_boxplot)

plt.figure(9)
plt.title("PCB Device Forearm boxplot - Delta values")
plt.xlabel('Sample number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
# here there isn't the -1 because boxplot index starts from 1 and not 0
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
plt.boxplot(data_for_boxplot_delta, patch_artist=True)

plt.figure(10)
plt.title("Sentec Device Forearm boxplot")
plt.xlabel('Sample number')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
plt.boxplot(S_data_for_boxplot)

plt.figure(11)
plt.title("Sentec Device Forearm boxplot - Delta values")
plt.xlabel('Sample number')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')
# here there isn't the -1 because boxplot index starts from 1 and not 0
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
plt.boxplot(S_data_for_boxplot_delta, patch_artist=True)

plt.figure(12)
plt.title("PCB Device Forearm boxplot normalized")
plt.xlabel('Sample number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
# here there isn't the -1 because boxplot index starts from 1 and not 0
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
plt.boxplot(data_for_boxplot_normalized, patch_artist=True)

plt.figure(13)
plt.title("Sentec Device Forearm boxplot normalized")
plt.xlabel('Sample number')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')
# here there isn't the -1 because boxplot index starts from 1 and not 0
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
plt.boxplot(S_data_for_boxplot_normalized, patch_artist=True)

# Aggregated plot
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.boxplot(data_for_boxplot_delta, patch_artist=True, boxprops=dict(facecolor='royalblue', color='black'),
            medianprops=dict(color='orange'),)
ax2.boxplot(S_data_for_boxplot_delta, patch_artist=True, boxprops=dict(facecolor='forestgreen', color='black'),
            medianprops=dict(color='orange'))
plt.title("PCB Device and Sentec Forearm boxplot comparison - Delta values")
ax2.set_ylabel('Sentec Delta [mmHg]', color='tab:green')
ax1.set_ylabel('PCB Device Delta [ppm]', color='tab:blue')
ax1.grid(axis='y')
# ax2.grid(axis='y')
# here there isn't the -1 because boxplot index starts from 1 and not 0
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.xlabel('Sample number')
#plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
#plt.boxplot(data_for_boxplot_delta, patch_artist=True)
#plt.boxplot(S_data_for_boxplot_delta, patch_artist=True)


'''
---------------------------------------------------------------------------------
INTERPOLATION - RAW VALUES

In the following section an exponential fitting is performed on PCB device
data.

Representative data are from subject SO3, 9-02-2022.

The plots to be drawn are 3:
    - Stimolus
    - PCB device response and fitting
    - Sentec device response

PARAMETERS: (in the interpolation section)
    - @param <delay>: time after the sensors delay in which the curve should
             be fitted.
    - @param <gap>: baseline (in the case of raw values) or deviation from the 
             baseline (in the case of delta values).

---------------------------------------------------------------------------------
'''

# PLOT OF THE STIMULUS
exp_x1 = []
exp_y1 = []
exp_x2 = []
exp_y2 = []
x_axis = []
x_axis2 = []
interval_duration = 12
tau = 2.5
amplitude = 5.0
plateau = 0

# To detach from y axis
for i in range(0, 10, 1):
    exp_y1.append(40)

# Physiological delay
for i in range(0, 5, 1):
    exp_y1.append(40)

count = 0
# Stimulus Exponential function construction
for i in np.arange(0, interval_duration, 1):
    x_axis.append(i)
    partial_exp_y = float(amplitude*(1 - np.exp(-i/tau))) + 40
    # print(i)
    # print(partial_exp_y)
    if(partial_exp_y < 40 + amplitude-0.5):
        exp_y1.append(partial_exp_y)
        count = count + 1
        plateau = partial_exp_y - 40

for i in range(0, int(interval_duration-count-1), 1):
    exp_y1.append(plateau + 40)

for i in np.arange(0, interval_duration, 1):
    x_axis2.append(i)
    partial_exp_y = float(plateau*(np.exp(-i/(tau/2)))) + 40
    if(partial_exp_y > 40 + 0.01):
        exp_y2.append(partial_exp_y)

for i in range(0, int(interval_duration*(1/1)-len(exp_y2)), 1):
    exp_y2.append(40)

# print(exp_y2)
len_x_axis = len(x_axis)

for i in range(0, len(x_axis2), 1):
    x_axis.append(x_axis2[i]+len_x_axis)


for i in range(0, len(exp_y2), 1):
    exp_y1.append(exp_y2[i])

print(exp_y1)

# INTERPOLATION FUNCTION
# Exctraction of x and y representative data
# array that contains all the data from the beginning of the rebreathing maneuver
y_repr_pcb = []
y_repr_sentec = []

# to check if the selected column is correct
y_repr_sentec = Data_matrix_sentec[subject_id]
y_repr_pcb = Data_matrix[subject_id]

print("\nData from SO3:")
print(y_repr_pcb)
y_repr_pcb = []
y_repr_sentec = []

# filling with post start rebreathing data
for i in range(int(index_start_rebreathing-offset), len(Data_matrix[subject_id]), 1):
    y_repr_pcb.append(float(Data_matrix[subject_id][i]))
    y_repr_sentec.append(float(Data_matrix_sentec[subject_id][i]))

print("\nData from SO3 after start rebreathing:")
print(y_repr_pcb)

print("\nLength of the array from START REBREATHING:")
print(len(y_repr_pcb))  # 79

# CREATION OF THE ARRAYS FOR OVERLAPPED PLOTS
arr_y_pcb = []  # array that contains all the data from the start of the rebreathing maneuver and the beginning 10 samples of the first value are added
arr_y_sentec = []

for i in range(0, 10, 1):
    arr_y_pcb.append(y_repr_pcb[0])
    arr_y_sentec.append(y_repr_sentec[0])

for i in range(0, len(y_repr_pcb), 1):
    arr_y_pcb.append(y_repr_pcb[i])
    arr_y_sentec.append(y_repr_sentec[i])

print("\nArray PCB for piled plots:")
print(arr_y_pcb)
print("\nArray Sentec for piled plots:")
print(arr_y_sentec)

print("\nLength of the Sentec and PCB arrays (overall):")
print(len(arr_y_pcb))  # 89
print("\nLength of the stimulus array (overall):")
print(len(exp_y1))

# Adding values to the stimulus plot to match the array dimensions
for i in range(0, len(arr_y_pcb) - len(exp_y1), 1):
    exp_y1.append(40)

x_axis_stimulus = range(0, len(arr_y_pcb), 1)  # for the stimulus plot
x_repr_pcb = range(0, len(arr_y_pcb), 1)
x_repr_sentec = range(0, len(arr_y_pcb), 1)

# We need to place the start of the rebreathing procedure 10 samples after. Then the physiological delay 5 samples after
fig15 = plt.figure(15)
plt.title("Provided stimulus")
plt.plot(x_axis_stimulus, exp_y1, 'k', color="black", linewidth='1',)
plt.axvline(x=10, color='forestgreen')
plt.axvline(x=15, color='blue')
plt.xlabel('Sample Number')
plt.ylabel('PCO2 [mmHg]')
plt.grid(axis='y')
plt.legend(['Stimulus', 'Start rebreathing',
           'Physiological delay'], loc="upper right")

fig16 = plt.figure(16)
plt.title("PCB post start rebreathing data")
plt.plot(x_repr_pcb, arr_y_pcb, 'k', color="black", linewidth='1')
plt.axvline(x=10, color='forestgreen')
plt.axvline(x=15, color='blue')
plt.axvline(x=18, color='red')
plt.xlabel('Sample Number')
plt.ylabel('PtCO2 [ppm]')
plt.grid(axis='y')
plt.legend(['Raw PCB device data', 'Start rebreathing', 'Physiological delay',
           'Sensors delay'], loc="lower right")

fig17 = plt.figure(17)
plt.title("Sentec post start rebreathing data")
plt.plot(x_repr_sentec, arr_y_sentec, 'k',
         color="black", linewidth='1',)
plt.axvline(x=10, color='forestgreen')
plt.axvline(x=15, color='blue')
plt.axvline(x=18, color='red')
plt.xlabel('Sample Number')
plt.ylabel('PtCO2 [mmHg]')
plt.grid(axis='y')
plt.legend(['Filtered Sentec device data', 'Start rebreathing', 'Physiological delay',
           'Sensors delay'], loc="upper right")


#####################################################################
#                    Interpolation with curve_fit                   #
#####################################################################

#################### PARAMETERS ####################
delay = 22
gap = 825
####################################################

x_repr_pcb = []
y_repr_pcb = []

for i in range(delay, len(arr_y_pcb), 1):
    x_repr_pcb.append(i)
    y_repr_pcb.append(arr_y_pcb[i])

print(y_repr_pcb)
print(x_repr_pcb)

p0 = (300, 2)  # start with values near those we expect
params, cv = scipy.optimize.curve_fit(
    lambda t, B, tau: B*(1 - np.exp((-(t-delay)/tau))) + gap,  x_repr_pcb,  y_repr_pcb)

print("\nFitting parameters: ")
print(params)
print("\nCV fitting: ")
print(cv)

B = params[0]
tau = params[1]

x_fitted = []
y_fitted = []
x_repr_pcb = range(0, len(arr_y_pcb), 1)
for i in range(delay, len(arr_y_pcb), 1):
    x_fitted.append(i)
    y_fitted.append(B*(1 - np.exp((-1*((x_fitted[i-delay])-delay)/tau))) + gap)

# Goodness of the fitting
r2_score_value = metrics.r2_score(y_repr_pcb, y_fitted)
print("\n\n=================================================================")
print("Fitting Goodness R2: ")
print(r2_score_value)
print("=================================================================")

fig18 = plt.figure(18)
plt.title("PCB post start rebreathing data and fitting")
plt.plot(x_repr_pcb, arr_y_pcb, 'k', color="black", linewidth='1')
plt.plot(x_fitted, y_fitted, 'm', label='Fitted curve')
plt.axvline(x=10, color='forestgreen')
plt.axvline(x=15, color='blue')
plt.axvline(x=18, color='red')
plt.xlabel('Sample Number')
plt.ylabel('PtCO2 [ppm]')
plt.grid(axis='y')
plt.legend(['Raw PCB device data', 'Fitted curve', 'Start rebreathing', 'Physiological delay',
           'Sensors delay'], loc="lower right")


'''
---------------------------------------------------------------------------------
INTERPOLATION - DELTA VALUES

In the following section an exponential fitting is performed on PCB device
data.

Representative data are from subject SO3, 9-02-2022.

The plots to be drawn are 3:
    - Stimolus
    - PCB device response and fitting
    - Sentec device response
---------------------------------------------------------------------------------
'''
# Exctraction of x and y DELTA representative data
y_repr_pcb_delta = []
y_repr_sentec_delta = []
y_repr_sentec_delta = delta_matrix_sentec[subject_id]
y_repr_pcb_delta = delta_matrix_pcb[subject_id]

print("\nDelta Data from SO3:")
print(y_repr_pcb_delta)
y_repr_pcb_delta = []
y_repr_sentec_delta = []
for i in range(int(index_start_rebreathing-offset), len(delta_matrix_pcb[subject_id]), 1):
    y_repr_pcb_delta.append(float(delta_matrix_pcb[subject_id][i]))
    y_repr_sentec_delta.append(float(delta_matrix_sentec[subject_id][i]))

print("\nDelta Data from SO3 after start rebreathing:")
print(y_repr_pcb_delta)

print("\nDelta Length of the array from START REBREATHING:")
print(len(y_repr_pcb_delta))  # 79

# CREATION OF THE ARRAYS FOR OVERLAPPED PLOTS
arr_y_pcb_delta = []
arr_y_sentec_delta = []

for i in range(0, 10, 1):
    arr_y_pcb_delta.append(y_repr_pcb_delta[0])
    arr_y_sentec_delta.append(y_repr_sentec_delta[0])

for i in range(0, len(y_repr_pcb_delta), 1):
    arr_y_pcb_delta.append(y_repr_pcb_delta[i])
    arr_y_sentec_delta.append(y_repr_sentec_delta[i])

print("\nArray delta PCB for piled plots:")
print(arr_y_pcb_delta)
print("\nArray delta Sentec for piled plots:")
print(arr_y_sentec_delta)

print("\nLength of the delta Sentec and delta PCB arrays (overall):")
print(len(arr_y_pcb_delta))
print("\nLength of the stimulus array (overall):")
print(len(exp_y1))

x_repr_pcb_delta = range(0, len(arr_y_pcb_delta), 1)
x_repr_sentec_delta = range(0, len(arr_y_pcb_delta), 1)

fig19 = plt.figure(19)
plt.title("Delta PCB post start rebreathing data")
plt.plot(x_repr_pcb_delta, arr_y_pcb_delta, 'k', color="black", linewidth='1')
plt.axvline(x=10, color='forestgreen')
plt.axvline(x=15, color='blue')
plt.axvline(x=18, color='red')
plt.xlabel('Sample Number')
plt.ylabel('PtCO2 [ppm]')
plt.grid(axis='y')
plt.legend(['Raw PCB device data - DELTA', 'Start rebreathing', 'Physiological delay',
           'Sensors delay'], loc="lower right")

fig20 = plt.figure(20)
plt.title("Delta Sentec post start rebreathing data")
plt.plot(x_repr_sentec_delta, arr_y_sentec_delta, 'k',
         color="black", linewidth='1',)
plt.axvline(x=10, color='forestgreen')
plt.axvline(x=15, color='blue')
plt.axvline(x=18, color='red')
plt.xlabel('Sample Number')
plt.ylabel('PtCO2 [mmHg]')
plt.grid(axis='y')
plt.legend(['Filtered Sentec device data - DELTA', 'Start rebreathing', 'Physiological delay',
           'Sensors delay'], loc="upper right")

#####################################################################
#                    Interpolation with curve_fit                   #
#####################################################################

#################### PARAMETERS ####################
delay = 22
gap = -38
####################################################

x_repr_pcb_delta = []
y_repr_pcb_delta = []

for i in range(delay, len(arr_y_pcb_delta), 1):
    x_repr_pcb_delta.append(i)
    y_repr_pcb_delta.append(arr_y_pcb_delta[i])

print(y_repr_pcb_delta)
print(x_repr_pcb_delta)

p0 = (300, 2)  # start with values near those we expect
params_delta, cv_delta = scipy.optimize.curve_fit(
    lambda t, B, tau: B*(1 - np.exp((-(t-delay)/tau))) + gap,  x_repr_pcb_delta,  y_repr_pcb_delta)

print("\nFitting parameters DELTA: ")
print(params_delta)
print("\nCV fitting DELTA: ")
print(cv)

B = params_delta[0]
tau = params_delta[1]

x_fitted_delta = []
y_fitted_delta = []
x_repr_pcb_delta = range(0, len(arr_y_pcb_delta), 1)
for i in range(delay, len(arr_y_pcb_delta), 1):
    x_fitted_delta.append(i)
    y_fitted_delta.append(
        B*(1 - np.exp((-1*((x_fitted_delta[i-delay])-delay)/tau))) + gap)

# Goodness of the fitting
r2_score_value_delta = metrics.r2_score(y_repr_pcb_delta, y_fitted_delta)
print("\n\n=================================================================")
print("Fitting Goodness R2 - delta: ")
print(r2_score_value_delta)
print("=================================================================")

fig21 = plt.figure(21)
plt.title("Delta PCB post start rebreathing data and fitting")
plt.plot(x_repr_pcb_delta, arr_y_pcb_delta, 'k', color="black", linewidth='1')
plt.plot(x_fitted_delta, y_fitted_delta, 'm', label='Fitted curve')
plt.axvline(x=10, color='forestgreen')
plt.axvline(x=15, color='blue')
plt.axvline(x=18, color='red')
plt.xlabel('Sample Number')
plt.ylabel('PtCO2 [ppm]')
plt.grid(axis='y')
plt.legend(['Raw PCB device data - DELTA', 'Fitted curve', 'Start rebreathing', 'Physiological delay',
           'Sensors delay'], loc="lower right")

plt.show()
