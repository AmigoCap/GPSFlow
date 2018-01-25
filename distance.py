# coding utf8
from math import radians, cos, sin, asin, sqrt
import data_parser as parser

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


def getDistance(file):
    df = file
    distance = []
    for i in range(df['timestampMs'].size - 1):
        distance.append(haversine(
                        df["longitude"][i],
                        df["latitude"][i],
                        df["longitude"][i+1],
                        df["latitude"][i+1]))
    distance.append(0)
    df['distance'] = distance

    return df

def velocity(dist, t1, t2):
    #Vitesse en metre par seconde
    v1 = (dist)/((float(t2)-float(t1))*pow(10, -3))
    #Vitesse en km/h
    v2 = v1*3.6
    return v2

def getVitesse(file):
    df = file
    vitesse = []
    for i in range(df['timestampMs'].size - 1):
        vitesse.append(velocity(
            df["distance"][i],
            df["timestampMs"][i+1],
            df["timestampMs"][i]
        ))
    vitesse.append(0)

    df['vitesse'] = vitesse

    return df

