from bs4 import BeautifulSoup
import urllib
import urllib.parse
import urllib.request as ur
import os

##IMAGE CRAWLER 2.1 IS MORE GENERAL PURPOSE
##2.2 WAS MADE TO SAVE TO ONE FOLDER FOR EXIF ANALYTICS


seed = input("Enter seed in form 'http://xxxxx/': ")

#Sets the initial seed
newseed = seed

#Creates the list of links to search
searchlist = [newseed]

#Number of images downloaded
imagenumber = 0

#Keeps track of URLs of downloaded images
imgsdownloaded = []

tag = urllib.parse.urlparse(seed).netloc
directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", tag)
if not os.path.exists(directory):
	os.makedirs(directory)





maxlinks = input("How many links should be searched?: (inf for infinite) ")
constantsite = input("Stay on site and only follow sub domains?  (y/n) ")
if constantsite == "y":
	constantsite = True
else:
	constantsite = False


if maxlinks != "inf":
	maxlinks = int(maxlinks)
	infinite = False
else:
	maxlinks = 1
	infinite = True

linknumber = 1

#Crawl and download loop
for searchedurl in searchlist:
	
	try:
		print("URL being searched: {}".format(searchedurl))
	
	
		#Downloads HTML site content from URL
		r = ur.urlopen(searchedurl).read()
		sitecontent = BeautifulSoup(r, "html.parser")
		
		
		#Creates a list of all the CCS links in the page source
		linklist = [a.attrs.get('href') for a in sitecontent.select('a[href]')]
		
		
		#HTML img Gatherer - Puts all the image URLs in a list IF they have not already been downloaded.
		imglist = []
		for img in sitecontent.find_all('img'):
			if img['src'] not in imgsdownloaded:
				imgsdownloaded.append(img['src'])
				imglist.append(img['src'])
				
		
		
		#Removes URL fragments from items in linklist
		for i in range(len(linklist)):
			linklist[i] =  urllib.parse.urldefrag(linklist[i])[0]
		
		for i in range(len(linklist)):
			if bool(urllib.parse.urlparse(linklist[i]).netloc) != True:
				linklist[i] = urllib.parse.urljoin(searchedurl, linklist[i])
		
		
		#Removes URL fragments from items in imglist
		for i in range(len(imglist)):
			imglist[i] =  urllib.parse.urldefrag(imglist[i])[0]
		
		for i in range(len(imglist)):
			if bool(urllib.parse.urlparse(imglist[i]).netloc) != True:
				imglist[i] = urllib.parse.urljoin(searchedurl, imglist[i])
		

		
		
		#Downloads images
		for i in range(len(imglist)):
			print(imglist[i])
			#Adds extension .jpg if none present
			if "." not in imglist[i][-4:]:
				addextension = ".jpg"
			else:
				addextension = ""
			
			#Names image according to its number
			filename = str(imagenumber) + " - " + urllib.parse.urlparse(imglist[i]).netloc + " - " + imglist[i][-4:] + addextension
			
			#Creates a directory related to the image URL
			# tag = urllib.parse.urlparse(imglist[i]).netloc
			# directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", tag)
			# if not os.path.exists(directory):
				# os.makedirs(directory)
			
			#Combines directory and filename
			fullfilename = os.path.join(directory, filename)
			#print(fullfilename)
			
			#Downloads image and increments number of images downloaded
			ur.urlretrieve(imglist[i], fullfilename)
			imagenumber += 1
			
		
		
		
		
		#Checks whether links are in search list, if not, adds them to the queue
		if (len(searchlist) < maxlinks) or (infinite == True):
			for j in range(len(linklist)):
				if not constantsite:
					if linklist[j] not in searchlist:
						searchlist.append(linklist[j])
						print("New link: {} ".format(linklist[j]))
				
				#If constantsite is true
				else:
					if linklist[j] not in searchlist:
						if seed in linklist[j]:
							searchlist.append(linklist[j])
							print("New link: {} ".format(linklist[j]))
						
		else:
			print("No new links added as at least {} links have been queued".format(maxlinks))

		print("{} links have been searched.".format(linknumber))
		print("Number of links: {}".format(len(searchlist)))
		print("Number of images downloaded: {}".format(imagenumber))
		print()
		print()
		
		if (linknumber >= maxlinks) and (infinite == False):
			break
		
		
		linknumber +=1
	except Exception:
		continue