'''
------------------------------------------------------------------------------------------
                        PYTHON SCRIPT FOR STATISTICAL ANALYSIS

Author: Luca Colombo, MSc Student in Biomedical Engineering - Technologies for Electronics

\brief:
This script is used to perform statistical analysis on data retrieved from script named
<Aggreagated_data_analysis>.

\Parameters:
    @param <filename.csv>: at the beginning of the script change the file name to
            associate the running of the script with the desired CSV file. It includes
            processing both for PCB device data and Sentec device data


In the following section dataframe is imported and statistical analysis are performed:

- Normality test to check the normality of the data acquired for each subject
- Kruskal Wallis repetability test for non parametric distributions (at a specific time
instant comparing all subjects lobe data and forearm data)
- Wilcoxon matched pairs test for non parametric distribution (between lobe and forearm
data from the same subject)

ANOVA, PAIRED T-TEST, INDEPENDENT T-TEST CANNOT BE DONE BECAUSE DISTRIBUTION IS NOT NORMAL 
(see p-value resulting from the normality test)
------------------------------------------------------------------------------------------
'''

from distutils.command import check
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
df_pcb = pd.read_csv('CO2_df_10_median_merged.csv', sep=";")
df_sentec = pd.read_csv('Sentec_df_10_median_merged.csv', sep=";")
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

'''
---------------------------------------------------------------------------------
NORMALITY INSPECTION

Data are analized to investigate if they are normalli distributed.
    
    scipy.stats.normaltest(a, axis=0, nan_policy='propagate')
    Test whether a sample differs from a normal distribution.   

    This function tests the null hypothesis that a sample comes from a normal 
    distribution. It is based on D’Agostino and Pearson’s [1], [2] test that 
    combines skew and kurtosis to produce an omnibus test of normality.

    If p-value > 0.05, data come from a normal distribution
---------------------------------------------------------------------------------
'''
pvalues_normality = []
for i in range(0, len(delta_matrix_pcb), 1):
    pvalues_normality.append(stats.normaltest(delta_matrix_pcb[i]))

print("\n\nP-values for normality: ")
normality_pvalue_pcb = pd.DataFrame(pvalues_normality)
print(normality_pvalue_pcb)
normality_pvalue_pcb.to_csv('Normality.csv', sep=';', index=False)

# Since pvalue for normality D'Agostino test is << 0.05, data are not normally distributed


'''
---------------------------------------------------------------------------------
KRUSKAL WALLIS

Considering a specific time instant, LOBE data from all the subjects are used to 
create the first array, then FOREARM data from all the subjects are used to 
create the second array.

In the end, Kruskal Wallis test is performed on the two arrays, iteratively 
for all the time instants of the experimental trial.

---------------------------------------------------------------------------------
'''
complete_row_pcb = []
complete_row_sentec = []
lobe_row_pcb = []
lobe_row_sentec = []
forearm_row_pcb = []
forearm_row_sentec = []

KruWal_pcb = []
KruWal_sentec = []
result_KW_pcb = 0
result_KW_sentec = 0

check_baseline_count = 0

# Extraction of complete rows and columns associated to lobe and forearm data
for j in range(0, rows, 1):

    lobe_row_pcb = []
    lobe_row_sentec = []
    forearm_row_pcb = []
    forearm_row_sentec = []
    check_baseline_count = 0

    for i in range(0, columns, 1):
        complete_row_pcb.append(delta_matrix_pcb[i][j])
        complete_row_sentec.append(delta_matrix_sentec[i][j])
        if(i % 2 == 0 or i == 0):
            lobe_row_pcb.append(delta_matrix_pcb[i][j])
            lobe_row_sentec.append(delta_matrix_sentec[i][j])
        else:
            forearm_row_pcb.append(delta_matrix_pcb[i][j])
            forearm_row_sentec.append(delta_matrix_sentec[i][j])

    # Check if the baseline array [0, 0, ..., 0] is met. In this case no KW test is performed
    for k in range(0, len(lobe_row_pcb), 1):
        if(lobe_row_pcb[k] == 0):
            check_baseline_count += 1

    if(check_baseline_count < len(lobe_row_pcb)):
        result_KW_pcb = stats.kruskal(lobe_row_pcb, forearm_row_pcb)
        result_KW_sentec = stats.kruskal(lobe_row_sentec, forearm_row_sentec)
        KruWal_pcb.append(result_KW_pcb)
        KruWal_sentec.append(result_KW_sentec)

