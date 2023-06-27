



# This script parses through a given folder,
#   and find the most recent NxM images and creates a web page showing
#   them all off in an HTML file
#
# If there are more than NxM images in the folder, we'll delete the oldest
#   ones.
#
# Place the script and the contents of the img folder in the same folder.
#   Feel free to place all of this outside the public_html, just will have to
#   set the -diOut setting here to correctly reference the public_html
#
# @author	Konstantin Shkurko (kshkurko@cs.utah.edu)
# @date		02.08.12
# @updated  03.04.13
# @version  0.141
#


# imports
import argparse, os, glob, datetime, time, shutil, re
from PIL import Image, ImageFont, ImageDraw, PngImagePlugin

#
# Parameters for text generation of the web-page. These should be
# a little easier to change as we need them.
#
PAGE_TYPE_LIVE     = 0;
PAGE_TYPE_SHOWCASE = 1;
PAGE_TYPE_TRIPTYCH = 2;

#
# define header text for each of the above (in the same order)
#

# title of the page
PAGE_TITLES = [ "MASC Showcase: Snowflakes in Freefall",
				"MASC Showcase: Snowflakes in Freefall",
				"MASC Showcase: Triplet Images of Snowflakes in Freefall"
			   ]
# what to show before the table of images (no need to use <br/> to set width of document any more)
PAGE_PREAMABLE = [
# live
"""<br/>
	This is a live showcase of snowflake images captured in freefall at <a href="http://www.alta.com/" title="Alta Ski Area">Alta Ski Area</a> using the 
	University of Utah <a href="http://www.inscc.utah.edu/~tgarrett/Snowflakes/MASC.html" title="MASC">MASC</a> (Multi Angle Snowflake Camera).
	<br/>
	""",

# showcase
"""<br/>
	This is a live showcase of snowflake images captured in freefall at <a href="http://www.alta.com/" title="Alta Ski Area">Alta Ski Area</a> using the 
	University of Utah <a href="http://www.inscc.utah.edu/~tgarrett/Snowflakes/MASC.html" title="MASC">MASC</a> (Multi Angle Snowflake Camera). For more information about 
	this <a href="http://www.utah.edu" title="University of Utah">University of Utah</a> and <a href="http://www.nsf.gov" title="National Science Foundation">National Science Foundation</a> project, or a gallery of snowflake 
	<a href="http://www.inscc.utah.edu/~tgarrett/Snowflakes/Gallery/" title="snowflake highlights">highlights</a>,
	please visit the <a href="http://www.inscc.utah.edu/~tgarrett/Snowflakes/Snowflakes.html" title="Snowflake Stereography and Fallspeed home page">Snowflake	Stereography and Fallspeed home page</a> or email <a href="http://www.inscc.utah.edu/~tgarrett/Garrett.html" title="Tim Garrett">Tim Garrett</a>.
	<br/><br/>
	When it is snowing, images of snowflakes captured live in free fall can be found 
	at Alta's <a href="http://www.alta.com/pages/snowflakeshowcase.php" title="Snowflake Showcase"> Snowflake Showcase</a>.
	<br/><br/>
	Images are taken at f/5.6 with an exposure of at least 1/25,000th of a second using
	1.2MP and 5MP industrial cameras with lenses ranging from 12 mm to 35 mm. The image resolution ranges from 9 
	micrometers to 40 micrometers.
	<br/><br/><br/>
        We appreciate any support to <a href="https://www.microryza.com/projects/what-do-snowflakes-really-look-like" title="improve the Snowflake Showcase at Alta">improve the Snowflake Showcase at Alta</a>.
        <br/><br/><br/>
	<span class="smaller">Click on any snowflake to see it in full resolution and to play a slide show.</span>
	<br/>
	""",

# triptych
"""<br/>
	This is a showcase of snowflakes photographed from three angles in freefall at <a href="http://www.alta.com/" title="Alta Ski Area">Alta Ski Area</a> using the
	University of Utah <a href="http://www.inscc.utah.edu/~tgarrett/Snowflakes/MASC.html" title="MASC">MASC</a> (Multi Angle Snowflake Camera). For more information about 
	this <a href="http://www.utah.edu" title="University of Utah">University of Utah</a> and <a href="http://www.nsf.gov" title="National Science Foundation">National Science Foundation</a> project, or a gallery of snowflake 
	<a href="http://www.inscc.utah.edu/~tgarrett/Snowflakes/Gallery/" title="snowflake highlights">highlights</a>,
	please visit the <a href="http://www.inscc.utah.edu/~tgarrett/Snowflakes/Snowflakes.html" title="Snowflake Stereography and Fallspeed home page">Snowflake	Stereography and Fallspeed home page</a> or email <a href="http://www.inscc.utah.edu/~tgarrett/Garrett.html" title="Tim Garrett">Tim Garrett</a>.
	<br/><br/>
	When it is snowing, images of snowflakes captured live in free fall can be found at Alta's <a href="http://www.alta.com/pages/snowflakeshowcase.php" title="Snowflake Showcase">Snowflake Showcase</a>.
	<br/><br/>
	Here, camera views are separated by 36 degrees. Images are taken at f/5.6 with an exposure of at least 1/25,000th of a second using
	1.2MP (outer) and 5MP (center) industrial cameras with lenses ranging from 12 mm to 35 mm. The image resolution ranges from 
	9 micrometers to 40 micrometers.
	<br/><br/><br/>
        We appreciate any support to <a href="https://www.microryza.com/projects/what-do-snowflakes-really-look-like" title="improve the Snowflake Showcase at Alta">improve the Snowflake Showcase at Alta</a>.
        <br/><br/><br/>
	<span class="smaller">Click on any snowflake to see it in full resolution and to play a slide show.</span>
	<br/>
	"""
	]

