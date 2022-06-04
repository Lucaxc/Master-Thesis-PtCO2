'''
------------------------------------------------------------------------------------------
                        PYTHON SCRIPT FOR MEAN VALUES EXTRACTION

Author: Luca Colombo, MSc Student in Biomedical Engineering - Technologies for Electronics

This script is used to extract averages value in the measurement data every other sample,
where the number of samples to be considered can vary. Some quantities has to be changed
when running the script, depending on user's needs.

\Parameters:
    @param <filename.csv>: at the beginning of the script change the file name to
            associate the running of the script with the desired CSV file.
    @param df.columns: change the names of the columns (ONLY AFTER THE COLUMN NAMED
            'SENTEC') with the name you want, if other columns are present.
    @param sample_number: number of samples in the interval on which the average is
            computed. Default value is 10.
------------------------------------------------------------------------------------------
'''

from functools import partial
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import statistics as stat

sample_number = 30

# Dataframe import for aggregate data analysis
print("------------------------------- New run ---------------------------------")
df = pd.read_csv('31_05P.csv', sep=";")
df.columns = ("Timestamp_CO2", "CO2Sange", "Timestamp_deltaCO2",
              "DeltaCO2", "Sentec", "Rebreathing_mark")
print(df.head(10))
print("\n")
print("Type of Sentec:")
print(type(df[["Sentec"]]))
print("\n")
print(df[["Sentec"]])

# Rebreathing marks extraction
options = ["R1", "R2"]
print(df[df["Rebreathing_mark"].isin(options)])

index_start_rebreathing = df[df["Rebreathing_mark"] == "R1"].index.values
print("\nIndex start rebreathing")
print(index_start_rebreathing)
print(type(index_start_rebreathing))
start_rebreathing = int(index_start_rebreathing[0])
print(start_rebreathing)
print(type(start_rebreathing))

index_end_rebreathing = df[df["Rebreathing_mark"] == "R2"].index.values
print("\nIndex end rebreathing\n")
print(index_end_rebreathing)
end_rebreathing = int(index_end_rebreathing[0])
print(end_rebreathing)
print(type(end_rebreathing))

# Conversion of CO2 and Sentec data from a dataframe object to array
CO2_data = df.iloc[:, 1].values
print("\nCO2 Raw data array:")
print(CO2_data)
print(type(CO2_data))

print("\nSentec Raw data array:")
Sentec_data = df.iloc[:, 4].values
# Sentec_data = list(map(float, Sentec_data))
print(Sentec_data)
print(type(Sentec_data))


'''
------------------------------------------------------------------------------------------
Mean values extraction - PRE-START OF REBREATHING MANEUVER

Firstly all data from the beginning of the procedure to the
start of the rebreathing phase are summed and an average on this value is computed.

Then, given a specific window of samples, the average value on this window is computed
and save in an array. Finally, the array is reversed, ready to be merged with the other
array that will be generated (this time sequentially) from the start rebreathing
index down.
------------------------------------------------------------------------------------------
'''
# Pre-rebreathing Mean value extraction
total_CO2 = 0
average_total_CO2 = 0
for i in range(start_rebreathing, 0, -1):
    total_CO2 += CO2_data[i]

# print("\n\nTotal CO2 before rebreathing:")
# print(total_CO2)

average_total_CO2 = float(total_CO2/start_rebreathing)
# print("\n\nAverage CO2 before rebreathing:")
# print(average_total_CO2)
# print("\n\n")

# Pre-rebreathing Mean interval values extraction (10 samples average)
total_CO2 = 0
total_Sentec = 0
partial_total_co2 = 0
partial_total_sentec = 0
add_co2 = 0
add_sentec = 0
averages_device_pre = []
averages_sentec_pre = []
j = 0

for i in range(start_rebreathing, 0, -1):
    partial_total_co2 += CO2_data[i]
    partial_total_sentec += Sentec_data[i]
    # print(CO2_data[i])
    if((start_rebreathing-i+1) % sample_number == 0 and (start_rebreathing-i+1) != 0):
        # print(i)
        add_co2 = round(float(partial_total_co2/sample_number), 2)
        add_sentec = round(float(partial_total_sentec/sample_number), 2)
        averages_device_pre.append(add_co2)
        averages_sentec_pre.append(add_sentec)
        j = j + 1
        partial_total_co2 = 0
        partial_total_sentec = 0

# print("\n\nArray of average values, first part")
# print(averages_device_pre)

