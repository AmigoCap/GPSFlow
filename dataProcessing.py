import parser
import distance
import math
import numpy as np
import gmplot
import colors
from sklearn.cluster import DBSCAN
import geocoder



def displayRawDay(day, complete_df, centerX=45.757589, centerY=4.831689, zoom=15) :
    df = parser.selectDate(day, complete_df)
    gmap = gmplot.GoogleMapPlotter(centerX, centerY, zoom, apikey="AIzaSyDsYwvF3UUxTx8RB40wd4SnUVzfnbW66LM")
    gmap.plot(df["latitude"], df["longitude"], colors.color_list[0], edge_width=1)
    gmap.scatter(df["latitude"], df["longitude"], '#000000', size=5, marker=False)
    gmap.draw("/" + day + "-raw.html")
    # return IFrame("processedGPS/" + day + "-raw.html", width=990, height=500)


def displayDay(day, complete_df, min_angle=15, max_speed=150, med_window=2, med_delay=150, sp_min=3, sp_radius=70, sp_outliers=5) :
    df = parser.selectDate(day, complete_df)
    df_duplicates = filterPerfectDuplicates(df)
    df_angle = filterByAngle(df_duplicates, min_angle)
    df_speed = filterBySpeed(df_angle, max_speed)
    df_med = filterByMedian(df_speed, n=med_window, min_delay=med_delay)
    segments, points = findSegments(df_med, sp_min, sp_radius, sp_outliers)
    grouped_points = groupPoints(points)
    reverseGeocode(grouped_points, segments)
    # return showOnMap(day, segments, grouped_points, centerX=45.775371, centerY=4.800596, zoom=13)


def filterPerfectDuplicates(df):
    size = df['date'].size
    lat = []
    lng = []
    to_keep = []

    for i in range(size):
        if df['latitude'][i] in lat and df['longitude'][i] in lng:
            # print("Duplicate !")
            # print(str(df['latitude'][i]) + " " + str(df['longitude'][i]))
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
    s = df[: start_stay_points[0] + 1]
    segments.append(s.reset_index(drop=True))

    for i in range(len(end_stay_points) - 1):
        s = df[end_stay_points[i] - 1: start_stay_points[i + 1] + 1]
        segments.append(s.reset_index(drop=True))

    s = df[end_stay_points[len(end_stay_points) - 1]:]
    segments.append(s.reset_index(drop=True))

    points = []
    for i in range(len(start_stay_points)):
        points.append([df["latitude"][start_stay_points[i]], df["longitude"][start_stay_points[i]]])

    return segments, points


def groupPoints(points, epsilon=150, min_samples=1):
    meters = []

    for p in points:
        coords = []
        coords.append(distance.haversineDistance(0, p[0], 0, 0))
        coords.append(distance.haversineDistance(p[1], 0, 0, 0))
        meters.append(coords)

    db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(meters)
    labels = db.labels_

    unique_labels = set(labels)
    grouped_points = []

    for current_label in unique_labels:
        lat_sum = 0
        lng_sum = 0
        count = 0
        for i in range((len(points))):
            if labels[i] == current_label:
                count += 1
                lat_sum += points[i][0]
                lng_sum += points[i][1]
        grouped_points.append([lat_sum / count, lng_sum / count])

    return grouped_points


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


def showOnMap(day, segments, points, centerX=45.757589, centerY=4.831689, zoom=15):
    gmap = gmplot.GoogleMapPlotter(centerX, centerY, zoom, apikey="AIzaSyDsYwvF3UUxTx8RB40wd4SnUVzfnbW66LM")

    cols = list(zip(*points))
    gmap.scatter(cols[0], cols[1], '#3B0B39', size=50, marker=False)

    for i in range(len(segments)):
        gmap.plot(segments[i]["latitude"], segments[i]["longitude"], colors.color_list[i], edge_width=3)
        gmap.scatter(segments[i]["latitude"], segments[i]["longitude"], '#000000', size=5, marker=False)

    # gmap.draw("processedGPS/" + day + ".html")
    # return IFrame("processedGPS/" + day + ".html", width=990, height=500)


''' Import des donnees '''
print('Chargement des donnees ...', sep=' ', end = '', flush = True)
df = parser.importJson("Data/Takout/android_small.json")
print(' Termine')

lDays=list(set(df['date']))

#displayRawDay(lDays[0],df)
displayDay(lDays[0], df)