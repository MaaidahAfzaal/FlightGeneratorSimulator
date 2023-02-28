import sys
import pandas as pd
import numpy as np
import math
import os
import random
from copy import deepcopy
import time
import json

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QWidget)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QDialog, QErrorMessage, QMessageBox, \
    QTableWidgetItem, QComboBox, QTableWidget, QPushButton, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap, QDrag
from PyQt5.QtCore import*
from PyQt5.QtCore import Qt, QMimeData


from main_page import Ui_MainPage
from config_parameters import *
from file_generation_latlong import get_data, get_current_time
from Dijkstra import get_shortest_path

group_data = []

################################################################################
############################## MAIN PAGE WINDOW ################################
################################################################################

class Window(QMainWindow, Ui_MainPage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.scenarios.setStyleSheet('font-size: 12')
        self.add_groups.clicked.connect(self.add_group_info)
        self.begin.clicked.connect(lambda: self.begin_exec(flag=False))
        self.edit.clicked.connect(self.load_scenario)
        self.update.clicked.connect(lambda: self.begin_exec(flag=True))

        # Loading json file that contains all poreviously saved scenarios
        with open(VS_PATH + 'Scenarios.json') as json_file:
            loaded_data = json.load(json_file)

        global generated_scenarios
        generated_scenarios = loaded_data
        last_scen = list(generated_scenarios.keys())[-1]
        last_scen = last_scen.split()
        self.num_scenario = int(last_scen[-1])
        
        # Adding all previous scenarios to dropdown to be edited
        for i in range(1, self.num_scenario+1):
            self.scenarios.addItem("")
            _translate = QtCore.QCoreApplication.translate
            self.scenarios.setItemText(i - 1, _translate("MainWindow", "Scenario "+str(i)+""))
        
    
    
    def closeEvent(self, event):
        """
            On closing the window all new scenarios are added to json file and 
            updated scenarios are changed

        Args:
            event (_type_): Triggered on closing of window
        """
        with open(VS_PATH + 'Scenarios.json', 'r') as outfile:
            json_data = json.load(outfile)

        json_data.update(generated_scenarios)

        with open(VS_PATH + 'Scenarios.json', 'w') as outfile:
            json.dump(json_data, outfile, indent=2)


    def add_group_info(self):
        """
            Function to open windows for entering data equal to the number of groups
        """
        _translate = QtCore.QCoreApplication.translate
        self.file_success.setText(_translate("MainWindow", ""))
        # try:
        groups = int(self.groups.displayText())
        for i in range(groups):
            dialog = AddGroup(i, self)
            dialog.show()
        # except:
        #    group_error_dialog(self)
        

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
        scen = self.scenarios.currentText()
        groups = len(generated_scenarios[scen])
        for i in range(groups):
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
                if time_key in generated_scenarios[scen][i].keys():
                    dialog.end_time_airliner.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["End Time"])))
                # dialog.takeoff.setCurrentText(_translate("MainWindow", takeoff_point))
                # dialog.destination.setCurrentText(_translate("MainWindow", destination_point))
                dialog.initial_time_airliner.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Initial Time"])))
                dialog.cruising_speed.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Initial Speed"])))
                dialog.cruising_altitude.setText(_translate("MainWindow", str(generated_scenarios[scen][i]["Waypoints"]["Altitude"][0])))
                # date = QtCore.Qdate.fromString(generated_scenarios[scen][i]["Date"], 'dd-MM-yyyy')
                if "Date" in generated_scenarios[scen][i].keys():
                    dialog.dateEdit_airliner.setDate(QtCore.QDate.fromString(generated_scenarios[scen][i]["Date"], 'dd-MM-yyyy'))
                else:
                    dialog.dateEdit_airliner.setDate(QtCore.QDate.currentDate())
                   
                if "Track ID" in generated_scenarios[scen][i]:
                        dialog.trackId_airliner.setCurrentText(_translate("MainWindow", generated_scenarios[scen][i]["Track ID"][str(j+1)]))

                
                # Entering values of Modes C, S and 3
                if (generated_scenarios[scen][i]["Mode Info"]["Mode C Height"]["1"] != -1):
                    dialog.mode_c_radio.setChecked(True)
                    dialog.mode_c_value.setText = (_translate("MainWindow", str(generated_scenarios[scen][i]["Mode Info"]["Mode C Height"]["1"])))
                    
                if (generated_scenarios[scen][i]["Mode Info"]["Mode S"]["1"] != -1):
                    dialog.mode_s_radio.setChecked(True)
                    dialog.mode_s_value.setText = (_translate("MainWindow", str(generated_scenarios[scen][i]["Mode Info"]["Mode S"]["1"])))

                if (generated_scenarios[scen][i]["Mode Info"]["IFF Mode 3"]["1"] != -1):
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
                    dialog.path_table.setItem(k, 0, QTableWidgetItem(stopover_point))
                    stopover = dialog.path_table.item(k, 0)
                    stopover.setTextAlignment(QtCore.Qt.AlignCenter)
                    stopover.setFont(font)

            # Loading fighter data
            else:
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
            if(flag):
                scen = self.scenarios.currentText()
                generated_scenarios[scen] = deepcopy(group_data)
            else:
                self.num_scenario += 1
                generated_scenarios["Scenario "+str(self.num_scenario)+""] = deepcopy(group_data)


            # Finding the total number of aircrafts
            total_aircrafts = 0
            for key in range(len(group_data)):
                total_aircrafts += int(group_data[key]["Aircrafts"])
            
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

            # Getting data after computations
            excel_data = []
            for key in range(0, len(group_data)):
                excel_data.append(get_data(group_data[key]))

            data_final = []
            # Getting data in required format
            for i in range(0, len(excel_data)):
                for j in range(0, len(excel_data[i])):
                    data_final.append(excel_data[i][j])
            
            # Converting data to dataframe
            df = pd.DataFrame(columns= COL, data= data_final)
            sorted_df = df.sort_values(by='Timestamp-sec', ascending=True)
            t2 = get_current_time()
            print("Time taken for processing : ", (t2-t1))

            if(flag):
                scen = self.scenarios.currentText()
                # If file already exists remove it
                if (os.path.exists(VS_PATH + scen +'.xcsv') and os.path.isfile(VS_PATH + scen +'.csv')):
                    os.remove(VS_PATH + scen +'.csv')
                sorted_df.to_csv(VS_PATH + scen +'.csv', index=False, float_format='%.3f')

                _translate = QtCore.QCoreApplication.translate
                self.file_success.setText(_translate("MainWindow", "File Updated Successfully!"))
            else:
                # If file already exists remove it
                if (os.path.exists(VS_PATH + 'Scenario ' + str(self.num_scenario) + '.csv') and os.path.isfile(VS_PATH + 'Scenario '+str(self.num_scenario)+'.csv')):
                    os.remove(VS_PATH + 'Scenario '+str(self.num_scenario)+'.csv')
                sorted_df.to_csv(VS_PATH + 'Scenario '+str(self.num_scenario)+'.csv', index=False, float_format='%.15f')

                # Displaying message on successful file saving
                # self.scenarios.addItem("")
                _translate = QtCore.QCoreApplication.translate
                self.file_success.setText(_translate("MainWindow", "File Saved Successfully!"))
                self.scenarios.addItem("Scenario "+str(self.num_scenario)+"")
                # self.scenarios.setItemText(self.num_scenario - 1, _translate("MainWindow", "Scenario "+str(self.num_scenario)+""))
            
            t3 = get_current_time()
            print("Time taken for writing to csv : ", (t3-t2))

            group_data.clear()

    

