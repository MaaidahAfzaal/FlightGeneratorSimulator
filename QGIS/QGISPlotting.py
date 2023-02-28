import pandas as pd
df1=pd.read_csv('D:\\AD TEWA\\ScenarioGenrator\\tracks.csv')
#print(df1.head())
data_latitude=list(df1['TrackLatitude'])
data_longitude=list(df1['TrackLongitude'])
streaming_layer=QgsVectorLayer('Point?crs=epsg:4326', 'MyPoints', "memory")
stream_data_provider=streaming_layer.dataProvider()
feature_mark=QgsFeature()
for i in range (len(data_latitude)):
    #if (track_number[i]==6938):
    feature_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(data_longitude[i],data_latitude[i])))
    stream_data_provider.addFeature(feature_mark)
    streaming_layer.reload()
QgsProject.instance().addMapLayer(streaming_layer)