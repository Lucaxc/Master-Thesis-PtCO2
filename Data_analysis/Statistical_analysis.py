'''
------------------------------------------------------------------------------------------
                        PYTHON SCRIPT FOR STATISTICAL ANALYSIS

Author: Luca Colombo, MSc Student in Biomedical Engineering - Technologies for Electronics

This script is used to perform statistical analysis on data retrieved from  script named
<Aggreagated_data_analysis>.

\Parameters:
    @param <filename.csv>: at the beginning of the script change the file name to
            associate the running of the script with the desired CSV file. It includes
            processing both for PCB device data and Sentec device data


In the following section statistical analysis are performed on the dataframe.

- Kruskal Wallis repetability test for non parametric distributions
- Anova test for detectability/sensitivity
------------------------------------------------------------------------------------------
'''

from functools import partial
from pickle import FALSE, TRUE
from turtle import color
from unittest.mock import patch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
from sklearn import preprocessing
from scipy import stats

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
df_pcb = pd.read_csv('CO2_df_30_median_merged.csv', sep=";")
df_sentec = pd.read_csv('Sentec_df_30_median_merged.csv', sep=";")
print("\n\nDataframe PCB with START:")
print(df_pcb)

# Rebreathing index identification
index_start_rebreathing = df_pcb[df_pcb["28_01L"] == "START"].index.values
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
#print("\n\nData matrix PCB: ")
# print(Data_matrix)
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


#################################################################################
#                               KRUSKAL WALLIS                                  #
#################################################################################
