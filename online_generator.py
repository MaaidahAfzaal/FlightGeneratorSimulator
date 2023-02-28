import geopy.distance
import sys
sys.path.append('D:\\ScenarioGenratorQGIS\\')
from config_parameters import *
from geographiclib.geodesic import Geodesic
import geopy
from copy import deepcopy
import math
import time
from datetime import datetime
import random
from threading import Thread
import sys
sys.path.append('D:\\ScenarioGenratorQGIS\\')
import socket
from struct import pack

# Setting up the UDP Server
# server_address_port = (SERVER_IP, SERVER_PORT)
# udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# udp_server_socket.bind((CLIENT_IP, CLIENT_PORT))

qgs_app = QgsApplication([], True)
qgs_app.setPrefixPath("C:/OSGeo4W64/apps/qgis-dev", True)
qgs_app.initQgis()


def window():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    widget = QWidget()
    widget.setGeometry(50, 50, 300, 200)
    sys.exit(app.exec_())


def add_point(layer, data_provider, feature, lat, lon, attributes):
    """
        Function to add point to points layer

    Args:
        layer (_type_): _description_
        data_provider (_type_): _description_
        feature (_type_): _description_
        lat (_type_): _description_
        lon (_type_): _description_
        attributes (_type_): _description_
    """
    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
    feature.setAttributes(attributes)
    data_provider.addFeatures([feature])
    layer.reload()
    layer.triggerRepaint()


def get_current_time():
    """
        Function to get the current time to schedule start of event

    Returns:
        milli(int): current time in milliseconds
    """
    current_time = datetime.now()
    current_time = current_time.strftime('%d/%m/%Y %H:%M:%S')
    t = datetime.strptime(current_time, '%d/%m/%Y %H:%M:%S')
    milli = time.mktime(t.timetuple())
    return int(milli)


