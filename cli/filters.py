import distance
import numpy as np
import math

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
