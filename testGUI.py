# !/usr/bin/env python
# coding=utf-8

"""
@project:   This is a viewer for some data, provided in the files file1.txt and
            file2.txt. The data in those files will be plotted and displayed in two
            tabs.
@intention: This program provides the possibility to test some advantages of a well
            structured gui, and the usage of threading in a gui. So one can see how
            smooth a gui works using threading, and how beautiful the code may be.
@author:    Tobias Tomski ( t.tomski@fz-juelich.de )
@date:      06.11.2015
"""

import Tkinter as tk
import gtk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import ttk
import time
import threading

# A reader reads data from a file constantly and saves it. The data is the provided
# for other objects to use
class Reader():
    # Initializes the reader
    def __init__(self, fileName):
        self._fileName = fileName
        self._xData = []
        self._yData = []
        self._stop_reading = False
        self._pointerLastReadByte = 0
        self._reading_thread = threading.Thread(target = self.read)
        self._reading_thread.daemon = True
        self._reading_thread.start()

    # This method reads or updates the data
    def read(self):
        while(not self._stop_reading):
            with open(self._fileName, "r") as currentFile:
                currentFile.seek(self._pointerLastReadByte)
                for currentLine in currentFile:
                    currentLine = currentLine.split(" ")
                    self._xData.append(currentLine[0].strip())
                    self._yData.append(currentLine[1].strip())
                self._pointerLastReadByte = currentFile.tell()
                time.sleep(1)

    # This method returns the data read until the time it gets called
    def getData(self):
       return self._xData, self._yData

    # This method returns the filename applied to the specific reader object
    def getFileName(self):
        return self._fileName


# This class is the starting frame in the root window. It provides the possibility
# to exit, or to view the plots, by providing two buttons
class FirstFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self)
        self.master = master
        self.labelWelcome = tk.Label(self, text="Welcome to a testing GUI!")
        self.buttonBye = tk.Button(self, text = "Bye", command = self.quit)
        self.buttonShowPlots = tk.Button(self, text = "Show plots",
                command = self.showPlots)
        self.packFrameElements()

    def packFrameElements(self):
        self.labelWelcome.grid(row = 0, column = 0, columnspan = 2)
        self.buttonBye.grid(row = 1, column = 0)
        self.buttonShowPlots.grid(row = 1, column = 1)

    # Close this frame by calling the depending method in the root window
    def quit(self):
        self.master.sendNotificationFrameDestroyed(self)

    # Show the frame containing the plots by calling the depending method in the
    # root window
    def showPlots(self):
        self.master.sendNotificationShowPlots()


# This class is the frame containing the plots in the root window
class SecondFrame(tk.Frame):
    # Initializes the class
    def __init__(self, master):
        tk.Frame.__init__(self)
        self.master = master
        self.notebookForPlots = ttk.Notebook(self)
        self._loadingLabelVar = tk.StringVar()
        self._loadingLabelVar.set("Loading plots")
        self._loadingLabel = tk.Label(self, textvariable = self._loadingLabelVar)
        self._loadingLabel.grid(row = 0, column = 0, sticky = tk.W)
        tempLoadingLabelThread = threading.Thread(target = self.changeLoadingLabel)
        tempLoadingLabelThread.daemon = True
        tempLoadingLabelThread.start()
        tempThread = threading.Thread(target = self.arangePlots)
        tempThread.daemon = True
        tempThread.start()
        self.buttonGoBack = tk.Button(self, text = "Go back to frame 1",
                command = self.showStartFrame)
        self.buttonGoBack.grid(row = 1, column = 0)
    
    # This method calls the master method to show the starting window
    def showStartFrame(self):
        self.master.sendNotificationShowStartFrame()

    # This method changes the loading label variable
    def changeLoadingLabel(self):
        while(self._loadingLabelVar is not None):
            s = self._loadingLabelVar.get()
            if "....." in s:
                s = s[:-5]
            s += "."
            self._loadingLabelVar.set(s)
            time.sleep(0.8)
        self._loadingLabel.grid_forget()

    # This method creates the Frames for the Plots, and adds them to the 
    # notebook ( Tab manager )
    def arangePlots(self):
        time.sleep(5)
        if(self.winfo_exists()):
            tab1 = FrameWithPlots(self)
            tab2 = FrameWithPlots(self)
            tab1.setDataFile("file1.txt")
            tab2.setDataFile("file2.txt")
            self.notebookForPlots.add(tab1, text = "Tab Number 1")
            self.notebookForPlots.add(tab2, text = "Tab Number 2")
            self.notebookForPlots.grid(row = 0, column = 0)
            self._loadingLabelVar = None
            self.master.center()



