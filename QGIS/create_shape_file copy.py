from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest
import numpy as np
from qgis.core import *
from qgis.utils import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
import sys
sys.path.append('D:\\ScenarioGenratorQGIS\\')
import os
import sys
import time
# from config_parameters import *


qgs_app = QgsApplication([], True)
qgs_app.setPrefixPath("C:/OSGeo4W64/apps/qgis-dev", True)
qgs_app.initQgis()


# Empty array for route name
route_name = []
# Empty array for QgsPoints of coordinates of Bases
points_route = [] 
# Empty array for Names of Bases
names_route = [] 

# Read the text file
txt=open(".\\Coordinates files\\Indian_Bases.txt",'r')

# Reading all lines in text file
coords_bases = [line.split(',') for line in txt.readlines()]
data = []
bases = []
id_bases = []
for coord in coords_bases:
    lat, long, id_base, base = coord[0].split()
    data.append([float(long), float(lat)])
    bases.append(base)
    id_bases.append(id_base)
# for coord in coords_bases:
#     coord[0] = float(coord[0])
#     coord[1] = float(coord[1].strip('\n'))
#     data.append(QgsPoint(coord[0], coord[1]))

# # Extracting names of routes from text file
# route_id = [id for id in coords_bases if len(id) == 1]



# coords_bases = [elem for elem in coords_bases if elem != ['0.000000', '9999.000000\n']]
# data = dict()
# for i in route_id:
#     if i != route_id[-1]:
#         first_index = coords_bases.index(i)
#         next_index = coords_bases.index(route_id[route_id.index(i) + 1])
#         data[i[0].strip('\n')] = coords_bases[first_index+1 : next_index]

# for keys, value in data.items():
#     for x in range(len(value)):
#         value[x][-1] = value[x][-1].strip('\n')
#         value[x].append(QgsPoint(float(value[x][1]), float(value[x][0])))
        

# coords_bases = coords_bases.remove(['0.000000', '9999.000000\n']) 
# for route_id in coords_bases:
#     if len(route_id) == 1:
#         route_ids.append 
# For loop converting strings to Qgs points
# for iter in range(len(coords_bases)):
#     points_bases.append(QgsPointXY(float(coords_bases[iter][1]), float(coords_bases[iter][0])))
#     id_bases.append(coords_bases[iter][2])
#     names_bases.append(coords_bases[iter][3])
# # See the size of list
# print(len(points_bases))

# Loop to Draw Points of Military Bases
Mil_basesPK = QgsVectorLayer("Point?crs=epsg:4326&field=lat:float&field=long:float&field=base:str&index=yes",
                                           "Indian Bases", "memory")
pr= Mil_basesPK.dataProvider()
feature = QgsFeature()

# for key, value in data.items():
#     for iter in range(len(value)-1):
#        ([QgsPoint(self.data_longitude[i], self.data_latitude[i]), QgsPoint(self.new_lon, self.new_lat)])
for i in range(len(data)):
    geom = QgsPointXY(data[i][0], data[i][1])
    feature.setGeometry(QgsGeometry.fromPointXY(geom))
    feature.setAttributes([data[i][1], data[i][0], bases[i]])
    Mil_basesPK.dataProvider().addFeatures([feature])
    # feature.setGeometry(QgsGeometry.fromPolyline(data[0: len(data)]))
    # feature.setAttributes([1])
    # pr.addFeatures([feature])
    Mil_basesPK.commitChanges()
    Mil_basesPK.updateFields()
    Mil_basesPK.updateExtents()
    
Mil_basesPK.renderer().symbol().setColor(Qt.red)

path= ".\\Layers\\Indian_Bases.shp"
options=QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "ESRI Shapefile"
_writer = QgsVectorFileWriter.writeAsVectorFormatV2(Mil_basesPK, path, QgsCoordinateTransformContext(), options)
Mil_basesPK.saveSldStyle(".\\Layers\\Indian_Bases.sld")