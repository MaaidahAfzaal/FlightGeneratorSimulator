import numpy as np
import pandas as pd
import sys
import os
import random
from config_parameters import *

scenario = "Scenario 4"

# reading excel file
if os.path.exists(VS_PATH + scenario + '.csv') and os.path.isfile(VS_PATH + scenario + '.csv'):
    data = pd.read_csv(VS_PATH + scenario + '.csv')

# finding unique tracks
data = data.values.tolist()
unique_tracks = set(data[x][SYS_TRACK_NO] for x in range(len(data)))
unique_tracks = list(unique_tracks)

# for loop to add random samples to data
final_data = []
# looping over all unique tracks
for j in unique_tracks:
    clean_data = []
    # adding all values of unique track j to new list
    for x in data:
        if x[SYS_TRACK_NO] == j:
            clean_data.append(x) 

    # getting 90% of those lat longs of unique track to add noise too 
    inds = np.arange(len(clean_data))
    M = int(len(clean_data) * 90 / 100)
    inds = np.random.choice(inds, M, replace=False)
    # making track quality of those tracks equal to nan
    for l in range(len(inds)):
        clean_data[inds[l]][TRACK_QUALITY] = float('Nan')

    noisy_data = pd.DataFrame(clean_data)

    noisy_data = np.array(noisy_data.dropna())
    for i in range(1, len(noisy_data)):
        noisy_data[i][TRACK_QUALITY] = random.sample(range(-1, 7), 1)[0]
    noisy_data[0][TRACK_QUALITY] = 7

    # if track quality is less than 3 than lat long of previous sec is retained
    for i in range(len(noisy_data)):
        if int(noisy_data[i][TRACK_QUALITY]) < 3:
            noisy_data[i][LATITUDE] = noisy_data[i-1][LATITUDE]
            noisy_data[i][LONGITUDE] = noisy_data[i-1][LONGITUDE]
            noisy_data[i][HEADING] = noisy_data[i-1][HEADING]
            noisy_data[i][SPEED] = noisy_data[i-1][SPEED]
            noisy_data[i][ALTITUDE] = noisy_data[i-1][ALTITUDE]

    final_data.append(noisy_data)

data_final = []
for i in range(0, len(final_data)):
    for j in range(0, len(final_data[i])):
        data_final.append(final_data[i][j])


# print(final_data)

dataframe = pd.DataFrame(columns= HEADER, data= data_final)
sorted_df = dataframe.sort_values(by='Timestamp-sec', ascending=True)

sorted_df.to_csv('./Noisy Track Files/' + scenario +' (Noisy).csv', index=False, float_format='%.3f')