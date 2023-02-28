from config_parameters import *

qgs_app = QgsApplication([], True)
qgs_app.setPrefixPath("C:/OSGeo4W64/apps/qgis-dev", True)
qgs_app.initQgis()

# Read the text file
vps = pd.read_csv('.\\Coordinates files\\dummy-vps-config-2.csv')

# Loop to Draw Points of Military Bases
Mil_basesPK = QgsVectorLayer("LineString?crs=epsg:4326&field=route_id:str&index=yes", "redline", "memory")
pr= Mil_basesPK.dataProvider()
feature = QgsFeature()

for key, value in vps.items():
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
Mil_basesPK.renderer().symbol().setColor ( QColor('#714423'))

path= "D:/PoCs/redline.shp"
options=QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "ESRI Shapefile"
_writer = QgsVectorFileWriter.writeAsVectorFormatV2(Mil_basesPK, path, QgsCoordinateTransformContext(), options)
Mil_basesPK.saveSldStyle("D:/PoCs/redlines.sld")