################################################################################
####################### WINDOW TO ENTER GROUP INFO #############################
################################################################################

class AddGroup(QMainWindow):

    def __init__(self, num, parent=None):
        super().__init__(parent=parent)
        loadUi("./ui/group_info_gui_tabs_modes_platforms.ui", self)
        self.add_items_to_dropdown()
        self.num = num
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Group "+str(self.num + 1)+""))
        self.save_btn.setStyleSheet("background-color: #266d19; color: white")
        self.setWindowIcon(QIcon('./Logos/Group.ico'))
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
        self.add_waypoint_btn.clicked.connect(self.add_row)
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
    
    def add_items_to_dropdown(self):
        """
            Function to add items to drop down menus
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
    #        Add and fill rows to platforms table based on number of platforms 
    #        entered
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

    #     if (num_air < aircrafts):
    #         _translate = QtCore.QCoreApplication.translate
    #         self.error.setText(_translate("MainWindow", "ERROR: Sum of aircrafts is less than total aircrafts in group!"))

    #     else:
    #         _translate = QtCore.QCoreApplication.translate
    #         self.error.setText(_translate("MainWindow", ""))


    def add_row(self): 
        """
            Function to add rows to waypoints table
        """
        
        rowPos = self.table.rowCount()
        self.table.insertRow(rowPos)
        # Setting font size property
        font = QtGui.QFont()
        font.setPointSize(10)

        # Setting default value of latitude column
        self.table.setItem(rowPos, 0, QTableWidgetItem("00.00"))
        lat = self.table.item(rowPos, 0)
        lat.setTextAlignment(QtCore.Qt.AlignCenter)
        lat.setFont(font)

        # Setting default value of longitude column
        self.table.setItem(rowPos, 1, QTableWidgetItem("00.00"))
        lon = self.table.item(rowPos, 1)
        lon.setTextAlignment(QtCore.Qt.AlignCenter)
        lon.setFont(font)

        # Setting default value of speed column
        self.table.setItem(rowPos, 2, QTableWidgetItem("000"))
        heading = self.table.item(rowPos, 2)
        heading.setTextAlignment(QtCore.Qt.AlignCenter)
        heading.setFont(font)

        # Setting default value of altitude column
        self.table.setItem(rowPos, 3, QTableWidgetItem("000"))
        heading = self.table.item(rowPos, 3)
        heading.setTextAlignment(QtCore.Qt.AlignCenter)
        heading.setFont(font)

        
    def delete_row(self):
        """
        Function to delete row from waypoints table
        """
        indices = self.table.selectionModel().selectedRows()
        for index in indices:
            self.table.removeRow(index.row())
    
    def save(self):
        """
        Function to save data of group 
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
                    if any(item == 0 for item in speed) and end_time == '':
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
                # Getting all entered values for Airliner
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
                    "Sys Track No" : {"1" : "-1"},
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
                    "Aircrafts Pos" : {"1" : [0,0]},
                    
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
        loadUi("./ui/formation.ui", self)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Add Formation"))
        self.setAcceptDrops(True)
        self.save_formation.clicked.connect(self.get_formation)
        
        # Adding aircraft icons equal to num of aircrafts
        for i in range(aircrafts):
            self.aircraft = Aircraft(i, self)
            self.aircraft.show()
        
    def get_formation(self):
        """
            Function to get distance and heading from formation made by user
        """
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
                if aircraft_pos[key][0] <= 0 and aircraft_pos[key][1] >= 0:
                    x[key]["angle"] = 90 - x[key]["angle"]
                elif aircraft_pos[key][0] <= 0 and aircraft_pos[key][1] < 0:
                    x[key]["angle"] = 90 + x[key]["angle"]
                elif aircraft_pos[key][0] > 0 and aircraft_pos[key][1] < 0:
                    x[key]["angle"] = 270 - x[key]["angle"]
                elif aircraft_pos[key][0] > 0 and aircraft_pos[key][1] >= 0:
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
        # pixmap = QPixmap('./Logos/plane1.png') if i==0 else QPixmap('./Logos/plane.png')
        self.setObjectName("aicraft"+str(i+1))
        # self.setPixmap(pixmap)
        # self.setScaledContents(True)
        self.setText(str(i+1))
        if i == 0:
            self.setStyleSheet("border-image: url("+'./Logos/plane1.png'+"); color: white")
        else:
            self.setStyleSheet("border-image: url("+'./Logos/plane.png'+"); color: white")
        self.setAlignment(QtCore.Qt.AlignCenter)
        
        self.resize(51, 31)
        self.move(70 + i * 70, 50)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.setHotSpot(e.pos() - self.rect().topLeft())
            drag.exec_(Qt.MoveAction)

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())


        