#print("\n\nKruskal Wallis results DEVICE:")
# print(KruWal_pcb)
print("\n\nLength Kruskal Wallis results DEVICE:")
print(len(KruWal_pcb))
#print("\n\nKruskal Wallis results SENTEC:")
# print(KruWal_sentec)

KW_df_pcb = pd.DataFrame(KruWal_pcb)
KW_df_sentec = pd.DataFrame(KruWal_sentec)
print(KW_df_pcb)

plt.figure(0)
y1 = KW_df_pcb['pvalue']
x1 = range(0, len(KruWal_pcb), 1)
plt.title("Kruskal Wallis P-value - PCB device")
plt.plot(x1, y1, 'x-', color="orange", linewidth='2',)
plt.xlabel('Sample Number')
plt.ylabel('pvalue')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['pvalues', 'Start rebreathing',
           'End rebreathing'], loc="upper left")

plt.figure(1)
y1 = KW_df_sentec['pvalue']
x1 = range(0, len(KruWal_pcb), 1)
plt.title("Kruskal Wallis P-value - Sentec device")
plt.plot(x1, y1, 'x-', color="blueviolet", linewidth='2',)
plt.xlabel('Sample Number')
plt.ylabel('pvalue')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['pvalues', 'Start rebreathing',
           'End rebreathing'], loc="upper left")

plt.figure(2)
y1 = KW_df_pcb['pvalue']
y2 = KW_df_sentec['pvalue']
x1 = range(0, len(KruWal_pcb), 1)
plt.title("Kruskal Wallis P-value - Comparison")
plt.plot(x1, y1, 'x-', color="orange", linewidth='2',)
plt.plot(x1, y2, 'o-', color="blueviolet", linewidth='2',)
plt.xlabel('Sample Number')
plt.ylabel('pvalue')
plt.grid(axis='y')
plt.axvline(x=index_start_rebreathing-offset-1, color='gold')
plt.axvline(x=index_start_rebreathing-offset+3, color='coral')
plt.legend(['PCB device', 'Sentec device',
           'Start rebreathing', 'End rebreathing'], loc="upper left")


'''
---------------------------------------------------------------------------------
WILCOXON MATCHED PAIRS TEST (a.k.a paird t-test for non normal distribution)

Considering a specific subject, LOBE data are compared with FOREARM for the
same subject.

In the end, Wilcoxon test is performed on the two arrays, iteratively 
for all the time instants of the experimental trial.

scipy.stats.wilcoxon(x, y=None, zero_method='wilcox', correction=False, 
                        alternative='two-sided', mode='auto', *, axis=0,
                        nan_policy='propagate')

The Wilcoxon signed-rank test tests the null hypothesis that two related paired 
samples come from the same distribution. In particular, it tests whether the 
distribution of the differences x - y is symmetric about zero. It is a 
non-parametric version of the paired T-test.

Hypotesis:
    - H0: there is not a difference between the two groups
    - H1: there is a difference between the two groups

If Pvalue < 0.05, H0 has to be rejected and H1 accepted.
---------------------------------------------------------------------------------
'''
lobe_pcb = []
lobe_sentec = []
forearm_pcb = []
forearm_sentec = []

Wilcx_pcb = []
Wilcx_sentec = []
result_Wcx_pcb = 0
result_Wcx_sentec = 0

check_baseline_count = 0

# Extraction of complete rows and columns associated to lobe and forearm data
for j in range(0, columns, 2):
    lobe_pcb = []
    lobe_sentec = []
    forearm_pcb = []
    forearm_sentec = []

    check_baseline_count = 0

    for i in range(0, rows, 1):
        if(i != index_start_rebreathing-offset-1):  # baseline not considered
            lobe_pcb.append(delta_matrix_pcb[j][i])
            forearm_pcb.append(delta_matrix_pcb[j+1][i])
            lobe_sentec.append(delta_matrix_sentec[j][i])
            forearm_sentec.append(delta_matrix_sentec[j+1][i])

    print(lobe_pcb)
    print(forearm_pcb)
    result_Wcx_pcb = stats.wilcoxon(lobe_pcb, forearm_pcb)
    result_Wcx_sentec = stats.wilcoxon(lobe_sentec, forearm_sentec)
    Wilcx_pcb.append(result_Wcx_pcb)
    Wilcx_sentec.append(result_Wcx_sentec)

