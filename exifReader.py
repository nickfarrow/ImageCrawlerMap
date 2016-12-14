import exifread
import os
import urllib.parse
import csv
import time

seed = input("Enter seed in form 'http://xxxxx/': ")

#GETS BASE OF SEED
tag = urllib.parse.urlparse(seed).netloc

#FILENAMES AND NEW DIRECTORY
writetag = tag + " locations"
directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", tag)

#CREATES A LIST OF ALL THE RELEVENT FILES
filesList = os.listdir(directory)

#GOOGLE SEARCH STRING
baseSearch = "https://www.google.com.au/maps/place/LAT0°LAT1'LAT2\"LATDIR+LONG0°LONG1'LONG2\"LONGDIR/"

#TAKES EXIF LIST FOR POSITION AND CONVERTS INTO A LIST
def classCleaner(exifObject):
	aList = str(tags[exifObject])[1:-1].split(", ")
	for i in range(len(aList)):
		if "/" in aList[i]:
			if aList[i] != "0/0":
				aList[i] = str(eval(aList[i]))
			else:
				aList[i] = "0"
	return aList

	
#CONVERTS DEGREES MINUTES SECONDS TO DECIMAL ANGLE
def degreesToDecimal(aList, direction):
	if (direction == "N") or (direction == "E"):
		multiplier = 1
	else:
		multiplier = -1
	return multiplier * (float(aList[0]) + float(aList[1])/60 + float(aList[2])/3600)
	
#WRITES LOCATIONS TO A CSV WHICH CAN BE UPLOADED TO GOOGLE MAPS
def writeCSV(filename, latitude, lonitude):
	print(latitude)
	print(lonitude)
	locationList = [filename, str(latitude), str(lonitude)]
	print(locationList)
	with open(writetag + '.csv', "a", newline='') as csvfile:
				writer = csv.writer(csvfile, delimiter=',')
				writer.writerow(locationList)
	
	
#CREATES INITIAL CSV WITH TITLES	
with open(writetag + '.csv', "a", newline='') as csvfile:
	writer = csv.writer(csvfile, delimiter=',')
	writer.writerow(["Image Name", "Latitude", "Longitude"])	
	
	
#COUNTS NUMBER OF FILES WHICH HAVE AN ASSOCIATED LOCATION
filesWithGPSCount = 0


#MAIN LOOP OVER EVER FILE
for filename in filesList:
	try:
	
		#GETS FILE AND THEN EXIF DATA
		print(filename)
		filePath = os.path.join(directory, filename)
		
		fileData = open(filePath, 'rb')
		tags = exifread.process_file(fileData)
	
		
		#IF THE EXIF DATA CONTAINS GPS INFO
		if "GPS GPSLongitude" in tags.keys():
			
			#EXIF DATA DIRECTORY
			infoDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", writetag)
			if not os.path.exists(infoDir):
				os.makedirs(infoDir)
			
			saveLoc = os.path.join(infoDir, filename)
			
			#CHANGES EXIF OBJECTS INTO LISTS
			with open(saveLoc + ".txt", "a+") as editingDatabase:
				longitudeList = classCleaner("GPS GPSLongitude")
				latitudeList = classCleaner("GPS GPSLatitude")
				longDirection = str(tags["GPS GPSLongitudeRef"])
				latDirection = str(tags["GPS GPSLatitudeRef"])
			
			
				#IF GPS DATA IS REAL
				if longitudeList != [0, 0, 0]:
					
					#STARTS GOOGLE SEARCH STRING
					searchURL = baseSearch
					
					
					for i in range(3):
						if latitudeList[i] != "0":
							searchURL = searchURL.replace("LAT" + str(i), latitudeList[i])
						else:
							searchURL = searchURL.replace('LAT' + str(i) + '"', "")
					
					for i in range(3):
						if longitudeList[i] != "0":
							searchURL = searchURL.replace("LONG" + str(i), longitudeList[i])
						else:
							searchURL = searchURL.replace('LONG' + str(i) + '"', "")
					searchURL = searchURL.replace("LATDIR", latDirection)
					searchURL = searchURL.replace("LONGDIR", longDirection)
					
					print(searchURL)
					
					#WRITES TO FILE
					editingDatabase.write(searchURL + "\n\n")
					filesWithGPSCount += 1
					
					#WRITE OTHER EXIF DATA TO FILE
					for tag in tags.keys():
						if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
							editingDatabase.write("Key: %s, value %s" % (tag, tags[tag]) + "\n")
							
					#WRITES TO CSV
					decimalLatitude = degreesToDecimal(latitudeList, latDirection)
					decimalLongitude = degreesToDecimal(longitudeList, longDirection)
					writeCSV(filename, decimalLatitude, decimalLongitude)
		
		
		print("{} files with GPS location have been found.".format(filesWithGPSCount))
		print()
		print()
	except Exception as e: 
		print(e)
		print("ERROR")
		continue
		
		
