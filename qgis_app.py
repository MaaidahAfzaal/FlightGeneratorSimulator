import sys
sys.path.append('D:\\ScenarioGenratorQGIS\\')
import pandas as pd
import numpy as np
import math
import os
import random
from copy import deepcopy
import json
from pyproj import Transformer


from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt5 import QtTest
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import*


from main_page import Ui_MainPage
from config_parameters import *
from file_generation_latlong import get_data, get_current_time
from Dijkstra import*
from qtwindow import Dialog_01

app = QgsApplication([], True)
app.setPrefixPath("C:/OSGeo4W64/apps/qgis-dev", True)
app.initQgis()

# Required for using Qgs class
d = QgsDistanceArea()
d.setEllipsoid('WGS84')
M_to_Nm = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceNauticalMiles, QgsUnitTypes.DistanceMeters)

group_data = []
QGIS_PATH = 'D:\\ScenarioGenratorQGIS\\'

trans_GPS_to_XYZ = Transformer.from_crs(4979, 4978)

################################################################################
############################## MAIN PAGE WINDOW ################################
################################################################################

class Window(QMainWindow, Ui_MainPage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.scenarios.setStyleSheet('font-size: 12')

        # Attaching functions to buttons
        self.add_groups.clicked.connect(self.add_group_info)
        self.begin.clicked.connect(lambda: self.begin_exec(flag=False))
        self.edit.clicked.connect(self.load_scenario)
        self.update.clicked.connect(lambda: self.begin_exec(flag=True))
        self.play.clicked.connect(self.play_scenario)
        self.random_data.clicked.connect(self.open_random_exe)


        # Loading json file that contains all poreviously saved scenarios
        with open(QGIS_PATH + 'Track Files\\Scenarios.json') as json_file:
            loaded_data = json.load(json_file)

        # Saving all thsoe scenarios in a global variable to access from anywhere
        global generated_scenarios
        generated_scenarios = loaded_data
        last_scen = list(generated_scenarios.keys())[-1]
        last_scen = last_scen.split()
        self.num_scenario = int(last_scen[-1])
        _translate = QtCore.QCoreApplication.translate

        for key in generated_scenarios.keys():
            # i = int(key.split())
            self.scenarios.addItem(key)
            # self.scenarios.setItemText(-1, _translate("MainWindow", key)
        # last_scen = list(generated_scenarios.keys())[-1]
        # last_scen = last_scen.split()
        # self.num_scenario = int(last_scen[-1])
        
        # # Adding all previous scenarios to dropdown to be edited
        # for i in range(1, self.num_scenario+1):
        #     self.scenarios.addItem("")
        #     _translate = QtCore.QCoreApplication.translate
        #     self.scenarios.setItemText(i - 1, _translate("MainWindow", "Scenario "+str(i)+""))
        
    
    
    def closeEvent(self, event):
        """
            On closing the window all new scenarios are added to json file and 
            updated scenarios are changed

        Args:
            event (_type_): Triggered on closing of window
        """
        with open(QGIS_PATH + 'Track Files\\Scenarios.json', 'r') as outfile:
            json_data = json.load(outfile)

        json_data.update(generated_scenarios)

        with open(QGIS_PATH + 'Track Files\\Scenarios.json', 'w') as outfile:
            json.dump(json_data, outfile, indent=2)


    def add_group_info(self):
        """
            Function to open windows for entering data equal to the number of groups
        """
        _translate = QtCore.QCoreApplication.translate
        self.file_success.setText(_translate("MainWindow", ""))
        try:
            groups = int(self.groups.displayText())
            for i in range(groups):
                dialog = AddGroup(i, self)
                dialog.show()
        except:
          group_error_dialog(self)
    
    def open_random_exe(self):
        # x = QtWidgets.QApplication(['Test'])
        dialog_1 = Dialog_01(self)
        dialog_1.show()
        # x.exec_()

    def save_data(self, df):
        """
            Function to save data of each group

        Args:
            df (dictionary): data of each group
        """
        group_data.append(df)


    def load_scenario(self):
        """
            Function to load the scenario that has been selected to be edited
        """
        group_data.clear()
        
        _translate = QtCore.QCoreApplication.translate
        self.file_success.setText(_translate("MainWindow", ""))
        # Reading which scenario has been selected to be edited
        scen = self.scenarios.currentText()
        # Finding number of groups in selected scenario
        groups = len(generated_scenarios[scen])
        # Iterating over each group
        for i in range(groups):
            # Opening window containing all the group info
            dialog = AddGroup(i, self)
            dialog.show()
            # Loading commercial flight data
            if generated_scenarios[scen][i]["Platform"]["1"] == "Airliner":
                time_key = "End Time"
                # Getting the takeoff and destination locations
                takeoff_lat = generated_scenarios[scen][i]["Waypoints"]["Latitude"][0]
                takeoff_lon = generated_scenarios[scen][i]["Waypoints"]["Longitude"][0]
                destination_lat = generated_scenarios[scen][i]["Waypoints"]["Latitude"][-1]
                destination_lon = generated_scenarios[scen][i]["Waypoints"]["Longitude"][-1]
                # takeoff_point = list(IAF_BASES.keys())[list(IAF_BASES.values()).index([takeoff_lat, takeoff_lon])]
                # destination_point = list(IAF_BASES.keys())[list(IAF_BASES.values()).index([destination_lat, destination_lon])]
                # Filling in all entries of group 
                _translate = QtCore.QCoreApplication.translate
                # If end time ahs been entered previosuly by user
                if time_key in generated_scenarios[scen][i].keys():
                    dialog.end_time_airliner.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["End Time"])))

                # dialog.takeoff.setCurrentText(_translate("MainWindow", takeoff_point))
                # dialog.destination.setCurrentText(_translate("MainWindow", destination_point))
                dialog.initial_time_airliner.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Initial Time"])))
                dialog.cruising_speed.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Initial Speed"])))
                dialog.cruising_altitude.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Waypoints"]["Altitude"][0])))

                # If specific date has been entered by user
                if "Date" in generated_scenarios[scen][i].keys():
                    dialog.dateEdit_airliner.setDate(QtCore.QDate.fromString(generated_scenarios[scen][i]["Date"], 'dd-MM-yyyy'))
                else:
                    dialog.dateEdit_airliner.setDate(QtCore.QDate.currentDate())
                
                if "Track ID" in generated_scenarios[scen][i]:
                        dialog.trackId_airliner.setCurrentText(_translate("MainWindow", generated_scenarios[scen][i]["Track ID"][str(j+1)]))

                
                # Entering values of Modes C, S and 3
                if (generated_scenarios[scen][i]["Mode Info"]["Mode C Height"]["1"] != "-1"):
                    dialog.mode_c_radio.setChecked(True)
                    dialog.mode_c_value.setText = (_translate("MainWindow", str(generated_scenarios[scen][i]["Mode Info"]["Mode C Height"]["1"])))
                    
                if (generated_scenarios[scen][i]["Mode Info"]["Mode S"]["1"] != "-1"):
                    dialog.mode_s_radio.setChecked(True)
                    dialog.mode_s_value.setText = (_translate("MainWindow", str(generated_scenarios[scen][i]["Mode Info"]["Mode S"]["1"])))

                if (generated_scenarios[scen][i]["Mode Info"]["IFF Mode 3"]["1"] != "-1"):
                    dialog.mode_3_radio.setChecked(True)
                    dialog.mode_3_value.setText = (_translate("MainWindow", str(generated_scenarios[scen][i]["Mode Info"]["IFF Mode 3"]["1"])))

                
                font = QtGui.QFont()
                font.setPointSize(10)

                for k in range(len(generated_scenarios[scen][i]["Waypoints"]["Latitude"])):
                    # Getting name of ATS point
                    stopover_lat = generated_scenarios[scen][i]["Waypoints"]["Latitude"][k]
                    stopover_lon = generated_scenarios[scen][i]["Waypoints"]["Longitude"][k]
                    # stopover_point = list(IAF_BASES.keys())[list(IAF_BASES.values()).index([stopover_lat, stopover_lon])]

                    rowPos = dialog.path_table.rowCount()
                    if k > 0: 
                        dialog.path_table.insertRow(rowPos)
                    # Adding ats route points to path table
                    # dialog.path_table.setItem(k, 0, QTableWidgetItem(stopover_point))
                    # stopover = dialog.path_table.item(k, 0)
                    # stopover.setTextAlignment(QtCore.Qt.AlignCenter)
                    # stopover.setFont(font)

            # Loading fighter data
            else:
                # unique = generated_scenarios[scen][i]["Platform"]
                time_key = "End Time"
                # Filling in all entries of group 
                _translate = QtCore.QCoreApplication.translate
                if time_key in generated_scenarios[scen][i].keys():
                    dialog.end_time.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["End Time"])))
                dialog.aircrafts.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Aircrafts"])))
                dialog.origin_base.setCurrentText(_translate("MainWindow", generated_scenarios[scen][i]["Origin"]))
                dialog.initial_time.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Initial Time"])))
                dialog.initial_speed.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Initial Speed"])))

                if "Date" in generated_scenarios[scen][i].keys():
                    dialog.dateEdit.setDate(QtCore.QDate.fromString(generated_scenarios[scen][i]["Date"], 'dd-MM-yyyy'))
                else:
                    dialog.dateEdit.setDate(QtCore.QDate.currentDate())

                if generated_scenarios[scen][i]["Aircrafts"] > 1:
                    dialog.add_formation_btn.setEnabled(True)

                if "Aircrafts Pos" in generated_scenarios[scen][i]:
                    dialog.aircraft_pos = generated_scenarios[scen][i]["Aircrafts Pos"]

                font = QtGui.QFont()
                font.setPointSize(10)

                for k in range(len(generated_scenarios[scen][i]["Waypoints"]["Latitude"])):
                    rowPos = dialog.table.rowCount()
                    if k > 0: 
                        dialog.table.insertRow(rowPos)
                    # Setting default value of time column
                    dialog.table.setItem(k, 0, QTableWidgetItem(str(float(np.round(generated_scenarios[scen][i]["Waypoints"]["Latitude"][k], 5)))))
                    time = dialog.table.item(k, 0)
                    time.setTextAlignment(QtCore.Qt.AlignCenter)
                    time.setFont(font)

                    # Setting default value of heading column
                    dialog.table.setItem(k, 1, QTableWidgetItem(str(float(np.round(generated_scenarios[scen][i]["Waypoints"]["Longitude"][k], 5)))))
                    heading = dialog.table.item(k, 1)
                    heading.setTextAlignment(QtCore.Qt.AlignCenter)
                    heading.setFont(font)

                    # Setting default value of speed column
                    dialog.table.setItem(k, 2, QTableWidgetItem(str(int(generated_scenarios[scen][i]["Waypoints"]["Speed"][k]))))
                    heading = dialog.table.item(k, 2)
                    heading.setTextAlignment(QtCore.Qt.AlignCenter)
                    heading.setFont(font)

                    # Setting default value of altitude column
                    dialog.table.setItem(k, 3, QTableWidgetItem(str(int(generated_scenarios[scen][i]["Waypoints"]["Altitude"][k]))))
                    heading = dialog.table.item(k, 3)
                    heading.setTextAlignment(QtCore.Qt.AlignCenter)
                    heading.setFont(font)

                # dialog.mode_table.setRowCount(0)
                for j in range(0, generated_scenarios[scen][i]["Aircrafts"]):
                    rowPos = dialog.mode_table.rowCount()
                    if j > 0: 
                        dialog.mode_table.insertRow(rowPos)

                    # Setting default value of track no column
                    if "Sys Track No" in generated_scenarios[scen][i]:
                        dialog.mode_table.setItem(j, 0, QTableWidgetItem(generated_scenarios[scen][i]["Sys Track No"][str(j+1)]))
                    else:
                        dialog.mode_table.setItem(j, 0, QTableWidgetItem(str(-1)))
                    mode1 = dialog.mode_table.item(j, 0)
                    mode1.setTextAlignment(QtCore.Qt.AlignCenter)
                    mode1.setFont(font)

                    # Settting value of track ID column
                    combo = ComboPlatforms(dialog)
                    dialog.mode_table.setCellWidget(j, 1, combo)
                    combo.addItems(TRACK_ID.keys())
                    if "Track ID" in generated_scenarios[scen][i]:
                        combo.setCurrentText(_translate("MainWindow", generated_scenarios[scen][i]["Track ID"][str(j+1)]))

                    # Adding combo box to platforms column
                    combo = ComboPlatforms(dialog)
                    dialog.mode_table.setCellWidget(j, 2, combo)
                    combo.addItems(PLATFORMS)
                    combo.setCurrentText(_translate("MainWindow", generated_scenarios[scen][i]["Platform"][str(j+1)]))


                    # Setting default value of Mode1 column
                    dialog.mode_table.setItem(j, 3, QTableWidgetItem(str(generated_scenarios[scen][i]["Mode Info"]["IFF Mode 1"][str(j+1)])))
                    mode1 = dialog.mode_table.item(j, 3)
                    mode1.setTextAlignment(QtCore.Qt.AlignCenter)
                    mode1.setFont(font)

                    # Setting default value of Mode2 column
                    dialog.mode_table.setItem(j, 4, QTableWidgetItem(str(generated_scenarios[scen][i]["Mode Info"]["IFF Mode 2"][str(j+1)])))
                    mode2 = dialog.mode_table.item(j, 4)
                    mode2.setTextAlignment(QtCore.Qt.AlignCenter)
                    mode2.setFont(font)

                    # Setting default value of Mode3 column
                    dialog.mode_table.setItem(j, 5, QTableWidgetItem(str(generated_scenarios[scen][i]["Mode Info"]["IFF Mode 3"][str(j+1)])))
                    mode3 = dialog.mode_table.item(j, 5)
                    mode3.setTextAlignment(QtCore.Qt.AlignCenter)
                    mode3.setFont(font)

                    # Setting default value of Mode6 column
                    dialog.mode_table.setItem(j, 6, QTableWidgetItem(str(generated_scenarios[scen][i]["Mode Info"]["IFF Mode 6"][str(j+1)])))
                    mode4 = dialog.mode_table.item(j, 6)
                    mode4.setTextAlignment(QtCore.Qt.AlignCenter)
                    mode4.setFont(font)

                    # Setting default value of Call sign column
                    dialog.mode_table.setItem(j, 7, QTableWidgetItem(str(generated_scenarios[scen][i]["Mode Info"]["Call Sign"][str(j+1)])))
                    mode5 = dialog.mode_table.item(j, 7)
                    mode5.setTextAlignment(QtCore.Qt.AlignCenter)
                    mode5.setFont(font)

                    # Setting default value of ICAO type column
                    dialog.mode_table.setItem(j, 8, QTableWidgetItem(str(generated_scenarios[scen][i]["Mode Info"]["ICAO Type"][str(j+1)])))
                    mode6 = dialog.mode_table.item(j, 8)
                    mode6.setTextAlignment(QtCore.Qt.AlignCenter)
                    mode6.setFont(font)

                    # Setting default value of ModeS column
                    dialog.mode_table.setItem(j, 9, QTableWidgetItem(str(generated_scenarios[scen][i]["Mode Info"]["Mode S"][str(j+1)])))
                    mode7 = dialog.mode_table.item(j, 9)
                    mode7.setTextAlignment(QtCore.Qt.AlignCenter)
                    mode7.setFont(font)

                    # Setting default value of ModeC column
                    dialog.mode_table.setItem(j, 10, QTableWidgetItem(str(generated_scenarios[scen][i]["Mode Info"]["Mode C Height"][str(j+1)])))
                    modec = dialog.mode_table.item(j, 10)
                    modec.setTextAlignment(QtCore.Qt.AlignCenter)
                    modec.setFont(font)



    def begin_exec(self, flag):
        """
           Main function that converts data to excel format

        Args:
            flag (bool): flag highlighting if scenario is new or old one is being
            updated
        """
        t1 = get_current_time()

        # For no change in file no update is made
        if(len(group_data) == 0):
            _translate = QtCore.QCoreApplication.translate
            self.file_success.setText(_translate("MainWindow", "File Already Exists!"))
        else:
            # If scenario is being edited
            if(flag):
                scen = self.scenarios.currentText()
                generated_scenarios[scen] = deepcopy(group_data)

            # If new scenario is being created
            else:
                self.num_scenario += 1
                generated_scenarios["Scenario "+str(self.num_scenario)+""] = deepcopy(group_data)


            # Finding the total number of aircrafts
            total_aircrafts = 0
            for key in group_data:
                total_aircrafts += int(key["Aircrafts"])
            
            # Checking which tracks don't contain track numbers
            i = 0
            taken_ids = []
            for key in range(len(group_data)):
                for a in group_data[key]["Sys Track No"]:
                    if group_data[key]["Sys Track No"][a] == "-1":
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
                    if group_data[key]["Sys Track No"][a] == "-1":
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

            # converting lat/longs to cartesian 
            data_cart = deepcopy(data_final)
            for x in data_cart:
                cart_coord = trans_GPS_to_XYZ.transform(x[LATITUDE], x[LONGITUDE], x[ALTITUDE] * 1000)
                x[LATITUDE] = np.round(cart_coord[0], 2)
                x[LONGITUDE] = np.round(cart_coord[1], 2)
                x[ALTITUDE] = np.round(cart_coord[2], 2)

            # Converting data to dataframe
            df = pd.DataFrame(columns= COL, data= data_final)
            sorted_df = df.sort_values(by='EpocTimeMilliSeconds', ascending=True)

            # Converting cartesian data to dataframe
            df_cart = pd.DataFrame(columns= COL_CARTESIAN, data= data_cart)
            sorted_df_cart = df_cart.sort_values(by='EpocTimeMilliSeconds', ascending=True)
            
            t2 = get_current_time()
            print("Time taken for processing : ", (t2-t1))

            if(flag):
                scen = self.scenarios.currentText()

                # If file already exists remove it
                if (os.path.exists(QGIS_PATH + 'Track Files\\'+scen+'.csv') and os.path.isfile(QGIS_PATH + 'Track Files\\'+scen+'.csv')):
                    os.remove(QGIS_PATH + 'Track Files\\'+scen+'.csv')
                # Write data to file
                sorted_df.to_csv(QGIS_PATH + 'Track Files\\'+scen+'.csv', index=False, float_format='%.15f')


                # Same for cartesian data
                if (os.path.exists(QGIS_PATH + 'Track Files\\'+scen+' (Cartesian).csv') and os.path.isfile(QGIS_PATH + 'Track Files\\'+scen+' (Cartesian).csv')):
                    os.remove(QGIS_PATH + 'Track Files\\'+scen+' (Cartesian).csv')
                sorted_df_cart.to_csv(QGIS_PATH + 'Track Files\\'+scen+' (Cartesian).csv', index=False, float_format='%.15f')

                _translate = QtCore.QCoreApplication.translate
                self.file_success.setText(_translate("MainWindow", "File Updated Successfully!"))
            else:
                # If file already exists remove it
                if (os.path.exists(QGIS_PATH + 'Track Files\\Scenario ' + str(self.num_scenario) + '.csv') and os.path.isfile(QGIS_PATH + 'Track Files\\Scenario '+str(self.num_scenario)+'.csv')):
                    os.remove(QGIS_PATH + 'Track Files\\Scenario '+str(self.num_scenario)+'.csv')
                sorted_df.to_csv(QGIS_PATH + 'Track Files\\Scenario '+str(self.num_scenario)+'.csv', index=False, float_format='%.15f')

                # Same for cartesian data
                if (os.path.exists(QGIS_PATH + 'Track Files\\Scenario ' + str(self.num_scenario) + ' (Cartesian).csv') and os.path.isfile(QGIS_PATH + 'Track Files\\Scenario '+str(self.num_scenario)+' (Cartesian).csv')):
                    os.remove(QGIS_PATH + 'Track Files\\Scenario '+str(self.num_scenario)+' (Cartesian).csv')
                sorted_df_cart.to_csv(QGIS_PATH + 'Track Files\\Scenario '+str(self.num_scenario)+' (Cartesian).csv', index=False, float_format='%.15f')

                # Displaying message on successful file saving
                _translate = QtCore.QCoreApplication.translate
                self.scenarios.addItem("Scenario "+str(self.num_scenario)+"")
                self.file_success.setText(_translate("MainWindow", "File Saved Successfully!"))
                # self.scenarios.setItemText(self.num_scenario - 1, _translate("MainWindow", "Scenario "+str(self.num_scenario)+""))
        
            t3 = get_current_time()
            print("Time taken for writing to csv : ", (t3-t2)) 
            group_data.clear()
        
    def play_scenario(self):
        scen = self.scenarios.currentText()
        map_animation = MapCanvas(parent=self, play= True, scenario= scen)
