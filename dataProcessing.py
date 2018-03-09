import parser
import distance
import math
import numpy as np
import gmplot
import colors
from sklearn.cluster import DBSCAN
import geocoder
from tqdm import tqdm
import json
import sys
import os.path
import speedClassification as speedClass

def filterPerfectDuplicates(df):
    size = df['date'].size
    lat = []
    lng = []
    to_keep = []

    for i in range(size):
        if df['latitude'][i] in lat and df['longitude'][i] in lng:
            to_keep.append(False)
        else:
            to_keep.append(True)
            lat.append(df['latitude'][i])
            lng.append(df['longitude'][i])

    df['to_keep'] = to_keep
    return df[df['to_keep'] == True].reset_index(drop=True)

def filterByAngle(df, min_angle):
    size = df['date'].size
    to_keep = []
    to_keep.append(True)

    for i in range(1, size - 1):
        lat0 = df['latitude'][i - 1]
        lng0 = df['longitude'][i - 1]
        lat1 = df['latitude'][i]
        lng1 = df['longitude'][i]
        lat2 = df['latitude'][i + 1]
        lng2 = df['longitude'][i + 1]

        d1 = distance.haversineDistance(lng1, lat1, lng2, lat2)
        d2 = distance.haversineDistance(lng1, lat1, lng0, lat0)

        if d1 < 50 or d2 < 50:
            to_keep.append(True)
        else:
            a = getAngle(lat0, lng0, lat1, lng1, lat2, lng2)

            if a > min_angle:
                to_keep.append(True)
            else:
                to_keep.append(False)

    to_keep.append(True)

    df['to_keep'] = to_keep
    return df[df['to_keep'] == True].reset_index(drop=True)

def getAngle(x0, y0, x1, y1, x2, y2):
    scalaire = (x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)
    norm1 = np.sqrt(math.pow((x0 - x1), 2) + math.pow((y0 - y1), 2))
    norm2 = np.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
    value = (scalaire / (norm1 * norm2))

    # Protect arccos
    if value > 0.9999:
        value = 0.9999
    elif value < -0.9999:
        value = -0.9999

    angle = np.arccos(value) * 180 / math.pi
    return angle

def filterBySpeed(df, speed_limit) :
    return df[df['velocity'] < speed_limit].reset_index(drop=True)

def filterByMedian(df, n=2, min_delay=150):
    lat_list = df['latitude'].tolist()
    lng_list = df['longitude'].tolist()
    size = len(lng_list)

    if size < 2 * n + 1:
        return lat_list, lng_list

    lat = []
    lng = []

    for i in range(n):
        lat.append(lat_list[i])
        lng.append(lng_list[i])

    for i in range(n, size - n):
        if df['delay'][i] < min_delay and df['delay'][i - 1] < min_delay:
            lat_window = df['latitude'][i - n:i + n + 1].tolist()
            lat_window.sort()
            lng_window = df['longitude'][i - n:i + n + 1].tolist()
            lng_window.sort()
            lat.append(lat_window[n])
            lng.append(lng_window[n])
        else:
            lat.append(lat_list[i])
            lng.append(lng_list[i])

    for i in range(n):
        lat.append(lat_list[size - n + i])
        lng.append(lng_list[size - n + i])

    df["latitude"] = lat
    df["longitude"] = lng

    return df

def fdistance(df, i, j) :
    return distance.haversineDistance(
        df["longitude"][i],
        df["latitude"][i],
        df["longitude"][j],
        df["latitude"][j])

def isInMouvement(i, lower_limit, radius, df) :
    in_mouvement = False
    for k in range(lower_limit) :
        if (fdistance(df, i, i + k + 1) > radius) :
            in_mouvement = True
    return in_mouvement

