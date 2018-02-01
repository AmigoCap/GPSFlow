# coding utf8

import parser
import matplotlib.pyplot as plt
import distance 
import pandas as pd


## Mean filter (utile pour des points proches)

def meanFilter(data, n=2):

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

	data['lat_mean_filt']=lat_filtered
	data['lng_mean_filt']=long_filtered

	return data


## Median filter 

def medianFilter(data, n=2):

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

	data['lat_med_filt']=lat_filtered
	data['lng_med_filt']=long_filtered

	return data


def errorDistances(data, filt_lat_name, filt_lng_name):
	error=[]
	for i in range(data['latitude'].size):
		error.append(distance.haversine(data["longitude"][i], data["latitude"][i], data[filt_lng_name][i], data[filt_lat_name][i]))
	return error


def sumErrorDistance(data, filt_lat_name, filt_lng_name):
	return sum(errorDistances(data, filt_lat_name, filt_lng_name))


def showMeanFilter(data):

	data = meanFilter(data)

	plt.plot(data['latitude'].values, data['longitude'].values, 'b')
	plt.plot(data['lat_mean_filt'].values, data['lng_mean_filt'].values, 'r')

	plt.show()


def showMedianFilter(data):

	data = medianFilter(data)

	plt.plot(data['latitude'].values, data['longitude'].values, 'b')
	plt.plot(data['lat_med_filt'].values, data['lng_med_filt'].values, 'r')

	plt.show()


def showError(data):
	plt.plot(errorDistances(meanFilter(data)))
	plt.plot(errorDistances(medianFilter(data)), 'r')
	plt.show()


		