#        map_animation.show()



################################################################################
####################### WINDOW TO ENTER GROUP INFO #############################
################################################################################

class AddGroup(QMainWindow):

    def __init__(self, num, parent=None):
        super().__init__(parent=parent)
        loadUi(QGIS_PATH + "ui\\group_info_gui_tabs_modes_platforms.ui", self)
        self.setup_tables()
        self.num = num
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Group "+str(self.num + 1)+""))
        self.save_btn.setStyleSheet("background-color: #266d19; color: white")
        self.setWindowIcon(QIcon(QGIS_PATH + 'Logos\\Group.ico'))
        self.dateEdit.setDate(QtCore.QDate.currentDate())
        self.dateEdit_airliner.setDate(QtCore.QDate.currentDate())
        # Setting mode radio buttons in airliner tab to unchecked
        self.mode_s_value.setEnabled(False)
        self.mode_c_value.setEnabled(False)
        self.mode_3_value.setEnabled(False)
        # Setting add formation button to disabled (enabled if aircrafts > 1)
        self.add_formation_btn.setEnabled(False)
        self.aircraft_pos = {}
        self.aircraft_locations = {}
        self.ref = [0, 0]

        # Attaching actions to buttons
        self.add_waypoint_btn.clicked.connect(self.add_waypoints)
        self.delete_row_btn.clicked.connect(self.delete_row)
        self.save_btn.clicked.connect(self.save)
        self.add_mode_info_btn.clicked.connect(self.edit_mode_table)
        self.add_path_btn.clicked.connect(self.add_path)
        self.mode_s_radio.toggled.connect(self.activate_btn_mode_s)
        self.mode_c_radio.toggled.connect(self.activate_btn_mode_c)
        self.mode_3_radio.toggled.connect(self.activate_btn_mode_3)
        self.add_above_btn.clicked.connect(self.add_above)
        self.add_below_btn.clicked.connect(self.add_below)
        self.add_formation_btn.clicked.connect(self.add_formation)
        self.formations.currentTextChanged.connect(self.add_aircrafts)

    def add_above(self):
        """
            Function to add stop over point to path generated above the selected
            stop
        """
        indices = self.path_table.selectionModel().selectedRows()
        path_to_add = self.add_path_combo.currentText()
        _translate = QtCore.QCoreApplication.translate
        
        self.path_table.insertRow(indices[0].row())

        font = QtGui.QFont()
        font.setPointSize(10)

        self.path_table.setItem(indices[0].row(), 0, QTableWidgetItem(path_to_add))
        path_item = self.path_table.item(indices[0].row(), 0)
        path_item.setTextAlignment(QtCore.Qt.AlignCenter)
        path_item.setFont(font)

    def add_below(self):
        """
            Function to add stop over point to path generated below the selected
            stop
        """
        indices = self.path_table.selectionModel().selectedRows()
        path_to_add = self.add_path_combo.currentText()
        _translate = QtCore.QCoreApplication.translate
        
        self.path_table.insertRow(indices[0].row()+1)

        font = QtGui.QFont()
        font.setPointSize(10)

        self.path_table.setItem(indices[0].row()+1, 0, QTableWidgetItem(path_to_add))
        path_item = self.path_table.item(indices[0].row()+1, 0)
        path_item.setTextAlignment(QtCore.Qt.AlignCenter)
        path_item.setFont(font)
        
    # Functions to activate Mode S, C and 3 radio buttons and make text editable
    def activate_btn_mode_s(self):
        if self.mode_s_radio.isChecked() == True:
            self.mode_s_value.setEnabled(True)
        else:
            self.mode_s_value.setEnabled(False)

    def activate_btn_mode_c(self):
        if self.mode_c_radio.isChecked() == True:
            self.mode_c_value.setEnabled(True)
        else:
            self.mode_c_value.setEnabled(False)

    def activate_btn_mode_3(self):
        if self.mode_3_radio.isChecked() == True:
            self.mode_3_value.setEnabled(True)
        else:
            self.mode_3_value.setEnabled(False)

    def setup_tables(self):
        """
            Function to setup tables
        """
        for i in range(11):
            self.mode_table.setColumnWidth(i, 166)
        self.mode_table.setColumnWidth(0, 220)
        self.mode_table.setColumnWidth(1, 230)
        self.mode_table.setColumnWidth(2, 230)
        self.mode_table.setColumnWidth(10, 230)

        for i in range(4):
            self.table.setColumnWidth(i, 230)
        self.path_table.setColumnWidth(0, 220)

        # Adding bases
        # self.origin_base.addItems(IAF_BASES.keys())
        self.origin_base.addItem("Unknown")
        # Adding formations
        self.formations.addItems(FORMATIONS.keys())
        # Adding track IDs of airliner
        self.trackId_airliner.addItems(TRACK_ID.keys())
        self.trackId_airliner.setCurrentText("NOT SPECIFIED (UPG)")
        # Adding takeoff, destination and 'add path' in airliner tab
        self.takeoff.addItems(GRAPH.keys())
        self.destination.addItems(GRAPH.keys())
        self.add_path_combo.addItems(GRAPH.keys())

        # Setting values of trackIds and platform types in fighter tab table
        combo = ComboPlatforms(self)
        self.mode_table.setCellWidget(0, 1, combo)
        combo.addItems(TRACK_ID.keys())

        combo = ComboPlatforms(self)
        self.mode_table.setCellWidget(0, 2, combo)
        combo.addItems(PLATFORMS)

    def add_aircrafts(self):
        formation = self.formations.currentText()
        aircrafts = len(FORMATIONS[formation])
        self.aircrafts.setText(str(aircrafts))
        self.aircraft_pos = FORMATIONS[formation]

    def add_path(self):
        """
            Function to find the shortest ATS route from the selected takeoff and 
            destination point and then add that route to the path table in Airliner
            tab
        """
        self.path_table.setRowCount(0)
        takeoff = self.takeoff.currentText()
        destination = self.destination.currentText()
        # Dijkstra algorithm is  used to find shortest path from takeoff to destination
        path = get_shortest_path(init_graph=GRAPH, nodes= list(GRAPH.keys()), start_node= takeoff, target_node= destination)

        _translate = QtCore.QCoreApplication.translate
        
        for k in range(len(path)):
            rowPos = self.path_table.rowCount()
            self.path_table.insertRow(rowPos)

            font = QtGui.QFont()
            font.setPointSize(10)

            self.path_table.setItem(k, 0, QTableWidgetItem(path[k]))
            path_item = self.path_table.item(k, 0)
            path_item.setTextAlignment(QtCore.Qt.AlignCenter)
            path_item.setFont(font)

    def edit_mode_table(self):
        """
            Function to set default values of the modes table in fighter tab 
        """
        try:
            aircrafts = int(self.aircrafts.displayText())
            if aircrafts > 1:
                self.add_formation_btn.setEnabled(True)
            font = QtGui.QFont()
            font.setPointSize(10)
            self.mode_table.setRowCount(0)

            for k in range(0, aircrafts):
                rowPos = self.mode_table.rowCount()
                self.mode_table.insertRow(rowPos)

                # Setting default value of system track no. column
                self.mode_table.setItem(k, 0, QTableWidgetItem("-1"))
                sys_track_no = self.mode_table.item(k, 0)
                sys_track_no.setTextAlignment(QtCore.Qt.AlignCenter)
                sys_track_no.setFont(font)

                # Adding combo box to platforms column
                combo = ComboPlatforms(self)
                self.mode_table.setCellWidget(k, 1, combo)
                combo.addItems(TRACK_ID.keys())

                # Adding combo box to platforms column
                combo = ComboPlatforms(self)
                self.mode_table.setCellWidget(k, 2, combo)
                combo.addItems(PLATFORMS)

                # Setting default value of Mode1 column
                self.mode_table.setItem(k, 3, QTableWidgetItem("-1"))
                mode1 = self.mode_table.item(k, 3)
                mode1.setTextAlignment(QtCore.Qt.AlignCenter)
                mode1.setFont(font)

                # Setting default value of Mode2 column
                self.mode_table.setItem(k, 4, QTableWidgetItem("-1"))
                mode2 = self.mode_table.item(k, 4)
                mode2.setTextAlignment(QtCore.Qt.AlignCenter)
                mode2.setFont(font)

                # Setting default value of Mode3 column
                self.mode_table.setItem(k, 5, QTableWidgetItem("-1"))
                mode3 = self.mode_table.item(k, 5)
                mode3.setTextAlignment(QtCore.Qt.AlignCenter)
                mode3.setFont(font)

                # Setting default value of Mode6 column
                self.mode_table.setItem(k, 6, QTableWidgetItem("-1"))
                mode6 = self.mode_table.item(k, 6)
                mode6.setTextAlignment(QtCore.Qt.AlignCenter)
                mode6.setFont(font)

                # Setting default value of Call sign column
                self.mode_table.setItem(k, 7, QTableWidgetItem("-1"))
                call_sign = self.mode_table.item(k, 7)
                call_sign.setTextAlignment(QtCore.Qt.AlignCenter)
                call_sign.setFont(font)

                # Setting default value of ICAO type column
                self.mode_table.setItem(k, 8, QTableWidgetItem("-1"))
                icao_type = self.mode_table.item(k, 8)
                icao_type.setTextAlignment(QtCore.Qt.AlignCenter)
                icao_type.setFont(font)

                # Setting default value of Mode-S column
                self.mode_table.setItem(k, 9, QTableWidgetItem("-1"))
                mode_s = self.mode_table.item(k, 9)
                mode_s.setTextAlignment(QtCore.Qt.AlignCenter)
                mode_s.setFont(font)

                # Setting default value of ModeC column
                self.mode_table.setItem(k, 10, QTableWidgetItem("-1"))
                mode_c = self.mode_table.item(k, 10)
                mode_c.setTextAlignment(QtCore.Qt.AlignCenter)
                mode_c.setFont(font)
        except:
            mode_error_dialog(self)


    # def add_platforms(self):
    #     """
    #        Add platforms to drop down menu in platforms table
    #     """
    #     platforms = int(self.platforms.currentText())
    #     self.platform_info_table.setRowCount(0)

    #     for i in range(0, platforms):
    #         self.platform_info_table.insertRow(i)

    #         font = QtGui.QFont()
    #         font.setPointSize(10)

    #         combo = ComboPlatforms(self)
    #         self.platform_info_table.setCellWidget(i, 0, combo)
    #         combo.addItems(PLATFORMS)
    #         self.platform_info_table.setItem(i, 1, QTableWidgetItem("0"))
    #         num_aircrafts = self.platform_info_table.item(i, 1)
    #         num_aircrafts.setTextAlignment(QtCore.Qt.AlignCenter)
    #         num_aircrafts.setFont(font)

            
    # def check(self):
    #     """
    #        Checks if the paltforms and aircrafts are equal to the total aircrafts
    #        mentioned
    #     """
    #     n_rows = self.platform_info_table.rowCount()
    #     aircrafts = int(self.aircrafts.displayText())
    #     num_air = 0
    #     for r in range(n_rows):
    #         num_air += float(self.platform_info_table.item(r, 1).text())
        
    #     if (num_air > aircrafts):
    #         _translate = QtCore.QCoreApplication.translate
    #         self.error.setText(_translate("MainWindow", "ERROR: Sum of aircrafts is greater than total aircrafts in group!"))

    #     elif (num_air < aircrafts):
    #         _translate = QtCore.QCoreApplication.translate
    #         self.error.setText(_translate("MainWindow", "ERROR: Sum of aircrafts is less than total aircrafts in group!"))

    #     else:
    #         _translate = QtCore.QCoreApplication.translate
    #         self.error.setText(_translate("MainWindow", ""))


    def add_waypoints(self):
        """
        Function to add row to waypoints table
        """
        self.table.setRowCount(0)
        Origin = self.origin_base.currentText()
        origin = [0, 0]
        map = MapCanvas(parent=self, origin=origin, play=False)
        map.save_signal.connect(self.fill_rows)
        
    def fill_rows(self):
        for i in range(len(point)):
            rowPos = self.table.rowCount()
            self.table.insertRow(rowPos)
            
            # Setting font size property
            font = QtGui.QFont()
            font.setPointSize(10)

            # Setting default value of time column
            self.table.setItem(i, 0, QTableWidgetItem(str(np.round(point[i][1], 5))))
            lat = self.table.item(i, 0)
            lat.setTextAlignment(QtCore.Qt.AlignCenter)
            lat.setFont(font)

            # Setting default value of heading column
            self.table.setItem(i, 1, QTableWidgetItem(str(np.round(point[i][0], 5))))
            lon = self.table.item(i, 1)
            lon.setTextAlignment(QtCore.Qt.AlignCenter)
            lon.setFont(font)

            # Setting default value of speed column
            self.table.setItem(i, 2, QTableWidgetItem("000"))
            heading = self.table.item(i, 2)
            heading.setTextAlignment(QtCore.Qt.AlignCenter)
            heading.setFont(font)

            # Setting default value of altitude column
            self.table.setItem(i, 3, QTableWidgetItem("000"))
            heading = self.table.item(i, 3)
            heading.setTextAlignment(QtCore.Qt.AlignCenter)
            heading.setFont(font)
        
        for row in reversed(range(self.table.rowCount())):
            lat = self.table.item(row, 0)
            if type(lat) == type(None):
                self.table.removeRow(row)
        
    def delete_row(self):
        """
        Function to delete row from waypoints table
        """
        indices = self.table.selectionModel().selectedRows()
        for index in indices:
            self.table.removeRow(index.row())
    
    def save(self):
        """
        Function to execute scenario generator
        """
        current_tab = self.tabWidget.currentWidget().objectName()
        if current_tab == "fighter_tab":
            try:
                
                aircrafts = int(self.aircrafts.displayText())
                # Checking if modes entered equate to the number of aircrafts
                if (aircrafts == self.mode_table.rowCount()):
                    # Getting all entered values for current group
                    origin = self.origin_base.currentText()
                    init_time = self.initial_time.displayText()
                    # If end time is given get the value else leave it empty
                    if self.end_time.text():
                        end_time = self.end_time.displayText()
                    else: 
                        end_time = ""
                    init_speed = float(self.initial_speed.displayText())
                    latitude, longitude, speed, altitude = self.get_table(self.table)
                    mode_info, platforms, track_no, track_id = self.get_modes(self.mode_table)
                    date = self.dateEdit.date().toString("dd-MM-yyyy")

                    # if both the end time and any one of speed columns is 0 or empty \
                    # error is shown
                    if any(item == 0 for item in speed) and end_time == "":
                        save_error_dialog(self)
                    # If formation hasnt been created and aicrafts > 1 show error
                    elif aircrafts > 1 and not self.aircraft_pos:
                        formation_error_dialog(self)
                    else: 

                        # Creating dictionary that contains information of the current group
                        group = {
                            "Sys Track No" : track_no,
                            "Track ID" : track_id,
                            "Aircrafts" : aircrafts,
                            "Platform" :platforms,
                            "Origin" : origin,
                            "Date" : date,
                            "Initial Time" : init_time,
                            "End Time" : end_time,
                            "Initial Speed": init_speed,
                            "Waypoints" : {
                                "Latitude" : latitude,
                                "Longitude" : longitude,
                                "Speed" : speed,
                                "Altitude" : altitude
                            },
                            "Mode Info" : mode_info,
                            "Aircrafts Pos" : self.aircraft_pos
                            # "Aircrafts Loc" : self.aircraft_locations,
                            # "Aicrafts Ref" : self.ref
                        }

                        # Calling function to save dict containing current group info
                        main_page = Window(self)
                        main_page.save_data(group)
                        

                        # Closing window of current group
                        self.close()        
                else:
                    save_error_dialog(self)
            except:
                save_error_dialog(self)

        else:
            try:
                # Getting all entered values for current group
                init_time = self.initial_time_airliner.displayText()
                if self.end_time_airliner.text():
                    end_time = self.end_time_airliner.displayText()
                else: 
                    end_time = ""
                speed = float(self.cruising_speed.displayText())
                altitude = float(self.cruising_altitude.displayText())
                date = self.dateEdit_airliner.date().toString("dd-MM-yyyy")    
                track_id = self.trackId_airliner.currentText()

                mode_s = "" 
                mode_c = ""
                mode_3 = ""
                if self.mode_s_radio.isChecked() == True:
                    mode_s = self.mode_s_value.displayText()
                
                if self.mode_c_radio.isChecked() == True:
                    mode_c = self.mode_c_value.displayText()

                if self.mode_3_radio.isChecked() == True:
                    mode_3 = self.mode_3_value.displayText()
                

                # Entering all the mode info in same format as for fighter tab to 
                # make computation simpler    
                mode_info = {}
                platforms = {}
                track_ID = {}
                mode_info["IFF Mode 1"] = {}
                mode_info["IFF Mode 2"] = {}
                mode_info["IFF Mode 3"] = {}
                mode_info["IFF Mode 6"] = {}
                mode_info["Call Sign"] = {}
                mode_info["ICAO Type"] = {}
                mode_info["Mode S"] = {}
                mode_info["Mode C Height"] = {}

                # Entering modes s, c and 3 info and leaving the rest as "-1"
                mode_info["IFF Mode 1"]["1"] = str(-1)
                mode_info["IFF Mode 2"]["1"] = str(-1)
                mode_info["IFF Mode 3"]["1"] = str(mode_3)
                mode_info["IFF Mode 6"]["1"] = str(-1)
                mode_info["Call Sign"]["1"] = str(-1)
                mode_info["ICAO Type"]["1"] = str(-1)
                mode_info["Mode S"]["1"] = str(mode_s)
                mode_info["Mode C Height"]["1"] = str(mode_c)
                platforms["1"] = "Airliner"
                track_ID["1"] = track_id
            
                nrows = self.path_table.rowCount()
                latitude = []
                longitude = []

                for row in range(0, nrows):
                    point = self.path_table.item(row, 0).text()
                    latitude.append(IAF_BASES[point][0])
                    longitude.append(IAF_BASES[point][1])
                # Creating dictionary that contains information of the current group
                group = {
                    "Sys Track No" :  {"1" : "-1"},
                    "Track ID" : track_ID,
                    "Aircrafts" : 1,
                    "Platform" : platforms,
                    "Origin" : "Unknown",
                    "Date" : date,
                    "Initial Time" : init_time,
                    "End Time" : end_time,
                    "Initial Speed": speed,
                    "Waypoints" : {
                        "Latitude" : latitude,
                        "Longitude" : longitude,
                        "Speed" : [speed for i in range(len(latitude))],
                        "Altitude" : [altitude for i in range(len(latitude))]
                    },
                    "Mode Info" : mode_info,
                    "Aircrafts Pos" : {"1" : [0,0]}
                }

                # Calling function to save dict containing current group info
                main_page = Window(self)
                main_page.save_data(group)
                
                # Closing window of current group
                self.close()        
                
            except:
                save_error_dialog(self)

    def get_modes(self, element):
        """
            Gets the informaton from modes table

        Args:
            element (QTableWidget): modes table

        Returns:
            platform_array(array): Data containing information obtained from modes table
        """
        nrows = element.rowCount()
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
        
        
        for row in range(0, nrows):
            track_no[str(row+1)] = str(element.item(row, 0).text())
            track_id[str(row+1)] = element.cellWidget(row, 1).currentText()
            platforms[str(row+1)] = element.cellWidget(row, 2).currentText()
            mode_info["IFF Mode 1"][str(row+1)] = str(element.item(row, 3).text())
            mode_info["IFF Mode 2"][str(row+1)] = str(element.item(row, 4).text())
            mode_info["IFF Mode 3"][str(row+1)] = str(element.item(row, 5).text())
            mode_info["IFF Mode 6"][str(row+1)] = str(element.item(row, 6).text())
            mode_info["Call Sign"][str(row+1)] = str(element.item(row, 7).text())
            mode_info["ICAO Type"][str(row+1)] = str(element.item(row, 8).text())
            mode_info["Mode S"][str(row+1)] = str(element.item(row, 9).text())
            mode_info["Mode C Height"][str(row+1)] = str(element.item(row, 10).text())
        
        return mode_info, platforms, track_no, track_id



    def get_table(self, element):
        """
        Function to get all the values of waypoints from the table

        Args:
            element (object): table containing waypoints

        Returns:
            time(time): waypoint time
            heading(int) : waypoint heading
            speed(float) : waypoint speed
            altitude(float) : waypoint altitude
        """
        nrows = element.rowCount()
        lat = []
        lon = []
        speed = []
        altitude = []

        for row in range(0, nrows):
            lat.append(float(element.item(row, 0).text()))
            lon.append(float(element.item(row, 1).text()))
            speed.append(float(element.item(row, 2).text()))
            altitude.append(float(element.item(row, 3).text()))

        return lat, lon, speed, altitude

    def add_formation(self):
        """
            Function to open formation window
        """
        aircrafts = int(self.aircrafts.displayText())
        formation = AddFormation(aircrafts, self)
        formation.show()

