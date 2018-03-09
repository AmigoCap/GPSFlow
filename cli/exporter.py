import json

def generateJson(data) : 
	result = "{\"days\":["
	
	for d in data :
		result += createDayJson(d["date"], d["segments"], d["points"])
		result += ","

	result = result[:-1] + "]}"
	return result

def createDayJson(date, segments, points) :
	result = "{"

	# Date and points_count
	result += "\"date\":\"" + date + "\","
	result += "\"points_count\":" + getPointsCount(segments) + ","
	
	# Segments
	if len(segments) == 0 :
		result += "\"segments\":[],"
	else :
		result += "\"segments\":["
		for i in range(len(segments)) :
			result += "{\"segment_id\":" + str(i) + ","
			result += "\"points\":"
			result += segments[i].to_json(path_or_buf=None, orient='records')
			result += "},"
		result = result[:-1] + "],"
	
	# Stay points
	result += "\"staypoints\":"
	result += json.dumps(str(points))
	result += "}"
	
	return result

def getPointsCount(segments) :
	result = 0
	for s in segments :
		result += s['ts'].size
	return str(result)