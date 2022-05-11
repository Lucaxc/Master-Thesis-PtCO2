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
from pickle import TRUE
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Importing dataframe
print("-------------------------------------------------------------------------")
print("------------------------------- New run ---------------------------------")
print("-------------------------------------------------------------------------")
df = pd.read_csv('Sentec_polso_aggregated.csv', sep=";")
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
print(type(df["28_01"][0]))

# Summing values row by row
Data_matrix = []
rows = len(df.index)
columns = len(df.columns)
# print(columns)

for i in range(0, len(df.columns), 1):
    append = df.iloc[:, i].values
    Data_matrix.append(append)

# print(Data_matrix[10][21])
print("\n\nMatrix:")
print(Data_matrix)

arr_sum = []
partial_total = 0

for j in range(0, rows, 1):
    for i in range(0, columns, 1):
        partial_total += round(float(Data_matrix[i][j]), 2)
    arr_sum.append(partial_total/columns)
    partial_total = 0

print("\n\nArray of the sum:")
print(arr_sum)

print("\n\nNumber of array elements:")
print(len(arr_sum))

figure1 = plt.figure(1)
y1 = arr_sum
x1 = range(0, len(arr_sum), 1)
plt.title("Mean values")
plt.plot(x1, y1, '.-', color="red", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [mmHg]')
plt.show()