def findSegments(df, lower_limit, radius, max_outliers):
    start_stay_points = []
    end_stay_points = []
    i = 0
    j = 0

    size = df["timestampMs"].size - max(lower_limit, max_outliers) - 1

    while i < size and j < size:
        if isInMouvement(i, lower_limit, radius, df):
            # Si on est en mouvement, suivant
            i += 1
        else:
            # Si on est immobile, trouver jusqu'a quel indice
            start_index = i

            outliers = max_outliers
            j = i + 1

            total_time_in_st = 0

            while outliers >= 0 and j < size:
                if fdistance(df, i, j) > radius:
                    outliers -= 1
                else:
                    outliers = max_outliers
                total_time_in_st += df["delay"][j]
                j += 1

            i = j - max_outliers - 1
            end_index = i

            if total_time_in_st > 500:
                # print("Time in st : " + str(total_time_in_st))
                start_stay_points.append(start_index)
                end_stay_points.append(end_index)
            else:
                # print("Not enough time in st : " + str(total_time_in_st))
                continue

    segments = []

    if len(start_stay_points) == 0 :
        segments.append(df)
        return segments, []
    else :
        s = df[: start_stay_points[0] + 1]
        segments.append(s.reset_index(drop=True))

        for i in range(len(end_stay_points) - 1):
            s = df[end_stay_points[i] - 1: start_stay_points[i + 1] + 1]
            segments.append(s.reset_index(drop=True))

        s = df[end_stay_points[len(end_stay_points) - 1]:]
        segments.append(s.reset_index(drop=True))

        points = []
        for i in range(len(start_stay_points)) :
            lat=0
            lng=0
            for k in range(start_stay_points[i], end_stay_points[i]):
                lat+=df["latitude"][k]/(end_stay_points[i]-start_stay_points[i])
                lng+=df["longitude"][k]/(end_stay_points[i]-start_stay_points[i])
            points.append({"lat":lat, "lng":lng, "start":df["timestampMs"][start_stay_points[i]], "end":df["timestampMs"][end_stay_points[i]], "addr":"Unknown"})

        return segments, points

def groupPoints(points, epsilon=150, min_samples=1) :

    if not points :
        return []

    meters = []

    for p in points :
        coords = []
        coords.append(distance.haversineDistance(0, p["lat"], 0, 0))
        coords.append(distance.haversineDistance(p["lng"], 0, 0, 0))
        meters.append(coords)

    db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(meters)
    labels = db.labels_

    unique_labels = set(labels)

    for current_label in unique_labels :
        lat_sum = 0
        lng_sum = 0
        count = 0
        for i in range((len(points))) :
            if labels[i] == current_label :
                lat_sum += points[i]["lat"]
                lng_sum += points[i]["lng"]
                count+=1
        for i in range(len(points)):
            if labels[i]==current_label:
                points[i]["label"] = current_label
                points[i]["lat"] = lat_sum/count
                points[i]["lng"] = lng_sum/count

    return points

def reverseGeocode(points, segments):
    for p in points:
        address = "Unknown"

        for i in range(5):
            g = geocoder.google([p[0], p[1]], method='reverse')
            if g.address is not None:
                address = g.address
                break
        p.append(address)

    for s in segments:
        lat = s['latitude'][0]
        lng = s['longitude'][0]

        point = findClosest(lat, lng, points)
        print (point[2])

def findClosest(lat, lng, points) :
    min = distance.haversineDistance(lng, lat, points[0][1], points[0][0])
    result = points[0]
    for p in points :
        dist = distance.haversineDistance(lng, lat, p[1], p[0])
        if dist < min :
            min = dist
            result = p
    #print (min)
    return result

def getUniqueDays(complete_df) :
    sequence = complete_df['date'].tolist()
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def cleanupColumns(segments) :

    for s in segments :
        s['ts'] = s['timestampMs']
        s['lat'] = s['latitude']
        s['lng'] = s['longitude']

    #columns = ["timestampMs", "latitude", "longitude", "date", "time", "delay", "distance", "velocity"]
    columns = ["ts", "lat", "lng"]
    for s in segments :
        for col in list(s) :
            if col not in columns :
                del s[col]

    return segments

def removeSmallSegments(segments, nb_points, min_dist) :
    k=0
    while k <len(segments):
        if len(segments[k])<nb_points:
            total_dist=0
            for i in range(1, len(segments[k])):
                total_dist+=distance.haversineDistance(segments[k]["longitude"][i-1], segments[k]["latitude"][i-1], segments[k]["longitude"][i], segments[k]["latitude"][i])
            if total_dist<min_dist:
                segments.pop(k)
                k-=1
        k+=1
    return segments

