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
import matplotlib as plt

# Dataframe import for aggregate data analysis
print("------------------------------- New run ---------------------------------")
df = pd.read_csv('3_05P.csv', sep=";")
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
#Sentec_data = list(map(float, Sentec_data))
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

print("\n\nTotal CO2 before rebreathing:")
print(total_CO2)

average_total_CO2 = float(total_CO2/start_rebreathing)
print("\n\nAverage CO2 before rebreathing:")
print(average_total_CO2)
print("\n\n")

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
sample_number = 10

for i in range(start_rebreathing, 0, -1):
    partial_total_co2 += CO2_data[i]
    partial_total_sentec += Sentec_data[i]
    # print(CO2_data[i])
    if((start_rebreathing-i+1) % sample_number == 0 and (start_rebreathing-i+1) != 0):
        # print(i)
        add_co2 = round(float(partial_total_co2/10), 2)
        add_sentec = round(float(partial_total_sentec/10), 2)
        averages_device_pre.append(add_co2)
        averages_sentec_pre.append(add_sentec)
        j = j + 1
        partial_total_co2 = 0
        partial_total_sentec = 0

print("\n\nArray of average values, first part")
print(averages_device_pre)

# Need of reverting the array because the for loop is done from
# start rebreathing up, so values need to be reindexed
averages_device_pre.reverse()
averages_sentec_pre.reverse()
print(averages_device_pre)
averages_device_pre.append("START")  # to martk start rebreathing
averages_sentec_pre.append("START")
print(averages_device_pre)


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
        add_co2 = round(float(partial_total_co2/10), 2)
        add_sentec = round(float(partial_total_sentec/10), 2)
        averages_device_post.append(add_co2)
        averages_sentec_post.append(add_sentec)
        j = j + 1
        partial_total_co2 = 0
        partial_total_sentec = 0

print("\n\nArray of average values, second part")
print(averages_device_post)

# Linking the two array parts and creating a df
averages_device_complete = np.concatenate(
    (averages_device_pre, averages_device_post))
averages_sentec_complete = np.concatenate(
    (averages_sentec_pre, averages_sentec_post))
# averages_device_pre.append(averages_device_post)
# print(averages_device_pre)
print("\n\nConcatenated array")
print(averages_device_complete)

print("\n\nDataframe")
CO2_df = pd.DataFrame(averages_device_complete)
Sentec_df = pd.DataFrame(averages_sentec_complete)

print("\n\nCO2 averages dataframe:")
print(CO2_df)

print("\n\nSentec averages dataframe:")
print(Sentec_df)

# Exporting data to CSV
CO2_df.to_csv('CO2_dataframe_exported.csv', sep=';')
Sentec_df.to_csv('Sentec_dataframe_exported.csv', sep=';')


plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

x = np.array([5, 4, 1, 4, 5])
y = np.sort(x)

plt.title("Line graph")
plt.plot(x, y, color="red")

plt.show()
