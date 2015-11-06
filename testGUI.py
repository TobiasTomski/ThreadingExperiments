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
        # Name of the file to read
        self._fileName = fileName
        # x-values of the data read
        self._xData = []
        # y-values of the data read
        self._yData = []
        # variable may be set to stop the constant reading
        self._stop_reading = False
        # pointer to the last read byte. There is no need to read the whole
        # data again every timestep
        self._pointerLastReadByte = 0
        # Create the thread where the reading happens as a daemon
        self._reading_thread = threading.Thread(target = self.read)
        self._reading_thread.daemon = True
        # Start the thread -> start reading the data
        self._reading_thread.start()

    # This method reads or updates the data
    def read(self):
        # Reading may be stopped by the user
        while(not self._stop_reading):
            # Opens the file applied to the reader for reading
            with open(self._fileName, "r") as currentFile:
                # Sets the pointer in the file to the saved one. Thus, the
                # data will only be updated, if there was data read before
                currentFile.seek(self._pointerLastReadByte)
                # Goes through every line in the file
                for currentLine in currentFile:
                    # Saves the current line's data in the depending variables
                    currentLine = currentLine.split(" ")
                    self._xData.append(currentLine[0].strip())
                    self._yData.append(currentLine[1].strip())
                # After reading all ( new ) data, sets the pointer, so the data
                # will only be updated on future readings, not read again entirely
                self._pointerLastReadByte = currentFile.tell()
                # Pauses the thread at this point, so the data will only get
                # updated every second
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
    # Initializes this class
    def __init__(self, master):
        # Initialize self as a frame
        tk.Frame.__init__(self)
        # Define attributes of self
        self.master = master
        # Add some labels
        self.labelWelcome = tk.Label(self, text="Welcome to a testing GUI!")
        # Add some buttons
        self.buttonBye = tk.Button(self, text = "Bye", command = self.quit)
        self.buttonShowPlots = tk.Button(self, text = "Show plots",
                command = self.showPlots)
        # Pack everything
        self.packFrameElements()

    # Pack everything
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
        # Initializes this class as a frame
        tk.Frame.__init__(self)
        # Setting the master of this frame
        self.master = master
        # Adding a notebook ( Tab manager ) containing the single plots
        self.notebookForPlots = ttk.Notebook(self)
        # Defining a variable containing the string for the 'loading bar'
        self._loadingLabelVar = tk.StringVar()
        self._loadingLabelVar.set("Loading plots")
        # Initializes the 'loading bar/label' with the predefined string
        self._loadingLabel = tk.Label(self, textvariable = self._loadingLabelVar)
        # Grids the loading label
        self._loadingLabel.grid(row = 0, column = 0, sticky = tk.W)
        # Creates the thread where the loading label changes
        tempLoadingLabelThread = threading.Thread(target = self.changeLoadingLabel)
        tempLoadingLabelThread.daemon = True
        # Starts this thread
        tempLoadingLabelThread.start()
        # Starts the thread loading and plotting the data
        tempThread = threading.Thread(target = self.arangePlots)
        tempThread.daemon = True
        # Starts this thread
        tempThread.start()
        # Initializes a button to go back to the start window
        self.buttonGoBack = tk.Button(self, text = "Go back to frame 1",
                command = self.showStartFrame)
        # Grids this button
        self.buttonGoBack.grid(row = 1, column = 0)
    
    # This method calls the master method to show the starting window
    def showStartFrame(self):
        self.master.sendNotificationShowStartFrame()

    # This method changes the loading label variable
    def changeLoadingLabel(self):
        # As long as the variable is not None ( this is the case when the plots
        # were created successfully )
        while(self._loadingLabelVar is not None):
            # Reads the current string into the variable s
            s = self._loadingLabelVar.get()
            # Cuts of the points if there are more than 5
            if "....." in s:
                s = s[:-5]
            # Adds a point to the label for an 'animated' loading label
            s += "."
            # Sets the loading label variable ( and so the label )
            self._loadingLabelVar.set(s)
            # Sleeps for some time for a smooth animation
            time.sleep(0.8)
        # If the thread finishes ( when the plots were created ), de-grids the
        # loading label
        self._loadingLabel.grid_forget()

    # This method creates the Frames for the Plots, and adds them to the 
    # notebook ( Tab manager )
    def arangePlots(self):
        # Random sleeper to demonstrate the mechanism that happens when the plots
        # are getting created
        time.sleep(5)
        # If self exists ( it can happen that the window gets closed while the thread
        # is still running )
        if(self.winfo_exists()):
            # Creates to tabs containing frames with plots
            tab1 = FrameWithPlots(self)
            tab2 = FrameWithPlots(self)
            # Adds a file to every frame to read the data from
            tab1.setDataFile("file1.txt")
            tab2.setDataFile("file2.txt")
            # Adds the tabs to the notebook ( tab manager )
            self.notebookForPlots.add(tab1, text = "Tab Number 1")
            self.notebookForPlots.add(tab2, text = "Tab Number 2")
            # Grids the notebook
            self.notebookForPlots.grid(row = 0, column = 0)
            # Sets the loading label variable to None, so the thread to animate
            # the label stops, and the loading label disappers
            self._loadingLabelVar = None
            # centers the master window after creating the plots and so rearranging
            # the widgets etc
            self.master.center()



