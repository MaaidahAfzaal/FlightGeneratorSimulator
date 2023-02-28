import pandas as pd
import numpy as np
import math
from PyQt5 import QtTest
#from config_parameters import*
import geopy
from geopy import Point
import geopy.distance

# Setting background map color
iface.mapCanvas().setCanvasColor(Qt.black)

# Importing pakistan border layer and indian basees
pakistan_border = QgsVectorLayer("D:\\AD TEWA\\ScenarioGenratorQGIS\\Layers\\PakistanIBPolyline.shp", "pakistan_border")
pakistan_border.renderer().symbol().setColor ( QColor(Qt.darkGray))

# Creating layer to plot offsets
streaming_layer=QgsVectorLayer('Point?crs=epsg:4326&field=x:float&field=y:float', 'tracks_layer', "memory")
stream_data_provider=streaming_layer.dataProvider()
feature_mark=QgsFeature()
streaming_layer.renderer().symbol().setColor ( QColor(Qt.yellow))

# Creating layer to plot center of coord
center_layer=QgsVectorLayer('Point?crs=epsg:4326&field=x:float&field=y:float', 'center_point', "memory")
center_data_provider=center_layer.dataProvider()
center_mark=QgsFeature()
center_layer.renderer().symbol().setColor ( QColor(Qt.red))

# Setting layers in QGS
QgsProject.instance().addMapLayers([streaming_layer, center_layer, pakistan_border])
iface.mapCanvas().setLayers([streaming_layer, center_layer, pakistan_border])

# Setting zoom level according to offset layer
iface.mapCanvas().setExtent(streaming_layer.extent())

def add_formation(lat_center, lon_center):
    """
        Funciton to add offsets for greater than 1 aircraft in group
    Args:
        aircrafts (int): number of aircrafts in group
        latitude (array): array of length of aircrafts containing latitudes without offset
        longitude (array): array of length of aircrafts containing longitudes without offset

    Returns:
        latitude(array): array containing latitudes of aircrafts with offset
        longitude(array): array containing longitudes of aircrafts with offset
    """
#    lat_center = math.radians(lat_center)
#    lon_center = math.radians(lon_center)
    center = geopy.point.Point(lat_center, lon_center)

    d = geopy.distance.distance(miles= 1.6)
    new_latitude = geopy.distance.distance(miles= 0.62).destination(point=center, bearing=45).latitude
  
    new_longitude = geopy.distance.distance(miles= 0.62).destination(point=center, bearing=45).longitude
    
    return new_latitude, new_longitude

    
lat = 23.0722
long = 72.6333
aircrafts = 3
abs_heading = 45
D = 7
R = 6371

#old_lat, old_long = add_offsets(abs_heading, rel_heading, old_lat, old_long) 
old_lat, old_long = add_formation(lat, long) 

print("latitudes = ", old_lat)
print("longitudes = ", old_long)
#print("latitudes geopy = ", old_lat_geopy)
#print("longitudes geopy = ", old_long_geopy)
#
# Plotting center coord point
center_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(long, lat)))
center_data_provider.addFeature(center_mark)
center_mark.setAttributes([long, lat])
center_layer.commitChanges()
center_layer.updateFields()
center_layer.reload()
iface.mapCanvas().refresh()

# Plotting all offsets
#for i in range(len(old_lat)):
feature_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(old_long,old_lat)))
stream_data_provider.addFeature(feature_mark)
feature_mark.setAttributes([old_long,old_lat])
streaming_layer.commitChanges()
streaming_layer.updateFields()
streaming_layer.reload()
iface.mapCanvas().refresh()

#    
#    feature_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(old_long_geopy[i],old_lat_geopy[i])))
#    stream_data_provider.addFeature(feature_mark)
#    feature_mark.setAttributes([old_long_geopy[i],old_lat_geopy[i]])
#    streaming_layer.commitChanges()
#    streaming_layer.updateFields()
#    streaming_layer.reload()
#    iface.mapCanvas().refresh()
#    