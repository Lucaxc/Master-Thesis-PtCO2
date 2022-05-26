'''
------------------------------------------------------------------------------------------
                        PYTHON SCRIPT FOR DATAFRAME ANALYSIS

Author: Luca Colombo, MSc Student in Biomedical Engineering - Technologies for Electronics

This script is used to perform statistical analysis on data retrieved from  script named
<Dataframe_Analysis>.

\Parameters:
    @param <filename.csv>: at the beginning of the script change the file name to
            associate the running of the script with the desired CSV file. It includes
            processing both for PCB device data and Sentec device data
------------------------------------------------------------------------------------------
'''

from functools import partial
from pickle import FALSE, TRUE
from turtle import color
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat

# Importing dataframe
print("-------------------------------------------------------------------------")
print("------------------------------- New run ---------------------------------")
print("-------------------------------------------------------------------------")


'''
---------------------------------------------------------------------------------
DATAFRAME IMPORT

In the following section dataframes are imported and prepared for data analysis.
---------------------------------------------------------------------------------
'''
df_pcb = pd.read_csv('CO2_df_30_median_p.csv', sep=";")
df_sentec = pd.read_csv('Sentec_df_30_median_p.csv', sep=";")
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
print("\n\nDataframe PCB without START row:")
print(df_pcb)

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
print("\n\nDataframe PCB without NaN rows:")
print(df_pcb)
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
delta_matrix_sentec = []
print("\n\n")
print(Data_matrix_no_offset[0])
print("\n\nColumns of data matrix: ")
print(len(Data_matrix_no_offset))  # numbers of columns
delta_PCB = []
delta_sentec = []
support_PCB = []
support_sentec = []
for i in range(0, len(Data_matrix_no_offset), 1):
    # support.append(Data_matrix_no_offset[i].astype(float))

    # conversion of data_matrix column into array of float
    support_PCB = Data_matrix_no_offset[i].astype(float)

    # baseline subrtaction from array
    support_PCB = support_PCB - baseline_arr_PCB[i]
    delta_matrix_pcb.append(support_PCB)
    # print(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]))
    delta_PCB.append(
        round(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]), 2))
    support_sentec = Data_matrix_no_offset_sentec[i].astype(float)

    # baseline subrtaction from array
    support_sentec = support_sentec - baseline_arr_sentec[i]
    delta_matrix_sentec.append(support_sentec)
    # print(support_sentec)
    # print(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]))
    delta_sentec.append(
        round(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]), 2))

print("\n\n------------------------------------------------------------------------------------")
print("\n\nMatrix of delta PCB:")
print(delta_matrix_pcb)
print("\n\nMatrix of delta Sentec:")
print(delta_matrix_sentec)
print("\n\n------------------------------------------------------------------------------------")
print("PCB Delta values from baseline: ")
print(delta_PCB)
print("\nSentec Delta values from baseline: ")
print(delta_sentec)
print("------------------------------------------------------------------------------------")

# Generation of a unique array for aggregated analysis
arr_sum_device = []
arr_sum_sentec = []
arr_sum_device_delta = []
arr_sum_sentec_delta = []
partial_total_device = 0
partial_total_sentec = 0
partial_total_device_delta = 0
partial_total_sentec_delta = 0

for j in range(0, rows, 1):
    for i in range(0, columns, 1):
        partial_total_device += round(float(Data_matrix[i][j]), 2)
        partial_total_sentec += round(float(Data_matrix_sentec[i][j]), 2)
        partial_total_device_delta += round(float(delta_matrix_pcb[i][j]), 2)
        partial_total_sentec_delta += round(
            float(delta_matrix_sentec[i][j]), 2)

    # print(Data_matrix[i][j])
    arr_sum_device.append(round(partial_total_device/columns, 2))
    arr_sum_sentec.append(round(partial_total_sentec/columns, 2))
    arr_sum_device_delta.append(round(partial_total_device_delta/columns, 2))
    arr_sum_sentec_delta.append(round(partial_total_sentec_delta/columns, 2))
    partial_total_device = 0
    partial_total_sentec = 0
    partial_total_device_delta = 0
    partial_total_sentec_delta = 0


print("\n\nArray of the sum:")
print(arr_sum_device)
print(arr_sum_sentec)

print("\n\nArray of the delta sum:")
print(arr_sum_device_delta)
print(arr_sum_sentec_delta)

print("\n\nNumber of array elements:")
print(len(arr_sum_device))
print(len(arr_sum_sentec))

print("\n\nNumber of array elements delta:")
print(len(arr_sum_device_delta))
print(len(arr_sum_sentec_delta))

# Plot with mean values (no standard deviation)
plt.figure(0)
y1 = arr_sum_sentec
x1 = range(0, len(arr_sum_sentec), 1)
plt.title("MEDIAN VALUES - Sentec Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1)
plt.legend(['Median values', 'Start rebreathing'], loc="upper left")

plt.figure(1)
y1 = arr_sum_sentec_delta
x1 = range(0, len(arr_sum_sentec_delta), 1)
plt.title("DELTA MEDIAN VALUES - Sentec Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1)
plt.legend(['Median values', 'Start rebreathing'], loc="upper left")

plt.figure(2)
y1 = arr_sum_device_delta
x1 = range(0, len(arr_sum_device_delta), 1)
plt.title("DELTA MEDIAN VALUES - PCB Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1)
plt.legend(['Median values', 'Start rebreathing'], loc="upper left")


plt.figure(3)
y1 = arr_sum_device
x1 = range(0, len(arr_sum_device), 1)
plt.title("MEDIAN VALUES - PCB Device Forearm data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1)
plt.legend(['Median values', 'Start rebreathing'], loc="upper left")

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
plt.figure(4)
plt.title("Mean values and Standard deviation - PCB Device Forearm data")
plt.errorbar(x1, y1, std_arr, color='blue',
             fmt='-*', ecolor="red", elinewidth=0.5)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.text(30, 1010, "Average Standard Deviation = %s ppm" %
         average_std, fontsize=7)
plt.axvline(x=index_start_rebreathing-offset-1)
plt.legend(['Start rebreathing', 'Average values and std'], loc="upper left")

# Plot with couples of delta values - for correlation
plt.figure(5)
plt.title("Sentec - PCB device correlation analysis")
plt.xlabel('Sentec measured CO2 [mmHg]')
plt.ylabel('PCB device measured [ppm]')
plt.plot(delta_sentec, delta_PCB, 'o', color="blue")


'''
---------------------------------------------------------------------------------
BOXPLOT

In the following section boxplots of PCB device data are generated
---------------------------------------------------------------------------------
'''
partial_data_for_boxplot = []
data_for_boxplot = []
for j in range(0, rows, 1):
    for i in range(0, columns, 1):
        partial_data_for_boxplot.append(round(float(Data_matrix[i][j]), 2))
    data_for_boxplot.append(partial_data_for_boxplot)
    print(partial_data_for_boxplot)
    partial_data_for_boxplot = []

print("\n\nData for boxplot (dataframe's rows extracted):")
print(data_for_boxplot)

plt.figure(6)
plt.title("PCB Device Forearm boxplot")
plt.xlabel('Sample number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1)
plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
plt.boxplot(data_for_boxplot)


plt.show()