# the footer of the page (after "Updated on:")
PAGE_FOOTER = """<br/><br/><br/><br/><img src=\"img/ss_NSF.png\" alt=\"NSF\" title=\"NSF\"/><img src=\"img/ss_ALTA.png\" alt=\"Alta\" title=\"Alta\"/>
	<span class=\"smaller\">Copyright, <a title = \"Particle Flux Analytics Inc.\" href=\"http://www.particleflux.net\">Particle Flux Analytics Inc. </a>,   """ + datetime.datetime.now().strftime( "%Y" ) + "</span>"

	

#
# try to parse out the date/time from file name
# we assume that the filename has the following 
# organization: "%Y.%m.%d_%H.%M.%S_<etc>",
#    where %<> corresponds to the Python time
#
# @param  inFile - input file name (string)
# @return datetime, if name parsing succeeded, otherwise - False
#
def parseDateTimeFromFileName( inFile ):

	# try splitting our filename
	try:
		tmp = os.path.basename( inFile )
		tmp = os.path.splitext( tmp )[0]
		tmp = tmp.split( '_' )
	except:
		return False

	# try parsing 1st item as date
	try:
		#print( "parsed time: " + tmp[0] + ", " + tmp[1] )
		d = time.strptime( tmp[0]+" "+tmp[1], "%Y.%m.%d %H.%M.%S" )
		return time.mktime( d )
	except:
		return False


#
# Parses file name of our snowflake, splits it based on '_'
# and returns the camera id of the image.
# For now assume %d_%T_flake_%f_cam_%c.png format (camId=5):
# +%f  flake id
# +%c  camera id
# +%d  date (yyyy.mm.dd)       %Y - year, %M - month,  %D - day
# +%T  time (hh.mm.ss)         %h - hour, %m - minute, %s - second
#
# @param inFile - input file name to parse
# @param camId  - id of the piece separated by '_' which corresponds to 
#				  the camera id (first is 0). If not passed in, return 
#				  full split of filename
# @return camera id of given image filename
#
def parseFileName( inFile, camId ):

	fileName = os.path.splitext( os.path.split( inFile )[1] )[0]
	#splitStr = fileName.split( '_' )
	#dt = splitStr[0]
	#tm = splitStr[1]
	#fk = splitStr[3]
	#cm = splitStr[5]
	#return [cm, fk, dt, tm, fk]
	if( camId==None ):
		return fileName.split( '_' )
	else:
		return fileName.split( '_' )[camId]


#
# Gets the PNG images in the directory sorted by modified date
#
# The date is extraced in the following order (until one succeeds)
#   1. Based on the "Creation Time" within image meta-data
#   2. Using parseDateTimeFromFileName function above
#   3. Using the os file system, file creation time (Windows) or 
#      last metadata modification time (*nix)
#
# @param  dir - directory which to check (default ".")
# @return list of PNG filenames sorted on timestamp in descending order
#
def getImagesInDir( dir = "." ):

	if( not os.path.exists( dir ) ):
		print( "ERROR: output path (" + dir + ")doesn't exist!")


	# init file info
	outInfo = [];

	# open the directory
	files = glob.glob( os.path.join( dir, '*.png' ) );
	for file in files:
		# get image tags to resave later (and parse out date)
		img      = Image.open( file )
		imgTags  = img.info
		if('Creation Time' in imgTags):
			imgCTime      = time.strptime( imgTags['Creation Time'], "%d %b %Y %H:%M:%S +0000" )
			outInfo.append( [file, time.mktime( imgCTime )] )
			#print "found: {0}, {1}".format( file, fileTimestamp )
		else:
			tmp = parseDateTimeFromFileName( file )
			if( tmp != False ):
				outInfo.append( [file, tmp] )
				#print "parse: {0}, {1}".format( file, tmp )
			else:
				fInfo = os.stat( file )
				outInfo.append( [file, fInfo.st_ctime] )
				#print "NOT: {0}, {1}".format( file, fInfo.st_ctime )
		del img

	# sort in descending order based on created timestamp (first NxM images)
	outInfo.sort( key=lambda tmp: tmp[1], reverse=True )
	return outInfo


