import Tkinter as tk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import ttk
import time
import threading

class Reader():
    def __init__(self, fileName):
        self._fileName = fileName
        self._xData = []
        self._yData = []
        self._stop_reading = False
        self._pointerLastReadByte = 0
        self._reading_thread = threading.Thread(target = self.read)
        self._reading_thread.daemon = True
        self._reading_thread.start()

    def read(self):
        while(not self._stop_reading):
            if(self._xData is None or self._yData is None):
                self._xData = []
                self._yData = []
                self._pointerLastReadByte = 0
            with open(self._fileName, "r") as currentFile:
                currentFile.seek(self._pointerLastReadByte)
                for currentLine in currentFile:
                    currentLine = currentLine.split(" ")
                    self._xData.append(currentLine[0].strip())
                    self._yData.append(currentLine[1].strip())
                self._pointerLastReadByte = currentFile.tell()
            time.sleep(2)

    def getData(self):
       return self._xData, self._yData

    def getFileName(self):
        return self._fileName

class FirstFrame(tk.Frame):
    def __init__(self, master):
        # initialize self as a frame
        tk.Frame.__init__(self)
        #define attributes of self
        self.master = master
        # add some labels
        self.labelWelcome = tk.Label(self, text="Welcome to a testing GUI!")
        # add some buttons
        self.buttonBye = tk.Button(self, text = "Bye", command = self.quit)
        self.buttonShowPlots = tk.Button(self, text = "Show plots",
                command = self.showPlots)
        # pack everything
        self.packFrameElements()

    # pack everything
    def packFrameElements(self):
        self.labelWelcome.grid(row = 0, column = 0, columnspan = 2)
        self.buttonBye.grid(row = 1, column = 0)
        self.buttonShowPlots.grid(row = 1, column = 1)

    # close this frame
    def quit(self):
        self.master.sendNotificationFrameDestroyed(self)

    def showPlots(self):
        self.master.sendNotificationShowPlots()

class SecondFrame(tk.Frame):
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

    def showStartFrame(self):
        self.master.sendNotificationShowStartFrame()

    def changeLoadingLabel(self):
        while(self._loadingLabelVar is not None):
            s = self._loadingLabelVar.get()
            s += "."
            self._loadingLabelVar.set(s)
            time.sleep(0.5)
        self._loadingLabel.grid_forget()

    def arangePlots(self):
        time.sleep(2)
        if(self.winfo_exists()):
            tab1 = FrameWithPlots(self)
            tab2 = FrameWithPlots(self)
            tab1.setDataFile("file1.txt")
            tab2.setDataFile("file2.txt")
            self.notebookForPlots.add(tab1, text = "Tab Number 1")
            self.notebookForPlots.add(tab2, text = "Tab Number 2")
            self.notebookForPlots.grid(row = 0, column = 0)
            self._loadingLabelVar = None


class FrameWithPlots(tk.Frame):
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

    def setDataFile(self, fileName):
        self._fileName = fileName
        self._reader = Reader(self._fileName)
        self.startAnimation()

    def setXAndYData(self, xData=None, yData=None):
        if(xData is not None and yData is not None):
            self._xData = xData
            self._yData = yData
        else:
            self._xData = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            self._yData = [5, 6, 7, 6, 5, 4, 3, 2, 3, 4]

    def plot(self):
        self._ax.clear()
        self._ax.plot(self._xData, self._yData)
        self.canvas.show()
        self.update_idletasks()

    def startAnimation(self):
        self._animation = animation.FuncAnimation(self._fig, self.readAndPlot,
                interval = 2000)

    def readAndPlot(self, i=None):
        if(self._reader is None):
            print "No data file given for this tab!"
            return
        # self._reader.read()
        xData, yData = self._reader.getData()
        self.setXAndYData(xData, yData)
        self.plot()

class Root(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.startFrame = FirstFrame(self)
        self.plotFrame = SecondFrame(self)
        self.startFrame.pack()
        self.mainloop()

    def sendNotificationFrameDestroyed(self, frame):
        self.destroy()

    def sendNotificationShowPlots(self):
        self.startFrame.pack_forget()
        self.plotFrame.pack()

    def sendNotificationShowStartFrame(self):
        self.plotFrame.pack_forget()
        self.startFrame.pack()
window = Root()
