from math import radians, cos, sin, asin, sqrt

def haversineDistance(lon1, lat1, lon2, lat2):
    '''
    Computes the great circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    m = 6371000 * c
    return m

def getDistances(df):
    size = df['timestampMs'].size
    distances = []
    for i in range(size - 1):
        distances.append(haversineDistance(
            df["longitude"][i],
            df["latitude"][i],
            df["longitude"][i+1],
            df["latitude"][i+1]))

    distances.append(0)
    return distances

def computeVelocity(dist, t1, t2):
    #Velocity in m/s
    v1 = (dist) / ((float(t2)-float(t1))*pow(10, -3))
    #Velocity in km/h
    v2 = v1 * 3.6
    return v2

def getVelocities(df):
    size = df['timestampMs'].size
    velocities = []
    for i in range(size - 1):
        velocities.append(computeVelocity(
            df["distance"][i],
            df["timestampMs"][i+1],
            df["timestampMs"][i]
        ))

    velocities.append(0)
    return velocities

def getAccelerations(df) :
    size = df['timestampMs'].size
    accelerations = []
    for i in range(size - 1):
        accelerations.append(computeVelocity(
            df["velocity"][i],
            df["timestampMs"][i+1],
            df["timestampMs"][i]
        ))

    accelerations.append(0)
    return accelerations