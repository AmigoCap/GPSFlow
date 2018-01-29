# coding utf8
from math import radians, cos, sin, asin, sqrt
import parser

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371000 * c
    return km


def getDistance(dataFrame):
    distance = []
    for i in range(dataFrame['timestampMs'].size - 1):
        distance.append(haversine(
            dataFrame["longitude"][i],
            dataFrame["latitude"][i],
            dataFrame["longitude"][i+1],
            dataFrame["latitude"][i+1]))
    distance.append(0)
    dataFrame['distance'] = distance

    return dataFrame

def calculateVelocity(dist, t1, t2):
    #Velocity in m/s
    v1 = (dist)/((float(t2)-float(t1))*pow(10, -3))
    #Velocity in km/h
    v2 = v1*3.6
    return v2

def getVelocity(dataFrame):
    velocities = []
    for i in range(dataFrame['timestampMs'].size - 1):
        velocities.append(calculateVelocity(
            dataFrame["distance"][i],
            dataFrame["timestampMs"][i+1],
            dataFrame["timestampMs"][i]
        ))
    velocities.append(0)

    dataFrame['velocity'] = velocities

    return dataFrame