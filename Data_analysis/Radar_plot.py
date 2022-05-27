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
df = pd.read_csv('Data_for_radarplot.csv', sep=";")
print("\n\nQuestionnairre dataframe:")
print(df)

categories = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5',
              'Q6', 'Q7', 'Q8', 'Q9', 'Q10']

categories = [*categories, categories[0]]

ideal = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
arr_S01 = []
arr_S02 = [5, 3, 4, 1, 4, 2, 3, 4, 4, 1]
arr_S03 = []
arr_S04 = [4, 1, 4, 1, 5, 1, 4, 3, 4, 1]
arr_S05 = [5, 4, 5, 1, 4, 1, 4, 1, 3, 1]
arr_S06 = [5, 1, 4, 1, 5, 1, 5, 3, 3, 1]
arr_S07 = [5, 2, 4, 1, 4, 2, 5, 2, 4, 1]
arr_S08 = [5, 1, 4, 1, 5, 2, 5, 1, 2, 1]
arr_S09 = [5, 1, 5, 1, 5, 2, 3, 2, 4, 1]
arr_S10 = []
arr_S11 = [5, 1, 4, 1, 5, 1, 4, 2, 4, 1]
arr_S12 = []
arr_S13 = []
arr_S14 = []

ideal = [*ideal, ideal[0]]
#arr_S01 = [*arr_S01, arr_S01[0]]
arr_S02 = [*arr_S02, arr_S02[0]]
#arr_S03 = [*arr_S03, arr_S03[0]]
arr_S04 = [*arr_S04, arr_S04[0]]
arr_S05 = [*arr_S05, arr_S05[0]]
arr_S06 = [*arr_S06, arr_S06[0]]
arr_S07 = [*arr_S07, arr_S07[0]]
arr_S08 = [*arr_S08, arr_S08[0]]
arr_S09 = [*arr_S09, arr_S09[0]]
#arr_S10 = [*arr_S10, arr_S10[0]]
arr_S11 = [*arr_S11, arr_S11[0]]
#arr_S12 = [*arr_S12, arr_S12[0]]
#arr_S13 = [*arr_S13, arr_S13[0]]
#arr_S14 = [*arr_S14, arr_S14[0]]


rows = len(df.index)
print(rows)

'''
support = []
answers = []
for i in range(0, rows, 1):
    support.append(df.iloc[i, :].values)
    support = support.astype(int)
    print(type(support[0]))
    support.append(int(df.iloc[i, 0]))
    answers.append((support))
    support = []

print(answers)
'''

label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(arr_S02))

plt.figure(1)
plt.subplot(polar=True)
#plt.plot(label_loc, arr_S01, label='S01')
plt.plot(label_loc, arr_S02, label='S02')
#plt.plot(label_loc, arr_S03, label='S03')
plt.plot(label_loc, arr_S04, label='S04')
plt.plot(label_loc, arr_S05, label='S05')
plt.plot(label_loc, arr_S06, label='S06')
plt.plot(label_loc, arr_S07, label='S07')
plt.plot(label_loc, arr_S08, label='S08')
plt.plot(label_loc, arr_S09, label='S09')
#plt.plot(label_loc, arr_S10, label='S10')
plt.plot(label_loc, arr_S11, label='S11')
#plt.plot(label_loc, arr_S12, label='S12')

plt.plot(label_loc, ideal, label='Ideal')
plt.title('Questonnaire response')
lines, labels = plt.thetagrids(np.degrees(label_loc), labels=categories)
# plt.legend(loc='best')
plt.show()
