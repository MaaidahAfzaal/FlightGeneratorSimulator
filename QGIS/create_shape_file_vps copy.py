from config_parameters import *

qgs_app = QgsApplication([], True)
qgs_app.setPrefixPath("C:/OSGeo4W64/apps/qgis-dev", True)
qgs_app.initQgis()

# Read the text file
vps = pd.read_csv('.\\Coordinates files\\dummy-vps-config-2.csv')
print(vps)
# Loop to Draw Points of Military Bases
Mil_basesPK = QgsVectorLayer("Point?crs=epsg:4326&field=lat:float&field=long:float&field=id:str&index=yes",
                                           "VPs", "memory")
pr= Mil_basesPK.dataProvider()
feature = QgsFeature()

for x in vps.iterrows():
    geom = QgsPointXY(float(x[1]['Long']), float(x[1]['Lat']))
    feature.setGeometry(QgsGeometry.fromPointXY(geom))
    feature.setAttributes([float(x[1]['Lat']), float(x[1]['Long']), str(x[1]['VP-ID'])])
    Mil_basesPK.dataProvider().addFeatures([feature])
    # feature.setGeometry(QgsGeometry.fromPolyline(data[0: len(data)]))
    # feature.setAttributes([1])
    # pr.addFeatures([feature])
    Mil_basesPK.commitChanges()
    Mil_basesPK.updateFields()
    Mil_basesPK.updateExtents()
Mil_basesPK.renderer().symbol().setColor(Qt.green)

path= ".\\Layers\\VPs.shp"
options=QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "ESRI Shapefile"
_writer = QgsVectorFileWriter.writeAsVectorFormatV2(Mil_basesPK, path, QgsCoordinateTransformContext(), options)
Mil_basesPK.saveSldStyle(".\\Layers\\VPs.sld")