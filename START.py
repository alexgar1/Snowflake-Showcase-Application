

# User Interface for intializing MASC and Snowflake Showcase
# Written by Alex Garrett for University of Utah, Summer 2023


# 1. Initilizes MASC 
# 2. Creates and interactive UI to configure filter specifications for snowflake showcase
# 3. When a new snowflake is captured that meets criteria it uploads it to snowflake showcase

from tkinter import *
from PIL import ImageTk, Image
import basicSort, os, time, shutil, genHTML, upload, initMASC

class getUI:  
    def __init__(self, mascpath, local, name, pw, time, m, n, remove):
        self.mascpath=mascpath
        self.local = local
        self.name = name
        self.pw = pw
        self.time = time
        self.m = m
        self.n = n
        self.remove = remove


    #############
    # APP LOGIC #
    #############

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

        if( not os.path.exists( self.mascpath ) ):
            print( "ERROR: output path (" + self.mascpath + ")doesn't exist!")

        # init file info
        outInfo = []
        files = []
        # open the directory
        for root, dirs, f in os.walk(self.mascpath):
            for file in f:
                if file.lower().endswith(('.png')):
                    files.append(os.path.join(root, file))

        for file in files:
            # get image tags to resave later (and parse out date)
            try:
                img      = Image.open( file )
            except:
                continue
            imgTags  = img.info
            if('Creation Time' in imgTags):
                imgCTime      = time.strptime( imgTags['Creation Time'], "%d %b %Y %H:%M:%S +0000" )
                outInfo.append( [file, time.mktime( imgCTime )] )
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

    def checkDir(self):
        ''' checks masc path for new images then updates html and copys both image and html file to server'''

        new = self.getImagesInDir()
        i=0
        while self.imgpaths[0][0] != new[i][0]:
            #print(self.imgpaths[0][0], new[i][0])
            print('new image:', new[i][0])

            # if new image found add it to imgpaths[]
            id = basicSort.check(new[i])
            if id[2] <= (self.blur.get()**2)/700 or id[3] <= (self.empty.get()**2)/10000000:
                i += 1
                continue

            new[i] = id
            
            # copy to chosen folder
            shutil.copy(new[i][0], '/Users/alexgarrett/Desktop/UofU/engUI/chosen/')

            # get HTML with (new) data
            genHTML.genOutputHTML('/Users/alexgarrett/Desktop/UofU/engUI/chosen/', '/Users/alexgarrett/Desktop/UofU/engUI/chosen/', 'index.html', 5, 6, 120, 120, 5000, False, False, 5)

            # get path of image in chosen folder
            dir, file = os.path.split(new[i][0])

            # upload image and HTML to server
            upload.copyHTML('./chosen/', file)
            print('UPLOADED:', file)
            i+=1

        for img in reversed(new[:i]):
            self.imgpaths.insert(0, img)

    
    def getImgSubset(self, value):
        ''' produces an image subset of most recent images that match criteria from sliders '''

        #print('size:', self.empty.get(), 'blur:', self.blur.get())

        # check for new images
        self.checkDir()
        self.subset = []

        # get subset images that match criteria
        for img in self.imgpaths:
            if len(self.subset)>8:
                 break
            if img[2] > (self.blur.get()**2)/700 and img[3] > (self.empty.get()**2)/10000000:
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

        # check folder every 5 seconds
        self.root.after(5000, self.getImgSubset, 0)


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
        Entry(root,textvariable=self.name, width=20).grid(row=2, padx=10)

        Label(root,text="Password",).grid(row=3, sticky=W, padx=10)
        self.pw = StringVar()
        Entry(root,textvariable=self.pw, show="*",width=20).grid(row=4, padx=10)
        
        #Submit
        Button(root, text='Enter', command=self.switch).grid(row=5, pady=20)
        mainloop()
    
    def getParameters(self):
        ''' get parameters for website specifications 
        
        NEEDS TO BE ADJUSTED FOR NEW WEBSITE DESIGN'''

        self.param = Toplevel(self.root)
        root = self.param
        root.winfo_toplevel().title("Showcase")

        Label(root, text='Website Parameters', font='Helvetica 18 bold').grid(row=0, pady=10)

        #Time between folder scans
        Label(root,text="Time between folder scans (s)",).grid(row=1, sticky=W, padx=10)
        self.time = StringVar()
        self.time.set(2)
        Entry(root,textvariable=self.time,width=2).grid(row=1, column=1, sticky=W)

        #Matrix dimensions
        matrix = LabelFrame(root)
        matrix.grid(row=2, column=1, sticky=W)
        Label(root,text="Size of image grid (NxM)",).grid(row=2, sticky=W, padx=10)
        self.n = StringVar()
        self.m = StringVar()
        self.n.set(5)
        self.m.set(12)
        Entry(matrix,textvariable=self.n, width= 2).grid(row=2, column=1, sticky=W)
        Label(matrix, text='x').grid(row=2, column=2)
        Entry(matrix,textvariable=self.m, width= 2).grid(row=2, column=3, sticky=W)

        #Remove labels
        self.remove = IntVar()
        Checkbutton(root, text='Remove Labels',variable=self.remove, onvalue=1, offvalue=0).grid(row=3, sticky=W, padx=10)

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
        self.empty = Scale(frame1, from_=0, to=100, command = self.getImgSubset, orient=HORIZONTAL)
        self.empty.grid(row=0, column=1, sticky=W)
        
        # Blur threshold
        Label(frame1, text='Sharpness').grid(row=1, sticky=W, padx=10)
        self.blur = Scale(frame1, from_=0, to=100, command = self.getImgSubset, orient=HORIZONTAL,)
        self.blur.grid(row=1, column=1, sticky=W)
        
        #Rrefesh
        # Button(frame1, text='REFRESH', command=self.getImgSubset).grid(row=2, sticky=S, pady=10)

        # IMAGE SUBSET
        self.frame2 = LabelFrame(root,text='Image Subset',padx=15, pady=15)
        self.frame2.grid(row=0, column=1)
        self.labels = []

        #Submit
        Button(frame1, text='Edit Website Parameters', command=self.getParameters).grid(row=6, pady=10)
        
        self.imgpaths = self.getImagesInDir()
        self.imgpaths = basicSort.process(self.imgpaths)
        #
        # imgpaths item order: ['name',date,sharpness,size]
        #
        self.root.after(0, self.getImgSubset, 0)
        mainloop()


def main():
    profile = getUI('/Users/alexgarrett/Desktop/UofU/engUI/sort/','.', '', '', 2, 5, 8, 1)

    # starts MASC
    #initMASC.callData()

    # displays login prompt
    profile.getCred()

    # displays image subset and parameter adjustment window
    profile.getFilters()

main()