# This class contains a frame creating and displaying plots.
class FrameWithPlots(tk.Frame):
    # Initializes self as a frame
    def __init__(self, master):
        tk.Frame.__init__(self)
        self.master = master
        self._xData = []
        self._yData = []
        self._fileName = None
        self._reader = None
        self._animation = None
        self._fig = Figure(figsize=(12, 8))
        self._ax = self._fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self._fig, self)
        self.canvas.get_tk_widget().pack()
        self.setXAndYData()
        self.plot()

    # Method to set the file to read the data from
    def setDataFile(self, fileName):
        self._fileName = fileName
        self._reader = Reader(self._fileName)
        self.startAnimation()

    # Possibility to manually set the x data and y data to plot in this frame
    def setXAndYData(self, xData=None, yData=None):
        if(xData is not None and yData is not None):
            self._xData = xData
            self._yData = yData
        else:
            self._xData = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            self._yData = [5, 6, 7, 6, 5, 4, 3, 2, 3, 4]

    # Method to plot the current data
    def plot(self):
        self._ax.clear()
        self._ax.plot(self._xData, self._yData)
        self.canvas.show()
        self.update_idletasks()

    # Method to start the animation
    def startAnimation(self):
        self._animation = animation.FuncAnimation(self._fig, self.readAndPlot,
                interval = 2000)

    # Method to get the current data and plot it after
    def readAndPlot(self, i=None):
        if(self._reader is None):
            print "No data file given for this tab!"
            return
        xData, yData = self._reader.getData()
        self.setXAndYData(xData, yData)
        self.plot()


# This is the root window. It will contain every frame, and so be the root of the GUI
class Root(tk.Tk):
    # Initializes self as tk.Tk ( root window )
    def __init__(self):
        tk.Tk.__init__(self)
        self.startFrame = FirstFrame(self)
        self.plotFrame = SecondFrame(self)
        self.startFrame.pack()
        self.center()
        self.mainloop()

    # Notification for a destroyed frame. If this notification is send,
    # the root window will be destroyed
    def sendNotificationFrameDestroyed(self, frame):
        self.destroy()

    # Notification to show the plot window. Will be send when the depending
    # button got pressed
    def sendNotificationShowPlots(self):
        self.startFrame.pack_forget()
        self.plotFrame.pack()
        self.center()

    # Notification to show the starting window. Will be send when the depending
    # button got pressed
    def sendNotificationShowStartFrame(self):
        self.plotFrame.pack_forget()
        self.startFrame.pack()
        self.center()

    # Method to center the window. Will not resize the window ( done automatically
    # in most cases )
    def center(self):
        self.update_idletasks()
        win = gtk.Window()
        screen = win.get_screen()
        numberOfMonitors = screen.get_n_monitors()
        monitorToDisplay = numberOfMonitors / 2
        xOffset, yOffset, xResolution, yResolution = screen.get_monitor_geometry\
                (monitorToDisplay)

        xMiddle = xOffset + (xResolution / 2)
        yMiddle = yOffset + (yResolution / 2)

        windowSize = tuple(int(_) for _ in self.geometry().split("+")[0].split("x"))

        xLeftUpperCorner = xMiddle - (windowSize[0] / 2)
        yLeftUpperCorner = yMiddle - (windowSize[1] / 2)

        self.geometry("+%d+%d" % (xLeftUpperCorner, yLeftUpperCorner)[:])
        self.update()


# if the program gets started, a new root window is created
if __name__ == "__main__":
    Root()
