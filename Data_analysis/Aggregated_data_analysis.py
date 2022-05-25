'''
------------------------------------------------------------------------------------------
                        PYTHON SCRIPT FOR DATAFRAME ANALYSIS

Author: Luca Colombo, MSc Student in Biomedical Engineering - Technologies for Electronics

This script is used to perform statistical analysis on data retrieved from  script named
<Dataframe_Analysis>.

\Parameters:
    @param <filename.csv>: at the beginning of the script change the file name to
            associate the running of the script with the desired CSV file.
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
df = pd.read_csv('CO2_dataframe_polso.csv', sep=";")
df_sentec = pd.read_csv('Sentec_dataframe_polso.csv', sep=";")
print("\n\nDataframe PCB with START:")
print(df)

# Rebreathing index identification
index_start_rebreathing = df[df["28_01P"] == "START"].index.values
print("\nIndex start rebreathing: ")
print(index_start_rebreathing)

# Baseline array extraction
baseline_arr_PCB = []
baseline_arr_sentec = []
for i in range(0, len(df.columns), 1):
    baseline_arr_PCB.append(
        round(float(df.iloc[index_start_rebreathing-1, i].values), 2))
    baseline_arr_sentec.append(
        round(float(df_sentec.iloc[index_start_rebreathing-1, i].values), 2))

print("\n\nBaseline array PCB: ")
print(baseline_arr_PCB)
print("\n\nBaseline array Sentec: ")
print(baseline_arr_sentec)

# START row removal
df = df.drop(index_start_rebreathing, axis=0)
df = df.reset_index()
df_sentec = df_sentec.drop(index_start_rebreathing, axis=0)
df_sentec = df_sentec.reset_index()
print("\n\nDataframe PCB without START row:")
print(df)

# Removing Rows with NaN
df = df.dropna()
df_sentec = df_sentec.dropna()
offset = df.iloc[0, 0]
offset = int(offset)

print("\n\nOffset is: %s" % offset)
df.pop('index')
df_sentec.pop('index')
df = df.reset_index(drop=TRUE)
df_sentec = df_sentec.reset_index(drop=TRUE)
print("\n\nDataframe PCB without NaN rows:")
print(df)
# print(type(df["28_01"][0]))

'''
---------------------------------------------------------------------------------
DATA MERGE

In the following section dataframes are imported and prepared for data analysis.
---------------------------------------------------------------------------------
'''
# Summing values row by row
Data_matrix = []
Data_matrix_sentec = []
Data_matrix_no_offset = []
Data_matrix_no_offset_sentec = []
rows = len(df.index)
columns = len(df.columns)
# print(columns)

for i in range(0, len(df.columns), 1):
    append = df.iloc[:, i].values
    Data_matrix.append(append)
    Data_matrix_sentec.append(df_sentec.iloc[:, i].values)
print("\n\nData matrix PCB: ")
print(Data_matrix)

# Generation of arrays corresponding to columns, subtraction of the baseline and deltas computation
Data_matrix_no_offset = Data_matrix
Data_matrix_no_offset_sentec = Data_matrix_sentec
print(Data_matrix_no_offset[0])
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
    # print(support_PCB)
    # print(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]))
    delta_PCB.append(
        round(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]), 2))
    support_sentec = Data_matrix_no_offset_sentec[i].astype(float)
    # baseline subrtaction from array
    support_sentec = support_sentec - baseline_arr_sentec[i]
    print(support_sentec)
    print(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]))
    delta_sentec.append(
        round(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]), 2))

print("\n\n------------------------------------------------------------------------------------")
print("PCB Delta values from baseline: ")
print(delta_PCB)
print("\nSentec Delta values from baseline: ")
print(delta_sentec)
print("------------------------------------------------------------------------------------")

# Generation of a unique array for aggregated analysis
arr_sum = []
partial_total = 0

for j in range(0, rows, 1):
    for i in range(0, columns, 1):
        partial_total += round(float(Data_matrix[i][j]), 2)
    # print(Data_matrix[i][j])
    arr_sum.append(partial_total/columns)
    partial_total = 0

print("\n\nArray of the sum:")
print(arr_sum)

print("\n\nNumber of array elements:")
print(len(arr_sum))

# Plot with mean values (no standard deviation)
plt.figure(1)
y1 = arr_sum
x1 = range(0, len(arr_sum), 1)
plt.title("MEAN VALUES - PCB Device Lobe data")
plt.plot(x1, y1, '.-', color="red", linewidth='1',)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset)
plt.legend(['Average values', 'Start rebreathing'], loc="upper left")

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
plt.figure(2)
plt.title("Mean values and Standard deviation - PCB Device Lobe data")
plt.errorbar(x1, y1, std_arr, color='blue',
             fmt='-*', ecolor="red", elinewidth=0.5)
plt.xlabel('Sample Number')
plt.ylabel('Measured value [ppm]')
plt.grid(axis='y')
plt.text(30, 1010, "Average Standard Deviation = %s ppm" %
         average_std, fontsize=7)
plt.axvline(x=index_start_rebreathing-offset)
plt.legend(['Start rebreathing', 'Average values and std'], loc="upper left")

# Plot with couples of delta values
plt.figure(3)
plt.title("Sentec - PCB device correlation analysis")
plt.xlabel('Sentec measured CO2 [mmHg]')
plt.ylabel('PCB device measured [ppm]')
plt.plot(delta_sentec, delta_PCB, 'o', color="blue")

plt.show()
