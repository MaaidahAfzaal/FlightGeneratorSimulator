from copy import deepcopy
from ctypes.wintypes import LONG
import numpy as np
import pandas as pd
import os
import random
import math
from pyparsing import trace_parse_action
from pyproj import Transformer
from config_parameters import *

scenario = "Scenario 4 (Cartesian)"
trans_XYZ_to_GPS = Transformer.from_crs(4978, 4979)
trans_GPS_to_XYZ = Transformer.from_crs(4979, 4978)

# radar lat/longs
RADAR_LONG = 78.078
RADAR_LAT = 25.872
# range of radar to cover all points in scenario
RADAR_RANGE = 9000000
# radius around track
TRACK_RADIUS = 0.05

# transforming radar lat longs to cartesian
radar_loc = trans_GPS_to_XYZ.transform(RADAR_LAT, RADAR_LONG, 0)

# reading excel file
if os.path.exists(VS_PATH + scenario + '.csv') and os.path.isfile(VS_PATH + scenario + '.csv'):
    data = pd.read_csv(VS_PATH + scenario + '.csv')

# random indices to drop
inds = np.arange(len(data))
# finding 10% of random indices to drop
M = int(len(data) * 0.01)
inds = np.random.choice(inds, M, replace=False)

# Looping over data at each second to add random samples 
for idx, row in data.iterrows():
    # random number of samples to add
    random_samples = random.randint(4, 6)

    # coord = trans_GPS_to_XYZ.transform(row['Track-X'], row['Track-Y'], row['Track-Z'])
    # data.at[idx, 'Track-X'] = coord[0]
    # data.at[idx, 'Track-Y'] = coord[1]

    # dropping the 10% of random indices
    if idx in inds:
        data = data.drop([idx])

    # generating random points equal to random number    
    rand = 1
    while rand <= random_samples:
        # random angle
        random_angle = 2 * math.pi * random.random()
        # random radius
        random_radius = RADAR_RANGE * math.sqrt(random.random())
        # calculating coordinates of point
        x = random_radius * math.cos(random_angle) + radar_loc[0]
        y = random_radius * math.sin(random_angle) + radar_loc[1]

        prob = random.randint(0, 10)
        # if prob is less than 50% and the random point lies in radar range but not in track range
        if prob < 4 and ((x - row['Track-X']) * (x - row['Track-X']) +
            (y - row['Track-Y']) * (y - row['Track-Y']) > TRACK_RADIUS * TRACK_RADIUS):
            # coord = trans_GPS_to_XYZ.transform(x, y, row['Track-Z'])
            insert = deepcopy(row)
            insert['Track-X'] = x
            insert['Track-Y'] = y
            
            data = pd.DataFrame(np.insert(data.values, idx + 1, insert.values, axis= 0), columns = data.columns)
            rand += 1

        # if random point generated lies within 0.05 of track and prob is greater than 50%
        elif prob >= 4 and ((x - row['Track-X']) * (x - row['Track-X']) +
            (y - row['Track-Y']) * (y - row['Track-Y']) <= TRACK_RADIUS * TRACK_RADIUS):

                # coord = trans_GPS_to_XYZ.transform(x, y, row['Track-Z'])
                insert = deepcopy(row)
                insert['Track-X'] = x
                insert['Track-Y'] = y

                data = pd.DataFrame(np.insert(data.values, idx + 1, insert.values, axis= 0), columns = data.columns)
                rand += 1

                
# sorting data according to time-stamp
data = data.sort_values(by='EpocTimeMilliSeconds', ascending=True)

# if file already exists delete it
if (os.path.exists("./Noisy Track Files/" + scenario + ' (Noisy).csv') and os.path.isfile("./Noisy Track Files/" + scenario +' (Noisy).csv')):
    os.remove("./Noisy Track Files/" + scenario +' (Noisy).csv')

# write to excel file
data.to_csv('./Noisy Track Files/' + scenario +' (Noisy).csv', index=False, float_format='%.3f')


 
