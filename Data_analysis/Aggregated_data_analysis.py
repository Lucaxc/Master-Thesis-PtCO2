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
df = pd.read_csv('Sentec_dataframe_lobo_aggregato.csv', sep=";")
print("\n\nDataframe with START:")
print(df)

# Removing START row
index_start_rebreathing = df[df["28_01"] == "START"].index.values
print(index_start_rebreathing)
df = df.drop(index_start_rebreathing, axis=0)
df = df.reset_index(drop=TRUE)
print("\n\nDataframe without START row:")
print(df)

# Removing Rows with NaN
df = df.dropna()
print("\n\nDataframe without NaN rows:")
print(df)
# print(type(df["28_01"][0]))

# Summing values row by row
Data_matrix = []
rows = len(df.index)
columns = len(df.columns)
# print(columns)

for i in range(0, len(df.columns), 1):
    append = df.iloc[:, i].values
    Data_matrix.append(append)

# print(Data_matrix[10][21])
# print("\n\nMatrix:")
# print(Data_matrix)

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
plt.title("Mean values")
plt.plot(x1, y1, '.-', color="red", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')

# Standard deviation computation
arr_row = []
std_arr = []
count = 0
for j in range(0, rows, 1):
    for i in range(0, columns, 1):
        arr_row.append(round(float(Data_matrix[i][j]), 2))
    std_arr.append(round(stat.stdev(arr_row), 2))
    count += 1
    #print("Standard Deviation of sample %s is % s " % (count, std_arr[j]))
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
plt.title("Mean values and Standard deviation")
plt.errorbar(x1, y1, std_arr, color='blue',
             fmt='-*', ecolor="red", elinewidth=0.5)
plt.xlabel('Time stamp')
plt.ylabel('Measured value [mmHg]')
plt.grid(axis='y')
plt.text(0, 55.5, "Average Standard Deviation = %s" % average_std, fontsize=7)

plt.show()
