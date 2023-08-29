

# User Interface for intializing MASC and Snowflake Showcase
# Written by Alex Garrett, alexgarrett2468@gmail.com, for University of Utah, Summer 2023


# 1. Initilizes MASC 
# 2. Displays UI to configure filter specifications for snowflake showcase (size and sharpness)
# 3. When a new snowflake is photographed that meets filter criteria it uploads it to snowflake showcase website
# 4. Updates data plots for data from masc (size and rate)


#! NOTE
# Be sure to change PATH global string if moving 'masc_showcase' folder to a new location or renaming
# Specify path where masc copies photos if changed under self.mascpath

'''
TO DO:

* create data plot webpage
    - make it so storms files dont overwrite when program restarts ie search for latest storm files and start there
    - make data plot's date accurate instead of adding 0s

    - works with deid data on seperate page


* initMASC.py

* get this program running on MASC computer hardware

'''

from tkinter import *
from datetime import timedelta, datetime
from PIL import ImageTk, Image
import basicSort, os, time, shutil, genHTML, initMASC, deltaStorm, paramiko, re, threading, glob, concurrent.futures

PATH =  'C:\\Users\\Cooper\\Desktop\\masc_showcase\\' # make sure ends with /

# default username and password
username = ''
password = ''

class Start:
    def __init__(self):
        self.mascpath = 'C:\\MASC\\The_Alta_Project_2022\\'
        self.name = ''
        self.pw = ''
        self.snowing = True
        self.storm = 1
        self.flakes = [0]
        self.sizes = [0.001]
        self.imgpaths = []
        self.ssh = None
        self.pixel = None
        self.success = 0

    #############
    # APP LOGIC #
    #############

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect('kingspeak34.chpc.utah.edu', username=self.name.get(), password=self.pw.get())


    def checkConnection(self):
        if self.ssh is None:
            return False
        
        try:
            transport = self.ssh.get_transport()
            if transport and transport.is_active():
                return True
            else:
                return False
        except Exception:
            return False
        
    def copy(self, image=False):
        
        try:
            scp = self.ssh.open_sftp()
            # copy data html
            scp.put(f'{PATH}data\\data{str(self.storm)}.txt', f'/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/data/data{str(self.storm)}.txt')
            scp.put(f'{PATH}data\\flakes{str(self.storm)}.txt', f'/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/data/flakes{str(self.storm)}.txt')

            if image != False:
                # copy showcase html
                scp.put(f'{PATH}chosen/images.html', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/images.html')

                # copy image
                new = os.path.join(PATH+'chosen', image)
                scp.put(new, '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/'+image)
                scp.put(new[:-4]+'_s.jpg', '/uufs/chpc.utah.edu/common/home/snowflake/public_html/LiveFeed/'+image[:-4]+'_s.jpg')

                print('Uploaded:', image)

            scp.close()

        except Exception as e:
            print(e)
            # if upload threads are overloaded upload image on main thread
            #self.update(False, image)

    
    def update(self, images=False, retry=False):

        max = 3 # number of threadsto create for upload
        # if you are getting "Secsh channel 44 open FAILED: open failed: Connect failed" or max recursion depth in output note that images 
        # will still be upload play around with the value of max keeping it as high as possible until that doesnt happen (I recommend making it a multiple of 3)

        # Connect to the remote server via SSH
        if self.checkConnection():
            if retry != False:
                self.copy(retry)
                return
            
            if images == False:
                self.copy()
                return
			
            for i in images:
                self.copy(i)
            
            '''
            while images != []:

                # create different threads for upload (makes upload much faster)
                threads = []
                for i in images[:max]:
                    thread = threading.Thread(target=self.copy, args=(i,))
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    if thread != threading.current_thread():
                        thread.join()
                
                images = images[max:]
            '''

        else:
            print()
            print("Reconnecting SSH...")
            self.connect()
            print("Back Online")
            print()
            

    def switch(self):
        self.root.destroy()

    def switch2(self):
        self.param.destroy()

    def parseDateTimeFromFileName(self, inFile):
        # # @author	Konstantin Shkurko (kshkurko@cs.utah.edu)

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
            #   1. Based on the "Creation Time" within image meta-data
            #   2. Using parseDateTimeFromFileName function above
            #   3. Using the os file system, file creation time (Windows) or 
            #      last metadata modification time (*nix)
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
        subdirectories = [d for d in os.listdir(self.mascpath) if os.path.isdir(os.path.join(self.mascpath, d))]

        # Sort the subdirectories based on modification time in descending order
        subdirectories.sort(key=lambda d: os.path.getmtime(os.path.join(self.mascpath, d)), reverse=True)

        dir = os.path.join(self.mascpath, subdirectories[0])

        # gets files
        for file in os.listdir(dir):
            if file.lower().endswith(('.png')):
                # Construct the full path of the file
                files.append(os.path.join(dir, file))

        for file in files:
            # get image tags to resave later (and parse out date)
            try:
                img      = Image.open( file )
            except:
                continue
            imgTags  = img.info
            if('Creation Time' in imgTags):
                try:
                    imgCTime      = time.strptime( imgTags['Creation Time'], "%d %b %Y %H:%M:%S +0000" )
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
        # sort in descending order based on created timestamp (first NxM images)
        outInfo.sort( key=lambda tmp: tmp[1], reverse=True )
        return outInfo
    
    def checkSnowing(self):
        # if snowing check if not snowing
        if self.snowing == True:
            if deltaStorm.storm(self.flakes) == True:
                self.snowing = False # end storm
                self.flakes = [0]
                self.sizes = [0.001]
                print("./././././.")
                print('END STORM', self.storm)
                print()

        # if not snowing check if snowing
        elif self.snowing == False:
            if deltaStorm.storm(self.flakes) == False:
                self.snowing = True
                self.storm += 1 # new storm
				
				# create new data files (redundancy)
                with open(f'data\\data{self.storm}.txt' ,'w'):
                    pass
                with open(f'data\\flakes{self.storm}.txt', 'w'):
                    pass
				
                print()
                print('NEW STORM', self.storm)
                print("\`\\`\\`\\`\\`\\`")
                print()


    def checkDir(self):
        ''' checks masc path for new images then updates html and copys both image and html file to server'''
        new = self.getImagesInDir()
        self.checkSnowing()
		
        if len(new)<len(self.imgpaths):
            self.imgpaths = []

        dif = len(new) - len(self.imgpaths)
        if dif!=0:
            print(dif, 'new images')
        
        files = []
        i=0
        for i in range(0,dif):

    	    #print('new image:', file)

    	    # get flakes rate of change
    	    self.flakes[-1] = deltaStorm.delta(new)
    	    #print('flakes:', self.flakes)
            new[i].append(self.storm)

    	    # if new image found add it to imgpaths[]. If meets criteria copy it, otherwise continue to next new snowflake
    	    new[i] = basicSort.check(new[i])
    	    self.sizes.append(new[i][4])
    	    #print(new[i][4], (self.empty.get()**2)/6)
    	    if new[i][3] <= (self.blur.get()**2)/700 or new[i][4] <= (self.empty.get()**2)/6: # make sure function is same as in getImgSubset
    		    i += 1
    		    continue

    	    # copy to chosen folder
    	    shutil.copy(new[i][0], PATH+'/chosen/')

    	    # get HTML with (new) data
    	    genHTML.genOutputHTML(PATH+'/chosen/', PATH+'/chosen/', 'images.html', 100, 9, 120, 120, 10000, False, False, 5)

    	    # get path of image in chosen folder
    	    dir, file = os.path.split(new[i][0])

    	    files.append(file)

        i+=1
		
        # upload image and new html
        self.update(files)

        for img in reversed(new[:i]):
            self.imgpaths.insert(0, img)

            # write to data.txt
            with open(f'{PATH}data/data{self.storm}.txt', 'a') as data:
                data.write('\n'+str(img)[6+len(PATH):-1])
                    

    def elapsed(self):
        # check folder and update flake rate data every given interval

        self.checkDir()
        self.getImgSubset(0)
        self.flakes.append(0)
        with open(f'{PATH}data/flakes{self.storm}.txt', 'w') as flakes:
            flakes.write(str(self.flakes))
        self.update()
        self.root.after(2000, self.elapsed)

    
    def getImgSubset(self, value):
        ''' produces an image subset of most recent images that match criteria from sliders '''

        
        # self.checkDir()
        self.subset = []

        # get subset images that match criteria
        for img in self.imgpaths:
            if len(self.subset)>8:
                 break
            if img[3] > (self.blur.get()**2)/700 and img[4] > (self.empty.get()**2)/6: # make sure function is same as in checkDir
                 self.subset.append(img)
                
        
        # if there are not enough images replace with default
        i = 0
        while len(self.subset) < 9:
            self.subset.append(['defaults/1.png',0,0,0])
            i+=1

        # get rid of old images
        for label in self.labels:
            label.destroy()

        # create image grid
        for i, imagepath in enumerate(self.subset):
            # Open the image using PIL
            img = Image.open(imagepath[0])

            # Resize the image
            img = img.resize((200, 200))

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
            formatted = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
            date = Label(self.frame2, text=formatted)
            date.grid(row=r + 1, column=c, padx=10)

            # Keep a reference to the ImageTk object to prevent it from being garbage collected
            label.image = img
            self.labels.append(label)
            self.labels.append(date)


    ###############
    # APP WINDOWS #
    ###############

    def getCred(self):
        ''' prompt login information for connection to CHPC computer where website is located '''
        self.root = Tk()
        root = self.root
        root.winfo_toplevel().title("Showcase")
        
        #Username and Password
        Label(root, text = 'Log In', font='Helvetica 18 bold').grid(row=0, pady=10)
        Label(root,text="UNID").grid(row=1, sticky=W, padx=10)
        self.name = StringVar()
        self.name.set(username)
        Entry(root,textvariable=self.name, width=20).grid(row=2, padx=10)

        Label(root,text="Password",).grid(row=3, sticky=W, padx=10)
        self.pw = StringVar()
        self.pw.set(password)
        Entry(root,textvariable=self.pw, show="*",width=20).grid(row=4, padx=10)
        
        #Submit
        Button(root, text='Enter', command=self.switch).grid(row=5, pady=20)
        mainloop()
        
    def getParameters(self):
        ''' get parameters for data plots '''
        
        params = []
        f =  open('dataparam.txt', 'r')
        content = f.readlines()
        for line in content:
            if line:
                match = re.search('\w+=(\d+\.\d+)', line)
                params.append(float(match.group(1)))
        

        self.param = Toplevel(self.root)
        root = self.param
        root.winfo_toplevel().title("Data Variables")

        Label(root, text='Change Defaults in dataparam.txt', font='Helvetica 12 bold').grid(row=0, pady=10)
            
        # Pixel Size
        Label(root,text="Pixel Size",).grid(row=1, sticky=W, padx=10)
        self.pixel = StringVar()
        self.pixel.set(params[0])
        Entry(root,textvariable=self.pixel,width=5).grid(row=1, column=1, sticky=W)

        Button(root, text='Submit', command=self.switch2).grid(row=4, pady=10)
        root.wait_window()

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

        # Size threshold
        Label(frame1, text='Size').grid(row=0, sticky=W, padx=10)
        self.empty = Scale(frame1, from_=0, to=100, orient=HORIZONTAL)
        self.empty.grid(row=0, column=1, sticky=W)
        
        # Blur threshold
        Label(frame1, text='Sharpness').grid(row=1, sticky=W, padx=10)
        self.blur = Scale(frame1, from_=0, to=100, orient=HORIZONTAL,)
        self.blur.grid(row=1, column=1, sticky=W)
        
        #Rrefesh
        # Button(frame1, text='REFRESH', command=self.getImgSubset).grid(row=2, sticky=S, pady=10)

        # IMAGE SUBSET
        self.frame2 = LabelFrame(root,text='Image Subset',padx=15, pady=15)
        self.frame2.grid(row=0, column=1)
        self.labels = []
        
        Button(frame1, text='Data Parameters', command=self. getParameters).grid(row=6, pady=10)

        #
        # imgpaths item order: ['name', date, storm, sharpness, size]
        #

        self.imgpaths = self.getImagesInDir()
		
        for i in self.imgpaths:
            i.append(0)
		
        print(self.imgpaths)

        self.imgpaths = basicSort.process(self.imgpaths) # appends
		
        print(self.imgpaths)

        ## find latest storm file

        # Construct the pattern for the glob function
        pattern = os.path.join(PATH+'data/', 'data*.txt')
        
        # Use glob to get all files matching the pattern
        files = glob.glob(pattern)

        # Extract the number from each filename and find the maximum
        for file_name in files:
            match = re.search(r'flakes(\d+).txt', os.path.basename(file_name))
            if match:
                number = int(match.group(1))
                self.storm = number+1
				
        with open(f'data\\data{self.storm}.txt', 'w'):
            pass

        print('Starting from storm', self.storm)
        print('Snowing = True')

        self.root.after(0, self.elapsed)
        mainloop()


def main():
    profile = Start()

    # starts MASC
    #initMASC.callData()

    # displays login prompt
    profile.getCred()

    # displays image subset and parameter adjustment window
    profile.getFilters()

main()