#
# Searches for images in a directory which fit a given naming convention
# while replacing camera ids...
# The basic idea is to match in the following order: exact, up to 1s seconds,
# up to 10s of seconds. All of the matches are accumulated into a list
# that is returned. 
#
# @param inDir        - input directory to check
# @param inBaseName   - basename of the image to check with
# @param inCamIds     - camera ID to check. Can be None, <int>, list
#                        + None:  matches to the camera ID in the basename
#                        + <int>: matches to given camera ID as this int
#                        + list:  matches to given list of ids as int
# @param inCamIDIndex - index of camera ID in file name, counted between _, starting at 0
# @return list of file basenames that fit
#
def findImageFileInFolder( inDir, inBaseName, inCamIds, inCamIDIndex ):

	# get basename and such so we can mess with it
	thisFilesSplit = parseFileName( inBaseName, None )
	parsedTime     = thisFilesSplit[1].split('.')
	
	if( inCamIds==None ):
		inCamIds = [thisFilesSplit[inCamIDIndex][0]]
	
	# check if list... if not, listify
	if( type(inCamIds)!=type(list()) ):
		inCamIds = [inCamIds]
		
	# run through all camera IDs
	foundNames = []
	for c in inCamIds:
		
		# check full name first
		tmpFilesSplit               = list(thisFilesSplit)
		tmpFilesSplit[inCamIDIndex] = str(c)
		tmpName                     = "_".join(tmpFilesSplit) + ".png"
		if( os.path.isfile( os.path.join( inDir, tmpName ) ) ):
			foundNames.append(tmpName)
			del tmpFilesSplit
			continue

		# check to 1s of seconds
		else:
			tmpTime    = list(parsedTime)
			tmpTime[2] = tmpTime[2][0] + '([0-9]+)(\.*)([0-9]*)'
			if( len(tmpTime)>3 ):
				tmpFilesSplit[1] = '.'.join(tmpTime[0:-1])
			else:
				tmpFilesSplit[1] = '.'.join(tmpTime)
			tmpName     = "_".join(tmpFilesSplit) + ".png"
			namesBefore = list( [os.path.basename(f1) for f1 in os.listdir(inDir) if re.search(tmpName, f1)] )
			if( len(namesBefore)>0 ):
				foundNames.append(namesBefore[0])
				del tmpTime, tmpFilesSplit, namesBefore
				continue

			# check to 10s of seconds
			else:
				tmpTime[2] = '([0-9]+)(\.*)([0-9]*)'
				if( len(tmpTime)>3 ):
					tmpFilesSplit[1] = '.'.join(tmpTime[0:-1])
				else:
					tmpFilesSplit[1] = '.'.join(tmpTime)
				tmpName     = "_".join(tmpFilesSplit) + ".png"
				namesBefore = list( [os.path.basename(f1) for f1 in os.listdir(inDir) if re.search(tmpName, f1)] )
				if( len(namesBefore)>0 ):
					foundNames.append(namesBefore[0])
					del tmpTime, tmpFilesSplit, namesBefore
					continue
			del tmpTime

		# done
		del tmpFilesSplit
	del thisFilesSplit, parsedTime
	return foundNames


