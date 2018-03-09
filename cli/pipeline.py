import parser
import filters
import segment

def process(df) :
	days = getUniqueDays(df)
	result = []

	for day in days :
		segments, points = processDay(day, df)
		result.append({
				"date" : day,
				"segments" : segments,
				"points" : points
			})

	return result

def getUniqueDays(df) :
	sequence = df['date'].tolist()
	seen = set()
	return [x for x in sequence if not (x in seen or seen.add(x))]

def processDay(day, df) :
	min_angle=15
	max_speed=150
	median_window=2
	median_delay=150
	staypoint_limit=3
	staypoint_radius=50
	staypoint_outliers=5
	small_points=5
	small_distance=30
	
	# Select date
	df = parser.selectDate(day, df)

	# Apply filters
	if df['date'].size > 3 :
		df = filters.filterPerfectDuplicates(df)
		df = filters.filterByAngle(df, min_angle)
		df = filters.filterBySpeed(df, max_speed)
		df = filters.filterByMedian(df, n=median_window, min_delay=median_delay)

	# Segments by stay point
	segments, points = segment.findSegments(df, staypoint_limit, staypoint_radius, staypoint_outliers)
	segments = segment.removeSmallSegments(segments, small_points, small_distance)
	points = segment.groupPoints(points)

	# Cleanup
	segments = cleanupColumns(segments)
	
	return segments, points

def cleanupColumns(segments) :
	for s in segments :
		s['ts'] = s['timestampMs']
		s['lat'] = s['latitude']
		s['lng'] = s['longitude']

	columns = ["ts", "lat", "lng"]
	for s in segments :
		for col in list(s) :
			if col not in columns :
				del s[col]
				
	return segments