def prepareDataKMeans(lSegments):
    for segment in lSegments:
        segment['dist'] = speedClass.getDistances(segment)
        segment['vel'] = speedClass.getVelocities(segment)
        segment['speedClass'] = speedClass.initSpeedClass(segment)
        segment['numSC'] = speedClass.initSpeedClass(segment)
    return lSegments

def fullSpeedSegmentation(lSegments):
    for segment_mouvement in lSegments:
        if len(segment_mouvement['vel'])>2:
            (lK,whitened)=speedClass.applyKMeans(segment_mouvement,
                                                 k=int(len(segment_mouvement['vel'])/10)+1)

            lBoundiaries=speedClass.getBoundiaries(lK)
            lFirstSpeedSegmentation=speedClass.calcFirstSegmentation(lBoundiaries,whitened,bPadd=False)
            lFirstSpeedSegmentation=speedClass.cancelWhithen(lFirstSpeedSegmentation,segment_mouvement)
            (speedAgglomerates,a)=speedClass.agglomerateSpeedSegments(lFirstSpeedSegmentation,
                                                                      lowThreshold=8,
                                                                      highThreshold=40,bMedian=False)
            offset=0
            lSpeedClass=[]
            numSC=[]
            for ii, plots in enumerate(speedAgglomerates):
                for jj, speed in enumerate(plots):
                    lSpeedClass.append(a[ii])
                    numSC.append(ii)
                offset+=jj
            segment_mouvement['speedClass']=lSpeedClass
            segment_mouvement['numSC']=numSC
    return lSegments


def pipeline(day, complete_df) :
    min_angle=15
    max_speed=150
    med_window=2
    med_delay=150
    sp_min=3
    sp_radius=50
    sp_outliers=5

    df = parser.selectDate(day, complete_df)
    df_duplicates = filterPerfectDuplicates(df)
    df_angle = filterByAngle(df_duplicates, min_angle)
    df_speed = filterBySpeed(df_angle, max_speed)
    df_med = filterByMedian(df_speed, n=med_window, min_delay=med_delay)
    segments, points = findSegments(df_med, sp_min, sp_radius, sp_outliers)
    segments = removeSmallSegments(segments, 5, 30)
    points = groupPoints(points)
    segments = cleanupColumns(segments)

    segments=prepareDataKMeans(segments)
    segments=fullSpeedSegmentation(segments)


    return segments, points

def generateJson(complete_df) :
    days = getUniqueDays(complete_df)
    result = "{ \"days\" : ["

    for i in range(len(days)) :
        segments, points = pipeline(days[i], complete_df)
        result += createDayJson(days[i], segments, points)
        result += ","
        print ("... Day " + str(i) + "/" + str(len(days)))

    result = result[:-1] + "]}"

    return result

def getPointsCount(segments) :
    result = 0
    for s in segments :
        result += s['ts'].size
    return str(result)

def createDayJson(date, segments, points) :
    result = "{"

    # Date and points_count
    result += " \"date\" : \"" + date + "\","
    result += " \"points_count\" : " + getPointsCount(segments) + ","

    # Segments
    result += "\"segments\" : ["
    for i in range(len(segments)) :
        result += "{ \"segment_id\" : " + str(i) + ","
        result += " \"points\" : "
        result += segments[i].to_json(path_or_buf=None, orient='records')
        result += "},"
    result = result[:-1] + "],"

    # Stay points
    result += "\"staypoints\" :"
    result += json.dumps(str(points))

    result += "}"

    return result

if __name__ == "__main__" :

    if len(sys.argv) == 1 :
        print("How to use : Give a path to the Google Takout JSON file to process.")
        print("Download your location history here")
        print("https://takeout.google.com/settings/takeout?pli=1")

    else :
        filepath = str(sys.argv[1])

        if os.path.isfile(filepath) and filepath.endswith('.json'):
            print("Import Json...")
            android_df = parser.importJson(filepath)
            print("Done !")

            print("Process trajectories...")
            json = generateJson(android_df)
            print("Done !")

            print("Write to output.json...")
            file = open("output.json", "w")
            file.write(json)
            file.close()
            print("Done !")

        elif not filepath.endswith('.json') :
            print("File must be in JSON format.")

        else :
            print("Could not find this file.")
