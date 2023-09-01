from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import*
from PyQt5.uic import loadUi


# Required for using Qgs class
DIST_AREA = QgsDistanceArea()
DIST_AREA.setEllipsoid('WGS84')
NM_TO_M = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceNauticalMiles, QgsUnitTypes.DistanceMeters)

DELAY_TIME = 1000
########################################## PATH CONSTANTS #########################################################

PATH_BORDER_SHP = "D:\\ScenarioGenratorQGIS\\Layers\\PakistanIBPolyline.shp"

########################################### COLOR CONSTANTS #######################################################

COLOR_MAP_LAYER = Qt.green
COLOR_POINTS_LAYER = QColor(148, 255, 210)
COLOR_WAYPOINTS_LAYER = Qt.yellow
COLOR_BLACK = Qt.black
COLOR_START = QColor(32, 125, 57)
COLOR_RED = Qt.red
COLOR_BLUE = Qt.blue
COLOR_DROP = QColor(109, 135, 100)
COLOR_SHOW = QColor(118, 96, 138)
COLOR_VPS = QColor(147, 112, 219)

########################################### TABLE CONSTANTS ######################################################

TABLE_HEADER = ['Track No.', 'Base', 'Speed (Nm)', 'Height (ft)', 'Track ID', 'Platform', 'Start All', 'Drop All']

##################################################################################################################

IAF_BASES = {
    "Ambala" : [30.370556, 76.817778],
    "Adampur" : [31.434879, 75.757256],
    "Armritsar" : [31.707778, 74.799167],
    "Awantipur" : [33.876628, 74.975681],
    "Gurugram" : [28.437098, 77.028544],
    "Faridabad" : [28.371888, 77.276432],
    "Hindon" : [28.707647, 77.35934],
    "Sirsa" : [29.562778, 75.005278],
    "Srinagar" : [33.994374, 74.765299],
    "Bathinda" : [30.268848, 74.75743],
    "Chandigarh" : [30.676290, 76.788535],
    "Faridabad" : [28.371888, 77.028544],
    "Halwara" : [30.748041, 75.633209],
    "Vadsar" : [23.146200, 72.481270],
    "Leh" : [34.137216, 77.546614],
    "Palam" : [34.137216, 77.114610],
    "Pathankot" : [32.236929, 75.633227],
    "Sarsawa" : [29.0993718, 77.430671],
    "Udhampur" : [32.911503, 75.154410],
    "Purnea" : [26.681111, 88.328611],
    "Bagdogra" : [26.681111, 88.328611],
    "Barapani" : [25.703611, 91.978611],
    "Barrackpore" : [22.781944, 88.359167],
    "Chabua" : [27.462222, 95.118056],
    "Hasimara" : [26.698056, 89.368889],
    "Jorhat" : [26.731667, 94.175556], 
    "Kalaikunda" : [22.339417, 87.214547],
    "Kumbhigram" : [24.913056, 92.978611],
    "Mohanbari" : [27.480556, 95.021667],
    "Mounain Shadow" : [26.106111, 91.585833],
    "Panagarh" : [23.474444, 87.4275],
    "Tawang" : [27.588611, 91.877778],
    "Tezpur" : [26.712222, 92.787222],
    "Agra" : [27.1575, 77.960833],
    "Bakshi Ka Talab" : [26.988611, 80.891389],
    "Bamrauli" : [25.44, 81.733889],
    "Bareilly" : [28.4225, 79.446944],
    "Bihhta" : [25.590833, 84.883333],
    "Chakeri" : [26.402778, 80.412222],
    "Darbhanga" : [26.194722, 85.9175],
    "Gorakhpur" : [26.739444, 83.449444],
    "Maharajpur" : [26.293333, 78.227778],
    "Car Nicobar" : [9.1525, 92.819722],
    "Sulur" : [11.013611, 77.159722],
    "Port Blair" : [11.641111, 92.729722],
    "Tambram" : [12.906944, 80.121111],
    "Thanjavur" : [10.722222, 79.101389],
    "Trivandrum" : [8.48, 76.92],
    "Suratgarh" : [29.387778, 73.903889],
    "Bhuj" : [23.287778, 69.67],
    "Deesa" : [24.268056, 72.204444],
    "Jaisalmer" : [26.889167, 70.864444],
    "Jamnagar" : [22.466389, 70.011389],
    "Jodhpur" : [26.251389, 73.048056],
    "Lohegaon" : [18.581944, 73.919444],
    "Nal-Bikaner" : [28.0725, 73.206667],
    "Naliya" : [23.22, 68.9],
    "Phalodi" : [27.112778, 72.388889],
    "Uttarlai" : [25.812778, 71.482222],
    "Makarpura" : [22.329444, 73.219444],
    "Begumpet" : [17.452222, 78.461111],
    "Bidar" : [17.907778, 77.485833],
    "Dundigal" : [17.629167, 78.403333],
    "Hakimpet" : [17.553333, 78.524722],
    "Yelahanka" : [13.135833, 77.605556],
    "Nagpur" : [21.091944, 79.046944],
    "Ojhar" : [20.119444, 73.913611],
    "Devlail" : [19.8551, 73.80375]
}

