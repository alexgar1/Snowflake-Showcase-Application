

# User Interface for intializing MASC and Snowflake Showcase
# Written by Alex Garrett, alexgarrett2468@gmail.com, for University of Utah, 2024
# Some functions borrowed from showcase version 1 written by Konstantin Shkurko


# 1. Displays UI to configure filter specifications for snowflake showcase (size and sharpness)
# 2. When a new snowflake is photographed that meets filter criteria it uploads it to snowflake showcase website
# 3. Updates data plots for data from masc images (size and rate)


#! NOTE
# Be sure to change 'PATH' global string if moving 'masc_showcase' folder to a new location or renaming
# Specify path where masc writes photos if changed under self.mascpath

'''
TO DO:

	- catch up from offline
	- new storm creates new file and needs to add to recent


'''

from tkinter import *
from tkinter import ttk
from datetime import timedelta, datetime
from PIL import ImageTk, Image
from memory_profiler import profile
import basicSort, os, time, shutil, genHTML, initMASC, deltaStorm, paramiko, re, threading, glob, sys, brighten, logging

PATH =	'C:\\Users\\Cooper\\Desktop\\masc_showcase\\' # make sure ends with \
SERVER = '/uufs/chpc.utah.edu/common/home/snowflake3/showcase/' # "
REFRESH = 120 # how often to check folder and update (seconds)


password = '' # use password if RSA is not working ( you have to change code in connection to use password instead )