# Need of reverting the array because the for loop is done from
# start rebreathing up, so values need to be reindexed
averages_device_pre.reverse()
averages_sentec_pre.reverse()
# print(averages_device_pre)
averages_device_pre.append("START")  # to martk start rebreathing
averages_sentec_pre.append("START")
# print(averages_device_pre)


'''
------------------------------------------------------------------------------------------
Mean values extraction - POST-START OF REBREATHING MANEUVER

Data from the start of the rebreathing phase are summed and an averaged.
Resulting vector will be attached to the previously generated one.
------------------------------------------------------------------------------------------
'''
partial_total_co2 = 0
partial_total_sentec = 0
averages_device_post = []
averages_sentec_post = []
add_co2 = 0
add_sentec = 0
j = 0

for i in range(start_rebreathing+1, len(CO2_data), 1):
    partial_total_co2 += CO2_data[i]
    partial_total_sentec += Sentec_data[i]
    if((i-(start_rebreathing+1)+1) % sample_number == 0 and (i-(start_rebreathing+1)+1) != 0):
        add_co2 = round(float(partial_total_co2/sample_number), 2)
        add_sentec = round(float(partial_total_sentec/sample_number), 2)
        averages_device_post.append(add_co2)
        averages_sentec_post.append(add_sentec)
        j = j + 1
        partial_total_co2 = 0
        partial_total_sentec = 0

# print("\n\nArray of average values, second part")
# print(averages_device_post)

# Linking the two array parts and creating a df
averages_device_complete = np.concatenate(
    (averages_device_pre, averages_device_post))
averages_sentec_complete = np.concatenate(
    (averages_sentec_pre, averages_sentec_post))
# averages_device_pre.append(averages_device_post)
# print(averages_device_pre)
# print("\n\nConcatenated array")
# print(averages_device_complete)
# print("\n\nArray elements type")
# it is a numpy string, must be converted to float
# print(type(averages_device_complete[0]))

print("\n\nDataframe")
CO2_df_mean = pd.DataFrame(averages_device_complete)
Sentec_df_mean = pd.DataFrame(averages_sentec_complete)

print("\nCO2 averages dataframe:")
print(CO2_df_mean)

print("\n\nSentec averages dataframe:")
print(Sentec_df_mean)

# Exporting data to CSV
CO2_df_mean.to_csv('CO2_df_exp_mean.csv', sep=';')
Sentec_df_mean.to_csv('Sentec_df_exp_mean.csv', sep=';')


'''
------------------------------------------------------------------------------------------
MEAN Data plotting

Complete arrays of averaged values are plotted, both for the PCB CO2 device and the
Sentec device
------------------------------------------------------------------------------------------
'''
averages_device_pre.remove("START")
averages_sentec_pre.remove("START")
averages_device_complete = np.concatenate(
    (averages_device_pre, averages_device_post))
averages_sentec_complete = np.concatenate(
    (averages_sentec_pre, averages_sentec_post))