# Radius of the Earth in kms
R = 6371

# Time interval after which data is recorded in secs
TIME_STEP = 1

# Time in mins = (min * 60000) for which to keep aircraft in final pos after waypoints completed
FINAL_TIME = 1 

# Knots to km conversion
KM = 1.852

# Distance between aircrafts in meters
D = 7

# Path to store track files
VS_PATH = "./Track Files/"

# Columns to add in excel file 
COL = ['TrackNumber', 'Platform', 'TrackLatitude', 'TrackLongitude', 'Track Id',
            'TrackLatLongAltitude', 'TrackSpeed', 'TrackHeading', 'EpocTimeMilliSeconds']

COL_CARTESIAN = ['TrackNumber', 'Platform', 'Track-X', 'Track-Y', 'Track Id',
            'Track-Z', 'TrackSpeed', 'TrackHeading', 'EpocTimeMilliSeconds']

SYS_TRACK_NO = 0
PLATFORM = 1
LATITUDE = 2
LONGITUDE = 3
TRACK_ID_COLUMN = 4
ALTITUDE = 5
SPEED = 6
HEADING = 7
TIME = 8

# Platform types array
PLATFORMS = ['Su-30', 'Mig-29', 'Mirage', 'Rafale', 'Tejas', 'Embraer', 'Mir-2000', 'Unknown', 'EMB-145', 'Force Multiplier']

# EW platforms
EW_PLAT = ['Embraer', 'Force Multiplier', 'EMB-145']

# Dictionary of all ATS paths and their distances in kms
GRAPH = {
    'BHILWARA': {'PATHANKOT': 463.6466449596023, 'BHUNTAR': 430.7902259530373,\
        'PANTNAGAR': 336.8607549599949, 'AGRA': 201.0316871361072, \
            'AHMEDABAD': 660.4444242548517, 'SURATGARH': 267.79586146722573, \
                'KOTA': 325.1014315755097}, 
    'AGRA': {'BHILWARA': 201.0316871361072, 'JHANSI': 194.2062289089977}, 
    'BARAMULA': {'JAMMU': 174.70387024612293, 'LEH': 291.5756380398763}, 
    'PATHANKOT': {'JAMMU': 90.62237937082519, 'LEH': 276.70532832259494, \
        'BHILWARA': 463.6466449596023, 'SURATGARH': 355.90174090467525}, 
    'AHMEDABAD': {'BHILWARA': 660.4444242548517, 'SURATGARH': 711.2246628683173, \
        'DAHOD': 327.31946517947534, 'KOTA': 400.0589337483766}, 
    'JAMMU': {'BARAMULA': 174.70387024612293, 'PATHANKOT': 90.62237937082519}, 
    'LEH': {'BARAMULA': 291.5756380398763, 'PATHANKOT': 276.70532832259494, \
        'BAREILLY': 658.7714449414464, 'PANTNAGAR': 594.4610300678962, \
            'BHUNTAR': 253.41576596783472}, 
    'BHOPAL': {'JHANSI': 273.8509817855237, 'JABALPUR': 278.5274797226497, \
        'DAHOD': 169.08198368470912}, 
    'KHAJURAO': {'KALYANPUR': 190.9973085143511, 'JABALPUR': 182.3640514289688}, 
    'JABALPUR': {'KHAJURAO': 182.3640514289688, 'BHOPAL': 278.5274797226497}, 
    'SURATGARH': {'PATHANKOT': 355.90174090467525, 'BHILWARA': 267.79586146722573, \
        'AHMEDABAD': 711.2246628683173}, 
    'BAREILLY': {'LEH': 658.7714449414464, 'KALYANPUR': 224.5440108431291}, 
    'DAHOD': {'BHOPAL': 169.08198368470912, 'AHMEDABAD': 327.31946517947534}, 
    'PANTNAGAR': {'LEH': 594.4610300678962, 'BHILWARA': 336.8607549599949}, 
    'JHANSI': {'AGRA': 194.2062289089977, 'BHOPAL': 273.8509817855237}, 
    'KALYANPUR': {'BAREILLY': 224.5440108431291, 'KHAJURAO': 190.9973085143511}, 
    'KOTA': {'BHILWARA': 325.1014315755097, 'AHMEDABAD': 400.0589337483766}, 
    'BHUNTAR': {'LEH': 253.41576596783472, 'BHILWARA': 430.7902259530373}
}

# Ratio to convert QWindow pixels to Nm for formation distance
P_TO_Nm = 2/40


######################## PRE-DEFINED FORMATIONS ################################

