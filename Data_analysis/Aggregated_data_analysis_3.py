'''
------------------------------------------------------------------------------------------
                        PYTHON SCRIPT FOR DATAFRAME ANALYSIS

Author: Luca Colombo, MSc Student in Biomedical Engineering - Technologies for Electronics

This script is used to perform statistical analysis on data retrieved from script named
<Dataframe_Analysis>. This script has CPET plots included, script branches for Lobe or
Forearm data and functions for various things (listed at the beginning of the script).

\Parameters:
    @param <filename.csv>: at the beginning of the script change the file name to
            associate the running of the script with the desired CSV file. It includes
            processing both for PCB device data, Sentec device data and CPET data.
    @param <subject_id>: subject that has to be considered in the exponential fitting 
            part of the script.
    @param <flag_lobo>: to differentiate the script if either Lobe data (1) or forearm
            data (0) are considered.
    @param <flag_30seconds>: to differentiate between 30s median computation (1) and 10s
            median computation (0).
------------------------------------------------------------------------------------------
'''

from functools import partial
from pickle import FALSE, NONE, TRUE
from re import sub
from tracemalloc import start
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
from scipy.signal import butter, lfilter, freqz
import statsmodels.api as sm

# Importing dataframe
print("-------------------------------------------------------------------------")
print("------------------------------- New run ---------------------------------")
print("-------------------------------------------------------------------------")

subject_id = 5
flag_lobo = 0  # 0 if forearm
flag_30seconds = 1  # 0 if 10 seconds

'''
---------------------------------------------------------------------------------
DATAFRAME IMPORT

In the following section dataframes are imported and prepared for data analysis.
Dataframes to be considered are separately for Lobe and forearm.
Merge dataset is used for statistical analysis in a related script
---------------------------------------------------------------------------------
'''
df_pcb = pd.read_csv('CO2_df_30_median_P.csv', sep=";")
df_sentec = pd.read_csv('Sentec_df_30_median_P.csv', sep=";")

# Importing CPET CSV; first row has not to be considered as header
df_cpet = pd.read_csv('CPET_P_T.csv', sep=";", header=None)
#print("\n\nDataframe PCB with START:")
# print(df_pcb)


'''
FUNCTIONS
Here there is the list and implementation of functions used throught the script

'''

################ PLOT DATA #################
# \brief: Function that is used to plot data.
# \parameters:
#   @param <figure_id>: figure number to be opened
#   @param <x>: x-axis array
#   @param <y>: y-axis array
#   @param <title>: string containing the plot's title
#   @param <xlabel>: string containing the x-axis label
#   @param <xlabel>: string containing the y-axis label
#   @param <legend>: array of strings containing the legend
#   @param <legend_location>: legend location
#   @param <style>: line style. If put to NONE, by default it will be black and continuous
#   @param <color>: color of the plot
#   @param <linewidth>: thickness of the plot
#   @param <gridx>: array to setup the x-axis grid
#   @param <ygrid>: boolean, TRUE or FALSE
#   @param <start_rebr>: rebreathing starting index
#   @param <end_rebr>: rebreathing ending index
# \return NONE
#############################################


def plot_data(figure_id, x, y, title, xlabel, ylabel, legend, legend_location, style, color, linewidth, gridx, ygrid, start_rebr, end_rebr):
    plt.figure(figure_id)
    y1 = y
    x1 = x
    plt.title(title)
    if(style == NONE):
        plt.plot(x1, y1, color, linewidth=linewidth)
    else:
        plt.plot(x1, y1, style, color=color, linewidth=linewidth)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if(ygrid == TRUE):
        plt.grid(axis='y')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=start_rebr, color='gold')
    plt.axvline(x=end_rebr, color='coral')
    if(gridx != NONE):
        plt.xticks(gridx)

    plt.legend(legend, loc=legend_location)


################ Butterworth Low-Pass #################
# \brief: Function that calls a Butterworth low pass filter.
# \parameters:
#   @param <figure_id>: figure number to be opened
#   @param <x>: x-axis array
#   @param <y>: y-axis array
#   @param <title>: string containing the plot's title
#   @param <xlabel>: string containing the x-axis label
#   @param <xlabel>: string containing the y-axis label
#   @param <legend>: array of strings containing the legend
#   @param <legend_location>: legend location
#   @param <style>: line style. If put to NONE, by default it will be black and continuous
#   @param <color>: color of the plot
#   @param <linewidth>: thickness of the plot
#   @param <gridx>: array to setup the x-axis grid
#   @param <ygrid>: boolean, TRUE or FALSE
#   @param <start_rebr>: rebreathing starting index
#   @param <end_rebr>: rebreathing ending index
# \return butterworth filter
######################################################
def butter_lowpass(cutoff, fs, order=5):
    return butter(order, cutoff, fs=fs, btype='low', analog=False)


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

#################################################################################
#                                       CPET                                    #
#################################################################################


# CPET columns indexes
columns_cpet = []
for i in range(0, len(df_cpet.columns), 1):
    columns_cpet.append(i)

df_cpet.columns = columns_cpet
print("\n\nCPET Dataframe:")
print(df_cpet)

# CPET plots for selected subject (0 is S01)
subject_cpet = df_cpet.iloc[subject_id]

# Dropping NANs
subject_cpet = subject_cpet.dropna()

# Dropping subject label
subject_cpet = subject_cpet.drop(0)
print("\n\nSelected subject's CPET:")
print(subject_cpet)
print(type(subject_cpet))

array_subject_cpet = subject_cpet.values

for i in range(0, len(array_subject_cpet), 1):
    if(array_subject_cpet[i] == 'START'):
        start_cpet = i
    if(array_subject_cpet[i] == 'END'):
        end_cpet = i

print("\n\nIndex start CPET:")
print(start_cpet)
print("\n\nIndex end CPET:")
print(end_cpet)

# +1 because of first row dropping at the beginning
drop_cpet = [start_cpet+1, end_cpet+1]

subject_cpet = subject_cpet.drop(drop_cpet)
array_subject_cpet = subject_cpet.values
array_subject_cpet = array_subject_cpet.astype(float)
print(array_subject_cpet)
breaths = []
for i in range(0, len(array_subject_cpet), 1):
    breaths.append(i)

plot_data(28, breaths, array_subject_cpet, "End-tidal CO2 partial pressure",
          'Breaths count', 'EtCO2 [mmHg]',
          ['CPET', 'Start rebreathing',
           'End rebreathing'], "upper left", NONE, 'k', '1',  NONE, TRUE, start_cpet, end_cpet)

plt.show()

#################################################################################
#                           PCB device and Sentec                               #
#################################################################################