#print("\n\nKruskal Wallis results DEVICE:")
# print(KruWal_pcb)
print("\n\nLength Wilcoxon results DEVICE:")
print(len(Wilcx_pcb))

# Always greater than 0.05, so the H0 hypothesis has to be accepted
#print("\n\nKruskal Wallis results SENTEC:")
# print(KruWal_sentec)

Wcx_df_pcb = pd.DataFrame(Wilcx_pcb)
Wcx_df_sentec = pd.DataFrame(Wilcx_sentec)
print(Wcx_df_pcb)
Wcx_df_pcb.to_csv("WCX_Device_10.csv", sep=';', index=False)

print("\n\nLength Wilcoxon results SENTEC:")
print(Wcx_df_sentec)
Wcx_df_sentec.to_csv("WCX_sentec_10.csv", sep=';', index=False)


'''
---------------------------------------------------------------------------------
ANOVA

Considering a specific time instant, LOBE data from all the subjects are used to 
create the first array, then FOREARM data from all the subjects are used to 
create the second array.

In the end, Kruskal Wallis test is performed on the two arrays, iteratively 
for all the time instants of the experimental trial.

---------------------------------------------------------------------------------
'''

###


'''
---------------------------------------------------------------------------------
FRIEDMAN

It is the non parametric alternative to the repeated measurements ANOVA.
Considering two specific time instants, LOBE data from all the subjects are used to 
create the first array, then FOREARM data from all the subjects are used to 
create the second array.

In the end, Friedman test is performed on the two arrays, iteratively 
for all the couples of time instants for all the data.

Null Hypothesis (H0): the mean for each time instant is equal.
Alternative Hypothesis (H1): at least one population mean is different from the rest.

If the pvalue < 0.05, we can reject the null Hypothesis (H0).

---------------------------------------------------------------------------------
'''
'''
complete_row_pcb = []
complete_row_sentec = []
lobe_row_pcb = []
lobe_row_sentec = []
forearm_row_pcb = []
forearm_row_sentec = []

Friedman_pcb = []
Friedman_sentec = []
result_FR_pcb = 0
result_FR_sentec = 0

check_baseline_count = 0

# Extraction of complete rows and columns associated to lobe and forearm data
for j in range(0, rows, 1):

    lobe_row_pcb = []
    lobe_row_sentec = []
    forearm_row_pcb = []
    forearm_row_sentec = []
    check_baseline_count = 0

    for i in range(0, columns, 1):
        complete_row_pcb.append(delta_matrix_pcb[i][j])
        complete_row_sentec.append(delta_matrix_sentec[i][j])
        if(i % 2 == 0 or i == 0):
            lobe_row_pcb.append(delta_matrix_pcb[i][j])
            lobe_row_sentec.append(delta_matrix_sentec[i][j])
        else:
            forearm_row_pcb.append(delta_matrix_pcb[i][j])
            forearm_row_sentec.append(delta_matrix_sentec[i][j])

    # Check if the baseline array [0, 0, ..., 0] is met. In this case no KW test is performed
    for i in range(0, columns, 1):
        complete_row_pcb.append(delta_matrix_pcb[i][j+1])
        complete_row_sentec.append(delta_matrix_sentec[i][j+1])
        if(i % 2 == 0 or i == 0):
            lobe_row_pcb.append(delta_matrix_pcb[i][j+1])
            lobe_row_sentec.append(delta_matrix_sentec[i][j+1])
        else:
            forearm_row_pcb.append(delta_matrix_pcb[i][j+1])
            forearm_row_sentec.append(delta_matrix_sentec[i][j+1])

#print("\n\nKruskal Wallis results DEVICE:")
# print(KruWal_pcb)
print("\n\nLength Friedman results DEVICE:")
print(len(Friedman_pcb))

FR_df_pcb = pd.DataFrame(Friedman_pcb)
FR_df_sentec = pd.DataFrame(Friedman_sentec)
print(FR_df_pcb)
'''

plt.show()