FORMATIONS ={
    "LEAD_TRAIL" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 5,
            "angle" : 180
        }
    },

    "BEARING" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 4.3,
            "angle" : 215
        }
    },

    "LINE_ABREAST" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 5,
            "angle" : 270
        },
        "3" : {
            "distance" : 5,
            "angle" : 90
        },
        "4" : {
            "distance" : 10,
            "angle" : 90
        }
    },

    "CONTAINER":  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 5,
            "angle" : 90
        },
        "3" : {
            "distance" : 5,
            "angle" : 180
        },
        "4" : {
            "distance" : 7.07,
            "angle" : 135
        }
    },

    "STRINGER" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 5.5,
            "angle" : 326.6
        },
        "3" : {
            "distance" : 5.5,
            "angle" : 32.55
        }
    },

    "WEDGE" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 5,
            "angle" : 216.7
        },
        "3" : {
            "distance" : 5,
            "angle" : 142.3
        }
    },

    "TWO_GROUPS_AZIMUTH" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 1.7,
            "angle" : 244.17
        },
        "3" : {
            "distance" : 6.5,
            "angle" : 262.5
        },
        "4" : {
            "distance" : 7.95,
            "angle" : 269.64
        }
    },

    "RANGE" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 2,
            "angle" : 232
        },
        "3" : {
            "distance" : 7.55,
            "angle" : 180.7
        },
        "4" : {
            "distance" : 8.47,
            "angle" : 191.58
        }
    },

    "ECHELON_LEFT" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 1.9,
            "angle" : 227
        },
        "3" : {
            "distance" : 10,
            "angle" : 213.6
        },
        "4" : {
            "distance" : 10,
            "angle" : 223.6
        }
    },

    "ECHELON_RIGHT" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 1.9,
            "angle" : 228.2
        },
        "3" : {
            "distance" : 6.24,
            "angle" : 138.9

        },
        "4" : {
            "distance" : 7.88,
            "angle" : 133.7
        }
    },

    "CHAMPAGNE" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 1.85,
            "angle" : 273.1
        },
        "3" : {
            "distance" : 8.15,
            "angle" : 33.5
        },
        "4" : {
            "distance" : 7.23,
            "angle" : 21
        },
        "5" : {
            "distance" : 8.17,
            "angle" : 324.46
        },
        "6" : {
            "distance" : 9.43,
            "angle" : 315.2
        }
    },

    "VIC" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 1.6,
            "angle" : 88.2
        },
        "3" : {
            "distance" : 9.5,
            "angle" : 130.3
        },
        "4" : {
            "distance" : 8.35,
            "angle" : 137.4
        },
        "5" : {
            "distance" : 7.05,
            "angle" : 209.3
        },
        "6" : {
            "distance" : 7.96,
            "angle" : 219.4
        }
    },

    "BOX" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 2,
            "angle" : 90
        },
        "3" : {
            "distance" : 10,
            "angle" : 90
        },
        "4" : {
            "distance" : 11.85,
            "angle" : 90
        },
        "5" : {
            "distance" : 8.85,
            "angle" : 180
        },
        "6" : {
            "distance" : 8.93,
            "angle" : 168
        },
        "7" : {
            "distance" : 13,
            "angle" : 130
        },
        "8" : {
            "distance" : 14.66,
            "angle" : 126.4
        }
    },

    "WALL" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 1.86,
            "angle" : 117.255
        },
        "3" : {
            "distance" : 4.95,
            "angle" : 91.1
        },
        "4" : {
            "distance" : 6.53,
            "angle" : 96.14
        },
        "5" : {
            "distance" : 3.3,
            "angle" : 269.13
        },
        "6" : {
            "distance" : 4.9,
            "angle" : 258.23
        },
        "7" : {
            "distance" : 7.95,
            "angle" : 270.7
        },
        "8" : {
            "distance" : 9.47,
            "angle" : 265.45
        }
    },

    "THREE_GROUP_LADDER" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 2,
            "angle" : 90
        },
        "3" : {
            "distance" : 6,
            "angle" : 180
        },
        "4" : {
            "distance" : 6.3,
            "angle" : 162
        },
        "5" : {
            "distance" : 12,
            "angle" : 180
        },
        "6" : {
            "distance" : 12.2,
            "angle" : 170
        }
    },

    "FIVE_GROUP_LADDER" :  {
        "1" : {
            "distance" : 0,
            "angle" : 0
        },
        "2" : {
            "distance" : 2.1,
            "angle" : 90 #0
        },
        "3" : {
            "distance" : 4.4,
            "angle" : 180.65
        },
        "4" : {
            "distance" : 4.85,
            "angle" : 155
        },
        "5" : {
            "distance" : 8.9,
            "angle" : 179
        },
        "6" : {
            "distance" : 9.1,
            "angle" : 166.6
        },
        "7" : {
            "distance" : 13.3,
            "angle" : 180
        },
        "8" : {
            "distance" : 13.35,
            "angle" : 171.4
        },
        "9" : {
            "distance" : 17.35,
            "angle" : 180
        },
        "10" : {
            "distance" : 17.4,
            "angle" : 173.4
        }
    }
}

# Track IDs
TRACK_ID = {
    "No Statement": 0,
    "FIGHTER (HGF)": 1,
    "AEW/RECCE/EW/DECOY (HGA)": 1,
    "NOT SPECIFIED (UPG)": 3,

}

CLIENT_IP = "192.168.1.25"
SERVER_IP = "192.168.1.25"
CLIENT_PORT = 46725
SERVER_PORT = 6004
BUFFER_SIZE = 1000000