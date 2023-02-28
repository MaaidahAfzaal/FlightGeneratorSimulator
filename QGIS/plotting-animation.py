import pandas as pd
from PyQt5 import QtTest
#from qgis import processing

# Setting background map color
iface.mapCanvas().setCanvasColor(Qt.black)

# Importing pakistan border layer and indian basees
pakistan_border = QgsVectorLayer("D:\\ScenarioGenratorQGIS\\Layers\\PakistanIBPolyline.shp", "pakistan_border")
pakistan_border.renderer().symbol().setColor ( QColor(Qt.darkGray))
#ats_routes_india = QgsVectorLayer("D:\\ScenarioGenratorQGIS\\Layers\\ATS_Routes_India_Dummy.shp", "ATS_routes_Indea")
#ats_routes_india.renderer().symbol().setColor ( QColor(Qt.white))
##processing.run("native:creategrid" , {
#                                        'TYPE': 1,
#                                        'EXTENT': pakistan_border,
#                                        'HSPACING': 1,
#                                        'VSPACING0': 1,
#                                        'CRS': 'ESPG:4326',
#                                        'OUTPUT': 'D:\\AD TEWA\\ScenarioGenratorQGIS\\Layers\\GRID.shp'})
#                                        
#processing.run("native:creategrid" , {
#                                        'TYPE': 1,
#                                        'EXTENT': pakistan_border,
#                                        'HSPACING': 0.16666667,
#                                        'VSPACING': 0.16666667,
#                                        'CRS': 'ESPG:4326',
#                                        'OUTPUT': 'D:\\AD TEWA\\ScenarioGenratorQGIS\\Layers\\smallGrid.shp'})


# Importing tracks file
df1=pd.read_csv('D:\\ScenarioGenratorQGIS\\Track Files\\Scenario 25 Aircrafts.csv')

# Getting data from tracks file
data_latitude=list(df1['TrackLatitude'])
data_longitude=list(df1['TrackLongitude'])
time=list(df1['EpocTimeMilliSeconds'])

# Creating layer to plot coordinates of tracks
streaming_layer=QgsVectorLayer('Point?crs=epsg:4326&field=x:float&field=y:float', 'tracks_layer', "memory")
stream_data_provider=streaming_layer.dataProvider()
feature_mark=QgsFeature()
streaming_layer.renderer().symbol().setColor(QColor(Qt.yellow))

# Setting layers in QGS
QgsProject.instance().addMapLayers([streaming_layer, pakistan_border])
iface.mapCanvas().setLayers([streaming_layer, pakistan_border])
# Setting zoom level according to pakistan border layer
iface.mapCanvas().setExtent(pakistan_border.extent())

# Loop for plotting coordinates
for i in range(len(data_latitude)):
    # If time has changed, add delay
    if (i>0 and time[i-1]!=time[i]):
        # Delay is of 0.5 seconds even though data is after every second so 
        # animation plays at x2 the speed
        QtTest.QTest.qWait((time[i]-time[i-1])*50)
        stream_data_provider.truncate()
    feature_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(data_longitude[i],data_latitude[i])))
    stream_data_provider.addFeature(feature_mark)
    feature_mark.setAttributes([data_longitude[i],data_latitude[i]])
    streaming_layer.commitChanges()
    streaming_layer.updateFields()
    streaming_layer.reload()
    iface.mapCanvas().refresh()
    
#feat = next(streaming_layer.getFeatures())
##print(feat.attributes())
#layer = QgsProject.instance().mapLayersByName('pakistan_border')[0]
#features_dict = {f.id(): QgsJsonUtils.exportAttributes(f) for f in layer.getFeatures()}
#print(features_dict)
#attributes = []
#for feature in streaming_layer.getFeatures():
#    attributes.append(feature.__geo_interface__["properties"])
#print(attributes)
#  
#layer = QgsProject.instance().mapLayersByName('pakistan_border')[0]  
#idx = layer.fields().indexOf('id')
#values = layer.uniqueValues(idx)
#print(values)
#