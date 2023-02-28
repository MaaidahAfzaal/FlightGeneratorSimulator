import numpy as np
from config_parameters import*
import time
from datetime import datetime 
import random
import geopy
import geopy.distance 
from geographiclib.geodesic import Geodesic
from trace_track import path_generator

def get_data(group):
    """
        Function to generate dataframe containing data in the form required by user

    Args:
        group (dict): Dictionary containing all info entered by user

    Returns:
        data(array): data containg all track info including coords and time
    """
    # Getting necessary values from dictionary
    t12 = get_current_time()

    latitudes = group["Waypoints"]["Latitude"]
    longitudes = group["Waypoints"]["Longitude"]
    speed = group["Waypoints"]["Speed"]
    altitude = group["Waypoints"]["Altitude"]
    aircrafts = group["Aircrafts"]
    track_no = group["Sys Track No"]
    track_id = group["Track ID"]
    init_speed = group["Initial Speed"]
    mode_info = group["Mode Info"]
    if "Aircrafts Pos" in group.keys():
        aircraft_pos = group["Aircrafts Pos"]
    if group["Origin"] != "Unknown":
        origin_lat, origin_lon = IAF_BASES[group["Origin"]]
        # Adding origin lat long to waypoints array
        latitudes = np.insert(latitudes, 0, origin_lat)
        longitudes = np.insert(longitudes, 0, origin_lon)
        # Adding initial altitude to array
        altitude =  np.insert(altitude, -1, 0)

    # Calling function to format time to milliseconds
    init_time = format_time(group["Initial Time"], group["Date"]) 
    end_time = 0 if group["End Time"] == "" else format_time(group["End Time"], group["Date"])

    # Finding distance between each waypoint
    dist = [geopy.distance.geodesic((latitudes[i], longitudes[i]), (latitudes[i+1]\
        , longitudes[i+1])).km for i in range(len(latitudes)-1)]

    
    if not "Aircrafts Pos" in group.keys():
        old_lat, old_long, rel_heading = get_rel_heading(aircrafts, latitudes[0], longitudes[0])
    else:
        # Creating dictionary that will contain lat longs of each aircraft according \
        # to their distance and heading from ref 
        old_lat = dict()
        old_long = dict()
        for i in range(1, aircrafts + 1):
            old_lat[str(i)] = latitudes[0]
            old_long[str(i)] = longitudes[0]

    # Finding speed if end time is given
    if end_time != 0:
        const_speed = get_speed(dist, init_time, end_time)
        speed = np.empty(len(latitudes))
        speed.fill(const_speed)
    elif (end_time == 0) and (group["Origin"] != "Unknown"):
        speed =  np.insert(speed, 0, init_speed)

    # Finding time taken to travel between each waypoint
    time_intervals = get_time_intervals(dist, speed)

    #  Finding heading at each point
    heading = [Geodesic.WGS84.Inverse(latitudes[i], longitudes[i], latitudes[i+1]\
        , longitudes[i+1])["azi1"] for i in range(len(latitudes)-1)]


  
    track = []
    data = []

    # Looping over all time_intervals
    for r in range(len(time_intervals)):
        # Finding total steps between each way point depending on time step
        steps = time_intervals[r] / TIME_STEP
        # Finding the lat longs at each step between waypoints
        track.append(path_generator(longitudes[r], longitudes[r+1], latitudes[r], \
            latitudes[r+1], steps, steps))

    # Looping over all waypoints
    for r in range(len(track)):
        for t in range(len(track[r])):
            # Adding offset to aircrafts formation
            for key in old_lat:
                old_lat[key] = track[r][t][1]
                old_long[key] = track[r][t][0]

            if (aircrafts > 1) and "Aircrafts Pos" in group.keys(): old_lat, old_long = add_formation(aircraft_pos, heading[r], track[r][t][1], track[r][t][0])
            elif (aircrafts > 1) and not "Aircrafts Pos" in group.keys(): old_lat, old_long = add_offsets(heading[r], rel_heading, old_lat, old_long)
            # Adjusting heading to write
            if heading[r] < 0:
                heading[r] += 360

            # Adding track info for all aircrafts to data     
            for s in track_no:
                data.append([str(-1)] * 9)
                data[-1][SYS_TRACK_NO] = track_no[s]
