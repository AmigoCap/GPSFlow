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