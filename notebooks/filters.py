# coding utf8

import parser
import distance 
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

## Mean filter (utile pour des points proches)

def meanFilter(df, n=2, replace=False):

	if replace:
		data = df.copy(deep=True)
	else:
		data=df

	## la fenêtre glissante sera de taille 2n+1

	lat_filtered=[0]*len(data)
	long_filtered=[0]*len(data)

	for i in range(n):
		lat_filtered[i]=data['latitude'][i]
		long_filtered[i]=data['longitude'][i]

	for i in range(len(data)-n,len(data)):
		lat_filtered[i]=data['latitude'][i]
		long_filtered[i]=data['longitude'][i]

	for i in range(n, len(data)-n):
		for j in range(i-n,i+n+1):
			lat_filtered[i]+=data['latitude'][j]/(2*n+1)
			long_filtered[i]+=data['longitude'][j]/(2*n+1)

	if replace:
		data['latitude']=lat_filtered
		data['longitude']=long_filtered
	else:
		data['lat_mean_filt']=lat_filtered
		data['lng_mean_filt']=long_filtered

	return data


def showMeanFilter(data):

	data = meanFilter(data)

	plt.plot(data['latitude'].values, data['longitude'].values, 'b')
	plt.plot(data['lat_mean_filt'].values, data['lng_mean_filt'].values, 'r')

	plt.show()


def meanFilterSegment(df, n, first_index, last_index):

	data = df.copy(deep=True)

	lat_filtered={}
	long_filtered={}

	for i in range(first_index+n, last_index-n):
		lat_filtered[i]=0
		long_filtered[i]=0
		for j in range(i-n,i+n+1):
			lat_filtered[i]+=data['latitude'][j]/(2*n+1)
			long_filtered[i]+=data['longitude'][j]/(2*n+1)

	for i in range(first_index+n, last_index-n):
		data['latitude'][i]=lat_filtered[i]
		data['longitude'][i]=long_filtered[i]

	return data


## Median filter 

def medianFilter(df, n=2, replace=False):

	if replace:
		data = df.copy(deep=True)
	else:
		data=df

	lat_filtered=[0]*len(data)
	long_filtered=[0]*len(data)

	for i in range(n):
		lat_filtered[i]=data['latitude'][i]
		long_filtered[i]=data['longitude'][i]

	for i in range(len(data)-n,len(data)):
		lat_filtered[i]=data['latitude'][i]
		long_filtered[i]=data['longitude'][i]

	for i in range(n, len(data)-n):
		lat_window = data['latitude'][i-n:i+n+1].tolist()
		lat_window.sort()
		long_window = data['longitude'][i-n:i+n+1].tolist()
		long_window.sort()

		lat_filtered[i] = lat_window[n]
		long_filtered[i] = long_window[n]

	if replace:
		data['latitude']=lat_filtered
		data['longitude']=long_filtered
	else:
		data['lat_med_filt']=lat_filtered
		data['lng_med_filt']=long_filtered

	return data


def medianFilterSegment(df, n, first_index, last_index):

	data = df.copy(deep=True)

	lat_filtered={}
	long_filtered={}

	for i in range(first_index+n, last_index-n):
		lat_window = data['latitude'][i-n:i+n+1].tolist()
		lat_window.sort()
		long_window = data['longitude'][i-n:i+n+1].tolist()
		long_window.sort()

		lat_filtered[i] = lat_window[n]
		long_filtered[i] = long_window[n]

	for i in range(first_index+n, last_index-n):
		data['latitude'][i]=lat_filtered[i]
		data['longitude'][i]=long_filtered[i]

	return data



def errorDistances(data, filt_lat_name, filt_lng_name):
	error=[]
	for i in range(data['latitude'].size):
		error.append(distance.haversineDistance(data["longitude"][i], data["latitude"][i], data[filt_lng_name][i], data[filt_lat_name][i]))
	return error


def sumErrorDistance(data, filt_lat_name, filt_lng_name):
	return sum(errorDistances(data, filt_lat_name, filt_lng_name))


## filtrage par segment

def delay_segment_dataframe(df, limit) :
	segnum = 0
	segments = []

	for i in range(df["time"].size) :
		if (df["delay"][i] > limit) :
			segments.append(segnum)
			segnum += 1;
		else :
			segments.append(segnum)

	df["segment"] = segments
	return df


def filterBySegment(input_data, limite):
	data = input_data.copy()
	lat_filtered=[0]*len(data)
	long_filtered=[0]*len(data)

	data = delay_segment_dataframe(data, limit=limite)
	segment_count = max(data['segment'])

	segment_indexes = [0]

	j=0
	for i in range(data['segment'].size):
		if data['segment'][i]!=j:
			j+=1
			segment_indexes.append(i)
			
	segment_indexes.append(data['segment'].size+1)

	for k in range(segment_count):
		distances = data["distance"][segment_indexes[k]:segment_indexes[k+1]]
		dist_moy = np.mean(distances)

		if dist_moy<20 and segment_indexes[k+1]-segment_indexes[k]>8:
			data = medianFilterSegment(data, 3, segment_indexes[k], segment_indexes[k+1])

		elif dist_moy<50 and segment_indexes[k+1]-segment_indexes[k]>6:
			data = medianFilterSegment(data, 2, segment_indexes[k], segment_indexes[k+1])

		elif dist_moy<150 and segment_indexes[k+1]-segment_indexes[k]>6:
			data = meanFilterSegment(data, 2, segment_indexes[k], segment_indexes[k+1])


	# Add distance, velocity and acceleration 
	data['distance'] = distance.getDistances(data)
	data['velocity'] = distance.getVelocities(data)
	data['acceleration'] = distance.getAccelerations(data)
	return data




		