#                data[-1][PLATFORM] = group["Platform"]
                data[-1][PLATFORM] = group["Platform"][s]
                data[-1][LATITUDE] = old_lat[s]
                data[-1][LONGITUDE] = old_long[s]
                data[-1][TRACK_ID_COLUMN] = TRACK_ID[track_id[s]]
                data[-1][SPEED] = speed[r]
                data[-1][HEADING] = heading[r]
                data[-1][ALTITUDE] = altitude[r]
                data[-1][TIME] = init_time
                # data.append([track_id[s], group["Platform"], old_lat[s+1], old_long[s+1], \
                #     altitude[r], speed[r], heading[r], mode_info["IFF Mode 1"][str(s+1)], init_time]) 
            init_time += TIME_STEP
            
            # Track is present for FINAL_TIME(1 mins) amount of time at last waypoint
            if r == (len(track)-1) and t == (len(track[r])-1):
                for i in range(FINAL_TIME):
                    for s in track_no:
                        data.append([str(-1)] * 9)
                        data[-1][SYS_TRACK_NO] = track_no[s]
#                        data[-1][PLATFORM] = group["Platform"]
                        data[-1][PLATFORM] = group["Platform"][s]
                        data[-1][LATITUDE] = old_lat[s]
                        data[-1][LONGITUDE] = old_long[s]
                        data[-1][TRACK_ID_COLUMN] = TRACK_ID[track_id[s]]
                        data[-1][SPEED] = speed[r]
                        data[-1][HEADING] = heading[r]
                        data[-1][ALTITUDE] = altitude[r]
                        data[-1][TIME] = init_time
                        # data.append([track_id[s], group["Platform"], old_lat[s+1], old_long[s+1], \
                        #     altitude[r], speed[r], heading[r], mode_info["IFF Mode 1"][str(s+1)], init_time]) 
                    init_time += TIME_STEP

    t13 = get_current_time()
    print("Time taken to create data array : ", (t13-t12))
    return data


def format_time(time, date):
    """
        Function to format time array to milliseconds

    Args:
        time (array): time array containing time of all waypoints

    Returns:
        milliseconds(array): array containing all time in milliseconds
    """

    date = datetime.strptime(date, '%d-%m-%Y')
    date_mil = date.timestamp()
#
    # Converting the time array from the input table to milliseconds    
    hrs, mins, secs = (["0", "0"] + time.split(":"))[-3:]
    hrs = int(hrs)
    mins = int(mins)
    secs = int(secs)
    milliseconds = int(3600 * hrs + 60 * mins + secs) 
    
    return (milliseconds + date_mil)


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


def get_speed(distance, init_time, end_time):
    """
        Function to get speed if end time is given
    """
    total_time = (end_time - init_time) / 3600
    total_distance = sum(distance)
    speed = (total_distance / total_time) / KM
    return speed

def get_time_intervals(dist, speed):
    """
        Function to find time taken to travel from one waypoint to the next

    Args:
        dist (float array): Distance between waypoints
        speed (float array): Speed of travel

    Returns:
        time_int(array): Array containing time intervals for each waypoint
    """
    time_int = []
    for i in range(len(dist)):
        time_int = np.append(time_int, ((dist[i] / (speed[i] * KM)) * 3600))

    return time_int

def add_formation(aircraft_pos, abs_heading, lat_ref, lon_ref):
    """
        Funciton to add offsets for greater than 1 aircraft in group
    Args:
        aircrafts_pos (dict): contains distance and angle of each aircraft wrt ref
        abs_heading (float) : absolute heading of formation from waypoint to next
        lat_ref (float): ref latitude
        lon_ref (float): ref longitude

    Returns:
        new_latitude(dict): dict containing latitudes of aircrafts with offset
        new_longitude(dict): dict containing longitudes of aircrafts with offset
    """

    ref = geopy.Point(lat_ref, lon_ref)

    new_latitude = {}
    new_longitude = {}
    
    for key in aircraft_pos:
        d = geopy.distance.distance(nautical= aircraft_pos[key]["distance"])
        new_latitude[key] = d.destination(point=ref, bearing=(aircraft_pos[key]["angle"] + abs_heading)).latitude
      
        new_longitude[key] = d.destination(point=ref, bearing=(aircraft_pos[key]["angle"] + abs_heading)).longitude

    return new_latitude, new_longitude


# def get_bearing(lat1, lon1, lat2, lon2):
#     """
#         Function to find heading / bearing between two lat longs

#     Args:
#         lat1 (float)
#         lon1 (float)
#         lat2 (float)
#         lon2 (float)

#     Returns:
#         B(float) : Heading/ bearing between lat longs
#     """
#     X = math.cos(lat2) * math.sin(lon2-lon1)
#     Y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) \
#         * math.cos(lon2 - lon1)
#     B = math.atan2(X, Y)
#     B = math.degrees(B)
#     B = (B + 360) % 360
#     B = 360 - B

