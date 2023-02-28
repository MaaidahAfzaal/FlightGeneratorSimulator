from PyQt5 import QtWidgets, QtGui, QtCore

from config_parameters import IAF_BASES
from large_data import generate_data

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def item_checked(self, index):
        item = self.model().item(index, 0)
        return item.checkState() == QtCore.Qt.Checked

    def check_items(self):
        checkedItems = []
        for i in range(self.count()):
            if self.item_checked(i):
                checkedItems.append(self.model().item(i, 0).text())
        return checkedItems

class Dialog_01(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(700,500)
        self.setWindowTitle("Generate Large Data")
        myQWidget = QtWidgets.QWidget()
        myBoxLayout = QtWidgets.QVBoxLayout()
        self.myIntroInputLayout = QtWidgets.QHBoxLayout()
        self.myAircraftsInputLayout = QtWidgets.QHBoxLayout()
        self.myEndTimeInputLayout = QtWidgets.QHBoxLayout()
        self.myRandomBasesInputLayout = QtWidgets.QHBoxLayout()
        self.myBasesInputLayout = QtWidgets.QHBoxLayout()
        self.myButtonsLayout = QtWidgets.QHBoxLayout()
        myQWidget.setLayout(myBoxLayout)
        self.setCentralWidget(myQWidget)

        self.intro_label = QtWidgets.QLabel("Enter info to generate data")
        self.label = QtWidgets.QLabel("Enter Number of Aircrafts :")
        self.aircrafts = QtWidgets.QLineEdit()
        self.end_time_label = QtWidgets.QLabel("Enter End Time : ")
        self.end_time = QtWidgets.QLineEdit("00:01:00")
        self.random_btn = QtWidgets.QRadioButton("Random Bases")
        self.random_btn.setChecked(True)
        self.num_bases = QtWidgets.QLineEdit()
        self.select_bases = QtWidgets.QRadioButton("Select Bases")
        self.ComboBox = CheckableComboBox()
        self.ComboBox.setEnabled(False)
        for i in range(len(IAF_BASES.keys())):
            self.ComboBox.addItem(list(IAF_BASES)[i])
            item = self.ComboBox.model().item(i, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.generate_data_btn = QtWidgets.QPushButton("Generate")

        self.myIntroInputLayout.addWidget(self.intro_label)
        self.myAircraftsInputLayout.addWidget(self.label)
        self.myAircraftsInputLayout.addWidget(self.aircrafts)
        self.myEndTimeInputLayout.addWidget(self.end_time_label)
        self.myEndTimeInputLayout.addWidget(self.end_time)
        self.myRandomBasesInputLayout.addWidget(self.random_btn)
        self.myRandomBasesInputLayout.addWidget(self.num_bases)
        self.myBasesInputLayout.addWidget(self.select_bases)
        self.myBasesInputLayout.addWidget(self.ComboBox)
        self.myButtonsLayout.addWidget(self.generate_data_btn)
        myBoxLayout.addLayout(self.myIntroInputLayout)
        myBoxLayout.addLayout(self.myAircraftsInputLayout)
        myBoxLayout.addLayout(self.myEndTimeInputLayout)
        myBoxLayout.addLayout(self.myRandomBasesInputLayout)
        myBoxLayout.addLayout(self.myBasesInputLayout)
        myBoxLayout.addLayout(self.myButtonsLayout)

        self.select_bases.toggled.connect(self.activate_btn)
        self.generate_data_btn.clicked.connect(self.generate_data_function)
    
    def activate_btn(self):
        if self.select_bases.isChecked() == True:
            self.ComboBox.setEnabled(True)
            self.num_bases.setEnabled(False)
        else:
            self.ComboBox.setEnabled(False)
            self.num_bases.setEnabled(True)

    def generate_data_function(self):
        aircrafts = int(self.aircrafts.displayText())
        end_time = str(self.end_time.displayText())
        if self.random_btn.isChecked() == True:
            bases = int(self.num_bases.displayText())
        elif self.select_bases.isChecked() == True:
            bases = self.ComboBox.check_items()

        generate_data(aircrafts, bases, end_time)
        


if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    dialog_1 = Dialog_01()
    dialog_1.show()
    app.exec_()
    