# This class contains a frame creating and displaying plots.
class FrameWithPlots(tk.Frame):
    # Initializes self as a frame
    def __init__(self, master):
        tk.Frame.__init__(self)
        # Sets the master window for this frame
        self.master = master
        # Sets the x and y data to plot
        self._xData = []
        self._yData = []
        # Defines the variables that will contain the filename, the reader, and the
        # animation for the plots
        self._fileName = None
        self._reader = None
        self._animation = None
        # Creates figure/axis to plot the data
        self._fig = Figure(figsize=(12, 8))
        self._ax = self._fig.add_subplot(111)
        # Puts the figure into a canvas
        self.canvas = FigureCanvasTkAgg(self._fig, self)
        self.canvas.get_tk_widget().pack()
        # Sets some initial x and y data
        self.setXAndYData()
        # Sets some initial plot
        self.plot()

    # Method to set the file to read the data from
    def setDataFile(self, fileName):
        self._fileName = fileName
        # Creates a reader reading this file
        self._reader = Reader(self._fileName)
        # Starts animating the plots as soon as a file has been added
        self.startAnimation()

    # Possibility to manually set the x data and y data to plot in this frame
    def setXAndYData(self, xData=None, yData=None):
        # If the given values are not None
        if(xData is not None and yData is not None):
            self._xData = xData
            self._yData = yData
        # If they are None, use some default data, so anything will be shown as
        # an example
        else:
            self._xData = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            self._yData = [5, 6, 7, 6, 5, 4, 3, 2, 3, 4]

    # Method to plot the current data
    def plot(self):
        # Clears the axis to prevent multiple graphs in a plot
        self._ax.clear()
        # Plots the current x and y data ( updated constantly )
        self._ax.plot(self._xData, self._yData)
        # Applies the changes of the axis to the canvas
        self.canvas.show()
        # Updates the GUI
        self.update_idletasks()

    # Method to start the animation
    def startAnimation(self):
        # Sets the animation for this frame, using the method read and plot.
        # The plot will be updated every 2 secons
        self._animation = animation.FuncAnimation(self._fig, self.readAndPlot,
                interval = 2000)

    # Method to get the current data and plot it after
    def readAndPlot(self, i=None):
        # If there is no reader applied to this frame, nothing will be plotted
        if(self._reader is None):
            print "No data file given for this tab!"
            return
        # Gathers the x and y data read in the reader
        xData, yData = self._reader.getData()
        # Sets the x and y data
        self.setXAndYData(xData, yData)
        # Plots the data
        self.plot()


# This is the root window. It will contain every frame, and so be the root of the GUI
class Root(tk.Tk):
    # Initializes self as tk.Tk ( root window )
    def __init__(self):
        tk.Tk.__init__(self)
        # Initializes both frames, so the reading of the data and creation of the
        # plots starts immediantly after the programm got started
        self.startFrame = FirstFrame(self)
        self.plotFrame = SecondFrame(self)
        # Packs the start frame, so this will be shown on startup
        self.startFrame.pack()
        # Centers the window
        self.center()
        # Sends the window into the mainloop, waiting for events
        self.mainloop()

    # Notification for a destroyed frame. If this notification is send,
    # the root window will be destroyed
    def sendNotificationFrameDestroyed(self, frame):
        self.destroy()

    # Notification to show the plot window. Will be send when the depending
    # button got pressed
    def sendNotificationShowPlots(self):
        # Unpacks the starting frame
        self.startFrame.pack_forget()
        # Packs the plot frame
        self.plotFrame.pack()
        # Centers the window
        self.center()

    # Notification to show the starting window. Will be send when the depending
    # button got pressed
    def sendNotificationShowStartFrame(self):
        # Unpacks the plot frame
        self.plotFrame.pack_forget()
        # Packs the starting frame
        self.startFrame.pack()
        # Centers the window
        self.center()

    # Method to center the window. Will not resize the window ( done automatically
    # in most cases )
    def center(self):
        # update idle tasks to resize the window correctly
        self.update_idletasks()
        # Get information about the current screen
        win = gtk.Window()
        screen = win.get_screen()
        # Get the number of monitors
        numberOfMonitors = screen.get_n_monitors()
        # Get the monitor to display the program gui
        monitorToDisplay = numberOfMonitors / 2
        # Get offsets and resolution of the monitor to display the gui
        xOffset, yOffset, xResolution, yResolution = screen.get_monitor_geometry\
                (monitorToDisplay)

        # Define the middle of the monitor to display the gui
        xMiddle = xOffset + (xResolution / 2)
        yMiddle = yOffset + (yResolution / 2)

        #Defines the window size to properly center the window
        windowSize = tuple(int(_) for _ in self.geometry().split("+")[0].split("x"))

        # Calculate the x-/y-values for the upper left corner of the window
        xLeftUpperCorner = xMiddle - (windowSize[0] / 2)
        yLeftUpperCorner = yMiddle - (windowSize[1] / 2)

        # Redefine the geometry with the current values
        self.geometry("+%d+%d" % (xLeftUpperCorner, yLeftUpperCorner)[:])
        # Update the window to apply the changes
        self.update()


# if the program gets started, a new root window is created
if __name__ == "__main__":
    Root()
