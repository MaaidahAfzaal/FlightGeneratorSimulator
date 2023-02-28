from qgis.gui import QgsMapToolEmitPoint

# Setting background map color
iface.mapCanvas().setCanvasColor(Qt.black)

# Importing pakistan border layer and indian basees
pakistan_border = QgsVectorLayer("D:\\AD TEWA\\ScenarioGenrator\\Layers\\PakistanIBPolyline.shp", "pakistan_border")
pakistan_border.renderer().symbol().setColor ( QColor(Qt.darkGray))

# Creating layer to plot coordinates of tracks
streaming_layer=QgsVectorLayer('Point?crs=epsg:4326&field=x:float&field=y:float', 'tracks_layer', "memory")
stream_data_provider=streaming_layer.dataProvider()
feature_mark=QgsFeature()
streaming_layer.renderer().symbol().setColor ( QColor(Qt.yellow))

QgsProject.instance().addMapLayers([streaming_layer, pakistan_border])
iface.mapCanvas().setLayers([streaming_layer, pakistan_border])
point = []

class PrintClickedPoint(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        
    def canvasPressEvent(self, e):
        point.append(self.toMapCoordinates(self.canvas.mouseLastXY()))
        feature_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point[-1][0], point[-1][1])))
        stream_data_provider.addFeature(feature_mark)
        feature_mark.setAttributes([point[-1][0], point[-1][1]])
        streaming_layer.commitChanges()
        streaming_layer.updateFields()
        streaming_layer.reload()
        iface.mapCanvas().refresh()
        print('Waypoint 1 : (Longitude = {:.4f}, Latitude = {:.4f})'.format(point_array[-1][0], point_array[-1][1]))
        

canvas_clicked = PrintClickedPoint(iface.mapCanvas())
iface.mapCanvas().setMapTool(canvas_clicked)