class Start:
	
	def __init__(self):
		self.mascpath = 'C:\\MASC\\The_Alta_Project_2023\\'
		#test folder
		#self.mascpath = 'C:\\Users\\Cooper\\Desktop\\masc_showcase\\test\\'
		self.subdirectories = []
		self.name = 'u6045297'
		self.pw = ''
		self.blur = None
		self.size = None
		self.snowing = False
		self.storm = 1
		self.flakes = [0]
		self.sizes = [0.001]
		self.imgpaths = []
		self.all = []
		self.hour = []
		self.ssh = None
		self.subset = []
		self.labels = []
		self.lock = threading.Lock()
		self.offline = False # set to true for testing without connecting
	
	

	def log(self, log_file='log\\application.log'):
		# Create a logger
		logger = logging.getLogger("ConsoleLogger")
		logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG to capture all levels of logs

		file_handler = logging.FileHandler(log_file)
		file_handler.setLevel(logging.DEBUG)
		
		formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
		file_handler.setFormatter(formatter)

		# Add the file handler to the logger
		logger.addHandler(file_handler)

		# Define a StreamToLogger class to redirect stdout and stderr to the logger
		class StreamToLogger:
			def __init__(self, logger, log_level):
				self.logger = logger
				self.log_level = log_level
				self.line_buffer = ""

			def write(self, message):
				if message != "\n":  # Skip blank lines
					self.line_buffer += message
				if message.endswith("\n"):
					self.logger.log(self.log_level, self.line_buffer.strip())
					self.line_buffer = ""

			def flush(self):
				if self.line_buffer:
					self.logger.log(self.log_level, self.line_buffer.strip())
					self.line_buffer = ""

		# Redirect stdout and stderr to the logger
		sys.stdout = StreamToLogger(logger, logging.INFO)  # Redirect stdout to INFO level
		sys.stderr = StreamToLogger(logger, logging.ERROR)  # Redirect stderr to ERROR level

		
				

	#############
	# APP LOGIC #
	#############


	def connect(self, backoff=0):
		try:
			if self.ssh is not None:
				self.ssh.close()
			self.ssh = paramiko.SSHClient()
			self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			
			self.ssh.connect('kingspeak33.chpc.utah.edu', username=self.name, pkey=paramiko.RSAKey.from_private_key_file(PATH+"id_rsa"))
			print('Connected')
			return True
		except Exception as e:
			print(e)
			if backoff > 1:
				print('backoff failed going offline...')
				self.offline = True
				return False
				
			print('connection failed again retrying...')
			if backoff==0:
			
				backoff=1
			time.sleep(backoff*2)
			self.connect(backoff*2)

	
	
	def checkConnection(self):
		if self.ssh is None:
			return False
		
		try:
			transport = self.ssh.get_transport()
			if transport and transport.is_active():
				return True
			else:
				self.ssh.close()
				return False
		except Exception as e:
			print(e, 'in checkConnection')
			return False
	
	

	def cpImg(self, scp, image, errorCount=0):
		try:
			# copy image
			new = os.path.join(PATH+'chosen\\', image)
			
			# gamma correct image
			#processed = brighten.brightening(new, minintens=0.0, maxintens=1.0, limitintens=0.95)
			# Save processed image
			#processed.save(new)
			
			scp.put(new, SERVER+'images/'+image)
			#scp.put(new[:-4]+'_s.jpg', SERVER+'images/'+image[:-4]+'_s.jpg')
			print('Uploaded:', image)
			
			# copy showcase html
			#scp.put(f'{PATH}chosen\\index.html', SERVER+'images/index.html')
			#print('Updated html')

			
			
		except Exception as e:
			print(e, 'in uploading', image)
			print('Trying', image, 'again...')
			time.sleep(1)
			if errorCount < 3:
				errorCount += 1
				self.cpImg(scp, image, errorCount)
			else:
				print('giving up on', image)
			
			

	def copy(self, image=False, restart=False):
			
			
		try:
			scp = self.ssh.open_sftp()
			if restart == True:
				scp.put('dataparam.txt', SERVER+'dataparam.txt')
			# copy data html
			scp.put(f'{PATH}data\\data{str(self.storm)}.txt', SERVER+f'data/data{str(self.storm)}.txt')
			print(f'DATA {self.storm} UPLOADED')
		
			if image != False:
				self.cpImg(scp, image)
				
			scp.close()

		except Exception as e:
			print(e, 'in copy')
			
		

	def update(self, image=False, retry=False):
		# Connect to the remote server via SSH
		if self.checkConnection():
			if retry != False:
				self.copy(retry)
				return
			
			if image == False:
				self.copy()
				return
			
		 
			self.copy(image)
				

		else:
			print()
			print("Reconnecting SSH...")
			if self.connect() == True:
				self.offline = False
				print("Back Online")
				print()
				
			else:
				print('Connection Failure: Showcase will still collect data')
				self.ssh.close()
			

	def switch(self):
		self.root.destroy()

	
	def parseDateTimeFromFileName(self, inFile):
		# # @author	   Konstantin Shkurko (kshkurko@cs.utah.edu)

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
	
	
	def getImagesInDir(self):
			# The date is extraced in the following order (until one succeeds)
			#	1. Based on the "Creation Time" within image meta-data
			#	2. Using parseDateTimeFromFileName function above
			#	3. Using the os file system, file creation time (Windows) or 
			#	   last metadata modification time (*nix)
			#
			# @return list of PNG filenames sorted on timestamp in descending order
			#
			# # original code written by Konstantin Shkurko (kshkurko@cs.utah.edu)
			# # modified by alex garrett

		if( not os.path.exists( self.mascpath ) ):
			print( "ERROR: output path (" + self.mascpath + ")doesn't exist!")

		# init file info
		outInfo = []
		files = []

		# Get a list of all subdirectories in the given directory

		# Sort the subdirectories based on modification time in descending order
		#subdirectories.sort(key=lambda d: os.path.getmtime(os.path.join(self.mascpath, d)), reverse=False)
		#subdirectories.reverse()
		
		self.subdirectories = [d for d in os.listdir(self.mascpath) if os.path.isdir(os.path.join(self.mascpath, d))]

		# Sort directories by birth time (creation time) if available; otherwise, use change time
		self.subdirectories.sort(key=lambda d: os.path.getmtime(os.path.join(self.mascpath, d)), reverse=True)
		
		
		#print(self.subdirectories[0])
		
		
		dir = os.path.join(self.mascpath, self.subdirectories[0])
 
		# gets files
		for file in os.listdir(dir):
			if file.lower().endswith(('.png')):
				# automatically ignore files under certain size (bytes)
				if os.path.getsize(dir+'\\'+file) > 3000:

					# Construct the full path of the file
					files.append(os.path.join(dir, file))

		for file in files:
			# get image tags to resave later (and parse out date)
			try:
				img		 = Image.open( file )
			except:
				continue
			imgTags	 = img.info
			if('Creation Time' in imgTags):
				try:
					imgCTime	  = time.strptime( imgTags['Creation Time'], "%d %b %Y %H:%M:%S +0000" )
					outInfo.append( [file, time.mktime( imgCTime )] )
				except:
					pass
			else:
				tmp = self.parseDateTimeFromFileName( file )
				if( tmp != False ):
					outInfo.append( [file, tmp] )
				else:
					fInfo = os.stat( file )
					outInfo.append( [file, fInfo.st_ctime] )
			del img

			# maybe add a slider to only check images in the past
		# sort in descending order based on created timestamp 
		outInfo.sort( key=lambda tmp: tmp[1], reverse=True)
		return outInfo
	
	
	def checkSnowing(self):
		
		# if snowing check if not snowing
		if self.snowing == True:
			if deltaStorm.toggle(self.all, True) == True:
				self.snowing = False # end storm
				self.storm += 1 # new storm
				with open(f'data\\data{self.storm}.txt', 'w'):
					pass
				
				print("./././././.")
				print('END STORM', self.storm)
				print()

		# if not snowing check if snowing
		elif self.snowing == False:
			if deltaStorm.toggle(self.all, False) == True:
				self.snowing = True
				self.sizes = [0.01]
		
				
				print()
				print('NEW STORM', self.storm)
				print("`\`\\`\\`\\`\\`\\")
				print()
				
		print('currently snowing:',self.snowing)

	def funcs(self, blur):
		# normalizes blur measurement for slider
		blurthresh = (blur**2)/10
		
		return blurthresh
	
	def writeData(self, img):
		# write to dataN.txt
		with open(f'{PATH}data/data{self.storm}.txt', 'a') as data:
			data.write('\n')
			data.write(img[0][len(self.mascpath)+22:]+',') # name
			data.write(str(img[1])+',') #					 date
			data.write(str(img[2])+',') #					 storm
			data.write(str(img[3])+',') #					 blur
			data.write(str(img[4])) #						 size
		
	
	def checkDir(self):
		''' checks masc path for new images then updates html and copys both image and html file to server'''
		
		new = self.getImagesInDir() # get new total images
		

		
		
		dif = len(new)-len(self.hour)
		if dif>0:
			print(dif, 'new images')
		
		
		for i in range(0,dif):
			img = new[i]
			if img[1] not in self.all:
				self.all.append(img[1])
				
			
				
			img.append(self.storm)
			
			# get size and sharpness info about snowflake appended to img
			img = basicSort.check(img, self.params)

			if img[4]<0.2: # any flakes below 0.2 mm are not considered
				continue
			
			# add new image to imgpaths 
			if img not in self.imgpaths: # redundancy
				self.imgpaths.insert(0, img)
				# write data (regardless of image upload criteria as long as flake is bigger than 0.2)
				self.writeData(img)
				
			print(round(img[4],1), 'mm flake', datetime.fromtimestamp(img[1]).strftime("%Y-%m-%d %H:%M:%S"))
			self.sizes.append(img[4])

			blurthresh = self.blur.get()
			sizethresh = self.size.get()
			
			
			if img[3] <= blurthresh or img[4] <= sizethresh:
				continue

			# copy to chosen folder
			shutil.copy(img[0], PATH+'\\chosen\\')

			# get HTML with (new) data
			#	 
			#try:
			#	 genHTML.genOutputHTML(PATH+'chosen\\', PATH+'chosen\\', 'index.html', 20, 9, 120, 120, 10000, False, False, 5)
			#except Exception as e:
			#	 print(e, 'generating html')
			

			# get path of image in chosen folder
			dir, file = os.path.split(img[0])
			
			##
			if self.offline == False:
				self.update(file)
			##
			
			self.getImgSubset(0)
		
		self.hour = new
		


	
	def getImgSubset(self, value):
		''' produces an image subset of most recent images that match criteria from sliders '''
		
		# self.checkDir()
		self.subset = []

		# get subset images that match criteria

		blurthresh = self.blur.get()
		sizethresh = self.size.get()
			
		
		for img in self.imgpaths:
			if len(self.subset)>8:
				 break
			if img[3] > blurthresh and img[4] > sizethresh:
				 self.subset.append(img)
				
		
		# if there are not enough images replace with default
		i = 0
		while len(self.subset) < 9:
			self.subset.append(['defaults/1.png',0,0,0,0])
			i+=1
			
		# Function to parse the data and extract sizes
		
			
	def updateUI(self):
		# get rid of old images
		for label in self.labels:
			label.image = None	# Remove reference to image
			label.destroy()
			
		self.labels.clear() 

		# create image grid
		for i, imagepath in enumerate(self.subset):
			# Open the image using PIL
			with Image.open(imagepath[0]) as img:

				# Resize the image
				img = img.resize((250, 250))

				# Create an ImageTk object to display the image in Tkinter
				img = ImageTk.PhotoImage(img)

				# position math
				r = i//3
				c = i%3

				if r!=0:
					r+=1
				if r==3:
					r+=1

				label = Label(self.frame2, image=img)
				label.grid(row=r, column=c)

				# Create a label for the date taken
				date_taken = imagepath[1]
				time_struct = time.localtime(date_taken)
				formatted = time.strftime(f"%m/%d %H:%M sharp:{round(imagepath[3],1)}, size:{round(imagepath[4], 1)}", time_struct)
				date = Label(self.frame2, text=formatted)
				date.grid(row=r + 1, column=c, padx=10)

				# Keep a reference to the ImageTk object to prevent it from being garbage collected
				label.image = img
				self.labels.append(label)
				self.labels.append(date)
				
		
		self.root.after(2000, lambda: self.updateUI())
	
		
	
	def startBackgroundTasks(self):
		# Create and start the background thread
		print('searching', self.mascpath)
		print('NOTE: images smaller than 3 KB and 0.2 mm are ignored')
		threading.Thread(target=self.background, daemon=True).start()

	
	def background(self):
		# every 60 seconds check masc for new images update server and generate plots on server
		print("Background task started")
		while True:
			with self.lock:
				
				self.checkDir()
				self.checkSnowing()
				
				# update data
				if self.offline == False:
					self.update()
				
				try:
					# generate plots on CHPC computer
					if self.offline == False:
						stdin, stdout, stderr = self.ssh.exec_command(f'cd {SERVER}; python3 genDataPlots.py')
						
						if stderr != None:
							print('PLOTS UPDATED',datetime.now() )
							
						else:
							print('ERROR GENERATING PLOTS')
				
				except Exception as e:
					print(e, 'while trying to run data plot generation on server')
			
			time.sleep(REFRESH) # wait 60 seconds
			
	def organize(self):
		'''SNOWFLAKE OBJECT: "self.imgpapths" (list in case more data is needed)
		# imgpaths item order: ['name', date, storm, sharpness, size]
		'''
		
		
		# Tokenize exisitng images (maybe useful in future for analysis of previous hour's folder)
		#self.imgpaths = self.getImagesInDir()
		#
		#for i in self.imgpaths:
			#i.append(0)
		#
		#self.imgpaths = basicSort.process(self.imgpaths, self.params) # appends
		
		
		self.subdirectories = [d for d in os.listdir(self.mascpath) if os.path.isdir(os.path.join(self.mascpath, d))]

		# Find the latest storm file
		pattern = os.path.join(PATH+'data\\', 'data*.txt')
		files = glob.glob(pattern)

		# Extract the number from each filename and find the maximum
		m = 0
		latest_file = None
		for file_name in files:
			match = re.search(r'data(\d+).txt', os.path.basename(file_name))
			if match:
				number = int(match.group(1))
				if number > m:
					self.storm = number
					m = number
					latest_file = file_name

		# Check if the latest file was modified in the last 24 hours
		if latest_file:
			last_modified = os.path.getmtime(latest_file)
			if (time.time() - last_modified) > 86400:  # 24 hours in seconds
				self.storm += 1
				print(f"Creating new data file for storm {self.storm}")
				with open(os.path.join(PATH, f'data\\data{self.storm}.txt'), 'w'):
					pass
		else:
			# If no files found, start with the first storm
			self.storm = 1
			with open(os.path.join(PATH, 'data\\data1.txt'), 'w'):
				pass

		self.params = []
		with open('dataparam.txt', 'r') as f:
			content = f.readlines()
			for line in content:
				if line:
					match = re.search('\w+=(\d+\.\d+)', line)
					if match:
						self.params.append(float(match.group(1)))

		print('Starting from new storm', self.storm)

	###############
	# APP WINDOWS #
	###############
	
	def closing(self):
		"""Function to be executed when the Tkinter window is closed."""
		print("Window closed by user.")
		
		self.root.destroy()	 # Close the Tkinter window
		sys.exit(1)		 # Exit the program

	def getCred(self):
		''' prompt login information for connection to CHPC computer where website is located '''
		self.root = Tk()
		root = self.root
		root.winfo_toplevel().title("Showcase")
		
		#Username
		Label(root, text = 'Log In', font='Helvetica 18 bold').grid(row=0, pady=10)
		Label(root,text="UNID").grid(row=1, sticky=W, padx=10)
		self.name = StringVar()
		self.name.set(username)
		Entry(root,textvariable=self.name, width=20).grid(row=2, padx=10)
		
		# password unecessary with RSA
		#Label(root,text="Password",).grid(row=3, sticky=W, padx=10)
		#self.pw = StringVar()
		#self.pw.set(password)
		#Entry(root,textvariable=self.pw, show="*",width=20).grid(row=4, padx=10)
		
		#Submit
		Button(root, text='Enter', command=self.switch).grid(row=5, pady=20)
		
		root.protocol("WM_DELETE_WINDOW", self.closing)
		mainloop()
		
		

	def getFilters(self):
		''' get sliders for sorting snowflake images and display image subset of most recent images that meet criteria
			images in subset are automatically updated as snowflakes fall
		'''

		self.root = Tk()
		root = self.root
		root.winfo_toplevel().title("Showcase")
		
		# PARAMETERS
		frame1 = LabelFrame(root, text='Parameters', padx=15, pady=15)
		frame1.grid(row=0, column=0)
		self.frame1 = LabelFrame(root,text=f'',padx=15,pady=15)

		# Size threshold
		Label(frame1, text=f'Size (mm)').grid(row=0, sticky=W, padx=10)
		self.size = Scale(frame1, from_=0.2, to=5, resolution=0.1, orient=HORIZONTAL, command=self.getImgSubset)
		self.size.grid(row=0, column=1, sticky=W)
		self.size.set(0.5)
		
		# Blur threshold
		Label(frame1, text='Sharpness').grid(row=1, sticky=W, padx=10)
		self.blur = Scale(frame1, from_=0, to=10, resolution=0.1, orient=HORIZONTAL, command=self.getImgSubset)
		self.blur.set(0)
		self.blur.grid(row=1, column=1, sticky=W)
		


		#Rrefesh
		#Button(frame1, text='REFRESH', command=self.checkDir).grid(row=2, sticky=S, pady=10)

		# IMAGE SUBSET
		self.frame2 = LabelFrame(root,text=f'Recent snowflakes that match criteria',padx=15, pady=15)
		self.frame2.grid(row=0, column=1)
		self.labels = []
		
		self.updateUI()
		

		
		root.protocol("WM_DELETE_WINDOW", self.closing)
		mainloop()

	   
		
		
def main():
	profile = Start()
	profile.log()


	# starts MASC
	#initMASC.callData()

	# displays login prompt
	if profile.offline == False:
		#profile.getCred()
		print('Connecting...')
		profile.connect()
		

	# get imgs in folder and latest storm
	profile.organize()
	
		
	
	#profile.copy(False, True)
	
	# starts searching masc folder
	profile.startBackgroundTasks()
	
	# displays image subset and parameter adjustment window
	profile.getFilters()   
	
	
	
	

if __name__ == '__main__':
	main()