#     P = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)["azi1"]
#     return P

# def latlong(old_lat, old_long, distance, heading):
#     """
#         Function to calculate lat long

#     Args:
#         old_lat (float): old latitude coord
#         old_long (float): old longitude coord
#         distance (float): distance travelled
#         heading (int): heading

#     Returns:
#         new_lat(float): new latitude coord
#         new_long(float): new longitude coord
#     """
#     # Converting old lat long to radians
#     old_lat = math.radians(old_lat)
#     old_long = math.radians(old_long)
    
#     # Converting heading to radians
#     heading = math.radians(heading)

#     # Finding new lat long
#     new_lat = math.asin(math.sin(old_lat) * math.cos(distance / R) + \
#     math.cos(old_lat) * math.sin(distance / R) * math.cos(heading)) 

#     new_long = old_long + math.atan2(math.sin(heading) * math.sin(distance / R) \
#         *math.cos(old_lat), math.cos(distance / R) - math.sin(old_lat) * \
#             math.sin(new_lat))

#     # Converting new lat long back to degrees
#     new_lat = math.degrees(new_lat)
#     new_long = math.degrees(new_long)

#     return new_lat, new_long

def get_rel_heading(aircrafts, lat, lon):

    # diff_heading = 360 / aircrafts
    # x = 0
    rel_heading = dict()
    old_lat = dict()
    old_long = dict()
    for i in range(1, aircrafts + 1):
        rel_heading[str(i)] = random.randint(0, 360)
        # rel_heading[str(i)] = x + diff_heading
        old_lat[str(i)] = lat
        old_long[str(i)] = lon
        # x += diff_heading

    return old_lat, old_long, rel_heading


# def get_latlong_dist(lat, lon):
#     """
#         Function to get distance between two lat longs

#     Args:
#         lat (array): Latitudes of all waypoints
#         lon (array): Longitudes of all waypoints

#     Returns:
#         dist(array): Distance between each waypoint
#     """
#     dist = [geopy.distance.geodesic((lat[i], lon[i]), (lat[i+1], lon[i+1])).km for i in range(len(lat)-1)]
#     dist = []
#     lat = [math.radians(d) for d in lat]
#     lon = [math.radians(d) for d in lon]
#     for i in range(len(lat)-1):
#         # # Using math
#         # d = 3443.92 * math.acos(math.sin(lat[i]) * math.sin(lat[i+1]) + math.cos(lat[i]) \
#         #      * math.cos(lat[i+1]) * math.cos(lon[i+1] - lon[i])) * KM
#         # dist.append(d)

#         # Using geopy library (doesn't work on qgis yet!!)
#         dist.append(geopy.distance.geodesic((lat[i], lon[i]), (lat[i+1], lon[i+1])).km)   

#     return dist


def add_offsets(abs_heading, rel_heading, latitude, longitude):
    """
        Funciton to add offsets for greater than 1 aircraft in group
    Args:
        aircrafts (int): number of aircrafts in group
        latitude (array): array of length of aircrafts containing latitudes without offset
        longitude (array): array of length of aircrafts containing longitudes without offset

    Returns:
        latitude(array): array containing latitudes of aircrafts with offset
        longitude(array): array containing longitudes of aircrafts with offset
    """
    # for key in latitude:
    #     latitude[key] = math.radians(latitude[key])
    #     longitude[key] = math.radians(longitude[key])
   
    new_latitude = dict()
    new_longitude = dict()

    for i in latitude.keys():
        heading = rel_heading[i] + abs_heading
        if heading >= 360:
           heading -= 360
        heading = 360 - heading
        # heading = math.radians(heading)

        location = geopy.Point(latitude[i], longitude[i])
        nm = random.random()
        d = geopy.distance.distance(kilometers = nm)

        new_latitude[i] = d.destination(location, heading).latitude
      
        new_longitude[i] = d.destination(location, heading).longitude
        # new_latitude[i] = math.degrees(math.asin(math.sin(latitude[i]) * math.cos(D / R) + \
        #     math.cos(latitude[i]) * math.sin(D / R) * math.cos(heading)))
        
        # new_longitude[i] = math.degrees(longitude[i] + math.atan2(math.sin(heading) \
        #     * math.sin(D / R) * math.cos(latitude[i]), math.cos(D / R) \
        #         - math.sin(latitude[i]) * math.sin(new_latitude[i])))

    return new_latitude, new_longitude
    