#
# Generates the output file based on all passed in parameters. See the README file
# which describes in detail meaning of each parameter in greater detail
#
# @param inDir   - input directory with images (this is where original image files are located,
#                   and then moved to output directory. Original images are NOT modified)
# @param outDir  - output directory with images (this is where HTML file will be placed)
#                   If inDir is NOT passed in, this directory will house the original images
#                   which will be modified in place
# @param outFile - name of the HTML file
# @param N       - N in NxM matrix of thumbnails
# @param M       - M in NxM matrix of thumbnails
# @param iw      - image width of the thumbnail (generated from original image)
# @param ih      - image height of the thumbnail (generated from original image)
# @param rTime   - refresh time (milliseconds) for the web page. If 0, then page will not have
#                   any refreshing and the introductory text is different. Also no
#                   image timestamps will be shown underneath thumbnails.
#                   Otherwise, page will refresh in rTime. Time stamps will be placed
#                   underneath thumbnails.
#                   NOTE: use rTime=0 for gallery, rTime>0 for live feed.
# @param tripFlg - flag whether to generate a triptych web page. It will trump
#                   time flag, etc.
# @param nolineFlg - flag whether to remove text and lines underneath the images
# @param camIdx    - index of the camera ID in the file name (as passed to parseFileName)
#
def genOutputHTML( inDir, outDir, outFile, N, M, iw, ih, rTime, tripFlg, nolineFlg, camIdx ):

	widthPerImgCell  = 30
	if( nolineFlg ):
		widthPerImgCell = 0

	reloadTimeInMSec = rTime;
	bodyWidth        = (widthPerImgCell + iw)*M + 15

	# determine which type of page we're generating based on some inputs
	pageTypeToGenerate = PAGE_TYPE_LIVE;
	# triptych
	if( tripFlg ):
		pageTypeToGenerate = PAGE_TYPE_TRIPTYCH
		reloadTimeInMSec   = 0
		M         = 6
		N         = 1000000
		bodyWidth = (widthPerImgCell + iw)*6 + widthPerImgCell + (int)(iw/2) + 15
	# LIVE
	elif( reloadTimeInMSec!=0 ):
		pageTypeToGenerate = PAGE_TYPE_LIVE
	else:
		# triptych
		if( tripFlg ):
			pageTypeToGenerate = PAGE_TYPE_TRIPTYCH
			reloadTimeInMSec   = 0
			M         = 6
			N         = 1000000
			bodyWidth = (widthPerImgCell + iw)*6 + widthPerImgCell + (int)(iw/2) + 15
		# showcase
		else:
			pageTypeToGenerate = PAGE_TYPE_SHOWCASE
		

	# generate the header for the file
	outStr = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<script type="text/javascript" src="js/jquery-1.7.1.min.js"></script>
	<script src="js/funcs.js" type="text/javascript"></script>
	<link rel="stylesheet" href="css/simple.css" type="text/css" media="screen" />
	<link rel="stylesheet" href="css/slimbox2.css" type="text/css" media="screen" />
	<script type="text/javascript" src="js/jquery.timers-1.2.js"></script>
	<script type="text/javascript" src="js/slimbox2.js"></script>
	<script type="text/javascript" src="js/autoload.js"></script>"""
	
	# add page title
	outStr += ("<title>%(s0)s</title>" % { 's0':PAGE_TITLES[pageTypeToGenerate] } )

	# body onload
	if( reloadTimeInMSec!=0 ):
		outStr += ("</head><body onload=\"Javascript:documentLoaded(%(s0)s);\" style=\"width:%(s1)spx\">" % {'s0':str(reloadTimeInMSec), 's1':str(bodyWidth)})
	else:
		outStr += ("</head><body style=\"width:%(s0)spx\">" % {'s0':str(bodyWidth)})
	
	# add page header and pre-amble text
	outStr += ("<h2>%(s0)s</h2>%(s1)s" % { 's0':PAGE_TITLES[pageTypeToGenerate], 's1':PAGE_PREAMABLE[pageTypeToGenerate] })
	
	# add automagic reloading flag 
	if( reloadTimeInMSec!=0 ):
		outStr += """<span class="smaller">Auto Refresh (<span id="timeLeft">in """ + str(reloadTimeInMSec/1000) + """ sec</span>): <a href="#" id="refreshOff" onclick="javascript:timedRefresh(0);return false;">Off</a> | 
	<a href="#" id="refreshOn" onclick="javascript:timedRefresh(""" + str(reloadTimeInMSec) + """); return false;">On</a></span><br/><br/>""";

	
	# compare the input and output directories, only if inDir is set!
	# if different, copy only images that aren't in outDirectory
	if( inDir != "" ):
		fullInPath  = os.path.abspath( inDir )
		fullOutPath = os.path.abspath( outDir )
		print(fullInPath, fullOutPath)
		if( not os.path.exists( fullInPath ) ):
			print ("ERROR: input path (" + fullInPath + ")doesn't exist!")
		if( not os.path.exists( fullOutPath ) ):
			print ("ERROR: output path (" + fullOutPath + ")doesn't exist!")

		if( fullInPath != fullOutPath ):
			filesIn   = glob.glob( os.path.join( fullInPath,  '*.png' ) )
			filesOut  = glob.glob( os.path.join( fullOutPath, '*.png' ) )
			filesIn1  = [os.path.basename(f) for f in filesIn]
			filesOut1 = [os.path.basename(f) for f in filesOut]
			print(filesIn)
			del filesIn, filesOut

			filesToMove = list( set(filesIn1) - set(filesOut1) )
			print(filesToMove)
			for f in filesToMove:
				print(fullOutPath, os.path.basename(f))
				if( pageTypeToGenerate!=PAGE_TYPE_TRIPTYCH ):
					# try copy for now, but might not work quite too well...
					bname = os.path.basename( f )
					#print "- copying file " + f + " to " + os.path.join( fullOutPath, bname )
					shutil.copy2( f, os.path.join( fullOutPath, bname ) )

				# if we are in triptych mode, we must rescale images to largest one during "copy"
				else:
					# check if this filename already moved
					bname = os.path.basename( f )
					
					# find all the files that fit
					stuffFound = findImageFileInFolder( fullOutPath, bname, None, camIdx )
					if( len(stuffFound)>0 ):
						del stuffFound
						continue
						
					# check if input actually has a tripplet
					stuffFound = findImageFileInFolder( fullInPath, bname, [0,1,2], camIdx )
					if( len(stuffFound)<3 ):
						print ("ERROR: we can't find a triplet using file: " + bname)
						print ("Instead we found: ")
						print (stuffFound)
						del stuffFound
						continue

					# parse out the file name, then get snowflake's sizes!
					# NOTE: we'll normalize the time to the 1st found snowflake
					# as in. Let's say we have 3 flake images:
					#   - 2013.02.06_14.14.20.123456_flake_3_cam_0.png
					#   - 2013.02.06_14.14.20.777777_flake_3_cam_1.png
					#   - 2013.02.06_14.14.21.111111_flake_3_cam_2.png
					# the resulting (copied) 3 images will be
					#   - 2013.02.06_14.14.20.123456_flake_3_cam_0.png
					#   - 2013.02.06_14.14.20.123456_flake_3_cam_1.png
					#   - 2013.02.06_14.14.20.123456_flake_3_cam_2.png
					thisFilesSplit = parseFileName( f, None )

					# get ith camera
					#namesBefore = [None,None,None]
					namesBefore = findImageFileInFolder( fullInPath, f, [0,1,2], camIdx )
					namesAfter  = [None,None,None]
					img = [None,None,None]
					ws  = [None,None,None]
					hs  = [None,None,None]
					hMax = -1
					wMax = -1
					for c in range(0,3):
						thisFilesSplit[camIdx] = str(c)
						tmpName        = "_".join(thisFilesSplit) + ".png"
						namesBefore[c] = os.path.join( fullInPath, namesBefore[c] )
						namesAfter[c]  = os.path.join( fullOutPath, tmpName )
							
						#print "looking at: " + namesBefore[c] + ", going to : " + namesAfter[c]
						img[c] = Image.open( namesBefore[c] )
						w, h   = img[c].size
						ws[c]  = w
						hs[c]  = h

						if( h > hMax ):
							hMax = h
							wMax = w

					# get max height and rescale images proportionally if need be,
					# saving them to output
					for c in range(0,3):
						# max image -> just copy
						if( ws[c]==hMax ):
							bname = os.path.basename( namesAfter[c] )
							shutil.copy2( namesBefore[c], os.path.join( fullOutPath, bname ) )
							continue

						# other image -> resize
						tmpw = wMax #ws[c]
						tmph = hMax #hs[c]
						#if( ws[c] > hs[c] ):
						#	tmph = int( tmpw * float( hs[c] ) / ws[c] )
						#else:
						tmpw = int( tmph * float( ws[c] ) / hs[c] )
						
						#print "--- original size (" + str(ws[c]) + ", " + str(hs[c]) + "), saving to (" + str(tmpw) +", " + str(tmph) +"), max size: (" + str(wMax) + ", " + str(hMax) + ")"
			
						imgTags = img[c].info
						#img2    = img.convert("RGB")
						img2    = img[c].resize( (tmpw, tmph), Image.ANTIALIAS )

						reservedTags = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect', 'icc_profile' )
						meta    = PngImagePlugin.PngInfo()
						mc		= 0
						for k,v in imgTags.iteritems():
							if k in reservedTags:
								meta.add( k, v )
								continue
							meta.add_text( k, v, 0 )
							#print "found meta {0}".format( k )
							mc = mc+1

						saveName = os.path.join( fullOutPath, os.path.basename( namesAfter[c] ) )
						if( mc>0 ):
							img2.save( saveName, "PNG", pnginfo=meta )
						else:
							img2.save( saveName, "PNG" )

						del img2, meta, imgTags, reservedTags
				
					#for f in namesBefore:
					#	print f
					#print "after:"
					#for f in namesAfter:
					#	print f
					#print "----------------------------"
				
					# clean up!
					del namesBefore, namesAfter, img, ws, hs

	# get images in folder + clean up the oldest ones
	numImgs = N*M
	imgs    = getImagesInDir( outDir )
	if( len(imgs)>numImgs ):
		for i in range(numImgs, len(imgs) ):
			os.remove( imgs[i][0] )
			os.remove( os.path.splitext(imgs[i][0])[0] + "_s.jpg" )
			#print "- removing file " + imgs[i][0]
		imgs = imgs[0:numImgs]


	# define font for overlay (just in case font I got is malicious, use it as last resort)
	fontSizeB = 16
	fontSizeS = 8
	try:
		overFontB = ImageFont.truetype( "Verdana.ttf", fontSizeB )
		overFontS = ImageFont.truetype( "Verdana.ttf", fontSizeS )
		# overFontB = ImageFont.truetype( "arial.ttf", fontSizeB )
		# overFontS = ImageFont.truetype( "arial.ttf", fontSizeS )
	except:
		overFontB = ImageFont.truetype( "img/Verdana.ttf", fontSizeB )
		overFontS = ImageFont.truetype( "img/Verdana.ttf", fontSizeS )		
	copyMsg       = "Tim Garrett, University of Utah, "
	reservedTags  = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect', 'icc_profile' )

	# get two images for overlay - larger versions
	#overNSFL   = Image.open( 'img/ssl_NSF_desat.png' )
	##overNSFL  = Image.open( 'img/ssl_NSF.png' )
	#overALTAL  = Image.open( 'img/ssl_ALTA.png' )
	#overNSFLw, overNSFLh   = overNSFL.size
	#overALTALw, overALTALh = overALTAL.size
	#overCombWL = overNSFLw + overALTALw + 5

	# get two images for overlay - smaller versions
	overNSF   = Image.open( 'img/ss_NSF_desat.png' )
	#overNSF  = Image.open( 'img/ss_NSF.png' )
	overALTA  = Image.open( 'img/ss_ALTA.png' )
	overNSFw, overNSFh   = overNSF.size
	overALTAw, overALTAh = overALTA.size
	overCombW = overNSFw + overALTAw + 5

	# insert the table with images
	c          = 1				# image counter
	lImgs      = len(imgs)		# total number of images
	locTriplet = 0				# triplet counter (used for triptych page only!)

	# do we need to include space around images and lines/writing underneath them
	if( nolineFlg ):
		outStr += "<table cellpadding='0' cellspacing='0'>\n\t<tr>\n"
	else:
		outStr += "<table cellpadding='15px' cellspacing='0'>\n\t<tr>\n"

	for f in imgs:
		
		#print "- file: " + f[0]
		
		# get the correct image dimensions
		tmpw = iw
		tmph = ih
		relp = f[0]
		thumbFileInfo = os.path.splitext( f[0] )
		trelp= thumbFileInfo[0] + "_s.jpg";
		img  = Image.open( f[0] )
		w, h = img.size
		if( w>iw or h>ih ):
			if( w > h ):
				tmph = int( tmpw * float( h ) / w )
			else:
				tmpw = int( tmph * float( w ) / h )
		else:
			tmpw     = w
			tmph     = h
			

		# do we need to generate a thumbnail (and create overlay)?
		# if need to do thumbnail -> newly added image
		timestp = datetime.datetime.fromtimestamp( f[1] )
		if( os.path.isfile( trelp )==False ):
			imgTags = img.info
			img2    = img.convert("RGB")
			img3    = img2.copy()

			# add copyright text + sponsor logos
			yearStr = timestp.strftime( '%Y' )
			draw    = ImageDraw.Draw( img2 )
			tmpStr  = copyMsg + yearStr
			txtBW, txtBH = overFontB.getsize( tmpStr )

			#  - largest logo + large font
			#if( w-overCombWL-10-txtBW > 0 ):
			#	img2.paste( overNSFL, (w-overNSFLw,h-overNSFLh) )
			#	img2.paste( overALTAL, (w-overCombWL,h-overALTALh) )
			#	txtDim   = (w-txtBW-10-overCombWL, (int)(h-1.5*fontSizeB))
			#	draw.text( txtDim, tmpStr, (255,255,255), font=overFontB )

			#  - small logo + large font
			#elif( w-overCombW-10-txtBW > 0 ):
			if( w-overCombW-10-txtBW > 0 ):
				img2.paste( overNSF, (w-overNSFw,h-overNSFh) )
				img2.paste( overALTA, (w-overCombW,h-overALTAh) )
				txtDim   = (w-txtBW-10-overCombW, (int)(h-1.5*fontSizeB))
				draw.text( txtDim, tmpStr, (255,255,255), font=overFontB )
				
				# label in top-left corner camera id
				if( pageTypeToGenerate==PAGE_TYPE_TRIPTYCH ):
					imgCamId       = parseFileName( relp, camIdx )
					imgCamIdStr    = str(imgCamId)
					txtBW2, txtBH2 = overFontB.getsize( imgCamIdStr )
					txtDim2 = (txtBW2+5, fontSizeB)
					draw.text( txtDim2, imgCamIdStr, (255,255,255), font=overFontB )

			#  - no logo + large font
			elif( w-txtBW-5 > 0 ):
				txtDim   = (w-txtBW-5, (int)(h-1.5*fontSizeB))
				draw.text( txtDim, tmpStr, (255,255,255), font=overFontB )
				
				# label in top-left corner camera id
				if( pageTypeToGenerate==PAGE_TYPE_TRIPTYCH ):
					imgCamId       = parseFileName( relp, camIdx )
					imgCamIdStr    = str(imgCamId)
					txtBW2, txtBH2 = overFontB.getsize( imgCamIdStr )
					txtDim2 = (txtBW2, fontSizeB)
					draw.text( txtDim2, imgCamIdStr, (255,255,255), font=overFontB )

			# - no logo + small font
			else:
				txtSW, txtSH = overFontS.getsize( tmpStr )
				draw.text( (w-txtSW-5,h-1.5*fontSizeS), tmpStr, (255,255,255), font=overFontS )
				
				# label in top-left corner camera id
				if( pageTypeToGenerate==PAGE_TYPE_TRIPTYCH ):
					imgCamId       = parseFileName( relp, camIdx )
					imgCamIdStr    = str(imgCamId)
					txtSW2, txtSH2 = overFontS.getsize( imgCamIdStr )
					txtDim2 = (txtSW2, fontSizeS)
					draw.text( txtDim2, imgCamIdStr, (255,255,255), font=overFontS )

			meta    = PngImagePlugin.PngInfo()
			mc		= 0
			for k,v in imgTags.items():
				if k in reservedTags:
					meta.add( k, v )
					continue
				meta.add_text( k, v, 0 )
				#print "found meta {0}".format( k )
				mc = mc+1
			# if( mc>0 ):
			# 	img2.save( thumbFileInfo[0] + ".png", "PNG", pnginfo=meta )
			# else:
			img2.save( thumbFileInfo[0] + ".png", "PNG" )

			# save full res + thumbnail (no overlay)
			img3.thumbnail( (tmpw,tmph), Image.ANTIALIAS )
			#draw2 = ImageDraw.Draw( img3 )
			#txtSW, txtSH = overFontS.getsize( tmpStr )
			#draw2.text( (tmpw-txtSW-5,tmph-1.5*fontSizeS), tmpStr, (255,255,255), font=overFontS )
			img3.save( trelp, "JPEG" )
			#del draw, img2, draw2, img3, meta, imgTags
			del draw, img2, img3, meta, imgTags

		# note, we'll keep the time stamp only for the live feed generation
		# LIVE
		if( reloadTimeInMSec!=0 ):
			if( nolineFlg ):
				outStr += ("\t\t<td style=\"border-bottom:none;\"><a href='%(s0)s' rel=\"lightbox[flakes]\" title=\"%(s2)s\" onclick=\"javascript:toggleTimedRefresh(1); return false;\"><img src='%(s1)s' width='%(s3)spx' height='%(s4)spx' alt='Snowflake from %(s2)s'/></a></td>\n" 
						% { 's0':os.path.basename(relp), 's1':os.path.basename(trelp), 's2':timestp.strftime('%Y.%m.%d, %H:%M:%S'), 's3':tmpw, 's4':tmph })
			else:
				outStr += ("\t\t<td><a href='%(s0)s' rel=\"lightbox[flakes]\" title=\"%(s2)s\" onclick=\"javascript:toggleTimedRefresh(1); return false;\"><img src='%(s1)s' width='%(s3)spx' height='%(s4)spx' alt='Snowflake from %(s2)s'/></a><br/>%(s2)s</td>\n" 
						% { 's0':os.path.basename(relp), 's1':os.path.basename(trelp), 's2':timestp.strftime('%Y.%m.%d, %H:%M:%S'), 's3':tmpw, 's4':tmph })
		# triptych
		elif( pageTypeToGenerate==PAGE_TYPE_TRIPTYCH ):
			#imgCamId = parseFileName( relp, camIdx )
			imgCamId  = locTriplet % 3
			splitName = parseFileName( relp, None )
			splitName[camIdx] = str(imgCamId)
			relp      = "_".join( splitName )
			if( camIdx==len(splitName)-1 ):
				relp += ".png"
			
			splitName = parseFileName( trelp, None )
			splitName[camIdx] = str(imgCamId)
			trelp     = "_".join( splitName )
			if( camIdx==len(splitName)-2 ):
				trelp += ".jpg"
			if( nolineFlg ):
				outStr += ("\t\t<td style=\"border-bottom:none;\"><a href='%(s0)s' rel=\"lightbox[flakes]\" title=\"%(s5)s\" onclick=\"javascript:toggleTimedRefresh(1); return false;\"><img src='%(s1)s' width='%(s3)spx' height='%(s4)spx' alt='Snowflake from %(s2)s'/></a></td>\n" 
							% { 's0':os.path.basename(relp), 's1':os.path.basename(trelp), 's2':timestp.strftime('%Y.%m.%d, %H:%M:%S'), 's3':tmpw, 's4':tmph, 's5':('Camera '+str(imgCamId)) })
			else:
				outStr += ("\t\t<td><a href='%(s0)s' rel=\"lightbox[flakes]\" title=\"%(s5)s\" onclick=\"javascript:toggleTimedRefresh(1); return false;\"><img src='%(s1)s' width='%(s3)spx' height='%(s4)spx' alt='Snowflake from %(s2)s'/></a><br/>%(s5)s</td>\n" 
							% { 's0':os.path.basename(relp), 's1':os.path.basename(trelp), 's2':timestp.strftime('%Y.%m.%d, %H:%M:%S'), 's3':tmpw, 's4':tmph, 's5':('Camera '+str(imgCamId)) })

			# do we need a space-filler column in the middle?
			locTriplet += 1
			if( locTriplet%6==0 ):
				locTriplet = 0

			elif( locTriplet%3==0 ):
				outStr += ("\t\t<td style=\"border-bottom:none;\" width='%(s0)spx'>  </td>\n" % {'s0':str((int)(iw/2))} )
					
			
		# showcase
		else:
			if( nolineFlg ):
				outStr += ("\t\t<td style=\"border-bottom:none;\"><a href='%(s0)s' rel=\"lightbox[flakes]\" title=\"\" onclick=\"javascript:toggleTimedRefresh(1); return false;\"><img src='%(s1)s' width='%(s3)spx' height='%(s4)spx' alt='Snowflake from %(s2)s'/></a></td>\n" 
							% { 's0':os.path.basename(relp), 's1':os.path.basename(trelp), 's2':timestp.strftime('%Y.%m.%d, %H:%M:%S'), 's3':tmpw, 's4':tmph })
			else:
				outStr += ("\t\t<td><a href='%(s0)s' rel=\"lightbox[flakes]\" title=\"\" onclick=\"javascript:toggleTimedRefresh(1); return false;\"><img src='%(s1)s' width='%(s3)spx' height='%(s4)spx' alt='Snowflake from %(s2)s'/></a></td>\n" 
							% { 's0':os.path.basename(relp), 's1':os.path.basename(trelp), 's2':timestp.strftime('%Y.%m.%d, %H:%M:%S'), 's3':tmpw, 's4':tmph })
		
		if( c%M==0 and lImgs>c ):
			outStr += "\t</tr>\n\t<tr>\n"
		c      += 1
	outStr += "\t</tr>\n</table>\n"


	# finalize file
	now     = datetime.datetime.now()
	outStr += "<br/><br/>\n<b>Updated on:</b> " + now.strftime( "%Y.%m.%d, %H:%M" ) + "<br/>"
	outStr += PAGE_FOOTER + "</body></html>"

	outFile1 = os.path.join( outDir, outFile )
	fOut = open( outFile1, "w" )
	fOut.write( outStr )
	fOut.close()