class AddCustomFormation(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Add Custom Formation"))
        self.setGeometry(1000, 1200, 2000, 500)
        self.setStyleSheet('background-color: black ;border: 1px solid grey;')

        self.save_formation = QPushButton("Save", self)
        self.save_formation.setGeometry(750, 400, 500, 50)
        self.save_formation.setStyleSheet(
            'border: 3px solid green; color: white; background: black')
        self.save_formation.clicked.connect(self.get_formation)

        self.setAcceptDrops(True)

        # Adding aircraft icons equal to num of aircrafts
        for i in range(len(self.parent.selected_track)):
            self.aircraft = Aircraft(self.parent.selected_track[i], i, self)
            self.aircraft.show()

    def get_formation(self):
        children = self.findChildren(QLabel)
        i = 0
        rel_aircraft_pos = {}

        # Getting position of all aicrafts
        for child in children:
            rel_aircraft_pos[str(self.parent.selected_track[i])] = [
                child.pos().x(), child.pos().y()]
            i += 1

        # Using aircrafts one (blue) as reference
        ref = deepcopy(next(iter((rel_aircraft_pos.items())))[1])
        ref_key = next(iter((rel_aircraft_pos.items())))[0]

        for key in rel_aircraft_pos:
            if key != ref_key:
                # Finding relative pos of all aircrafts wrt reference and converting
                # to nautical miles
                rel_aircraft_pos[key][0] = (
                    ref[0] - rel_aircraft_pos[key][0]) * P_TO_Nm
                rel_aircraft_pos[key][1] = (
                    ref[1] - rel_aircraft_pos[key][1]) * P_TO_Nm
                self.parent.abs_aircraft_pos[key] = {}

                #  Finding distance of each aircraft from reference aircraft
                self.parent.abs_aircraft_pos[key]["distance"] = math.hypot(rel_aircraft_pos[ref_key][0] - rel_aircraft_pos[key][0],
                                                                           rel_aircraft_pos[ref_key][1] - rel_aircraft_pos[key][1])

                # Finding the angle of each aircraft wrt to ref and then find actual \
                # angle of that aircraft according to the quadrant it lies in wrt refernce
                self.parent.abs_aircraft_pos[key]["angle"] = math.degrees(math.acos(
                    abs(rel_aircraft_pos[key][0]) / self.parent.abs_aircraft_pos[key]["distance"]))
                if rel_aircraft_pos[key][0] < 0 and rel_aircraft_pos[key][1] > 0:
                    self.parent.abs_aircraft_pos[key]["angle"] = 90 - \
                        self.parent.abs_aircraft_pos[key]["angle"]
                elif rel_aircraft_pos[key][0] < 0 and rel_aircraft_pos[key][1] < 0:
                    self.parent.abs_aircraft_pos[key]["angle"] = 90 + \
                        self.parent.abs_aircraft_pos[key]["angle"]
                elif rel_aircraft_pos[key][0] > 0 and rel_aircraft_pos[key][1] < 0:
                    self.parent.abs_aircraft_pos[key]["angle"] = 270 - \
                        self.parent.abs_aircraft_pos[key]["angle"]
                elif rel_aircraft_pos[key][0] > 0 and rel_aircraft_pos[key][1] > 0:
                    self.parent.abs_aircraft_pos[key]["angle"] = 270 + \
                        self.parent.abs_aircraft_pos[key]["angle"]

                # Since formation is made at a heading of 90 degrees, that is subtracted from all angles \
                # to get heading due north
                self.parent.abs_aircraft_pos[key]["angle"] -= 90
                # If any angle is negative, changing it to fit between 0 and 360
                self.parent.abs_aircraft_pos[key]["angle"] = 360 + self.parent.abs_aircraft_pos[key]["angle"] \
                    if self.parent.abs_aircraft_pos[key]["angle"] < 0 else self.parent.abs_aircraft_pos[key]["angle"]
            else:
                rel_aircraft_pos[key][0] = 0
                rel_aircraft_pos[key][1] = 0
                self.parent.abs_aircraft_pos[key] = {}
                self.parent.abs_aircraft_pos[key]["distance"] = 0
                self.parent.abs_aircraft_pos[key]["angle"] = 0

        self.close()

    # Following functions are to allow drag and drop ability for aicrafts
    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        widget.move(pos)
        e.setDropAction(Qt.MoveAction)
        e.accept()


class AddBuiltInFormation(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate(
            "MainWindow", "Add Pre-defined Formation"))
        self.setGeometry(1000, 1200, 500, 400)
        self.setStyleSheet('background-color: black ;border: 1px solid grey;')\

        self.formation = QComboBox(self)
        self.formation.setGeometry(50, 50, 400, 75)
        self.formation.setStyleSheet(
            'border: 3px solid black; color: white; background: black')
        self.formation.addItems(FORMATIONS.keys())

        self.save_formation = QPushButton("Save", self)
        self.save_formation.setGeometry(50, 130, 400, 75)
        self.save_formation.setStyleSheet(
            'border: 3px solid green; color: white; background: black')
        self.save_formation.clicked.connect(self.get_formation)

        self.error_dialog = QLabel("", self)
        self.error_dialog.setGeometry(50, 215, 400, 100)
        self.error_dialog.setWordWrap(True)
        self.error_dialog.setStyleSheet(
            'border: 3px solid black; color: white; background: black')

    def get_formation(self):
        formation = self.formation.currentText()
        rel_aircraft_pos = FORMATIONS[formation]

        if len(rel_aircraft_pos) == len(self.parent.selected_track):
            i = 0
            for track in self.parent.selected_track:
                key = list(rel_aircraft_pos)[i]
                self.parent.abs_aircraft_pos[str(track)] = {}
                self.parent.abs_aircraft_pos[str(
                    track)]["distance"] = rel_aircraft_pos[key]['distance']
                self.parent.abs_aircraft_pos[str(
                    track)]["angle"] = rel_aircraft_pos[key]['angle']
                i += 1
            self.close()
        else:
            self.error_dialog.setText(
                'Number of aircrafts selected is not equal to aicrafts in formation')


class Aircraft(QLabel):
    def __init__(self, aircraft, i, parent=None):
        QLabel.__init__(self, parent=parent)
        self.setObjectName("aicraft"+str(i))
        self.i = i
        self.aircraft = aircraft
        self.img1 = QImage('D:\\ScenarioGenratorQGIS\\Logos\\plane1.png')
        self.img2 = QImage('D:\\ScenarioGenratorQGIS\\\\Logos\\plane.png')
        self.img1 = self.img1.scaled(
            71, 61, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.img2 = self.img2.scaled(
            71, 61, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.resize(self.img1.size())
        self.move(70 + i * 81, 50)
        self.setStyleSheet(
            'border: 1px solid black; color: black; background: black')

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        if self.i == 0:
            p.drawImage(0, 0, self.img1)
        else:
            p.drawImage(0, 0, self.img2)
        self.drawText(event, p)

    def drawText(self, event, p):
        p.setPen(QColor(255, 255, 255))
        p.drawText(event.rect(), Qt.AlignCenter, str(self.aircraft))

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.setHotSpot(e.pos() - self.rect().topLeft())
            drag.exec_(Qt.MoveAction)


class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter


class PrintClickedPoint(QgsMapToolEmitPoint):
    """
        Class to get lat, long waypoints from user click
    """

    def __init__(self,  canvas, layer, parent):
        self.canvas = canvas
        self.layer = layer
        self.layer_data_provider = self.layer.dataProvider()
        self.layer_feature = QgsFeature()
        # self.track_num = track_num
        self.parent = parent
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def canvasReleaseEvent(self, event):
        # Adding the waypoint selected by user to dictionary
        lat = round(self.toMapCoordinates(event.pos())[1], 5)
        long = round(self.toMapCoordinates(event.pos())[0], 5)
        new_tracks = [track for track in self.parent.selected_track if str(
            track) not in self.parent.point.keys()]
        for track in new_tracks:
            self.parent.point[str(track)] = []
        for track in self.parent.selected_track:
            self.parent.point[str(track)].append([lat, long])
            add_point(self.layer, self.layer_data_provider,
                      self.layer_feature, lat, long, [lat, long, str(track)])


class selectTool(QgsMapToolIdentifyFeature):
    """
        Class to select the track whose waypoint is to be set by user
    """

    def __init__(self, canvas, layer, parent):
        self.layer = layer
        self.canvas = canvas
        self.parent = parent
        self.track_num = None
        QgsMapToolIdentifyFeature.__init__(self, self.canvas, self.layer)

    def canvasPressEvent(self, event):
        found_features = self.identify(
            event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
        if found_features and self.parent.selected_track:
            row = self.parent.aircraft_info_table.findItems(
                str(self.parent.selected_track), Qt.MatchExactly)[0].row()
            self.parent.aircraft_info_table.item(
                row, 0).setBackground(COLOR_BLACK)

        for f in found_features:
            self.layer.startEditing()
            self.track_num = f.mFeature.attributes()[0]
            self.parent.selected_track = self.track_num

        if self.track_num:
            row = self.parent.aircraft_info_table.findItems(
                str(self.track_num), Qt.MatchExactly)[0].row()
            self.parent.aircraft_info_table.item(
                row, 0).setBackground(COLOR_BLUE)


class DeleteTool(QgsMapToolIdentifyFeature):

    def __init__(self, canvas, layer, parent):
        self.layer = layer
        self.canvas = canvas
        self.parent = parent
        QgsMapToolIdentifyFeature.__init__(self, self.canvas, self.layer)

    def canvasPressEvent(self, event):
        found_features = self.identify(
            event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
        for f in found_features:
            # delete by feature id
            self.layer.startEditing()
            self.layer.deleteFeature(f.mFeature.id())
            lat = float(f.mFeature.attributes()[0])
            lon = float(f.mFeature.attributes()[1])
            track_num = str(f.mFeature.attributes()[2])
            self.parent.point[track_num].remove([lat, lon])
            self.layer.commitChanges()
            self.layer.updateFields()
            self.canvas.refresh()
            self.canvas.repaint()


class MapCanvas(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Live Scenario Generator")
        self.setWindowIcon(QtGui.QIcon('.\Logos\Window Icon.png'))
        self.data = []

        self.play = False

        # Map layer
        self.map_layer = QgsVectorLayer(PATH_BORDER_SHP, "map layer")
        self.map_layer.renderer().symbol().setColor(COLOR_MAP_LAYER)

        # Main tracks layer
        self.tracks_layer = QgsVectorLayer(
            'Point?crs=epsg:4326&field=track_no:int&field=platform:string', 
            'tracks_layer', "memory")
        self.tracks_layer.renderer().symbol().setColor(COLOR_POINTS_LAYER)
        self.tracks_dp = self.tracks_layer.dataProvider()
        self.tracks_feat = QgsFeature()

        # Setting label for tracks layer
        track_label = QgsPalLayerSettings()
        track_label.fieldName = "platform"
        track_label.enabled = True
        track_label = QgsVectorLayerSimpleLabeling(track_label)
        self.tracks_layer.setLabelsEnabled(True)
        self.tracks_layer.setLabeling(track_label)

        # Layer that shows the waypoints added
        self.waypoints_layer = QgsVectorLayer(
            'Point?crs=epsg:4326&field=lat:float&field=long:float&field=track_no:int', 
            'waypoints_layer', "memory")
        layer_style = QgsStyle.defaultStyle().symbol('topo pop village')
        self.waypoints_layer.renderer().setSymbol(layer_style)
        self.waypoints_dp = self.waypoints_layer.dataProvider()
        self.waypoints_feat = QgsFeature()

        # Setting label for tracks layer
        track_label = QgsPalLayerSettings()
        track_label.fieldName = "track_no"
        track_label.enabled = True
        track_label = QgsVectorLayerSimpleLabeling(track_label)
        self.waypoints_layer.setLabelsEnabled(True)
        self.waypoints_layer.setLabeling(track_label)

        # Adding map canvas
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(COLOR_BLACK)

        # Setting canvas extent and adding layers to canvas
        self.canvas.setExtent(self.map_layer.extent())
        self.canvas.setLayers(
            [self.map_layer, self.tracks_layer, self.waypoints_layer])

        self.setCentralWidget(self.canvas)

        self.setStyleSheet("QTableWidget {Background-color: black;}"
                           "QTableWidget {color : white;}"
                           "QTableWidget::item {font: bold 22px;}"
                           "QHeaderView {color: black; font: bold 24px;}")

        # Setting up the table
        self.tracks_data = {}
        self.add_aircraft_info()

        # Time label
        time_font = QFont()
        time_font.setPointSize(16)
        self.time_label = QLabel("", self)
        self.time_label.setGeometry(3310, 10, 300, 50)
        self.time_label.setStyleSheet("color: white")
        self.time_label.setFont(time_font)

        # Play Button
        self.play_button = QPushButton("Play", self)
        self.play_button.setGeometry(0, 551, 275, 50)
        self.play_button.setCheckable(True)
        self.play_button.setStyleSheet(
            "border: 4px solid green; color: white; background: black")
        self.play_button.clicked.connect(self.begin)

        # Pause button
        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setGeometry(276, 551, 275, 50)
        self.pause_button.setCheckable(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setStyleSheet(
            "border: 4px solid orange; color: white; background: black")
        self.pause_button.clicked.connect(self.pause)

        # Add track button
        self.add_track_button = QPushButton("Add Track", self)
        self.add_track_button.setGeometry(551, 551, 275, 50)
        self.add_track_button.setEnabled(True)
        self.add_track_button.setStyleSheet(
            "border: 3px solid white; color: white; background: black")
        self.add_track_button.clicked.connect(self.add_track)

        # Delete track button
        self.delete_track_button = QPushButton("Delete Track", self)
        self.delete_track_button.setGeometry(826, 551, 275, 50)
        self.delete_track_button.setEnabled(True)
        self.delete_track_button.setStyleSheet(
            "border: 3px solid white; color: white; background: black")
        self.delete_track_button.clicked.connect(self.delete_track)

        # Select Track Button
        self.select_track_button = QPushButton("Select Track", self)
        self.select_track_button.setGeometry(0, 602, 367, 50)
        self.select_track_button.setCheckable(True)
        self.select_track_button.setEnabled(False)
        self.select_track_button.setStyleSheet(
            "border: 3px solid grey; color: white; background: black")
        self.select_track_button.clicked.connect(self.select_track)

        # Add waypoint button
        self.add_waypoint_button = QPushButton("Add Waypoint", self)
        self.add_waypoint_button.setGeometry(368, 602, 366, 50)
        self.add_waypoint_button.setCheckable(True)
        self.add_waypoint_button.setStyleSheet(
            "border: 3px solid blue; color: white; background: black")
        self.add_waypoint_button.clicked.connect(self.add_waypoint)
        self.point = {}
        self.selected_track = []
        self.overwrite = False

        # Delete waypoint button
        self.delete_waypoint_button = QPushButton("Delete Waypoint", self)
        self.delete_waypoint_button.setGeometry(735, 602, 366, 50)
        self.delete_waypoint_button.setCheckable(True)
        self.delete_waypoint_button.setStyleSheet(
            "border: 3px solid purple; color: white; background: black")
        self.delete_waypoint_button.clicked.connect(self.delete_waypoint)

        # Add formation button
        self.add_formation_buton = QPushButton("Add Formation", self)
        self.add_formation_buton.setGeometry(0, 652, 367, 50)
        self.add_formation_buton.setCheckable(True)
        self.add_formation_buton.setStyleSheet(
            "border: 3px solid pink; color: white; background: black")
        self.add_formation_buton.clicked.connect(self.add_formation)
        self.abs_aircraft_pos = {}

        # Save as file button
        self.save_file_button = QPushButton("Save File", self)
        self.save_file_button.setGeometry(3630, 10, 200, 50)
        self.save_file_button.setCheckable(True)
        self.save_file_button.setStyleSheet(
            "border: 4px solid yellow; color: white; background: black")
        self.save_file_button.clicked.connect(self.save_file)

        self.showMaximized()

    def save_file(self):
        file_name = QFileDialog.getSaveFileName(self, 'Save File', "", "Excel File (*.csv)")
        if self.data and file_name[0]:
            df = pd.DataFrame(columns= COL, data= self.data)
            file_to_save = df.sort_values(by='EpocTimeMilliSeconds', ascending=True)
            file_to_save.to_csv(file_name[0], index=False, float_format='%.5f')
        else:
            error_dialog = QErrorMessage()
            error_dialog.setWindowTitle("Error")
            error_dialog.showMessage("Nothing to Save!")
            error_dialog.exec_()

    def overWriteWaypoint(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Over-write Waypoint")
        dlg.setText("Do you want to overwrite the waypoints?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            self.overwrite = True
            """
                If we are overwriting the waypoints we want to save the current offsets of the tracks as their locations, since for now
                we are adding an offset at every instance to a central lat/long.
            """
            for track in self.selected_track:
                current_track = self.tracks_data[str(track)]
                if str(track) not in self.abs_aircraft_pos.keys():
                    self.abs_aircraft_pos[str(track)] = {'angle': 0, 'distance': 0} 
                if self.selected_track.index(track) == 0:
                    current_track['Lat'], current_track['Long'] = self.add_offset(str(track),
                                                                                  current_track['Lat'], 
                                                                                  current_track['Long'], 
                                                                                  current_track['Heading'])
                    # Saving the first track as the reference to calculate offsets of the other tracks from
                    ref_lat = deepcopy(current_track['Lat'])
                    ref_long = deepcopy(current_track['Long'])                  

                    self.abs_aircraft_pos[str(track)]["angle"] = 0
                    self.abs_aircraft_pos[str(track)]["distance"] = 0
                else:
                    current_track['Lat'], current_track['Long'] = self.add_offset(str(track),
                                                                                  current_track['Lat'], 
                                                                                  current_track['Long'], 
                                                                                  current_track['Heading'])
                    
                    self.abs_aircraft_pos[str(track)]["angle"] = int(Geodesic.WGS84.Inverse(current_track['Lat'], 
                                                                                            current_track['Long'],
                                                                                            ref_lat, ref_long)["azi1"])
                    self.abs_aircraft_pos[str(track)]["angle"] = (self.abs_aircraft_pos[str(track)]["angle"] + 360) \
                        if self.abs_aircraft_pos[str(track)]["angle"] < 0 else (self.abs_aircraft_pos[str(track)]["angle"])

                    self.abs_aircraft_pos[str(track)]["distance"] = geopy.distance.geodesic((current_track['Lat'], 
                                                                                             current_track['Long']),
                                                                                            (ref_lat, ref_long)).nautical
                    
        else:
            self.overwrite = False

    def custom_formation(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Custom or Pre-defined formation")
        dlg.setText("Do you want add predfined formation or custom formation?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Ok)
        buttonY = dlg.button(QMessageBox.Yes)
        buttonY.setText('Custom Formation')
        buttonN = dlg.button(QMessageBox.No)
        buttonN.setText('Predefined Formation')
        buttonO = dlg.button(QMessageBox.Ok)
        buttonO.setText('Random Offset')
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            formation = AddCustomFormation(self)
            formation.show()
        elif button == QMessageBox.No:
            formation = AddBuiltInFormation(self)
            formation.show()
        elif button == QMessageBox.Ok:
            self.add_random_offsets()          

    def add_aircraft_info(self):
        """
            Function to add table to window and fill it in
        """
        self.aircraft_info_table = QTableWidget(self)
        self.aircraft_info_table.setGeometry(0, 0, 1100, 550)
        self.aircraft_info_table.setColumnCount(8)
        self.aircraft_info_table.setColumnWidth(0, 130)
        self.aircraft_info_table.setColumnWidth(1, 120)
        self.aircraft_info_table.setColumnWidth(2, 155)
        self.aircraft_info_table.setColumnWidth(3, 145)
        self.aircraft_info_table.setColumnWidth(4, 150)
        self.aircraft_info_table.setColumnWidth(5, 115)
        self.aircraft_info_table.setColumnWidth(6, 110)
        self.aircraft_info_table.setColumnWidth(7, 110)
        self.aircraft_info_table.setHorizontalHeaderLabels(TABLE_HEADER)
        self.aircraft_info_table.horizontalHeaderItem(
            6).setBackground(COLOR_START)
        self.aircraft_info_table.horizontalHeaderItem(
            7).setBackground(COLOR_DROP)
        self.all_start = False
        self.all_drop = False
        self.track_numbers = []
        delegate = AlignDelegate(self.aircraft_info_table)
        self.aircraft_info_table.setItemDelegate(delegate)

        self.aircraft_info_table.itemChanged.connect(self.update_info)
        self.aircraft_info_table.doubleClicked.connect(self.start_drop_single_track)
        self.aircraft_info_table.horizontalHeader(
        ).sectionClicked.connect(self.start_drop_all_tracks)

        rowPos = self.aircraft_info_table.rowCount()
        self.aircraft_info_table.insertRow(rowPos)
        self.aircraft_info_table.blockSignals(True)
        self.add_row(rowPos)
        self.aircraft_info_table.blockSignals(False)

    def add_row(self, row, font_size=10):
        """
            Function to add row to table

        Args:
            table (_type_): _description_
            row (_type_): _description_
            column (_type_): _description_
            value (_type_): _description_
            font_size (int, optional): _description_. Defaults to 10.
        """
        font = QFont()
        font.setPointSize(font_size)

        # TRACK NUMBER
        num_rows = self.aircraft_info_table.rowCount()
        taken_ids = []
        for r in range(num_rows - 1):
            taken_ids.append(int(self.aircraft_info_table.item(r, 0).text()))

        total_id_range = range(1000, 9000)
        avail_ids = (num for num in total_id_range if num not in taken_ids)
        track_id = random.sample(list(avail_ids), 1)

        self.aircraft_info_table.setItem(
            row, 0, QTableWidgetItem(str(track_id[0])))
        self.aircraft_info_table.item(row, 0).setFont(font)
        self.tracks_data[str(track_id[0])] = {}

        self.track_numbers.append(str(track_id[0]))

        # BASE OF ORIGIN
        combo = QComboBox()
        combo.addItems(IAF_BASES.keys())
        combo.setStyleSheet("background-color: black; color: white;")
        combo.currentTextChanged.connect(
            lambda: self.update_info(item=[row, 1]))
        self.aircraft_info_table.setCellWidget(row, 1, combo)
        self.tracks_data[str(track_id[0])]['Origin'] = next(iter(IAF_BASES))
        self.tracks_data[str(track_id[0])]['Lat'], self.tracks_data[str(
            track_id[0])]['Long'] = IAF_BASES[self.tracks_data[str(track_id[0])]['Origin']]
        self.tracks_data[str(track_id[0])]['Heading'] = 0

        # SPEED
        self.aircraft_info_table.setItem(row, 2, QTableWidgetItem("350"))
        self.aircraft_info_table.item(row, 2).setFont(font)
        self.tracks_data[str(track_id[0])]['Speed'] = 350

        # HEIGHT
        self.aircraft_info_table.setItem(row, 3, QTableWidgetItem("10000"))
        self.aircraft_info_table.item(row, 3).setFont(font)
        self.tracks_data[str(track_id[0])]['Height'] = 10000

        # TRACK ID
        combo = QComboBox()
        combo.addItems(TRACK_ID.keys())
        combo.setStyleSheet("background-color: black; color: white;")
        combo.currentTextChanged.connect(
            lambda: self.update_info(item=[row, 4]))
        self.aircraft_info_table.setCellWidget(row, 4, combo)
        self.tracks_data[str(track_id[0])]['Track ID'] = next(iter(TRACK_ID))

        # PLATFORM
        combo = QComboBox()
        combo.addItems(PLATFORMS)
        combo.setStyleSheet("background-color: black; color: white;")
        combo.currentTextChanged.connect(
            lambda: self.update_info(item=[row, 5]))
        self.aircraft_info_table.setCellWidget(row, 5, combo)
        self.tracks_data[str(track_id[0])]['Platform'] = next(iter(PLATFORMS))

        # START BUTTON
        self.aircraft_info_table.setItem(row, 6, QTableWidgetItem("Start"))
        self.aircraft_info_table.item(row, 6).setFont(font)
        self.aircraft_info_table.item(row, 6).setFlags(QtCore.Qt.ItemIsEnabled)
        self.tracks_data[str(track_id[0])]['Start'] = False
        self.aircraft_info_table.item(row, 6).setBackground(COLOR_START)

        # DROP BUTTON
        self.aircraft_info_table.setItem(row, 7, QTableWidgetItem("Drop"))
        self.aircraft_info_table.item(row, 7).setFont(font)
        self.aircraft_info_table.item(row, 7).setFlags(QtCore.Qt.ItemIsEnabled)
        self.tracks_data[str(track_id[0])]['Drop'] = False
        self.aircraft_info_table.item(row, 7).setBackground(COLOR_DROP)

    def begin(self):
        """
            Function to toggle play flag to start execution after reading values from table or to reset everything
        """
        if self.play_button.isChecked():
            self.play = True
            self.pause_button.setEnabled(True)
            self.select_track_button.setEnabled(True)
            self.play_button.setText("Reset")
            self.play_button.setStyleSheet(
                "border: 3px solid red; color: white; background: black")
        else:
            self.play = False
            self.pause_button.setEnabled(False)
            self.select_track_button.setEnabled(False)
            self.play_button.setText("Play")
            self.play_button.setStyleSheet(
                "border: 3px solid green; color: white; background: black")
            
            # Resetting everything
            self.tracks_data = {}
            self.data = []
            self.aircraft_info_table.setRowCount(0)
            self.point = {}
            self.selected_track = []
            self.overwrite = False
            self.abs_aircraft_pos = {}
            self.aircraft_info_table.horizontalHeaderItem(
                6).setBackground(COLOR_START)
            self.aircraft_info_table.horizontalHeaderItem(
                7).setBackground(COLOR_DROP)
            self.all_start = False
            self.all_drop = False
            self.track_numbers = []
            self.waypoints_dp.truncate()
            self.tracks_dp.truncate()

    def pause(self):
        """
            Function to pause execution
        """
        if self.pause_button.isChecked():
            self.play = False
            self.play_button.setChecked(False)
            self.pause_button.setText("Resume")
            self.pause_button.setStyleSheet(
                "border: 3px solid yellow; color: white; background: black")
        else:
            self.play = True
            self.play_button.setChecked(True)
            self.pause_button.setText("Pause")
            self.pause_button.setStyleSheet(
                "border: 3px solid orange; color: white; background: black")

    def start_drop_single_track(self, item):
        if item.column() == 6:
            track_num = self.aircraft_info_table.item(item.row(), 0).text()
            if not self.tracks_data[track_num]['Start']:
                self.tracks_data[track_num]['Start'] = True
                self.aircraft_info_table.item(item.row(), 6).setText("Stop")
                self.aircraft_info_table.item(
                    item.row(), 6).setBackground(COLOR_RED)
            else:
                self.tracks_data[track_num]['Start'] = False
                self.aircraft_info_table.item(item.row(), 6).setText("Start")
                self.aircraft_info_table.item(
                    item.row(), 6).setBackground(COLOR_START)

        elif item.column() == 7:
            track_num = self.aircraft_info_table.item(item.row(), 0).text()
            if not self.tracks_data[track_num]['Drop']:
                self.tracks_data[track_num]['Drop'] = True
                self.aircraft_info_table.item(item.row(), 7).setText("Show")
                self.aircraft_info_table.item(
                    item.row(), 7).setBackground(COLOR_SHOW)
            else:
                self.tracks_data[track_num]['Drop'] = False
                self.aircraft_info_table.item(item.row(), 7).setText("Drop")
                self.aircraft_info_table.item(
                    item.row(), 7).setBackground(COLOR_DROP)

    def start_drop_all_tracks(self, index):
        if index == 6 and not self.all_start:
            self.all_start = True
            self.aircraft_info_table.horizontalHeaderItem(
                6).setText("Stop All")
            self.aircraft_info_table.horizontalHeaderItem(
                6).setBackground(COLOR_RED)
            for key, value in self.tracks_data.items():
                value['Start'] = True
                row = self.aircraft_info_table.findItems(
                    key, Qt.MatchExactly)[0].row()
                self.aircraft_info_table.item(row, 6).setText("Stop")
                self.aircraft_info_table.item(row, 6).setBackground(COLOR_RED)

        elif index == 6 and self.all_start:
            self.all_start = False
            self.aircraft_info_table.horizontalHeaderItem(
                6).setText("Start All")
            self.aircraft_info_table.horizontalHeaderItem(
                6).setBackground(COLOR_START)
            for key, value in self.tracks_data.items():
                value['Start'] = False
                row = self.aircraft_info_table.findItems(
                    key, Qt.MatchExactly)[0].row()
                self.aircraft_info_table.item(row, 6).setText("Start")
                self.aircraft_info_table.item(
                    row, 6).setBackground(COLOR_START)

        if index == 7 and not self.all_drop:
            self.all_drop = True
            self.aircraft_info_table.horizontalHeaderItem(
                7).setText("Show All")
            self.aircraft_info_table.horizontalHeaderItem(
                7).setBackground(COLOR_SHOW)
            for key, value in self.tracks_data.items():
                value['Drop'] = True
                row = self.aircraft_info_table.findItems(
                    key, Qt.MatchExactly)[0].row()
                self.aircraft_info_table.item(row, 7).setText("Show")
                self.aircraft_info_table.item(row, 7).setBackground(COLOR_SHOW)

        elif index == 7 and self.all_drop:
            self.all_drop = False
            self.aircraft_info_table.horizontalHeaderItem(
                7).setText("Drop All")
            self.aircraft_info_table.horizontalHeaderItem(
                7).setBackground(COLOR_DROP)
            for key, value in self.tracks_data.items():
                value['Drop'] = False
                row = self.aircraft_info_table.findItems(
                    key, Qt.MatchExactly)[0].row()
                self.aircraft_info_table.item(row, 7).setText("Drop")
                self.aircraft_info_table.item(row, 7).setBackground(COLOR_DROP)

    def add_track(self):
        def num_track_input():
            text, pressed = QInputDialog.getInt(
                self, "Number of Tracks", "Enter number of tracks to add:", 1, 1, 1000, 1)
            if pressed:
                return text
            else:
                return 0

        num_tracks = num_track_input()

        for i in range(num_tracks):
            rowPos = self.aircraft_info_table.rowCount()
            self.aircraft_info_table.insertRow(rowPos)

            self.aircraft_info_table.blockSignals(True)
            self.add_row(rowPos)
            self.aircraft_info_table.blockSignals(False)

    def delete_track(self):
        """
        Function to delete row from waypoints table
        """
        indices = self.aircraft_info_table.selectionModel().selectedRows()
        for index in indices:
            track_num = self.aircraft_info_table.item(index.row(), 0).text()
            self.tracks_data.pop(track_num)
            feature = [feature.id() if str(feature.attributes()[2]) == track_num else None
                       for feature in self.waypoints_layer.getFeatures()]
            feature = list(filter(None, feature))
            self.waypoints_layer.startEditing()
            self.waypoints_layer.deleteFeatures(feature)
            self.point.pop(
                track_num) if track_num in self.point.keys() else None
            self.aircraft_info_table.removeRow(index.row())
            self.track_numbers.remove(track_num)

    def add_waypoint(self):
        """
            Function to add the next waypoint for track 
        """
        if self.add_waypoint_button.isChecked() and self.select_track_button.isChecked():
            self.overWriteWaypoint()
            # If overwrite option has been opted for a selected track, delete all previous 
            # waypoitns for that track
            if self.overwrite and self.selected_track:
                for track in self.selected_track:
                    self.point[str(track)] = []
                    feature = [feature.id() if str(feature.attributes()[2]) == str(track) \
                               else None for feature in self.waypoints_layer.getFeatures()]
                    feature = list(filter(None, feature))
                    self.waypoints_layer.startEditing()
                    self.waypoints_layer.deleteFeatures(feature)
            self.add = PrintClickedPoint(
                self.canvas, self.waypoints_layer, self)
            self.canvas.setMapTool(self.add)
        else:
            self.canvas.unsetMapTool(self.add)

    def delete_waypoint(self):
        """
            Function to add the next waypoint for track 
        """
        if self.delete_waypoint_button.isChecked():
            self.delete = DeleteTool(self.canvas, self.waypoints_layer, self)
            self.canvas.setMapTool(self.delete)
        else:
            self.canvas.unsetMapTool(self.delete)

    def select_track(self):
        """
            Function to select which track is to be edited
        """
        def add_tracks_to_selection(rect):
            # First set previous selection to null
            for track in self.selected_track:
                row = self.aircraft_info_table.findItems(
                    str(track), Qt.MatchExactly)[0].row()
                self.aircraft_info_table.item(
                    row, 0).setBackground(COLOR_BLACK)

            # Get new selection
            self.select_multiple_tracks_tool.clearRubberBand()
            self.selected_track = [f.attributes(
            )[0] for f in self.tracks_layer.getFeatures() if f.geometry().intersects(rect)]
            for track in self.selected_track:
                row = self.aircraft_info_table.findItems(str(track), Qt.MatchExactly)[0].row()
                self.aircraft_info_table.blockSignals(True)
                self.aircraft_info_table.item(row, 0).setBackground(COLOR_BLUE)
                self.aircraft_info_table.blockSignals(False)
            self.canvas.unsetMapTool(self.select_multiple_tracks_tool)

        if self.select_track_button.isChecked():
            self.select_multiple_tracks_tool = QgsMapToolExtent(self.canvas)
            self.canvas.setMapTool(self.select_multiple_tracks_tool)
            self.select_multiple_tracks_tool.extentChanged.connect(
                add_tracks_to_selection)

        else:
            self.canvas.unsetMapTool(self.select_multiple_tracks_tool)
            for track in self.selected_track:
                row = self.aircraft_info_table.findItems(str(track), Qt.MatchExactly)[0].row()
                self.aircraft_info_table.blockSignals(True)
                self.aircraft_info_table.item(row, 0).setBackground(COLOR_BLACK)
                self.aircraft_info_table.blockSignals(False)
            self.selected_track = []

    def update_info(self, item):
        """
            This function updates the info the track    

        Args:
            item (list or int): If a dropdown menu has been updated, item contains a list containing the row and column
            number of the dropdown that was updated. Otherwise it contains the qtablewidget item which was changed.
        """
        if type(item) == list:
            track_num = self.aircraft_info_table.item(item[0], 0).text()
            # If base of origin was updated
            if item[1] == 1:
                self.tracks_data[track_num]['Origin'] = self.aircraft_info_table.cellWidget(
                    item[0], 1).currentText()
                self.tracks_data[track_num]['Lat'], self.tracks_data[track_num][
                    'Long'] = IAF_BASES[self.tracks_data[track_num]['Origin']]
            # If track ID was updated
            elif item[1] == 4:
                self.tracks_data[track_num]['Track ID'] = self.aircraft_info_table.cellWidget(
                    item[0], 4).currentText()
            # If platform type was updated
            elif item[1] == 5:
                self.tracks_data[track_num]['Platform'] = self.aircraft_info_table.cellWidget(
                    item[0], 5).currentText()
        else:
            track_num = self.track_numbers[item.row()]
            # If track number was updated
            if item.column() == 0:
                new_track_num = self.aircraft_info_table.item(item.row(), 0).text()
                self.tracks_data[new_track_num] = self.tracks_data[track_num]
                self.tracks_data.pop(track_num)
                self.track_numbers[item.row()] = new_track_num
            # If speed was updated
            elif item.column() == 2:
                self.tracks_data[track_num]['Speed'] = int(
                    self.aircraft_info_table.item(item.row(), 2).text())
            # If altitude was updated
            elif item.column() == 3:
                self.tracks_data[track_num]['Height'] = int(
                    self.aircraft_info_table.item(item.row(), 3).text())

    def add_formation(self):
        """
            This function is to add open window to add the custom formation for the aircrafts
        """
        self.custom_formation()

    def add_offset(self, track, lat, long, heading):
        """
            This function is to add offset to aircrafts if formation has been defined

        Args:
            track (int): track number
            lat (float): current latitude
            long (float): current longitude
            heading (int): current heading

        Returns:
            new_lat(float), new_long(float): new latitudes and longitudes of aircraft
        """
        ref = geopy.Point(lat, long)
        d = geopy.distance.distance(
            nautical=self.abs_aircraft_pos[str(track)]["distance"])
        new_lat = round(d.destination(point=ref, bearing=(
            self.abs_aircraft_pos[track]["angle"] + heading)).latitude, 5)
        new_long = round(d.destination(point=ref, bearing=(
            self.abs_aircraft_pos[track]["angle"] + heading)).longitude, 5)
        return new_lat, new_long

    def add_random_offsets(self):
        """
            Funciton to add random offsets for greater than 1 aircraft in group
        """
        for track in self.selected_track:
                self.abs_aircraft_pos[str(track)] = {}
                self.abs_aircraft_pos[str(track)]["distance"] = random.random()
                self.abs_aircraft_pos[str(track)]["angle"] = random.randint(0, 360)

    def create_tracks(self):
        """
            Main funciton which plots all the tracks
        """
        epoch_time = get_current_time()
        self.time_label.setText(datetime.fromtimestamp(
            epoch_time).strftime("%d.%m.%Y  %H:%M:%S"))
        while True:
            # If play button is pressed
            if self.play:
                # Add delay for playback purposes and then dispaly current time
                QtTest.QTest.qWait(DELAY_TIME)
                epoch_time = get_current_time()
                self.time_label.setText(datetime.fromtimestamp(
                    epoch_time).strftime("%d.%m.%Y  %H:%M:%S"))

                # Delete previous tarcks
                features = [feature.id()
                            for feature in self.tracks_layer.getFeatures()]
                self.tracks_layer.startEditing()
                self.tracks_layer.deleteFeatures(features)
                self.tracks_layer.reload()
                self.tracks_layer.triggerRepaint()

                for key, value in self.tracks_data.items():
                    # If the track has been started
                    if value and 'Start' in value.keys() and value['Start']:
                        new_lat = value['Lat']
                        new_long = value['Long']
                        new_lat, new_long = self.add_offset(
                            key, value['Lat'], value['Long'], value['Heading']) if key in \
                                self.abs_aircraft_pos else (new_lat, new_long)

                        if not value['Drop']:
                            # Plot track points on map canvas
                            add_point(self.tracks_layer, self.tracks_dp, self.tracks_feat, 
                                      new_lat, new_long, [key, value['Platform']])

                            # Data for sending
                            print(key, value['Platform'], new_lat, new_long, 
                                  TRACK_ID[value['Track ID']], value['Speed'], value['Height'], value['Heading'], epoch_time)
                            
                            # Adding to save to file
                            self.data.append([str(1)] * 40)
                            self.data[-1][SYS_TRACK_NO] = key
                            self.data[-1][PLATFORM] = value['Platform']
                            self.data[-1][LATITUDE] = new_lat
                            self.data[-1][LONGITUDE] = new_long
                            self.data[-1][TRACK_ID_COLUMN] = TRACK_ID[value['Track ID']]
                            self.data[-1][SPEED] = value['Speed']
                            self.data[-1][HEADING] = value['Heading']
                            self.data[-1][ALTITUDE] = value['Height']
                            self.data[-1][TIME] = epoch_time

                        # Find next lat/long of track, if waypoint has been added find next point in that direction
                        if key in self.point.keys() and self.point[key]:
                            # Finding heading between current lat/long and next waypoint
                            value['Heading'] = int(Geodesic.WGS84.Inverse(
                                value['Lat'], value['Long'], self.point[key][0][0], self.point[key][0][1])["azi1"])

                            # Finding distance traveled in 1 second
                            distance = value['Speed'] / 3600

                            # Finding the next lat/long of track
                            d = geopy.distance.distance(nautical=distance)
                            next_point = d.destination(geopy.Point(
                                value['Lat'], value['Long']), value['Heading'])
                            value['Lat'] = round(next_point.latitude, 5)
                            value['Long'] = round(next_point.longitude, 5)

                            # Calculating distance between current lat/long and waypoint
                            distance_to_waypoint = geopy.distance.geodesic((value['Lat'], value['Long']),
                                                                           (self.point[key][0][0], 
                                                                            self.point[key][0][1])).nautical
                            # If distance is less than 0.1 nautical mile remove waypoint
                            if distance_to_waypoint < 0.1:
                                features = [feature.id() if str(feature.attributes()[0]) == str(self.point[key][0][0])
                                            and str(feature.attributes()[1]) == str(self.point[key][0][1]) else None
                                            for feature in self.waypoints_layer.getFeatures()]
                                features = list(filter(None, features))
                                self.waypoints_layer.startEditing()
                                self.waypoints_layer.deleteFeatures(features)
                                self.point[key].pop(0)

                        # If no waypoint has been added, find next direction either due north or in the direction of 
                        # last waypoint
                        else:
                            distance = value['Speed'] / 3600
                            d = geopy.distance.distance(nautical=distance)
                            next_point = d.destination(geopy.Point(
                                value['Lat'], value['Long']), value['Heading'])
                            value['Lat'] = round(next_point.latitude, 5)
                            value['Long'] = round(next_point.longitude, 5)

                        # Data for sending
                        value['Heading'] = (
                            value['Heading'] + 360) if value['Heading'] < 0 else (value['Heading'])


map_canvas = MapCanvas()
map_canvas.show()

plot_thread = Thread(target=map_canvas.create_tracks)
plot_thread.start()

if __name__ == "__main__":
    window()
qgs_app.exitQgs()
