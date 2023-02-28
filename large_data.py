import numpy as np
import pandas as pd
import random
from datetime import date
import os
from copy import deepcopy

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt5 import QtTest
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import*

from file_generation_latlong import get_data, get_current_time
from config_parameters import IAF_BASES, PLATFORMS, COL

QGIS_PATH = 'D:\\ScenarioGenratorQGIS\\'

pakistan_border = QgsVectorLayer(QGIS_PATH + "Layers\\redline.shp", "pakistan_border")

def get_lat_longs(base):
    base_point = QgsPointXY(IAF_BASES[base][1], IAF_BASES[base][0])
    geom = next(pakistan_border.getFeatures())
    lat_long_point = geom.geometry().nearestPoint(QgsGeometry.fromPointXY(base_point))
    return lat_long_point

def generate_data(total_aircrafts, bases, end_time):

    if isinstance(bases, int):
        # Selecting random bases from which points will originate
        bases = random.sample(IAF_BASES.keys(), bases)
    
    # Selecting random number of points from each base
    points_per_base = [0] * len(bases)
     
    # To make the sum of the final list as n
    for i in range(total_aircrafts) :
        # Increment any random element
        # from the array by 1
        points_per_base[random.randint(0, total_aircrafts) % len(bases)] += 1
 
    group_data = []
    for groups in range(len(bases)):
        init_speed = 350
        lat_long_point = get_lat_longs(bases[groups])
        longitude = lat_long_point.asPoint().x()
        latitude = lat_long_point.asPoint().y()
        
        # longitude, latitude = get_lat_longs(bases[groups])
        speed, altitude = 350, 5000

        mode_info = {}
        mode_info["IFF Mode 1"] = {}
        mode_info["IFF Mode 2"] = {}
        mode_info["IFF Mode 3"] = {}
        mode_info["IFF Mode 6"] = {}
        mode_info["Call Sign"] = {}
        mode_info["ICAO Type"] = {}
        mode_info["Mode S"] = {}
        mode_info["Mode C Height"] = {}
        platforms = {}
        track_no = {}
        track_id = {}
        current_date = date.today()
        current_date = current_date.strftime("%d-%m-%Y")
        # print(str(current_date))

        for row in range(points_per_base[groups]):
            track_no[str(row+1)] = str(1)
            track_id[str(row+1)] = "FIGHTER (HGF)"
            platforms[str(row+1)] = random.choice(PLATFORMS)
            mode_info["IFF Mode 1"][str(row+1)] = str(1)
            mode_info["IFF Mode 2"][str(row+1)] = str(1)
            mode_info["IFF Mode 3"][str(row+1)] = str(1)
            mode_info["IFF Mode 6"][str(row+1)] = str(1)
            mode_info["Call Sign"][str(row+1)] = str(1)
            mode_info["ICAO Type"][str(row+1)] = str(1)
            mode_info["Mode S"][str(row+1)] = str(1)
            mode_info["Mode C Height"][str(row+1)] = str(1)
            
        group = {
                "Sys Track No" : track_no,
                "Track ID" : track_id,
                "Aircrafts" : points_per_base[groups],
                "Platform" :platforms,
                "Origin" : bases[groups],
                "Date" : str(current_date),
                "Initial Time" : "00:00:00",
                "End Time" : end_time,
                "Initial Speed": init_speed,
                "Waypoints" : {
                    "Latitude" : latitude,
                    "Longitude" : longitude,
                    "Speed" : speed,
                    "Altitude" : altitude
                },
                "Mode Info" : mode_info
                # "Aircrafts Pos" : self.aircraft_pos
                # "Aircrafts Loc" : self.aircraft_locations,
                # "Aicrafts Ref" : self.ref
            }

        group_data.append(group)

    # Checking which tracks don't contain track numbers
    i = 0
    taken_ids = []
    for key in range(len(group_data)):
        for a in group_data[key]["Sys Track No"]:
            if group_data[key]["Sys Track No"][a] == "1":
                i += 1
            else:
                taken_ids.append(int(group_data[key]["Sys Track No"][a]))


    # Assigning random track ids to aircrafts not containing track no
    range_id = range(1000, 9000)
    avail_range = (num for num in range_id if num not in taken_ids)
    tracks_id = random.sample(list(avail_range), total_aircrafts-len(taken_ids))
    i = 0
    for key in range(len(group_data)):
        for a in group_data[key]["Sys Track No"]:
            if group_data[key]["Sys Track No"][a] == "1":
                group_data[key]["Sys Track No"][a] = tracks_id[i]
                i += 1

    # Getting data in required format
    excel_data = []
    for key in group_data:
        excel_data.append(get_data(key))

    data_final = []
    # Adding current time to time epocs
    for i in excel_data:
        for j in i:
            data_final.append(j)

    # Converting data to dataframe
    df = pd.DataFrame(columns= COL, data= data_final)
    sorted_df = df.sort_values(by='EpocTimeMilliSeconds', ascending=True)


    # If file already exists remove it
    if (os.path.exists(QGIS_PATH + 'Track Files\\Scenario ' + str(total_aircrafts) + ' Aircrafts.csv') and os.path.isfile(QGIS_PATH + 'Track Files\\Scenario ' + str(total_aircrafts) + ' Aircrafts.csv')):
        os.remove(QGIS_PATH + 'Track Files\\Scenario ' + str(total_aircrafts) + ' Aircrafts.csv')
    sorted_df.to_csv(QGIS_PATH + 'Track Files\\Scenario ' + str(total_aircrafts) + ' Aircrafts.csv', index=False, float_format='%.15f')


    
    print(bases)


# generate_data(total_aircrafts= 100, bases= 5)

