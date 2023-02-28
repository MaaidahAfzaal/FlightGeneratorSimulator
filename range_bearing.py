from copy import deepcopy
from ctypes.wintypes import LONG
import numpy as np
import pandas as pd
import os
import math
from pyproj import Transformer
from config_parameters import *

scenario = "Scenario 4"
trans_GPS_to_XYZ = Transformer.from_crs(4979, 4978)

RADAR_LONG = 78.078
RADAR_LAT = 25.872
radar_pos = trans_GPS_to_XYZ.transform(RADAR_LAT, RADAR_LONG, 0)

# reading excel file
if os.path.exists("./Noisy Track Files/" + scenario + ' (Cartesian) (Noisy).csv') and os.path.isfile("./Noisy Track Files/" + scenario + ' (Cartesian) (Noisy).csv'):
    data = pd.read_csv("./Noisy Track Files/" + scenario + ' (Cartesian) (Noisy).csv')

# creating dict to write data
excel_data = {}
excel_data['Time-stamp'] = []
excel_data['Range'] = []
excel_data['Bearing'] = []

# iterating over excel file
for idx, row in data.iterrows():
    # converting to range and bearing
    range = np.linalg.norm(np.subtract([row['Track-X'], row['Track-Y']], [radar_pos[0], radar_pos[1]]))
    bearing = math.atan2((row['Track-Y'] - radar_pos[1]), (row['Track-X'] - radar_pos[0]))

    # appending to excel file
    excel_data['Time-stamp'].append(int(row['EpocTimeMilliSeconds'] - data['EpocTimeMilliSeconds'][0]))
    excel_data['Range'].append(range)
    excel_data['Bearing'].append(bearing)

# if file already exists delete it
if os.path.exists("./Noisy Track Files/" + scenario + ' (radar).csv') and os.path.isfile("./Noisy Track Files/" + scenario + ' (radar).csv'):
    os.remove("./Noisy Track Files/" + scenario + ' (radar).csv')

# write dict to excel file
(pd.DataFrame.from_dict(data=excel_data, orient='columns').to_csv("./Noisy Track Files/" + scenario + ' (radar).csv', header=True, index=False))