# Rebreathing index identification
if(flag_lobo):
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
        support_PCB_normalized = np.round(support_PCB_normalized, 2)
        delta_matrix_pcb.append(support_PCB)
        delta_matrix_pcb_normalized.append(support_PCB_normalized)
        # print(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]))
        # Array of delta values from start rebreathing to maximum
        delta_PCB.append(
            round(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]), 2))
        support_sentec = Data_matrix_no_offset_sentec[i].astype(float)

        # baseline subrtaction from array
        support_sentec = support_sentec - baseline_arr_sentec[i]
        support_sentec = np.round(support_sentec, 2)
        support_sentec_normalized = (
            support_sentec/baseline_arr_sentec[i]) * 100
        support_sentec_normalized = np.round(support_sentec_normalized, 2)
        delta_matrix_sentec.append(support_sentec)
        delta_matrix_sentec_normalized.append(support_sentec_normalized)
        # print(support_sentec)
        # print(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]))
        delta_sentec.append(
            round(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]), 2))
    '''
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
    '''

    # Filtering (individual selected subject)
    order = 2
    fs = 1.0       # sample rate, Hz
    cutoff = 0.2  # desired cutoff frequency of the filter, Hz
    filtered_co2 = butter_lowpass_filter(
        Data_matrix_no_offset[subject_id].astype(float), cutoff, fs, order)

    filtered_co2_cut = []
    # Elimination of the first bias
    for i in range(5, len(filtered_co2), 1):
        filtered_co2_cut.append(filtered_co2[i])

    y_pcb = Data_matrix_no_offset[subject_id].astype(float)
    x_pcb = range(0, len(Data_matrix_no_offset[subject_id]), 1)
    x_pcb_cut = range(0, len(filtered_co2_cut), 1)
    plt.figure()
    plt.plot(x_pcb, y_pcb, 'k')
    plt.title("Pre-filtering signal")
    plt.grid(axis='y')
    plt.axvline(x=index_start_rebreathing-1-offset, color='gold')
    plt.axvline(x=index_start_rebreathing+3-offset, color='coral')
    plt.figure()
    plt.plot(x_pcb_cut, filtered_co2_cut, 'k')
    plt.title("Filtered signal")
    plt.grid(axis='y')
    plt.axvline(x=index_start_rebreathing-1-offset, color='gold')
    plt.axvline(x=index_start_rebreathing+3-offset, color='coral')

    # Maximal value extraction for each subject
    max_sentec = []
    max_pcb = []
    for i in range(0, len(Data_matrix_no_offset), 1):
        filtered_co2 = butter_lowpass_filter(
            Data_matrix_no_offset[i].astype(float), cutoff, fs, order)

        filtered_co2_cut = []
        # Elimination of the first bias
        for j in range(5, len(filtered_co2), 1):
            filtered_co2_cut.append(filtered_co2[j])

        support_sentec = Data_matrix_no_offset_sentec[i].astype(float)
        max_sentec.append(
            round(max(support_sentec[(int(index_start_rebreathing)-offset):-1]), 2))
        max_pcb.append(
            round(max(filtered_co2_cut[(int(index_start_rebreathing)-offset):-1]), 2))

    print("\n\nArray of max SENTEC")
    print(max_sentec)
    print("\n\nArray of max PCB")
    print(max_pcb)
    print(len(max_sentec))
    print(len(max_pcb))

    # Scatterplot with maximal values
    plt.figure()
    plt.plot(max_sentec, max_pcb, 'o', color='royalblue')
    plt.title("Correlation on maximal values, PCB device and Sentec device")
    plt.grid(axis='both')
    plt.xlabel('Sentec device - [mmHg]')
    plt.ylabel('PCB device - [ppm]')

    # Delta PCB and Sentec and Normalized PCB and Sentec dataframe export
    # print(delta_matrix_pcb)
    delta_matrix_pcb_T = np.transpose(delta_matrix_pcb)
    delta_matrix_pcb_normalized_T = np.transpose(delta_matrix_pcb_normalized)
    delta_matrix_sentec_T = np.transpose(delta_matrix_sentec)
    delta_matrix_sentec_normalized_T = np.transpose(
        delta_matrix_sentec_normalized)
    # print(delta_matrix_pcb_T)
    df_delta_pcb = pd.DataFrame(delta_matrix_pcb_T, columns=['28_01L', '9_02L', '15_02L',	'22_02L', '8_03L',
                                                             '15_03L', '22_03L',	'12_04L', '19_04L', '3_05L', '10_05L', '24_05L',
                                                             '31_05L', '14_06L', '21_06L', '5_07L', '12_07L', '18_07L', '19_07L'
                                                             ])

    df_delta_pcb_normalized = pd.DataFrame(delta_matrix_pcb_normalized_T, columns=['28_01L', '9_02L', '15_02L',	'22_02L', '8_03L',
                                                                                   '15_03L', '22_03L',	'12_04L', '19_04L', '3_05L', '10_05L', '24_05L',
                                                                                   '31_05L', '14_06L', '21_06L', '5_07L', '12_07L', '18_07L', '19_07L'
                                                                                   ])

    df_delta_sentec = pd.DataFrame(delta_matrix_sentec_T, columns=['28_01L', '9_02L', '15_02L',	'22_02L', '8_03L',
                                                                   '15_03L', '22_03L',	'12_04L', '19_04L', '3_05L', '10_05L', '24_05L',
                                                                   '31_05L', '14_06L', '21_06L', '5_07L', '12_07L', '18_07L', '19_07L'
                                                                   ])

    df_delta_sentec_normalized = pd.DataFrame(delta_matrix_sentec_normalized_T, columns=['28_01L', '9_02L', '15_02L',	'22_02L', '8_03L',
                                                                                         '15_03L', '22_03L',	'12_04L', '19_04L', '3_05L', '10_05L', '24_05L',
                                                                                         '31_05L', '14_06L', '21_06L', '5_07L', '12_07L', '18_07L', '19_07L'
                                                                                         ])
    print(df_delta_sentec)
    df_delta_pcb.to_csv('PCB_df_delta.csv', sep=';', index=False)
    df_delta_pcb_normalized.to_csv(
        'PCB_df_normalized.csv', sep=';', index=False)
    df_delta_sentec.to_csv('Sentec_df_delta.csv', sep=';', index=False)
    df_delta_sentec_normalized.to_csv(
        'Sentec_df_normalized.csv', sep=';', index=False)

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
            partial_total_device_delta += round(
                float(delta_matrix_pcb[i][j]), 2)
            partial_total_sentec_delta += round(
                float(delta_matrix_sentec[i][j]), 2)
            partial_total_device_normalized += round(
                float(delta_matrix_pcb_normalized[i][j]), 2)
            partial_total_sentec_normalized += round(
                float(delta_matrix_sentec_normalized[i][j]), 2)

        # print(Data_matrix[i][j])
        arr_sum_device.append(round(partial_total_device/columns, 2))
        arr_sum_sentec.append(round(partial_total_sentec/columns, 2))
        arr_sum_device_delta.append(
            round(partial_total_device_delta/columns, 2))
        arr_sum_sentec_delta.append(
            round(partial_total_sentec_delta/columns, 2))
        arr_sum_device_normalized.append(
            round(partial_total_device_normalized, 2))
        arr_sum_sentec_normalized.append(
            round(partial_total_sentec_normalized, 2))
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

    #################################################################

    #                            30 s                               #

    #################################################################
    if(flag_30seconds):
        # X axis time stamp creation
        x_seconds = []
        time_stamp = 45
        for i in range(0, len(arr_sum_sentec), 1):
            time_stamp += 30
            x_seconds.append(time_stamp)
        time_stamp = 45

        # X axis decimal time stamp creation
        x_seconds_decimal = []
        time_offset_decimal = 1.45
        minutes = 1
        for i in range(0, len(arr_sum_sentec), 1):
            time_offset_decimal += 0.30
            if(time_offset_decimal > 0.60 + minutes):
                minutes += 1
                time_offset_decimal = time_offset_decimal - 0.60 + 1
            if(i == index_start_rebreathing-offset-1):
                index_start_rebreathing_decimal = round(time_offset_decimal, 2)

            if(i == index_start_rebreathing-offset+3):
                index_end_rebreathing_decimal = round(time_offset_decimal, 2)
            x_seconds_decimal.append(round(time_offset_decimal, 2))
        time_offset_decimal = 0.45
        print("\n\nx_seconds_decimal 30s:")
        print(x_seconds_decimal)

        # Time to be displayed on x axis
        gridx = []
        for i in range(0, len(x_seconds_decimal), 1):
            if(i % 2 == 1):
                gridx.append(x_seconds_decimal[i])

        # To detect where to plot the vertical line when using decimal x axis time stamps
        print("\n\nindex_start_rebreathing_decimal and end 30s:")
        print(index_start_rebreathing_decimal)
        print(index_end_rebreathing_decimal)

    #################################################################

    #                            10 s                               #

    #################################################################
    if(flag_30seconds == 0):
        # X axis time stamp creation
        x_seconds = []
        time_stamp = 70
        for i in range(0, len(arr_sum_sentec), 1):
            time_stamp += 10
            x_seconds.append(time_stamp)
        time_stamp = 70

        # X axis decimal time stamp creation
        x_seconds_decimal = []
        time_offset_decimal = 1.10
        minutes = 1
        for i in range(0, len(arr_sum_sentec), 1):
            time_offset_decimal += 0.10
            if(time_offset_decimal > 0.60 + minutes):
                minutes += 1
                time_offset_decimal = time_offset_decimal - 0.60 + 1
            if(i == index_start_rebreathing-offset-1):
                index_start_rebreathing_decimal = round(time_offset_decimal, 2)

            if(i == index_start_rebreathing-offset+11):
                index_end_rebreathing_decimal = round(time_offset_decimal, 2)
            x_seconds_decimal.append(round(time_offset_decimal, 2))
        time_offset_decimal = 0.45
        print("\n\nx_seconds_decimal 10s:")
        print(x_seconds_decimal)

        # Time to be displayed on x axis
        gridx = []
        j = 0
        for i in range(0, len(x_seconds_decimal), 1):
            j += 1
            if(i == 1.5 or j == 6):
                j = 0
                gridx.append(x_seconds_decimal[i])

        # To detect where to plot the vertical line when using decimal x axis time stamps
        print("\n\nindex_start_rebreathing_decimal and end 10s:")
        print(index_start_rebreathing_decimal)
        print(index_end_rebreathing_decimal)

    '''
    ----------------------------------------------------------------------------------------
    BLAND ALTMAN PLOT

    In the following lines the BLAND-ALTMAN test is performed considering the subject_id
    selected at the beginning of the script
    ----------------------------------------------------------------------------------------
    '''
    y_pcb = Data_matrix[subject_id].astype(float)
    y_sentec = Data_matrix_sentec[subject_id].astype(float)
    x_pcb = range(0, len(Data_matrix[subject_id]), 1)
    x_sentec = range(0, len(Data_matrix_sentec[subject_id]), 1)
    #y_pcb = delta_matrix_pcb[subject_id].astype(float)
    #y_sentec = delta_matrix_sentec[subject_id].astype(float)
    #x_pcb = range(0, len(delta_matrix_pcb[subject_id]), 1)
    #x_sentec = range(0, len(delta_matrix_sentec[subject_id]), 1)
    plot_data(31, x_pcb, y_pcb, "Subject Data plot - PCB",
              'Time [m.s]', 'Measured value [mmHg]',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  NONE, TRUE,
              index_start_rebreathing-offset-1, index_start_rebreathing-offset+4-1)
    plot_data(32, x_sentec, y_sentec, "Subject Data plot - Sentec",
              'Time [m.s]', 'Measured value [mmHg]',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  NONE, TRUE,
              index_start_rebreathing-offset-1, index_start_rebreathing-offset+4-1)
    plt.show()

    df_blandalt = pd.DataFrame({'PCB': delta_matrix_pcb_normalized[subject_id],
                                'Sentec': delta_matrix_sentec_normalized[subject_id]})

    PCB_ass = [5.3, 5.3, 5, 6, 5.3, 4.3, 2, 6.3,
               2.3, 6, 6, 4.3, 5.3, 10, 5, 3.3, 6.3]
    PCB_picc = [5, 6.3, 5.3, 3.3, 14, 11, 6,
                6.3, 5.3, 6.3, 6, 9, 7, 8, 11, 7, 10]
    PCB_sat = [8, 9, 11, 4, 14, 14, 8, 12,
               5.3, 6.3, 6.3, 14, 7, 14, 14, 14, 10]
    sentec_ass = [1.3, 1.3, 5.3, 6, 4.3, 2.3, 8.3,
                  5.3, 7, 4, 10, 6, 10, 1.3, 4.3, 10, 6.3]
    sentec_picc = [3.3, 3.3, 4.3, 3.3, 3.3,
                   3.3, 3.3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    sentec_sat = [10.3, 14, 9.3, 6.3, 14, 10,
                  9, 6, 14, 6, 9, 8, 8.3, 9, 14, 7.3, 14]

    df_blandalt_ass = pd.DataFrame({'PCB': PCB_ass,
                                    'Sentec': sentec_ass})

    df_blandalt_picc = pd.DataFrame({'PCB': PCB_picc,
                                     'Sentec': sentec_picc})

    df_blandalt_sat = pd.DataFrame({'PCB': PCB_sat,
                                    'Sentec': sentec_sat})

    f, ax = plt.subplots(1, figsize=(8, 5))
    sm.graphics.mean_diff_plot(df_blandalt.PCB, df_blandalt.Sentec, ax=ax)

    f, ax = plt.subplots(1, figsize=(8, 5))
    ax.set_title("BLDALT - Baseline")
    sm.graphics.mean_diff_plot(
        df_blandalt_ass.PCB, df_blandalt_ass.Sentec, ax=ax)

    f, ax = plt.subplots(1, figsize=(8, 5))
    ax.set_title("BLDALT - Peak")
    sm.graphics.mean_diff_plot(
        df_blandalt_picc.PCB, df_blandalt_picc.Sentec, ax=ax)

    f, ax = plt.subplots(1, figsize=(8, 5))
    ax.set_title("BLDALT - Saturation")
    sm.graphics.mean_diff_plot(
        df_blandalt_sat.PCB, df_blandalt_sat.Sentec, ax=ax)

    plt.figure(32)
    plt.title("Sentec - PCB device correlation analysis")
    plt.xlabel('Sentec time [min]')
    plt.ylabel('PCB time [min]')
    plt.plot(sentec_ass, PCB_ass, 'o', color="blue")
    plt.plot(sentec_picc, PCB_picc, 'o', color="red")
    plt.plot(sentec_sat, PCB_sat, 'o', color="green")
    plt.legend(["Baseline", "Peak", "Saturation"], loc='best')
    plt.grid(axis='both')
    plt.show()

    # Plot with median values (no standard deviation)
    y1 = arr_sum_sentec
    x1 = range(0, len(arr_sum_sentec), 1)
    plot_data(0, x_seconds_decimal, y1, "MEDIAN VALUES - Sentec Device Lobe data",
              'Time [m.s]', 'Measured value [mmHg]',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  gridx, TRUE,
              index_start_rebreathing_decimal, index_end_rebreathing_decimal)

    y1 = arr_sum_sentec_delta
    x1 = range(0, len(arr_sum_sentec_delta), 1)
    plot_data(1, x_seconds_decimal, y1, "DELTA MEDIAN VALUES - Sentec Device Lobe data",
              'Time [m.s]', 'Measured value [mmHg]',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  gridx, TRUE,
              index_start_rebreathing_decimal, index_end_rebreathing_decimal)

    y1 = arr_sum_device_delta
    x1 = range(0, len(arr_sum_device_delta), 1)
    plot_data(2, x_seconds_decimal, y1, "DELTA MEDIAN VALUES - PCB Device Lobe data",
              'Time [m.s]', 'Measured value [ppm]',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  gridx, TRUE,
              index_start_rebreathing_decimal, index_end_rebreathing_decimal)

    y1 = arr_sum_device
    x1 = range(0, len(arr_sum_device), 1)
    plot_data(3, x_seconds_decimal, y1, "MEDIAN VALUES - PCB Device Lobe data",
              'Time [m.s]', 'Measured value [ppm]',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  gridx, TRUE,
              index_start_rebreathing_decimal, index_end_rebreathing_decimal)

    y1 = arr_sum_device_normalized
    x1 = range(0, len(arr_sum_device_normalized), 1)
    plot_data(4, x_seconds_decimal, y1, "NORMALIZED VALUES - PCB Device Lobe data",
              'Time [m.s]', 'Normalized value',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  gridx, TRUE,
              index_start_rebreathing_decimal, index_end_rebreathing_decimal)

    y1 = arr_sum_sentec_normalized
    x1 = range(0, len(arr_sum_sentec_normalized), 1)
    plot_data(5, x_seconds_decimal, y1, "NORMALIZED VALUES - Sentec Device Lobe data",
              'Time [m.s]', 'Normalized value',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  gridx, TRUE,
              index_start_rebreathing_decimal, index_end_rebreathing_decimal)

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
    plt.title("Mean values and Standard deviation - PCB Device Lobe data")
    # plt.errorbar(x_seconds, y1, std_arr, color='blue',
    #             fmt='-*', ecolor="red", elinewidth=0.5)
    plt.errorbar(x_seconds_decimal, y1, std_arr, color='blue',
                 fmt='-*', ecolor="red", elinewidth=0.5)
    plt.xlabel('Time [m.s]')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    plt.text(30, 1010, "Average Standard Deviation = %s ppm" %
             average_std, fontsize=7)
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Start rebreathing', 'End rebreathing',
                'Average values and std'], loc="upper left")

    # Plot with couples of delta values - for correlation
    plt.figure(7)
    plt.title("Sentec - PCB device correlation analysis")
    plt.xlabel('Sentec measured CO2 [mmHg]')
    plt.ylabel('PCB device measured [ppm]')
    plt.plot(delta_sentec, delta_PCB, 'o', color="blue")

    plt.figure(22)
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    y1 = arr_sum_device_delta
    y2 = arr_sum_sentec_delta
    plt.title("Delta VALUES - Sentec and PCB Device Lobe data")
    #plt.plot(x_seconds, y1, '.-', color="red", linewidth='1',)
    ax1.plot(x_seconds_decimal, y1, '.-', color="royalblue", linewidth='1',)
    ax2.plot(x_seconds_decimal, y2, '.-', color="forestgreen", linewidth='1',)
    ax2.set_ylabel('Sentec Delta [mmHg]', color='tab:green')
    ax1.set_ylabel('PCB Device Delta [ppm]', color='tab:blue')
    ax1.grid(axis='y')
    plt.xlabel('Time [m.s]')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Median values', 'Start rebreathing',
                'End rebreathing'], loc="upper left")

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
        S_data_for_boxplot_normalized.append(
            S_partial_data_for_boxplot_normalized)
        # print(S_partial_data_for_boxplot_delta)
        S_partial_data_for_boxplot = []
        S_partial_data_for_boxplot_delta = []
        S_partial_data_for_boxplot_normalized = []

    #print("\n\nData for boxplot (dataframe's rows extracted):")
    # print(data_for_boxplot)

    plt.figure(8)
    plt.title("PCB Device Lobe boxplot")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(data_for_boxplot)

    plt.figure(9)
    plt.title("PCB Device Lobe boxplot - Delta values")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(data_for_boxplot_delta, patch_artist=True)

    plt.figure(10)
    plt.title("Sentec Device Lobe boxplot")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [mmHg]')
    plt.grid(axis='y')
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(S_data_for_boxplot)

    plt.figure(11)
    plt.title("Sentec Device Lobe boxplot - Delta values")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [mmHg]')
    plt.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(S_data_for_boxplot_delta, patch_artist=True)

    plt.figure(12)
    plt.title("PCB Device Lobe boxplot normalized")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(data_for_boxplot_normalized, patch_artist=True)

    plt.figure(13)
    plt.title("Sentec Device Lobe boxplot normalized")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [mmHg]')
    plt.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(S_data_for_boxplot_normalized, patch_artist=True)

    # Aggregated plot
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.boxplot(data_for_boxplot_delta, patch_artist=True, boxprops=dict(facecolor='royalblue', color='black'),
                medianprops=dict(color='orange'),)
    ax2.boxplot(S_data_for_boxplot_delta, patch_artist=True, boxprops=dict(facecolor='forestgreen', color='black'),
                medianprops=dict(color='orange'))
    plt.title("PCB Device and Sentec Lobe boxplot comparison - Delta values")
    ax2.set_ylabel('Sentec Delta [mmHg]', color='tab:green')
    ax1.set_ylabel('PCB Device Delta [ppm]', color='tab:blue')
    ax1.grid(axis='y')
    # ax2.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.xlabel('Sample number')
    #plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    #plt.boxplot(data_for_boxplot_delta, patch_artist=True)
    #plt.boxplot(S_data_for_boxplot_delta, patch_artist=True)

    # plt.show()
    '''
    ---------------------------------------------------------------------------------
    INTERPOLATION - RAW VALUES - SAMPLES

    In the following section an exponential fitting is performed on PCB device
    data. IT IS NECESSARY TO USE DATA WITH 10s RESOLUTION

    Representative data are from subject SO3, 9-02-2022.

    The plots to be drawn are 3:
        - Stimulus
        - PCB device response and fitting
        - Sentec device response

    PARAMETERS: (in the interpolation section)
        - @param <delay_pcb>: time after the sensors delay in which the curve should
                be fitted.
        - @param <delay_sentec>: delay from start rebreathing where the Sentec signal
                starts to rise.
        - @param <gap>: baseline (in the case of raw values) or deviation from the 
                baseline (in the case of delta values).
        - @param <end_fitting>: sample number where to stop the exponential fitting.
    ---------------------------------------------------------------------------------
    '''
    if(flag_30seconds == 0):
        subject_id = 18

        delay_pcb = 19
        delay_sentec = 18
        delay_phys = 14

        gap = 1480
        gap_delta = -25
        end_fitting = 88

        derivative_evaluation = 0

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

        # print(exp_y1)

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

        #print("\nLength of the Sentec and PCB arrays (overall):")
        # print(len(arr_y_pcb))  # 89
        #print("\nLength of the stimulus array (overall):")
        # print(len(exp_y1))

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
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_pcb, color='red')
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
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_sentec, color='red')
        plt.xlabel('Sample Number')
        plt.ylabel('PtCO2 [mmHg]')
        plt.grid(axis='y')
        plt.legend(['Filtered Sentec device data', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="upper right")

        #####################################################################
        #                    Interpolation with curve_fit                   #
        #####################################################################

        #################### PARAMETERS ####################
        #gap = 700
        #end_fitting = 80
        ####################################################

        x_repr_pcb = []
        y_repr_pcb = []

        # Check if end_fitting index is smaller than overall array length
        if(end_fitting > len(arr_y_pcb)):
            end_fitting = len(arr_y_pcb)

        for i in range(delay_pcb, end_fitting, 1):
            x_repr_pcb.append(i)
            y_repr_pcb.append(arr_y_pcb[i])

        # print(y_repr_pcb)
        # print(x_repr_pcb)

        p0 = (300, 2)  # start with values near those we expect
        params, cv = scipy.optimize.curve_fit(
            lambda t, B, tau: B*(1 - np.exp((-(t-delay_pcb)/tau))) + gap,  x_repr_pcb,  y_repr_pcb)

        print("\nFitting parameters (raw): ")
        print(params)
        print("\nCV fitting (raw): ")
        print(cv)

        B = params[0]
        tau = params[1]

        x_fitted = []
        y_fitted = []

        x_repr_pcb = []
        for i in range(0, len(arr_y_pcb), 1):
            x_repr_pcb.append(i)

        for i in range(delay_pcb, end_fitting, 1):
            x_fitted.append(i)
            y_fitted.append(
                B*(1 - np.exp((-1*((x_fitted[i-delay_pcb])-delay_pcb)/tau))) + gap)

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
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_pcb, color='red')
        plt.xlabel('Sample Number')
        plt.ylabel('PtCO2 [ppm]')
        plt.grid(axis='y')
        plt.legend(['Raw PCB device data', 'Fitted curve', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="lower right")

        '''
        ---------------------------------------------------------------------------------
        INTERPOLATION - DELTA VALUES - SAMPLES

        In the following section an exponential fitting is performed on PCB device
        data.

        Representative data are from subject SO3, 9-02-2022.

        The plots to be drawn are 3:
            - Stimulus
            - PCB device response and fitting
            - Sentec device response
        ---------------------------------------------------------------------------------
        '''

        # Exctraction of x and y DELTA representative data
        y_repr_pcb_delta = []
        y_repr_sentec_delta = []
        y_repr_sentec_delta = delta_matrix_sentec[subject_id]
        y_repr_pcb_delta = delta_matrix_pcb[subject_id]

        #print("\nDelta Data from SO3:")
        # print(y_repr_pcb_delta)
        y_repr_pcb_delta = []
        y_repr_sentec_delta = []
        for i in range(int(index_start_rebreathing-offset), len(delta_matrix_pcb[subject_id]), 1):
            y_repr_pcb_delta.append(float(delta_matrix_pcb[subject_id][i]))
            y_repr_sentec_delta.append(
                float(delta_matrix_sentec[subject_id][i]))

        #print("\nDelta Data from SO3 after start rebreathing:")
        # print(y_repr_pcb_delta)

        #print("\nDelta Length of the array from START REBREATHING:")
        # print(len(y_repr_pcb_delta))  # 79

        # CREATION OF THE ARRAYS FOR OVERLAPPED PLOTS
        arr_y_pcb_delta = []
        arr_y_sentec_delta = []

        for i in range(0, 10, 1):
            arr_y_pcb_delta.append(y_repr_pcb_delta[0])
            arr_y_sentec_delta.append(y_repr_sentec_delta[0])

        for i in range(0, len(y_repr_pcb_delta), 1):
            arr_y_pcb_delta.append(y_repr_pcb_delta[i])
            arr_y_sentec_delta.append(y_repr_sentec_delta[i])

        #print("\nArray delta PCB for piled plots:")
        # print(arr_y_pcb_delta)
        #print("\nArray delta Sentec for piled plots:")
        # print(arr_y_sentec_delta)

        #print("\nLength of the delta Sentec and delta PCB arrays (overall):")
        # print(len(arr_y_pcb_delta))
        #print("\nLength of the stimulus array (overall):")
        # print(len(exp_y1))

        x_repr_pcb_delta = range(0, len(arr_y_pcb_delta), 1)
        x_repr_sentec_delta = range(0, len(arr_y_pcb_delta), 1)

        fig19 = plt.figure(19)
        plt.title("Delta PCB post start rebreathing data")
        plt.plot(x_repr_pcb_delta, arr_y_pcb_delta,
                 'k', color="black", linewidth='1')
        plt.axvline(x=10, color='forestgreen')
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_pcb, color='red')
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
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_sentec, color='red')
        plt.xlabel('Sample Number')
        plt.ylabel('PtCO2 [mmHg]')
        plt.grid(axis='y')
        plt.legend(['Filtered Sentec device data - DELTA', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="upper right")

        #####################################################################
        #                    Interpolation with curve_fit                   #
        #####################################################################

        #################### PARAMETERS ####################
        #gap_delta = -20
        ####################################################

        x_repr_pcb_delta = []
        y_repr_pcb_delta = []

        for i in range(delay_pcb, end_fitting, 1):
            x_repr_pcb_delta.append(i)
            y_repr_pcb_delta.append(arr_y_pcb_delta[i])

        # print(y_repr_pcb_delta)
        # print(x_repr_pcb_delta)

        p0 = (300, 2)  # start with values near those we expect
        params_delta, cv_delta = scipy.optimize.curve_fit(
            lambda t, B, tau: B*(1 - np.exp((-(t-delay_pcb)/tau))) + gap_delta,  x_repr_pcb_delta,  y_repr_pcb_delta)

        print("\nFitting parameters DELTA: ")
        print(params_delta)
        print("\nCV fitting DELTA: ")
        print(cv)

        B = params_delta[0]
        tau = params_delta[1]

        x_fitted_delta = []
        y_fitted_delta = []
        x_repr_pcb_delta = range(0, len(arr_y_pcb), 1)

        for i in range(delay_pcb, end_fitting, 1):
            x_fitted_delta.append(i)
            y_fitted_delta.append(
                B*(1 - np.exp((-1*((x_fitted_delta[i-delay_pcb])-delay_pcb)/tau))) + gap_delta)

        # Goodness of the fitting
        r2_score_value_delta = metrics.r2_score(
            y_repr_pcb_delta, y_fitted_delta)
        print("\n\n=================================================================")
        print("Fitting Goodness R2 - delta: ")
        print(r2_score_value_delta)
        print("=================================================================")

        fig21 = plt.figure(21)
        plt.title("Delta PCB post start rebreathing data and fitting")
        plt.plot(x_repr_pcb_delta, arr_y_pcb_delta,
                 'k', color="black", linewidth='1')
        plt.plot(x_fitted_delta, y_fitted_delta, 'm', label='Fitted curve')
        plt.axvline(x=10, color='forestgreen')
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_pcb, color='red')
        plt.xlabel('Sample Number')
        plt.ylabel('PtCO2 [ppm]')
        plt.grid(axis='y')
        plt.legend(['Raw PCB device data - DELTA', 'Fitted curve', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="lower right")

        '''
        ---------------------------------------------------------------------------------
        INTERPOLATION - DELTA VALUES - SECONDS

        In the following section an exponential fitting is performed on PCB device
        data.

        Representative data are from subject SO3, 9-02-2022.

        The plots to be drawn are 3:
            - Stimulus
            - PCB device response and fitting
            - Sentec device response
        ---------------------------------------------------------------------------------
        '''
        # Exctraction of x and y DELTA representative data
        y_repr_pcb_delta = []
        y_repr_sentec_delta = []
        y_repr_sentec_delta = delta_matrix_sentec[subject_id]
        y_repr_pcb_delta = delta_matrix_pcb[subject_id]

        #print("\nDelta Data from SO3:")
        # print(y_repr_pcb_delta)
        y_repr_pcb_delta = []
        y_repr_sentec_delta = []
        for i in range(int(index_start_rebreathing-offset), len(delta_matrix_pcb[subject_id]), 1):
            y_repr_pcb_delta.append(float(delta_matrix_pcb[subject_id][i]))
            y_repr_sentec_delta.append(
                float(delta_matrix_sentec[subject_id][i]))

        # CREATION OF THE ARRAYS FOR OVERLAPPED PLOTS
        arr_y_pcb_delta = []
        arr_y_sentec_delta = []

        for i in range(0, 10, 1):
            arr_y_pcb_delta.append(y_repr_pcb_delta[0])
            arr_y_sentec_delta.append(y_repr_sentec_delta[0])

        for i in range(0, len(y_repr_pcb_delta), 1):
            arr_y_pcb_delta.append(y_repr_pcb_delta[i])
            arr_y_sentec_delta.append(y_repr_sentec_delta[i])

        x_repr_pcb_delta = []
        x_repr_sentec_delta = []
        for i in range(0, len(arr_y_pcb_delta), 1):
            x_repr_pcb_delta.append(i*10)
            x_repr_sentec_delta.append(i*10)

        fig19 = plt.figure(25)
        plt.title("Delta PCB post start rebreathing data")
        plt.plot(x_repr_pcb_delta, arr_y_pcb_delta,
                 'k', color="black", linewidth='1')
        plt.axvline(x=10*10, color='forestgreen')
        plt.axvline(x=delay_phys*10, color='blue')
        plt.axvline(x=delay_pcb*10, color='red')
        plt.xlabel('Time [s]')
        plt.ylabel('PtCO2 [ppm]')
        plt.grid(axis='y')
        plt.legend(['Raw PCB device data - DELTA', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="lower right")

        fig20 = plt.figure(26)
        plt.title("Delta Sentec post start rebreathing data")
        plt.plot(x_repr_sentec_delta, arr_y_sentec_delta, 'k',
                 color="black", linewidth='1',)
        plt.axvline(x=10*10, color='forestgreen')
        plt.axvline(x=delay_phys*10, color='blue')
        plt.axvline(x=delay_sentec*10, color='red')
        plt.xlabel('Time [s]')
        plt.ylabel('PtCO2 [mmHg]')
        plt.grid(axis='y')
        plt.legend(['Filtered Sentec device data - DELTA', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="upper right")

        #####################################################################
        #                    Interpolation with curve_fit                   #
        #####################################################################

        x_repr_pcb_delta = []
        y_repr_pcb_delta = []

        for i in range(delay_pcb, end_fitting, 1):
            x_repr_pcb_delta.append(i*10)
            y_repr_pcb_delta.append(arr_y_pcb_delta[i])

        # print(y_repr_pcb_delta)
        # print(x_repr_pcb_delta)

        p0 = (300, 2)  # start with values near those we expect
        params_delta, cv_delta = scipy.optimize.curve_fit(
            lambda t, B, tau: B*(1 - np.exp((-(t-delay_pcb*10)/tau))) + gap_delta,  x_repr_pcb_delta,  y_repr_pcb_delta)

        print("\nFitting parameters DELTA (seconds): ")
        print(params_delta)
        print("\nCV fitting DELTA (seconds): ")
        print(cv)

        B = params_delta[0]
        tau = params_delta[1]

        x_repr_pcb_delta = []
        for i in range(0, len(arr_y_pcb_delta), 1):
            x_repr_pcb_delta.append(i*10)

        x_fitted_delta = []
        y_fitted_delta = []
        for i in range(delay_pcb, end_fitting, 1):
            x_fitted_delta.append(i*10)
            y_fitted_delta.append(
                B*(1 - np.exp((-1*((x_fitted_delta[i-delay_pcb])-delay_pcb*10)/tau))) + gap_delta)

        # Goodness of the fitting
        r2_score_value_delta = metrics.r2_score(
            y_repr_pcb_delta, y_fitted_delta)
        print("\n\n=================================================================")
        print("Fitting Goodness R2 - delta (seconds): ")
        print(r2_score_value_delta)
        print("=================================================================")

        fig21 = plt.figure(27)
        plt.title("Delta PCB post start rebreathing data and fitting")
        plt.plot(x_repr_pcb_delta, arr_y_pcb_delta,
                 'k', color="black", linewidth='1')
        plt.plot(x_fitted_delta, y_fitted_delta, 'm', label='Fitted curve')
        plt.axvline(x=10*10, color='forestgreen')
        plt.axvline(x=delay_phys*10, color='blue')
        plt.axvline(x=delay_pcb*10, color='red')
        plt.xlabel('Time [s]')
        plt.ylabel('PtCO2 [ppm]')
        plt.grid(axis='y')
        plt.legend(['Raw PCB device data - DELTA', 'Fitted curve', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="lower right")

# plt.show()


#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################


if(flag_lobo == 0):
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
        support_PCB_normalized = np.round(support_PCB_normalized, 2)
        delta_matrix_pcb.append(support_PCB)
        delta_matrix_pcb_normalized.append(support_PCB_normalized)
        # print(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]))
        # Array of delta values from start rebreathing to maximum
        delta_PCB.append(
            round(max(support_PCB[(int(index_start_rebreathing)-offset-1):-1]), 2))
        support_sentec = Data_matrix_no_offset_sentec[i].astype(float)

        # baseline subrtaction from array
        support_sentec = support_sentec - baseline_arr_sentec[i]
        support_sentec = np.round(support_sentec, 2)
        support_sentec_normalized = (
            support_sentec/baseline_arr_sentec[i]) * 100
        support_sentec_normalized = np.round(support_sentec_normalized, 2)
        delta_matrix_sentec.append(support_sentec)
        delta_matrix_sentec_normalized.append(support_sentec_normalized)
        # print(support_sentec)
        # print(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]))
        delta_sentec.append(
            round(max(support_sentec[(int(index_start_rebreathing)-offset-1):-1]), 2))
    '''
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
    '''

    # Filtering (individual selected subject)
    order = 2
    fs = 1.0       # sample rate, Hz
    cutoff = 0.2  # desired cutoff frequency of the filter, Hz
    filtered_co2 = butter_lowpass_filter(
        Data_matrix_no_offset[subject_id].astype(float), cutoff, fs, order)

    filtered_co2_cut = []
    # Elimination of the first bias
    for i in range(5, len(filtered_co2), 1):
        filtered_co2_cut.append(filtered_co2[i])

    y_pcb = Data_matrix_no_offset[subject_id].astype(float)
    x_pcb = range(0, len(Data_matrix_no_offset[subject_id]), 1)
    x_pcb_cut = range(0, len(filtered_co2_cut), 1)
    plt.figure()
    plt.plot(x_pcb, y_pcb, 'k')
    plt.title("Pre-filtering signal")
    plt.grid(axis='y')
    plt.axvline(x=index_start_rebreathing-1-offset, color='gold')
    plt.axvline(x=index_start_rebreathing+3-offset, color='coral')
    plt.figure()
    plt.plot(x_pcb_cut, filtered_co2_cut, 'k')
    plt.title("Filtered signal")
    plt.grid(axis='y')
    plt.axvline(x=index_start_rebreathing-1-offset, color='gold')
    plt.axvline(x=index_start_rebreathing+3-offset, color='coral')

    # Maximal value extraction for each subject
    max_sentec = []
    max_pcb = []
    for i in range(0, len(Data_matrix_no_offset), 1):
        filtered_co2 = butter_lowpass_filter(
            Data_matrix_no_offset[i].astype(float), cutoff, fs, order)

        filtered_co2_cut = []
        # Elimination of the first bias
        for j in range(5, len(filtered_co2), 1):
            filtered_co2_cut.append(filtered_co2[j])

        support_sentec = Data_matrix_no_offset_sentec[i].astype(float)
        max_sentec.append(
            round(max(support_sentec[(int(index_start_rebreathing)-offset):-1]), 2))
        max_pcb.append(
            round(max(filtered_co2_cut[(int(index_start_rebreathing)-offset):-1]), 2))

    print("\n\nArray of max SENTEC")
    print(max_sentec)
    print("\n\nArray of max PCB")
    print(max_pcb)
    print(len(max_sentec))
    print(len(max_pcb))

    # Scatterplot with maximal values
    plt.figure()
    plt.plot(max_sentec, max_pcb, 'o', color='royalblue')
    plt.title("Correlation on maximal values, PCB device and Sentec device")
    plt.grid(axis='both')
    plt.xlabel('Sentec device - [mmHg]')
    plt.ylabel('PCB device - [ppm]')

    # Delta PCB and Sentec and Normalized PCB and Sentec dataframe export
    # print(delta_matrix_pcb)
    delta_matrix_pcb_T = np.transpose(delta_matrix_pcb)
    delta_matrix_pcb_normalized_T = np.transpose(delta_matrix_pcb_normalized)
    delta_matrix_sentec_T = np.transpose(delta_matrix_sentec)
    delta_matrix_sentec_normalized_T = np.transpose(
        delta_matrix_sentec_normalized)
    # print(delta_matrix_pcb_T)
    df_delta_pcb = pd.DataFrame(delta_matrix_pcb_T, columns=['28_01P', '9_02P', '15_02P',	'22_02P', '8_03P',
                                                             '15_03P', '22_03P',	'12_04P', '19_04P', '3_05P', '10_05P', '24_05P',
                                                             '31_05P', '14_06P', '21_06P', '5_07P', '12_07P', '18_07P', '19_07P'
                                                             ])

    df_delta_pcb_normalized = pd.DataFrame(delta_matrix_pcb_normalized_T, columns=['28_01P', '9_02P', '15_02P',	'22_02P', '8_03P',
                                                                                   '15_03P', '22_03P',	'12_04P', '19_04P', '3_05P', '10_05P', '24_05P',
                                                                                   '31_05P', '14_06P', '21_06P', '5_07P', '12_07P', '18_07P', '19_07P'
                                                                                   ])

    df_delta_sentec = pd.DataFrame(delta_matrix_sentec_T, columns=['28_01P', '9_02P', '15_02P',	'22_02P', '8_03P',
                                                                   '15_03P', '22_03P',	'12_04P', '19_04P', '3_05P', '10_05P', '24_05P',
                                                                   '31_05P', '14_06P', '21_06P', '5_07P', '12_07P', '18_07P', '19_07P'
                                                                   ])

    df_delta_sentec_normalized = pd.DataFrame(delta_matrix_sentec_normalized_T, columns=['28_01P', '9_02P', '15_02P',	'22_02P', '8_03P',
                                                                                         '15_03P', '22_03P',	'12_04P', '19_04P', '3_05P', '10_05P', '24_05P',
                                                                                         '31_05P', '14_06P', '21_06P', '5_07P', '12_07P', '18_07P', '19_07P'
                                                                                         ])
    df_delta_pcb.to_csv('PCB_df_delta.csv', sep=';', index=False)
    df_delta_pcb_normalized.to_csv(
        'PCB_df_normalized.csv', sep=';', index=False)
    df_delta_sentec.to_csv('Sentec_df_delta.csv', sep=';', index=False)
    df_delta_sentec_normalized.to_csv(
        'Sentec_df_normalized.csv', sep=';', index=False)
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
            partial_total_device_delta += round(
                float(delta_matrix_pcb[i][j]), 2)
            partial_total_sentec_delta += round(
                float(delta_matrix_sentec[i][j]), 2)
            partial_total_device_normalized += round(
                float(delta_matrix_pcb_normalized[i][j]), 2)
            partial_total_sentec_normalized += round(
                float(delta_matrix_sentec_normalized[i][j]), 2)

        # print(Data_matrix[i][j])
        arr_sum_device.append(round(partial_total_device/columns, 2))
        arr_sum_sentec.append(round(partial_total_sentec/columns, 2))
        arr_sum_device_delta.append(
            round(partial_total_device_delta/columns, 2))
        arr_sum_sentec_delta.append(
            round(partial_total_sentec_delta/columns, 2))
        arr_sum_device_normalized.append(
            round(partial_total_device_normalized, 2))
        arr_sum_sentec_normalized.append(
            round(partial_total_sentec_normalized, 2))
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

    #################################################################

    #                            30 s                               #

    #################################################################
    if(flag_30seconds):
        # X axis time stamp creation
        x_seconds = []
        time_stamp = 45
        for i in range(0, len(arr_sum_sentec), 1):
            time_stamp += 30
            x_seconds.append(time_stamp)
        time_stamp = 45

        # X axis decimal time stamp creation
        x_seconds_decimal = []
        time_offset_decimal = 1.45
        minutes = 1
        for i in range(0, len(arr_sum_sentec), 1):
            time_offset_decimal += 0.30
            if(time_offset_decimal > 0.60 + minutes):
                minutes += 1
                time_offset_decimal = time_offset_decimal - 0.60 + 1
            if(i == index_start_rebreathing-offset-1):
                index_start_rebreathing_decimal = round(time_offset_decimal, 2)

            if(i == index_start_rebreathing-offset+3):
                index_end_rebreathing_decimal = round(time_offset_decimal, 2)
            x_seconds_decimal.append(round(time_offset_decimal, 2))
        time_offset_decimal = 0.45
        print("\n\nx_seconds_decimal 30s:")
        print(x_seconds_decimal)

        # Time to be displayed on x axis
        gridx = []
        for i in range(0, len(x_seconds_decimal), 1):
            if(i % 2 == 1):
                gridx.append(x_seconds_decimal[i])

        # To detect where to plot the vertical line when using decimal x axis time stamps
        print("\n\nindex_start_rebreathing_decimal and end 30s:")
        print(index_start_rebreathing_decimal)
        print(index_end_rebreathing_decimal)

    #################################################################

    #                            10 s                               #

    #################################################################
    if(flag_30seconds == 0):
        # X axis time stamp creation
        x_seconds = []
        time_stamp = 70
        for i in range(0, len(arr_sum_sentec), 1):
            time_stamp += 10
            x_seconds.append(time_stamp)
        time_stamp = 70

        # X axis decimal time stamp creation
        x_seconds_decimal = []
        time_offset_decimal = 1.10
        minutes = 1
        for i in range(0, len(arr_sum_sentec), 1):
            time_offset_decimal += 0.10
            if(time_offset_decimal > 0.60 + minutes):
                minutes += 1
                time_offset_decimal = time_offset_decimal - 0.60 + 1
            if(i == index_start_rebreathing-offset-1):
                index_start_rebreathing_decimal = round(time_offset_decimal, 2)

            if(i == index_start_rebreathing-offset+11):
                index_end_rebreathing_decimal = round(time_offset_decimal, 2)
            x_seconds_decimal.append(round(time_offset_decimal, 2))
        time_offset_decimal = 0.45
        print("\n\nx_seconds_decimal 10s:")
        print(x_seconds_decimal)

        # Time to be displayed on x axis
        gridx = []
        j = 0
        for i in range(0, len(x_seconds_decimal), 1):
            j += 1
            if(i == 1.5 or j == 6):
                j = 0
                gridx.append(x_seconds_decimal[i])

        # To detect where to plot the vertical line when using decimal x axis time stamps
        print("\n\nindex_start_rebreathing_decimal and end 10s:")
        print(index_start_rebreathing_decimal)
        print(index_end_rebreathing_decimal)

    '''
    ----------------------------------------------------------------------------------------
    BLAND ALTMAN PLOT

    In the following lines the BLAND-ALTMAN test is performed considering the subject_id
    selected at the beginning of the script
    ----------------------------------------------------------------------------------------
    '''
    y_pcb = Data_matrix[subject_id].astype(float)
    y_sentec = Data_matrix_sentec[subject_id].astype(float)
    x_pcb = range(0, len(Data_matrix[subject_id]), 1)
    x_sentec = range(0, len(Data_matrix_sentec[subject_id]), 1)
    #y_pcb = delta_matrix_pcb[subject_id].astype(float)
    #y_sentec = delta_matrix_sentec[subject_id].astype(float)
    #x_pcb = range(0, len(delta_matrix_pcb[subject_id]), 1)
    #x_sentec = range(0, len(delta_matrix_sentec[subject_id]), 1)
    plot_data(31, x_pcb, y_pcb, "Subject Data plot - PCB",
              'Time [m.s]', 'Measured value [mmHg]',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  NONE, TRUE,
              index_start_rebreathing-offset-1, index_start_rebreathing-offset+4-1)
    plot_data(32, x_sentec, y_sentec, "Subject Data plot - Sentec",
              'Time [m.s]', 'Measured value [mmHg]',
              ['Median values', 'Start rebreathing',
               'End rebreathing'], "upper left", '.-', "red", '1',  NONE, TRUE,
              index_start_rebreathing-offset-1, index_start_rebreathing-offset+4-1)
    plt.show()

    PCB_ass = [4, 8, 5, 4.3, 3, 4, 10, 4.3, 5, 4, 7, 3, 3, 3.3]
    PCB_picc = [4, 4.3, 6.3, 7.3, 4, 10.3, 6.3, 6.3, 6, 5.3, 8, 12, 6.3, 9]
    PCB_sat = [4, 4.3, 6.3, 7.3, 4.3, 14, 6.3, 6.3, 6, 14, 8, 12, 6.3, 11]
    sentec_ass = [10, 3, 7.3, 7, 10, 3, 6, 7.3, 4, 8.3, 10, 10, 5, 10]
    sentec_picc = [4, 4, 4, 4.3, 4.3, 4, 3, 3.3, 3.3, 3.3, 4, 3.3, 3.3, 4]
    sentec_sat = [14, 14, 14, 14, 14, 9.3, 7.3, 7, 6, 14, 8, 9, 14, 8]

    df_blandalt_ass = pd.DataFrame({'PCB': PCB_ass,
                                    'Sentec': sentec_ass})

    df_blandalt_picc = pd.DataFrame({'PCB': PCB_picc,
                                     'Sentec': sentec_picc})

    df_blandalt_sat = pd.DataFrame({'PCB': PCB_sat,
                                    'Sentec': sentec_sat})

    f, ax = plt.subplots(1, figsize=(8, 5))
    ax.set_title("BLDALT - Baseline")
    sm.graphics.mean_diff_plot(
        df_blandalt_ass.PCB, df_blandalt_ass.Sentec, ax=ax)

    f, ax = plt.subplots(1, figsize=(8, 5))
    ax.set_title("BLDALT - Peak")
    sm.graphics.mean_diff_plot(
        df_blandalt_picc.PCB, df_blandalt_picc.Sentec, ax=ax)

    f, ax = plt.subplots(1, figsize=(8, 5))
    ax.set_title("BLDALT - Saturation")
    sm.graphics.mean_diff_plot(
        df_blandalt_sat.PCB, df_blandalt_sat.Sentec, ax=ax)

    plt.figure(32)
    plt.title("Sentec - PCB device correlation analysis")
    plt.xlabel('Sentec time [min]')
    plt.ylabel('PCB time [min]')
    plt.plot(sentec_ass, PCB_ass, 'o', color="blue")
    plt.plot(sentec_picc, PCB_picc, 'o', color="red")
    plt.plot(sentec_sat, PCB_sat, 'o', color="green")
    plt.legend(["Baseline", "Peak", "Saturation"], loc='best')
    plt.grid(axis='both')

    plt.show()

    df_blandalt = pd.DataFrame({'PCB': delta_matrix_pcb_normalized[subject_id],
                                'Sentec': delta_matrix_sentec_normalized[subject_id]})

    f, ax = plt.subplots(1, figsize=(8, 5))
    sm.graphics.mean_diff_plot(df_blandalt.PCB, df_blandalt.Sentec, ax=ax)
    # plt.show()

    # Plot with mean values (no standard deviation)
    plt.figure(0)
    y1 = arr_sum_sentec
    x1 = range(0, len(arr_sum_sentec), 1)
    plt.title("MEDIAN VALUES - Sentec Device Forearm data")
    plt.plot(x_seconds_decimal, y1, '.-', color="red", linewidth='1',)
    plt.xlabel('Time [m.s]')
    plt.ylabel('Measured value [mmHg]')
    plt.grid(axis='y')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Median values', 'Start rebreathing',
                'End rebreathing'], loc="upper left")

    plt.figure(1)
    y1 = arr_sum_sentec_delta
    x1 = range(0, len(arr_sum_sentec_delta), 1)
    plt.title("DELTA MEDIAN VALUES - Sentec Device Forearm data")
    #plt.plot(x_seconds, y1, '.-', color="red", linewidth='1',)
    plt.plot(x_seconds_decimal, y1, '.-', color="red", linewidth='1',)
    plt.xlabel('Time [m.s]')
    plt.ylabel('Measured value [mmHg]')
    plt.grid(axis='y')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Median values', 'Start rebreathing',
                'End rebreathing'], loc="upper left")

    plt.figure(2)
    y1 = arr_sum_device_delta
    x1 = range(0, len(arr_sum_device_delta), 1)
    plt.title("DELTA MEDIAN VALUES - PCB Device Forearm data")
    #plt.plot(x_seconds, y1, '.-', color="red", linewidth='1',)
    plt.plot(x_seconds_decimal, y1, '.-', color="red", linewidth='1',)
    plt.xlabel('Time [m.s]')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Median values', 'Start rebreathing',
                'End rebreathing'], loc="upper left")

    plt.figure(3)
    y1 = arr_sum_device
    x1 = range(0, len(arr_sum_device), 1)
    plt.title("MEDIAN VALUES - PCB Device Forearm data")
    #plt.plot(x_seconds, y1, '.-', color="red", linewidth='1',)
    plt.plot(x_seconds_decimal, y1, '.-', color="red", linewidth='1',)
    plt.xlabel('Time [m.s]')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Median values', 'Start rebreathing',
                'End rebreathing'], loc="upper left")

    plt.figure(4)
    y1 = arr_sum_device_normalized
    x1 = range(0, len(arr_sum_device_normalized), 1)
    plt.title("NORMALIZED VALUES - PCB Device Forearm data")
    #plt.plot(x_seconds, y1, '.-', color="red", linewidth='1',)
    plt.plot(x_seconds_decimal, y1, '.-', color="red", linewidth='1',)
    plt.xlabel('Time [m.s]')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Median values', 'Start rebreathing',
                'End rebreathing'], loc="upper left")

    plt.figure(5)
    y1 = arr_sum_sentec_normalized
    x1 = range(0, len(arr_sum_sentec_normalized), 1)
    plt.title("NORMALIZED VALUES - Sentec Device Forearm data")
    #plt.plot(x_seconds, y1, '.-', color="red", linewidth='1',)
    plt.plot(x_seconds_decimal, y1, '.-', color="red", linewidth='1',)
    plt.xlabel('Time [m.s]')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

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
    # plt.errorbar(x_seconds, y1, std_arr, color='blue',
    #             fmt='-*', ecolor="red", elinewidth=0.5)
    plt.errorbar(x_seconds_decimal, y1, std_arr, color='blue',
                 fmt='-*', ecolor="red", elinewidth=0.5)
    plt.xlabel('Time [m.s]')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    plt.text(30, 1010, "Average Standard Deviation = %s ppm" %
             average_std, fontsize=7)
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Start rebreathing', 'End rebreathing',
                'Average values and std'], loc="upper left")

    # Plot with couples of delta values - for correlation
    plt.figure(7)
    plt.title("Sentec - PCB device correlation analysis")
    plt.xlabel('Sentec measured CO2 [mmHg]')
    plt.ylabel('PCB device measured [ppm]')
    plt.plot(delta_sentec, delta_PCB, 'o', color="blue")

    plt.figure(22)
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    y1 = arr_sum_device_delta
    y2 = arr_sum_sentec_delta
    plt.title("Delta VALUES - Sentec and PCB Device Forearm data")
    #plt.plot(x_seconds, y1, '.-', color="red", linewidth='1',)
    ax1.plot(x_seconds_decimal, y1, '.-', color="royalblue", linewidth='1',)
    ax2.plot(x_seconds_decimal, y2, '.-', color="forestgreen", linewidth='1',)
    ax2.set_ylabel('Sentec Delta [mmHg]', color='tab:green')
    ax1.set_ylabel('PCB Device Delta [ppm]', color='tab:blue')
    ax1.grid(axis='y')
    plt.xlabel('Time [m.s]')
    # ---------If seconds are needed------------
    # plt.axvline(x=(index_start_rebreathing-offset-1)
    #            * 30 + time_stamp + 30, color='gold')
    # plt.axvline(x=(index_start_rebreathing-offset+3)
    #           * 30 + time_stamp + 30, color='coral')
    # ---------If minutes are needed------------
    plt.axvline(x=index_start_rebreathing_decimal, color='gold')
    plt.axvline(x=index_end_rebreathing_decimal, color='coral')
    plt.xticks(gridx)

    plt.legend(['Median values', 'Start rebreathing',
                'End rebreathing'], loc="upper left")

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
        S_data_for_boxplot_normalized.append(
            S_partial_data_for_boxplot_normalized)
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
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(data_for_boxplot)

    plt.figure(9)
    plt.title("PCB Device Forearm boxplot - Delta values")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(data_for_boxplot_delta, patch_artist=True)

    plt.figure(10)
    plt.title("Sentec Device Forearm boxplot")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [mmHg]')
    plt.grid(axis='y')
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(S_data_for_boxplot)

    plt.figure(11)
    plt.title("Sentec Device Forearm boxplot - Delta values")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [mmHg]')
    plt.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(S_data_for_boxplot_delta, patch_artist=True)

    plt.figure(12)
    plt.title("PCB Device Forearm boxplot normalized")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [ppm]')
    plt.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    plt.boxplot(data_for_boxplot_normalized, patch_artist=True)

    plt.figure(13)
    plt.title("Sentec Device Forearm boxplot normalized")
    plt.xlabel('Sample number')
    plt.ylabel('Measured value [mmHg]')
    plt.grid(axis='y')
    # here there isn't the -1 because boxplot index starts from 1 and not 0
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
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
    plt.axvline(x=index_start_rebreathing-offset, color='gold')
    plt.axvline(x=index_start_rebreathing-offset+4, color='coral')
    plt.xlabel('Sample number')
    #plt.legend(['Start Rebreathing', 'Start rebreathing'], loc="upper left")
    #plt.boxplot(data_for_boxplot_delta, patch_artist=True)
    #plt.boxplot(S_data_for_boxplot_delta, patch_artist=True)

    # plt.show()
    '''
    ---------------------------------------------------------------------------------
    INTERPOLATION - RAW VALUES - SAMPLES

    In the following section an exponential fitting is performed on PCB device
    data. IT IS NECESSARY TO USE DATA WITH 10s RESOLUTION

    Representative data are from subject SO3, 9-02-2022.

    The plots to be drawn are 3:
        - Stimulus
        - PCB device response and fitting
        - Sentec device response

    PARAMETERS: (in the interpolation section)
        - @param <delay_pcb>: time after the sensors delay in which the curve should
                be fitted.
        - @param <delay_sentec>: delay from start rebreathing where the Sentec signal
                starts to rise.
        - @param <gap>: baseline (in the case of raw values) or deviation from the 
                baseline (in the case of delta values).
        - @param <end_fitting>: sample number where to stop the exponential fitting.
    ---------------------------------------------------------------------------------
    '''
    if(flag_30seconds == 0):
        subject_id = 18

        delay_pcb = 19
        delay_sentec = 18
        delay_phys = 14

        gap = 1480
        gap_delta = -25
        end_fitting = 88

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

        # print(exp_y1)

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

        #print("\nLength of the Sentec and PCB arrays (overall):")
        # print(len(arr_y_pcb))  # 89
        #print("\nLength of the stimulus array (overall):")
        # print(len(exp_y1))

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
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_pcb, color='red')
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
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_sentec, color='red')
        plt.xlabel('Sample Number')
        plt.ylabel('PtCO2 [mmHg]')
        plt.grid(axis='y')
        plt.legend(['Filtered Sentec device data', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="upper right")

        #####################################################################
        #                    Interpolation with curve_fit                   #
        #####################################################################

        #################### PARAMETERS ####################
        #gap = 700
        #end_fitting = 80
        ####################################################

        x_repr_pcb = []
        y_repr_pcb = []

        # Check if end_fitting index is smaller than overall array length
        if(end_fitting > len(arr_y_pcb)):
            end_fitting = len(arr_y_pcb)

        for i in range(delay_pcb, end_fitting, 1):
            x_repr_pcb.append(i)
            y_repr_pcb.append(arr_y_pcb[i])

        # print(y_repr_pcb)
        # print(x_repr_pcb)

        p0 = (300, 2)  # start with values near those we expect
        params, cv = scipy.optimize.curve_fit(
            lambda t, B, tau: B*(1 - np.exp((-(t-delay_pcb)/tau))) + gap,  x_repr_pcb,  y_repr_pcb)

        print("\nFitting parameters (raw): ")
        print(params)
        print("\nCV fitting (raw): ")
        print(cv)

        B = params[0]
        tau = params[1]

        x_fitted = []
        y_fitted = []

        x_repr_pcb = []
        for i in range(0, len(arr_y_pcb), 1):
            x_repr_pcb.append(i)

        for i in range(delay_pcb, end_fitting, 1):
            x_fitted.append(i)
            y_fitted.append(
                B*(1 - np.exp((-1*((x_fitted[i-delay_pcb])-delay_pcb)/tau))) + gap)

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
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_pcb, color='red')
        plt.xlabel('Sample Number')
        plt.ylabel('PtCO2 [ppm]')
        plt.grid(axis='y')
        plt.legend(['Raw PCB device data', 'Fitted curve', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="lower right")

        '''
        ---------------------------------------------------------------------------------
        INTERPOLATION - DELTA VALUES - SAMPLES

        In the following section an exponential fitting is performed on PCB device
        data.

        Representative data are from subject SO3, 9-02-2022.

        The plots to be drawn are 3:
            - Stimulus
            - PCB device response and fitting
            - Sentec device response
        ---------------------------------------------------------------------------------
        '''

        # Exctraction of x and y DELTA representative data
        y_repr_pcb_delta = []
        y_repr_sentec_delta = []
        y_repr_sentec_delta = delta_matrix_sentec[subject_id]
        y_repr_pcb_delta = delta_matrix_pcb[subject_id]

        #print("\nDelta Data from SO3:")
        # print(y_repr_pcb_delta)
        y_repr_pcb_delta = []
        y_repr_sentec_delta = []
        for i in range(int(index_start_rebreathing-offset), len(delta_matrix_pcb[subject_id]), 1):
            y_repr_pcb_delta.append(float(delta_matrix_pcb[subject_id][i]))
            y_repr_sentec_delta.append(
                float(delta_matrix_sentec[subject_id][i]))

        #print("\nDelta Data from SO3 after start rebreathing:")
        # print(y_repr_pcb_delta)

        #print("\nDelta Length of the array from START REBREATHING:")
        # print(len(y_repr_pcb_delta))  # 79

        # CREATION OF THE ARRAYS FOR OVERLAPPED PLOTS
        arr_y_pcb_delta = []
        arr_y_sentec_delta = []

        for i in range(0, 10, 1):
            arr_y_pcb_delta.append(y_repr_pcb_delta[0])
            arr_y_sentec_delta.append(y_repr_sentec_delta[0])

        for i in range(0, len(y_repr_pcb_delta), 1):
            arr_y_pcb_delta.append(y_repr_pcb_delta[i])
            arr_y_sentec_delta.append(y_repr_sentec_delta[i])

        #print("\nArray delta PCB for piled plots:")
        # print(arr_y_pcb_delta)
        #print("\nArray delta Sentec for piled plots:")
        # print(arr_y_sentec_delta)

        #print("\nLength of the delta Sentec and delta PCB arrays (overall):")
        # print(len(arr_y_pcb_delta))
        #print("\nLength of the stimulus array (overall):")
        # print(len(exp_y1))

        x_repr_pcb_delta = range(0, len(arr_y_pcb_delta), 1)
        x_repr_sentec_delta = range(0, len(arr_y_pcb_delta), 1)

        fig19 = plt.figure(19)
        plt.title("Delta PCB post start rebreathing data")
        plt.plot(x_repr_pcb_delta, arr_y_pcb_delta,
                 'k', color="black", linewidth='1')
        plt.axvline(x=10, color='forestgreen')
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_pcb, color='red')
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
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_sentec, color='red')
        plt.xlabel('Sample Number')
        plt.ylabel('PtCO2 [mmHg]')
        plt.grid(axis='y')
        plt.legend(['Filtered Sentec device data - DELTA', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="upper right")

        #####################################################################
        #                    Interpolation with curve_fit                   #
        #####################################################################

        #################### PARAMETERS ####################
        #gap_delta = -20
        ####################################################

        x_repr_pcb_delta = []
        y_repr_pcb_delta = []

        for i in range(delay_pcb, end_fitting, 1):
            x_repr_pcb_delta.append(i)
            y_repr_pcb_delta.append(arr_y_pcb_delta[i])

        # print(y_repr_pcb_delta)
        # print(x_repr_pcb_delta)

        p0 = (300, 2)  # start with values near those we expect
        params_delta, cv_delta = scipy.optimize.curve_fit(
            lambda t, B, tau: B*(1 - np.exp((-(t-delay_pcb)/tau))) + gap_delta,  x_repr_pcb_delta,  y_repr_pcb_delta)

        print("\nFitting parameters DELTA: ")
        print(params_delta)
        print("\nCV fitting DELTA: ")
        print(cv)

        B = params_delta[0]
        tau = params_delta[1]

        x_fitted_delta = []
        y_fitted_delta = []
        x_repr_pcb_delta = range(0, len(arr_y_pcb), 1)

        for i in range(delay_pcb, end_fitting, 1):
            x_fitted_delta.append(i)
            y_fitted_delta.append(
                B*(1 - np.exp((-1*((x_fitted_delta[i-delay_pcb])-delay_pcb)/tau))) + gap_delta)

        # Goodness of the fitting
        r2_score_value_delta = metrics.r2_score(
            y_repr_pcb_delta, y_fitted_delta)
        print("\n\n=================================================================")
        print("Fitting Goodness R2 - delta: ")
        print(r2_score_value_delta)
        print("=================================================================")

        fig21 = plt.figure(21)
        plt.title("Delta PCB post start rebreathing data and fitting")
        plt.plot(x_repr_pcb_delta, arr_y_pcb_delta,
                 'k', color="black", linewidth='1')
        plt.plot(x_fitted_delta, y_fitted_delta, 'm', label='Fitted curve')
        plt.axvline(x=10, color='forestgreen')
        plt.axvline(x=delay_phys, color='blue')
        plt.axvline(x=delay_pcb, color='red')
        plt.xlabel('Sample Number')
        plt.ylabel('PtCO2 [ppm]')
        plt.grid(axis='y')
        plt.legend(['Raw PCB device data - DELTA', 'Fitted curve', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="lower right")

        '''
        ---------------------------------------------------------------------------------
        INTERPOLATION - DELTA VALUES - SECONDS

        In the following section an exponential fitting is performed on PCB device
        data.

        Representative data are from subject SO3, 9-02-2022.

        The plots to be drawn are 3:
            - Stimulus
            - PCB device response and fitting
            - Sentec device response
        ---------------------------------------------------------------------------------
        '''
        # Exctraction of x and y DELTA representative data
        y_repr_pcb_delta = []
        y_repr_sentec_delta = []
        y_repr_sentec_delta = delta_matrix_sentec[subject_id]
        y_repr_pcb_delta = delta_matrix_pcb[subject_id]

        #print("\nDelta Data from SO3:")
        # print(y_repr_pcb_delta)
        y_repr_pcb_delta = []
        y_repr_sentec_delta = []
        for i in range(int(index_start_rebreathing-offset), len(delta_matrix_pcb[subject_id]), 1):
            y_repr_pcb_delta.append(float(delta_matrix_pcb[subject_id][i]))
            y_repr_sentec_delta.append(
                float(delta_matrix_sentec[subject_id][i]))

        # CREATION OF THE ARRAYS FOR OVERLAPPED PLOTS
        arr_y_pcb_delta = []
        arr_y_sentec_delta = []

        for i in range(0, 10, 1):
            arr_y_pcb_delta.append(y_repr_pcb_delta[0])
            arr_y_sentec_delta.append(y_repr_sentec_delta[0])

        for i in range(0, len(y_repr_pcb_delta), 1):
            arr_y_pcb_delta.append(y_repr_pcb_delta[i])
            arr_y_sentec_delta.append(y_repr_sentec_delta[i])

        x_repr_pcb_delta = []
        x_repr_sentec_delta = []
        for i in range(0, len(arr_y_pcb_delta), 1):
            x_repr_pcb_delta.append(i*10)
            x_repr_sentec_delta.append(i*10)

        fig19 = plt.figure(25)
        plt.title("Delta PCB post start rebreathing data")
        plt.plot(x_repr_pcb_delta, arr_y_pcb_delta,
                 'k', color="black", linewidth='1')
        plt.axvline(x=10*10, color='forestgreen')
        plt.axvline(x=delay_phys*10, color='blue')
        plt.axvline(x=delay_pcb*10, color='red')
        plt.xlabel('Time [s]')
        plt.ylabel('PtCO2 [ppm]')
        plt.grid(axis='y')
        plt.legend(['Raw PCB device data - DELTA', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="lower right")

        fig20 = plt.figure(26)
        plt.title("Delta Sentec post start rebreathing data")
        plt.plot(x_repr_sentec_delta, arr_y_sentec_delta, 'k',
                 color="black", linewidth='1',)
        plt.axvline(x=10*10, color='forestgreen')
        plt.axvline(x=delay_phys*10, color='blue')
        plt.axvline(x=delay_sentec*10, color='red')
        plt.xlabel('Time [s]')
        plt.ylabel('PtCO2 [mmHg]')
        plt.grid(axis='y')
        plt.legend(['Filtered Sentec device data - DELTA', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="upper right")

        #####################################################################
        #                    Interpolation with curve_fit                   #
        #####################################################################

        x_repr_pcb_delta = []
        y_repr_pcb_delta = []

        for i in range(delay_pcb, end_fitting, 1):
            x_repr_pcb_delta.append(i*10)
            y_repr_pcb_delta.append(arr_y_pcb_delta[i])

        # print(y_repr_pcb_delta)
        # print(x_repr_pcb_delta)

        p0 = (300, 2)  # start with values near those we expect
        params_delta, cv_delta = scipy.optimize.curve_fit(
            lambda t, B, tau: B*(1 - np.exp((-(t-delay_pcb*10)/tau))) + gap_delta,  x_repr_pcb_delta,  y_repr_pcb_delta)

        print("\nFitting parameters DELTA (seconds): ")
        print(params_delta)
        print("\nCV fitting DELTA (seconds): ")
        print(cv)

        B = params_delta[0]
        tau = params_delta[1]

        x_repr_pcb_delta = []
        for i in range(0, len(arr_y_pcb_delta), 1):
            x_repr_pcb_delta.append(i*10)

        x_fitted_delta = []
        y_fitted_delta = []
        for i in range(delay_pcb, end_fitting, 1):
            x_fitted_delta.append(i*10)
            y_fitted_delta.append(
                B*(1 - np.exp((-1*((x_fitted_delta[i-delay_pcb])-delay_pcb*10)/tau))) + gap_delta)

        # Goodness of the fitting
        r2_score_value_delta = metrics.r2_score(
            y_repr_pcb_delta, y_fitted_delta)
        print("\n\n=================================================================")
        print("Fitting Goodness R2 - delta (seconds): ")
        print(r2_score_value_delta)
        print("=================================================================")

        fig21 = plt.figure(27)
        plt.title("Delta PCB post start rebreathing data and fitting")
        plt.plot(x_repr_pcb_delta, arr_y_pcb_delta,
                 'k', color="black", linewidth='1')
        plt.plot(x_fitted_delta, y_fitted_delta, 'm', label='Fitted curve')
        plt.axvline(x=10*10, color='forestgreen')
        plt.axvline(x=delay_phys*10, color='blue')
        plt.axvline(x=delay_pcb*10, color='red')
        plt.xlabel('Time [s]')
        plt.ylabel('PtCO2 [ppm]')
        plt.grid(axis='y')
        plt.legend(['Raw PCB device data - DELTA', 'Fitted curve', 'Start rebreathing', 'Physiological delay',
                    'Sensors delay'], loc="lower right")

    # plt.show()
