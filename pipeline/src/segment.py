import distance
import numpy
from sklearn.cluster import DBSCAN

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
				start_stay_points.append(numpy.clip(start_index, 0, df["timestampMs"].size - 1))
				end_stay_points.append(numpy.clip(end_index, 0, df["timestampMs"].size - 1))
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
			s = df[end_stay_points[i] - 1 : start_stay_points[i + 1] + 1]
			segments.append(s.reset_index(drop=True))

		s = df[end_stay_points[len(end_stay_points) - 1]:]
		segments.append(s.reset_index(drop=True))

		points = []
		for i in range(len(start_stay_points)) :
			lat=0
			lng=0
			for k in range(start_stay_points[i], end_stay_points[i]):
				lat += df["latitude"][k]/(end_stay_points[i]-start_stay_points[i])
				lng += df["longitude"][k]/(end_stay_points[i]-start_stay_points[i])

			points.append({
					"lat" : float(lat), 
					"lng" : float(lng), 
					"start" : int(df["timestampMs"][start_stay_points[i]]), 
					"end" : int(df["timestampMs"][end_stay_points[i]]), 
					"addr" : "Unknown"})
	
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
				points[i]["label"] = int(current_label)
				points[i]["lat"] = lat_sum/count
				points[i]["lng"] = lng_sum/count
			
	return points

def removeSmallSegments(segments, nb_points, min_dist) :
	k=0
	while k <len(segments):
		if len(segments[k])<nb_points:
			total_dist=0
			for i in range(1, len(segments[k])):
				total_dist+=distance.haversineDistance(
									segments[k]["longitude"][i-1], 
									segments[k]["latitude"][i-1], 
									segments[k]["longitude"][i], 
									segments[k]["latitude"][i])
			if total_dist<min_dist:
				segments.pop(k)
				k-=1
		k+=1
	return segments
