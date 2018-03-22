import sys
import os.path
import parser
import pipeline
import exporter
import sklearn

if __name__ == "__main__" :

	if len(sys.argv) == 2 :
		filepath = str(sys.argv[1])

		if os.path.isfile(filepath) and filepath.endswith('.json'):
			print("Import Google Takout data (can be long)... ", end='')
			df = parser.importJson(filepath)	
			print("Done !")

			print("Process trajectories... ", end='')
			data = pipeline.process(df)
			print("Done !")

			print("Export to json... ", end='')
			json = exporter.generateJson(data)
			print("Done !")

			print("Write to file... ", end='')
			file = open("output.json", "w") 
			file.write(json)
			file.close()
			print("Done !")

		elif not filepath.endswith('.json') :
			print("File must be in JSON format.")
		
		else :
			print("Could not find this file.")
	
	else :
		print()
		print("How to use :")
		print()
		print("    ./gpsflow <path_to_takout.json>")
		print()
		print("If you don't have your takout.json file, download it here :")
		print("https://takeout.google.com/settings/takeout")
		print("Only download your 'Location History'")
		print()