figure1 = plt.figure(1)
y1 = averages_sentec_complete
x1 = range(0, len(averages_sentec_complete), 1)
plt.title("Sentec - MEAN")
plt.plot(x1, y1, '.-', color="red", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [mmHg]')

figure2 = plt.figure(2)
y2 = averages_device_complete
x2 = range(0, len(averages_device_complete), 1)
plt.title("Device PCB - MEAN")
plt.plot(x2, y2, '*-', color="blue", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [ppm]')


####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

'''
------------------------------------------------------------------------------------------
Median values extraction - PRE-START OF REBREATHING MANEUVER

Firstly all data from the beginning of the procedure to the
start of the rebreathing phase are grouped and median values are computed.

Then, given a specific window of samples, the median value on this window is computed
and save in an array. Finally, the array is reversed, ready to be merged with the other
array that will be generated (this time sequentially) from the start rebreathing
index down.
------------------------------------------------------------------------------------------
'''
# Pre-rebreathing Median interval values extraction
median_partial_array_device = []
median_partial_array_sentec = []
median_array_device_pre = []
median_array_sentec_pre = []

for i in range(start_rebreathing, 0, -1):
    median_partial_array_device.append(round(float(CO2_data[i]), 2))
    median_partial_array_sentec.append(round(float(Sentec_data[i]), 2))
    # print(CO2_data[i])
    if((start_rebreathing-i+1) % sample_number == 0 and (start_rebreathing-i+1) != 0):
        median_array_device_pre.append(round(float(
            stat.median(median_partial_array_device)), 2))
        median_array_sentec_pre.append(round(float(
            stat.median(median_partial_array_sentec)), 2))
        # print(median_array_sentec_pre)
        # print(median_array_device_pre)
        median_partial_array_device = []
        median_partial_array_sentec = []

# Need of reverting the array because the for loop is done from
# start rebreathing up, so values need to be reindexed
median_array_device_pre.reverse()
median_array_sentec_pre.reverse()
# print(median_array_device_pre)

median_array_device_pre.append("START")  # to martk start rebreathing
median_array_sentec_pre.append("START")
# print(median_array_device_pre)

'''
------------------------------------------------------------------------------------------
Median values extraction - POST-START OF REBREATHING MANEUVER

Data from the start of the rebreathing phase are collected in an array and median is
computed.
Resulting vector will be attached to the previously generated one.
------------------------------------------------------------------------------------------
'''
median_partial_array_device = []
median_partial_array_sentec = []
median_array_device_post = []
median_array_sentec_post = []

median_device = []
median_sentec = []

for i in range(start_rebreathing+1, len(CO2_data), 1):
    median_partial_array_device.append(round(float(CO2_data[i]), 2))
    median_partial_array_sentec.append(round(float(Sentec_data[i]), 2))
    if((i-(start_rebreathing+1)+1) % sample_number == 0 and (i-(start_rebreathing+1)+1) != 0):
        median_array_device_post.append(
            round(float(stat.median(median_partial_array_device)), 2))
        median_array_sentec_post.append(round(float(
            stat.median(median_partial_array_sentec)), 2))
        # print(median_array_sentec_post)
        # print(median_array_device_post)
        median_partial_array_device = []
        median_partial_array_sentec = []

# print("\n\nArray of average values, second part")
# print(averages_device_post)

# Linking the two array parts and creating a df
median_device = np.concatenate(
    (median_array_device_pre, median_array_device_post))
median_sentec = np.concatenate(
    (median_array_sentec_pre, median_array_sentec_post))

print("\n\nMedian arrays: ")
print(median_device)
print(median_sentec)

'''
------------------------------------------------------------------------------------------
MEDIAN Dataframe export
------------------------------------------------------------------------------------------
'''
print("\n\nDataframe")
CO2_df_median = pd.DataFrame(median_device)
Sentec_df_median = pd.DataFrame(median_sentec)

print("\nCO2 averages dataframe:")
print(CO2_df_median)

print("\n\nSentec averages dataframe:")
print(Sentec_df_median)

# Exporting data to CSV
CO2_df_median.to_csv('CO2_df_exp_median.csv', sep=';')
Sentec_df_median.to_csv('Sentec_df_exp_median.csv', sep=';')

'''
------------------------------------------------------------------------------------------
MEDIAN Data plotting

Complete arrays of median values are plotted, both for the PCB CO2 device and the
Sentec device
------------------------------------------------------------------------------------------
'''
median_array_device_pre.remove("START")
median_array_sentec_pre.remove("START")
median_device = np.concatenate(
    (median_array_device_pre, median_array_device_post))
median_sentec = np.concatenate(
    (median_array_sentec_pre, median_array_sentec_post))

figure3 = plt.figure(3)
y1 = median_sentec
x1 = range(0, len(median_sentec), 1)
plt.title("Sentec - MEDIAN")
plt.plot(x1, y1, '.-', color="red", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [mmHg]')

figure4 = plt.figure(4)
y2 = median_device
x2 = range(0, len(median_device), 1)
plt.title("Device PCB - MEDIAN")
plt.plot(x2, y2, '*-', color="red", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [ppm]')

# Overlapped plots
figure5 = plt.figure(5)
y1 = averages_sentec_complete
x1 = range(0, len(averages_sentec_complete), 1)
plt.title("Sentec")
plt.plot(x1, y1, '.-', color="blue", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [mmHg]')

figure6 = plt.figure(6)
y2 = averages_device_complete
x2 = range(0, len(averages_device_complete), 1)
plt.title("Device PCB")
plt.plot(x2, y2, '*-', color="blue", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [ppm]')

figure5 = plt.figure(5)
y1 = median_sentec
x1 = range(0, len(median_sentec), 1)
plt.title("Sentec")
plt.plot(x1, y1, '.-', color="red", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [mmHg]')
plt.legend(['Mean', 'Median'], loc="upper left")

figure6 = plt.figure(6)
y2 = median_device
x2 = range(0, len(median_device), 1)
plt.title("Device PCB")
plt.plot(x2, y2, '*-', color="red", linewidth='1')
plt.xlabel('Time stamp')
plt.ylabel('Measured value [ppm]')
plt.legend(['Mean', 'Median'], loc="upper left")

plt.show()