class ComboPlatforms(QComboBox):
    """
        Combination box widget 
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet('font-size: 10')

################################################################################
############################ ERROR DIALOG BOXES ################################
################################################################################
        
def group_error_dialog(self):
        error_dialog = QErrorMessage()
        error_dialog.setWindowTitle("Error")
        error_dialog.showMessage("Please Enter No. of Groups!")
        error_dialog.exec_()

def mode_error_dialog(self):
        error_dialog = QErrorMessage()
        error_dialog.setWindowTitle("Error")
        error_dialog.showMessage("Please Enter No. of Aircrafts!")
        error_dialog.exec_()

def save_error_dialog(self):
        error_dialog = QErrorMessage()
        error_dialog.setWindowTitle("Error")
        error_dialog.showMessage("Please Enter Correct Values!")
        error_dialog.exec_()

def begin_error_dialog(self):
        error_dialog = QErrorMessage()
        error_dialog.setWindowTitle("Error")
        error_dialog.showMessage("ERROR: Error in saving file. Please enter data again.")
        error_dialog.exec_()
        
def formation_error_dialog(self):
        error_dialog = QErrorMessage()
        error_dialog.setWindowTitle("Error")
        error_dialog.showMessage("Add formation to continue!")
        error_dialog.exec_()

################################################################################
####################### WINDOW TO ADD FORMATION ################################
################################################################################

class AddFormation(QMainWindow):

    def __init__(self, aircrafts, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        loadUi(QGIS_PATH + "ui\\formation.ui", self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Add Formation"))
        self.setAcceptDrops(True)
        self.save_formation.clicked.connect(self.get_formation)
        
        # Adding aircraft icons equal to num of aircrafts
        for i in range(aircrafts):
            self.aircraft = Aircraft(i, self)
            self.aircraft.show()
        
    def get_formation(self):
        children = self.findChildren(QLabel)
        i = 1
        aircraft_pos = {}
        x = {}
        # Getting position of all aicrafts 
        for child in children:
            aircraft_pos[str(i)] = [child.pos().x(), child.pos().y()]
            i+=1

        # Using aircrafts one (blue) as reference
        ref = deepcopy(aircraft_pos["1"])
    
        for key in aircraft_pos:
            if key != "1":
                # Finding relative pos of all aircrafts wrt reference and converting 
                # to nautical miles
                aircraft_pos[key][0] = (ref[0] - aircraft_pos[key][0]) * P_TO_Nm
                aircraft_pos[key][1] = (ref[1] - aircraft_pos[key][1]) * P_TO_Nm
                x[key] ={}

                #  Finding distance of each aircraft from reference aircraft
                x[key]["distance"] = math.hypot(aircraft_pos["1"][0] - aircraft_pos[key][0], aircraft_pos["1"][1] - aircraft_pos[key][1])

                # Finding the angle of each aircraft wrt to ref and then find actual \
                # angle of that aircraft according to the quadrant it lies in wrt refernce
                x[key]["angle"] = math.degrees(math.acos(abs(aircraft_pos[key][0]) / x[key]["distance"]))
                if aircraft_pos[key][0] < 0 and aircraft_pos[key][1] > 0:
                    x[key]["angle"] = 90 - x[key]["angle"]
                elif aircraft_pos[key][0] < 0 and aircraft_pos[key][1] < 0:
                    x[key]["angle"] = 90 + x[key]["angle"]
                elif aircraft_pos[key][0] > 0 and aircraft_pos[key][1] < 0:
                    x[key]["angle"] = 270 - x[key]["angle"]
                elif aircraft_pos[key][0] > 0 and aircraft_pos[key][1] > 0:
                    x[key]["angle"] = 270 + x[key]["angle"]

                # Since formation is made at a heading of 90 degrees, that is subtracted from all angles \
                # to get heading due north
                x[key]["angle"] -= 90
                # If any angle is negative, changing it to fit between 0 and 360
                x[key]["angle"] = 360 + x[key]["angle"] if x[key]["angle"] < 0  else x[key]["angle"]
            else:
                aircraft_pos[key][0] = 0
                aircraft_pos[key][1] = 0
                x[key] ={}
                x[key]["distance"] = 0
                x[key]["angle"] = 0

    
        self.parent.aircraft_pos = x
        self.parent.aircraft_locations = aircraft_pos
        self.parent.ref = ref
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

# Aircraft image representation
class Aircraft(QLabel):
    def __init__(self, i , parent=None):
        QLabel.__init__(self, parent=parent)
        self.setObjectName("aicraft"+str(i+1))
        self.i = i
        self.img1 = QImage(QGIS_PATH + '\\Logos\\plane1.png')
        self.img2 = QImage(QGIS_PATH + '\\Logos\\plane.png')
        self.img1 = self.img1.scaled(51, 31, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.img2 = self.img2.scaled(51, 31, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.resize(self.img1.size())
        self.move(70 + i * 70, 50)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        if self.i == 0:
            p.drawImage(0, 0, self.img1)
        else:
            p.drawImage(0, 0, self.img2)
        self.drawText(event, p)
            
    def drawText(self, event, p):
        p.setPen(QColor(255,255,255))
        p.drawText(event.rect(), Qt.AlignCenter, str(self.i+1))

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.setHotSpot(e.pos() - self.rect().topLeft())
            drag.exec_(Qt.MoveAction)


################################################################################
########################### QGIS CANVAS PLOTTING ###############################
################################################################################

class PrintClickedPoint(QgsMapToolEmitPoint):
    """
        Class to get lat, long waypoints from user click
    """
    def __init__(self,  canvas, streaming_layer, origin):
        self.canvas = canvas
        self.streaming_layer = streaming_layer
        self.origin = origin
        global point
        point = []
        self.stream_data_provider = self.streaming_layer.dataProvider()
        self.feature_mark = QgsFeature()
        # Adding origin to map if it is given for user reference
        if self.origin != [0, 0]:
            self.feature_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.origin[0], self.origin[1])))
            self.stream_data_provider.addFeature(self.feature_mark)
            self.feature_mark.setAttributes([self.origin[0], self.origin[1]])
            self.streaming_layer.commitChanges()
            self.streaming_layer.updateFields()
            self.streaming_layer.reload()
            self.canvas.refresh()
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        
        
    def canvasReleaseEvent(self, event):
        waypoint = self.toMapCoordinates(event.pos())
        point.append([waypoint[0], waypoint[1]])
        self.feature_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point[-1][0], point[-1][1])))
        self.feature_mark.setAttributes([point[-1][0], point[-1][1]])
        self.stream_data_provider.addFeature(self.feature_mark)
        self.streaming_layer.commitChanges()
        self.streaming_layer.updateFields()
        self.streaming_layer.reload()
        self.canvas.refresh()
        

class MapCanvas(QMainWindow):
    """
        Class to create canvas for map plotting
    """
    save_signal = pyqtSignal()
    def __init__(self, parent, origin= [0, 0], play= False, scenario = ""):
        super().__init__(parent=parent)
        self.origin = origin
        self.play = play
        self.scenario = scenario
        
        self.show()
        loadUi(QGIS_PATH + "ui\\map.ui", self)
        self.canvas = QgsMapCanvas()
        self.setCentralWidget(self.canvas)
        self.canvas.setCanvasColor(Qt.black)
        
        # Importing pakistan border layer, pakistan bases, indian bases and ATS routes
        self.pakistan_border = QgsVectorLayer(QGIS_PATH + "Layers\\PakistanIBPolyline.shp", "pakistan_border")
        self.pakistan_border.renderer().symbol().setColor ( QColor(Qt.darkGray))   
        self.ats_routes_india = QgsVectorLayer(QGIS_PATH + "Layers\\ATS_Routes_India_Dummy.shp", "ATS_routes_Indea")
        self.ats_routes_india.renderer().symbol().setColor ( QColor(Qt.white))
        self.grid = QgsVectorLayer(QGIS_PATH + "Layers\\GRID.shp", "Grid")
        self.grid.renderer().symbol().setColor ( QColor(Qt.white))
        self.grid.setOpacity(0.2)
        self.smallgrid = QgsVectorLayer(QGIS_PATH + "Layers\\smallGRID.shp", "Small Grid")
        self.smallgrid.renderer().symbol().setColor ( QColor(Qt.darkGray))
        self.smallgrid.setOpacity(0.4)
                
        
        self.streaming_layer = QgsVectorLayer('Point?crs=epsg:4326&field=x:float&field=y:float&field=Heading:float', 'tracks_layer', "memory")
        self.streaming_layer.renderer().symbol().setColor ( QColor(Qt.yellow))
#        self.streaming_layer.renderer().setSymbol(QgsStyle.defaultStyle().symbol('topo airport'))
#        self.streaming_layer.renderer().symbol().setSize(4)

        # Creating layer to add line showing heading
        self.heading_line_layer=QgsVectorLayer("LineString?crs=epsg:4326", "heading line layer", "memory")
        self.heading_line_layer.renderer().symbol().setColor ( QColor(Qt.white))
        # Setting layers
        self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer])
        self.canvas.setExtent(self.pakistan_border.extent())      
        self.canvas.show()
        
        # PAN BUTTON
        self.actionPan = QAction("Pan", self)
        self.actionPan.setCheckable(True) 
        self.actionPan.triggered.connect(self.pan)
        # add to toolbar
        self.toolbar = self.addToolBar("Canvas action")
        self.toolbar.addAction(self.actionPan)
        
        # RESET ZOOM BUTTON
        self.actionResetZoom = QAction("Reset", self)
        self.actionResetZoom.setCheckable(False) 
        self.actionResetZoom.triggered.connect(self.resizeEvent)
        # add to toolbar
        self.toolbar = self.addToolBar("Canvas action")
        self.toolbar.addAction(self.actionResetZoom)
        
        
        # create the map tools
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(self.actionPan)
        
        if(self.play):
            # Importing tracks file
            self.df1 = pd.read_csv(QGIS_PATH + 'Track Files\\'+self.scenario+'.csv')

            # Getting data from tracks file
            self.data_latitude = list(self.df1['TrackLatitude'])
            self.data_longitude = list(self.df1['TrackLongitude'])
            self.time = list(self.df1['EpocTimeMilliSeconds'])
            self.heading = list(self.df1['TrackHeading'])

            # Creating layer to plot coordinates of tracks
            self.stream_data_provider = self.streaming_layer.dataProvider()
            self.feature_mark = QgsFeature()
            self.heading_data_provider=self.heading_line_layer.dataProvider()
            self.heading_line_feat=QgsFeature()
            
            # Loop for plotting coordinates
            for i in range (len(self.data_latitude)):
                # If time has changed, add delay
                if (i>0 and self.time[i-1] != self.time[i]):
                    # Delay is of 0.5 seconds even though data is after every second so 
                    # animation plays at x2 the speed
                    QtTest.QTest.qWait(int((self.time[i] - self.time[i-1])*50))
                    self.streaming_layer.startEditing()
                    self.stream_data_provider.truncate()
                    self.heading_data_provider.truncate()
                    
                self.feature_mark.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.data_longitude[i], self.data_latitude[i])))
                self.stream_data_provider.addFeature(self.feature_mark)
                self.feature_mark.setAttributes([self.data_longitude[i], self.data_latitude[i]])
                self.streaming_layer.commitChanges()
                self.streaming_layer.updateFields()
                
                next_coord = d.computeSpheroidProject(QgsPointXY(self.data_longitude[i], self.data_latitude[i]), 100 * M_to_Nm, math.radians(self.heading[i]))

                # self.location = geopy.Point(math.radians(self.data_latitude[i]), math.radians(self.data_longitude[i]))
                # self.d = geopy.distance.distance(nautical = 100)
                # self.new_lat = math.degrees(self.d.destination(self.location, self.heading[i]).latitude)
                # self.new_lon = math.degrees(self.d.destination(self.location, self.heading[i]).longitude)

                self.new_x, self.new_y = next_coord.y(), next_coord.x()

                self.line_geom = QgsGeometry.fromPolyline([QgsPoint(self.data_longitude[i], self.data_latitude[i]), QgsPoint(self.new_y, self.new_x)])
                self.heading_line_feat.setGeometry(self.line_geom)
                self.heading_data_provider.addFeature(self.heading_line_feat)
                self.heading_line_layer.reload()
                self.canvas.refresh()
                self.canvas.repaint()

                
        else:      
            # SAVE BUTTON
            self.actionSave = QAction("Save", self)
            self.actionSave.setCheckable(False) 
            self.actionSave.triggered.connect(self.save)
            # add to toolbar
            self.toolbar = self.addToolBar("Canvas action")
            self.toolbar.addAction(self.actionSave)
            
            # DELETE BUTTON
            self.actionDelete = QAction("Delete", self)
            self.actionDelete.setCheckable(True) 
            self.actionDelete.triggered.connect(self.delete)
            # add to toolbar
            self.toolbar = self.addToolBar("Canvas action")
            self.toolbar.addAction(self.actionDelete)
            
            # ADD COMMERCIAL ROUTE BUTTON
            self.actionAddRouteData = QAction("Add Commercial Routes", self)
            self.actionAddRouteData.setCheckable(True) 
            self.actionAddRouteData.triggered.connect(self.addRouteData)
            # add to toolbar
            self.toolbar = self.addToolBar("Canvas action")
            self.toolbar.addAction(self.actionAddRouteData)
            
            # ADD COMMERCIAL ROUTE BUTTON
            self.actionToggleGrid = QAction("Grid", self)
            self.actionToggleGrid.setCheckable(True) 
            self.actionToggleGrid.triggered.connect(self.toggleGrid)
            # add to toolbar
            self.toolbar = self.addToolBar("Canvas action")
            self.toolbar.addAction(self.actionToggleGrid)
            
            # Attaching listener to add waypoints
            self.canvas_clicked = PrintClickedPoint(self.canvas, self.streaming_layer, self.origin)
            self.canvas.setMapTool(self.canvas_clicked)
        
    def newcoord(self, coord1, coord2, dist):
        (x1,y1) = coord1
        (x2,y2) = coord2
        dx = x2 - x1
        dy = y2 - y1
        linelen = math.hypot(dx, dy)

        x3 = x2 + dx/linelen * dist
        y3 = y2 + dy/linelen * dist    
        return x3, y3

    def save(self):  
        """
            Function to save waypoints 
        """
        self.save_signal.emit()
        QgsProject.instance().removeAllMapLayers()
        self.canvas.refresh()
        self.close()
        
        
    def pan(self):
        """
            Function to add pan feature
        """
        if(self.actionPan.isChecked()):
            self.canvas.setMapTool(self.toolPan)
        elif not self.actionPan.isChecked() and not self.play:
            self.canvas.setMapTool(self.canvas_clicked)
        elif not self.actionPan.isChecked() and self.play:
            self.canvas.unsetMapTool(self.toolPan)
    
    def addRouteData(self):
        """
            Function to show commercial routes in click
        """
        self.canvas.instance().addMapLayer(self.ats_routes_india)
        # if self.actionAddRouteData.isChecked() and not self.actionToggleGrid.isChecked():
        #     self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer, self.ats_routes_india])        
        # elif self.actionAddRouteData.isChecked() and self.actionToggleGrid.isChecked():
        #     self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer, self.ats_routes_india,\
        #     self.grid, self.smallgrid])
        # elif not self.actionAddRouteData.isChecked() and not self.actionToggleGrid.isChecked():
        #     self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer])
        # elif not self.actionAddRouteData.isChecked() and self.actionToggleGrid.isChecked():
        #     self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer,\
        #     self.grid, self.smallgrid])
            
        self.canvas.refresh()
        self.canvas.repaint()

    def toggleGrid(self):
        if self.actionToggleGrid.isChecked():
            self.canvas.addLayer(self.grid)
        # if self.actionAddRouteData.isChecked() and not self.actionToggleGrid.isChecked():
        #     self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer, self.ats_routes_india])        
        # elif self.actionAddRouteData.isChecked() and self.actionToggleGrid.isChecked():
        #     self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer, self.ats_routes_india,\
        #     self.grid, self.smallgrid])
        # elif not self.actionAddRouteData.isChecked() and not self.actionToggleGrid.isChecked():
        #     self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer, ])
        # elif not self.actionAddRouteData.isChecked() and self.actionToggleGrid.isChecked():
        #     self.canvas.setLayers([self.streaming_layer, self.pakistan_border, self.heading_line_layer,\
        #     self.grid, self.smallgrid])
            
        self.canvas.refresh()
        self.canvas.repaint()
        
    def closeEvent(self, event):
        """
            Functionality on closing window
        """
        QgsProject.instance().removeAllMapLayers()
        self.canvas.refresh()
        self.close()
        
    # def resizeEvent(self, event):
    #     """
    #         Funcitonality on resizing window
    #     """
    #     self.canvas.setExtent(self.pakistan_border.extent())
        
    def delete(self):
        if self.actionDelete.isChecked():
            self.select = selectTool(self.canvas, self.streaming_layer)
            self.canvas.setMapTool(self.select)
        else:
            self.canvas.setMapTool(self.canvas_clicked)
        

class selectTool(QgsMapToolIdentifyFeature):
    
    def __init__(self, canvas, layer):
        self.layer = layer
        self.canvas = canvas
        QgsMapToolIdentifyFeature.__init__(self, self.canvas, self.layer)
        
    def canvasPressEvent(self, event):
        found_features = self.identify(event.x(), event.y(), [self.layer], QgsMapToolIdentify.TopDownAll)
        for f in found_features:
            #delete by feature id
            self.layer.startEditing()
            self.layer.deleteFeature(f.mFeature.id())
            lat = float(f.mFeature.attributes()[0])
            lon = float(f.mFeature.attributes()[1])
            point.remove([lat, lon])
            self.layer.commitChanges()
            self.layer.updateFields()
            self.canvas.refresh()
            self.canvas.repaint()
            
        
        

win = Window()
win.show()
exitcode = app.exec_()
sys.exit(exitcode)