#
#  MAIN - parses the command line options
#
def main():

	# set-up parser
	# from: http://www.doughellmann.com/PyMOTW/argparse/
	parser = argparse.ArgumentParser( description = 'Creation of Snowflake Showcase HTML', add_help = True )

	# output parameters
	parser.add_argument( '-v', action='store_true', default=False, help="Verbose output (default: %(default)s)" )
	parser.add_argument( '-n', type=int, default=8, help="N in Image Matrix NxM (default: %(default)s)" )
	parser.add_argument( '-m', type=int, default=5, help="M in Image Matrix NxM (default: %(default)s)" )
	parser.add_argument( '-pw', type=int, default=120, help="Shown image width (default: %(default)s)" )
	parser.add_argument( '-ph', type=int, default=120, help="Shown image height (default: %(default)s)" )
	parser.add_argument( '-din',  default="",  help="Input image directory (default: %(default)s)" )
	parser.add_argument( '-dout', default=".", help="Output directory (default: %(default)s)" )
	parser.add_argument( '-fout', default="snowflakes.html", help="Output HTML file (default: %(default)s)" )
	parser.add_argument( '-rtime', type=int, default=5000, help="Time before each page refreshes in msec, 0=never (default: %(default)s)" )
	parser.add_argument( '-triptych', action='store_true', default=False, help="Flag whether generate triptych page (default: %(default)s)" )
	parser.add_argument( '-nolines', action='store_true', default=False, help="Flag whether to remove labels and lines underneath images (default: %(default)s)" )
	parser.add_argument( '-camIx', type=int, default=5, help="Id of piece of filename (between _) for camera id (default: %(default)s)" )

	# attempt to parse the command line and process program
	try:
		parsedVal = parser.parse_args()

		# dump the parsed info
		if( parsedVal.v ):
			# update visuals for triptych
			if( parsedVal.triptych ):
				parsedVal.m = 6
				parsedVal.n = 1000000
				parsedVal.rtime = 0
		
			print( "\nThe following parameters will be used for generation:" )
			print( " -input directory:   %s" % (parsedVal.din) )
			print( " -output directory:  %s" % (parsedVal.dout) )
			print( " -output file:       %s" % (parsedVal.fout) )
			print( " -image matrix dim:  %sx%s" % (parsedVal.n, parsedVal.m) )
			print( " -shown image dim:   %sx%s" % (parsedVal.pw, parsedVal.ph) )
			print( " -refresh time (ms): %s" % (parsedVal.rtime) )
			print( " -triptych flag:     %s" % (parsedVal.triptych) )
			print( " -no lines flag:     %s" % (parsedVal.nolines) )
			print( " -id of camera indx: %s" % (parsedVal.camIx) )
			print( "" )

		# do the work
		genOutputHTML( parsedVal.din, parsedVal.dout, parsedVal.fout, parsedVal.n, parsedVal.m, 
					   parsedVal.pw, parsedVal.ph, parsedVal.rtime, parsedVal.triptych, 
					   parsedVal.nolines, parsedVal.camIx )


	except IOError as msg:
		parser.error( str(msg) )


if __name__ == "__main__":
	main()



