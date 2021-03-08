# To do ---------------------------------------------------------------------------------------------------------------

# Legend for live graph
# Error handling
# Temperature and humidity in one file, 2 columns


# Libraries ---------------------------------------------------------------------------------------------------------------
from tkinter import *
from tkinter import messagebox
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font

import serial
import serial.tools.list_ports
from serial import *
from serial import Serial

from threading import Thread 
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

import numpy as np
import pandas as pd


# Global Variables ---------------------------------------------------------------------------------------------------------------
timeTempHumFile = "data/timeTempHum.txt"
tempFileName = "data/temp.cvs"
humFileName = "data/hum.cvs"

global serialThreadBoolean
serialThreadBoolean = False
global textFileLines
textFileLines = 0

numberOfGraphPoints = 15


# Functions ---------------------------------------------------------------------------------------------------------------
# Tkinter -------------------
def selectionClear(*args):
	root.focus()
	pass

def onClosing():
	root.destroy()
	pass

def showHideText():
	if showHideTextButton.cget('text') == "Hide Raw Data":
		rawText.pack_forget()
		verticalScrollBar.pack_forget()
		showHideTextButton.configure(text="Show Raw Data")
	else:
		rawText.pack(side="left", fill="both", expand=True)
		verticalScrollBar.pack(side="right", fill="y")
		showHideTextButton.configure(text="Hide Raw Data")

def tempStatsWindow():
	temps = getTempFile()
	tStatsWin = tk.Toplevel()

	title = ttk.Label(tStatsWin, text="Temperature Statistics")
	title.grid(row=0, column=0, columnspan=2)
	title['font'] = toplevelTitleFont

	minLabel = ttk.Label(tStatsWin, text="Minimum Temperature: ")
	minLabel.grid(row=1, column=0)
	maxLabel = ttk.Label(tStatsWin, text="Maximum Temperature: ")
	maxLabel.grid(row=2, column=0)
	medLabel = ttk.Label(tStatsWin, text="Median Temperature: ")
	medLabel.grid(row=3, column=0)
	meanLabel = ttk.Label(tStatsWin, text="Mean Temperature: ")
	meanLabel.grid(row=4, column=0)

	minValLabel = ttk.Label(tStatsWin, text="{:.2f}".format(temps.min()))
	minValLabel.grid(row=1, column=1)
	maxValLabel = ttk.Label(tStatsWin, text="{:.2f}".format(temps.max()))
	maxValLabel.grid(row=2, column=1)
	medValLabel = ttk.Label(tStatsWin, text="{:.2f}".format(np.median(temps)))
	medValLabel.grid(row=3, column=1)
	meanValLabel = ttk.Label(tStatsWin, text="{:.2f}".format(temps.mean()))
	meanValLabel.grid(row=4, column=1)

	minLabel['font'] = textFont
	maxLabel['font'] = textFont
	medLabel['font'] = textFont
	meanLabel['font'] = textFont
	minValLabel['font'] = textFont
	maxValLabel['font'] = textFont
	medValLabel['font'] = textFont
	meanValLabel['font'] = textFont

	for child in tStatsWin.winfo_children(): 
		child.grid_configure(padx=5, pady=5)

def humStatsWindow():
	hums = getHumFile()
	hStatsWin = tk.Toplevel()

	title = ttk.Label(hStatsWin, text="Humidity Statistics")
	title.grid(row=0, column=0, columnspan=2)
	title['font'] = toplevelTitleFont

	minLabel = ttk.Label(hStatsWin, text="Minimum Humidity: ")
	minLabel.grid(row=1, column=0)
	maxLabel = ttk.Label(hStatsWin, text="Maximum Humidity: ")
	maxLabel.grid(row=2, column=0)
	medLabel = ttk.Label(hStatsWin, text="Median Humidity: ")
	medLabel.grid(row=3, column=0)
	meanLabel = ttk.Label(hStatsWin, text="Mean Humidity: ")
	meanLabel.grid(row=4, column=0)

	minValLabel = ttk.Label(hStatsWin, text="{:.2f}".format(hums.min()))
	minValLabel.grid(row=1, column=1)
	maxValLabel = ttk.Label(hStatsWin, text="{:.2f}".format(hums.max()))
	maxValLabel.grid(row=2, column=1)
	medValLabel = ttk.Label(hStatsWin, text="{:.2f}".format(np.median(hums)))
	medValLabel.grid(row=3, column=1)
	meanValLabel = ttk.Label(hStatsWin, text="{:.2f}".format(hums.mean()))
	meanValLabel.grid(row=4, column=1)

	minLabel['font'] = textFont
	maxLabel['font'] = textFont
	medLabel['font'] = textFont
	meanLabel['font'] = textFont
	minValLabel['font'] = textFont
	maxValLabel['font'] = textFont
	medValLabel['font'] = textFont
	meanValLabel['font'] = textFont

	for child in hStatsWin.winfo_children(): 
		child.grid_configure(padx=5, pady=5)

def allStatsWindow():
	hums = getHumFile()
	temps = getTempFile()
	aStatsWin = tk.Toplevel()

	title = ttk.Label(aStatsWin, text="All Statistics")
	title.grid(row=0, column=0, columnspan=2)
	title['font'] = toplevelTitleFont

	minHLabel = ttk.Label(aStatsWin, text="Minimum Humidity: ")
	minHLabel.grid(row=1, column=0)
	maxHLabel = ttk.Label(aStatsWin, text="Maximum Humidity: ")
	maxHLabel.grid(row=2, column=0)
	medHLabel = ttk.Label(aStatsWin, text="Median Humidity: ")
	medHLabel.grid(row=3, column=0)
	meanHLabel = ttk.Label(aStatsWin, text="Mean Humidity: ")
	meanHLabel.grid(row=4, column=0)

	minHValLabel = ttk.Label(aStatsWin, text="{:.2f}".format(hums.min()))
	minHValLabel.grid(row=1, column=1)
	maxHValLabel = ttk.Label(aStatsWin, text="{:.2f}".format(hums.max()))
	maxHValLabel.grid(row=2, column=1)
	medHValLabel = ttk.Label(aStatsWin, text="{:.2f}".format(np.median(hums)))
	medHValLabel.grid(row=3, column=1)
	meanHValLabel = ttk.Label(aStatsWin, text="{:.2f}".format(hums.mean()))
	meanHValLabel.grid(row=4, column=1)

	minHLabel['font'] = textFont
	maxHLabel['font'] = textFont
	medHLabel['font'] = textFont
	meanHLabel['font'] = textFont
	minHValLabel['font'] = textFont
	maxHValLabel['font'] = textFont
	medHValLabel['font'] = textFont
	meanHValLabel['font'] = textFont

	minTLabel = ttk.Label(aStatsWin, text="Minimum Temperature: ")
	minTLabel.grid(row=5, column=0)
	maxTLabel = ttk.Label(aStatsWin, text="Maximum Temperature: ")
	maxTLabel.grid(row=6, column=0)
	medTLabel = ttk.Label(aStatsWin, text="Median Temperature: ")
	medTLabel.grid(row=7, column=0)
	meanTLabel = ttk.Label(aStatsWin, text="Mean Temperature: ")
	meanTLabel.grid(row=8, column=0)

	minTValLabel = ttk.Label(aStatsWin, text="{:.2f}".format(temps.min()))
	minTValLabel.grid(row=5, column=1)
	maxTValLabel = ttk.Label(aStatsWin, text="{:.2f}".format(temps.max()))
	maxTValLabel.grid(row=6, column=1)
	medTValLabel = ttk.Label(aStatsWin, text="{:.2f}".format(np.median(temps)))
	medTValLabel.grid(row=7, column=1)
	meanTValLabel = ttk.Label(aStatsWin, text="{:.2f}".format(temps.mean()))
	meanTValLabel.grid(row=8, column=1)

	minTLabel['font'] = textFont
	maxTLabel['font'] = textFont
	medTLabel['font'] = textFont
	meanTLabel['font'] = textFont
	minTValLabel['font'] = textFont
	maxTValLabel['font'] = textFont
	medTValLabel['font'] = textFont
	meanTValLabel['font'] = textFont

	for child in aStatsWin.winfo_children(): 
		child.grid_configure(padx=5, pady=5)

def tempStatistics():
	tempStatsWindow()
	tempHistogram()

def humStatistics():
	humStatsWindow()
	humHistogram()

def allStatistics():
	allStatsWindow()
	allHistograms()

# Serial -------------------
def serialPorts():
	return [p.device for p in serial.tools.list_ports.comports()]
	pass

def serialInit():
	global serialPort
	serialPort = serial.Serial()
	serialPort.baudrate = 9600
	serialPort.port = COMPortCombobox.get()
	serialPort.open()
	main()

def startSerialThread():
	global serialThreadBoolean
	if not serialThreadBoolean and not (COMPortCombobox.get() == 'None' or COMPortCombobox.get() == ''):
		serialThreadBoolean = True
		serialThread = Thread(target=serialInit, daemon=True)
		serialThread.start()

def stopSerialThread():
	global serialThreadBoolean
	serialThreadBoolean = False

def serialPortToLine():
	global line
	line = str(serialPort.readline())
	line = line[2:len(line)-5]


#Graphing ----------------
def graphSecondsInit():	
	global figureSeconds
	global axisSeconds
	style.use('fivethirtyeight')
	figureSeconds = plt.figure("Last 15 values", figsize=(15, 6))
	axisSeconds = figureSeconds.add_subplot()
	axisSeconds.set_xlabel('Time')
	axisSeconds.set_ylabel('Values')
	showSecondsGraph()

def animateSeconds(i):
	linesS = []
	if textFileLines >= numberOfGraphPoints:
		head = []
		with open(timeTempHumFile) as myfile:
			head = [next(myfile) for x in range(numberOfGraphPoints)]
		head.reverse()
		linesS = listToString(head).split('\n')
	else:
		head = []
		for line in reversed(list(open(timeTempHumFile))):
			head += line.rstrip() + "\n"
		linesS = listToString(head).split('\n')

	timesS = []
	temperaturesS = []
	humiditiesS = []
	for oneLine in linesS:
		if len(oneLine) > 1:
			tTimeS, tTempS, tHumS = oneLine.split(',')
			tTimeS = tTimeS[3:len(tTimeS)]
			timesS.append(tTimeS)
			temperaturesS.append(int(tTempS))
			humiditiesS.append(int(tHumS))
		axisSeconds.clear()
		axisSeconds.plot(timesS, temperaturesS, label='Temperature')
		axisSeconds.plot(timesS, humiditiesS, label='Humidity')

def showSecondsGraph():
	animationSeconds = animation.FuncAnimation(figureSeconds, animateSeconds, interval=1000)
	plt.show()

def tempHistogram():
	style.use('seaborn-deep')
	temps = getTempFile()
	bins = np.linspace(0, 50, 20)

	plt.figure("Temperature Histogram")
	plt.hist(temps, bins)
	plt.show()

def humHistogram():
	style.use('seaborn-deep')
	hums = getHumFile()
	bins = np.linspace(0, 100, 20)
	print(hums)


	plt.figure("Humidity Histogram")
	plt.hist(hums, bins)
	plt.show()

def allHistograms():
	style.use('seaborn-deep')
	temps = getTempFile()
	hums = getHumFile()
	bins = np.linspace(0, 100, 20)

	plt.figure("Histogram")
	plt.hist([temps, hums], bins, label=['Temperature', 'Humidity'])
	plt.legend(loc='upper right')
	plt.show()	


# Data maipulation -----------
def resetFiles():
	if messagebox.askokcancel("Reset files", "Do you want to reset files?"):
		file = open(timeTempHumFile, "w")
		file.close()
		file = open(tempFileName, "w")
		file.close()
		file = open(humFileName, "w")
		file.close()

def listToString(s):  
    outString = ""  
    for element in s:  
        outString += element  
    return outString  

def getTempFile():
	file = open(tempFileName, 'r')
	content = file.read()
	file.close()
	content = content[:len(content)-1]
	content = content.split(',')
	return np.array(content).astype(np.float64)

def getHumFile():
	file = open(humFileName, 'r')
	content = file.read()
	file.close()
	content = content[:len(content)-1]
	content = content.split(',')
	return np.array(content).astype(np.float64)

def linePrepender(line):
	global textFileLines
	textFileLines += 1
	with open(timeTempHumFile, 'r+') as file:
		content = file.read()
		file.seek(0, 0)
		file.write(line.rstrip('\r\n') + '\n' + content)
		file.close()

def addTimeToLine():
	global line
	line = time.strftime("%H:%M:%S") + "," + line + "\n"

def addToHumFile(string):
	file = open(humFileName, "a")
	file.write(string + ",")
	file.close()

def addToTempFile(string):
	file = open(tempFileName, "a")
	file.write(string + ",")
	file.close()

def updateValues():
	tempHumTime = line.split(",")
	timeValueLabel.config(text=tempHumTime[0])

	temperatureValueLabel.config(text=tempHumTime[1] + " °C")
	addToTempFile(tempHumTime[1])

	tempHumTime[2] = tempHumTime[2][:len(tempHumTime[2])-1]
	humidityValueLabel.config(text=tempHumTime[2] + " %")
	addToHumFile(tempHumTime[2])

	rawText.insert("end", line)
	rawText.see("end")

def loopMain():
	time.sleep(.1)
	main()

def main():
	global serialThreadBoolean
	global line
	if serialThreadBoolean:
		serialPortToLine()
		if len(line) > 1:
			addTimeToLine()
			updateValues()
			linePrepender(line)
			
		loopMain()


# Tkinter window ---------------------------------------------------------------------------------------------------------------
root = tk.Tk()
root.title("DH11 data logger")
root.geometry("900x700")
root.columnconfigure(1, weight=1)
root.protocol("WM_DELETE_WINDOW", onClosing)

# Fonts ----------------------------------------------
buttonFont = font.Font(family='Helvetica', size='15')
textFont = font.Font(family='Helvetica', size='12')
titleFont = font.Font(family='Helvetica', size='30')
toplevelTitleFont = font.Font(family='Helvetica', size='20')

# Mainframe ---------------------------------------------------------------------------------------------------------------
mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0)

titleLabel = ttk.Label(mainframe, text="DH11 Data Logger")
titleLabel.grid(row=0, column=0, columnspan=2)
titleLabel['font'] = titleFont

COMPortLabel = ttk.Label(mainframe, text="COM port")
COMPortLabel.grid(row=1, column=0, sticky=E)
COMPortLabel['font'] = textFont

COMPortCombobox = ttk.Combobox(mainframe, values=serialPorts(), width=10)
COMPortCombobox.grid(row=1, column=1, sticky=W)
COMPortCombobox.set('None')
COMPortCombobox.state(["readonly"])
COMPortCombobox.bind('<<ComboboxSelected>>', selectionClear)
COMPortCombobox['font'] = textFont

comPortBlankLabel = ttk.Label(mainframe, text="")
comPortBlankLabel.grid(row=2, column=0)

startLoggingButton = tk.Button(mainframe, text='Start Logging', command=startSerialThread)
startLoggingButton.grid(row=3, column=0, sticky=E)
startLoggingButton['font'] = buttonFont

stopLoggingButton = tk.Button(mainframe, text='Stop Logging', command=stopSerialThread)
stopLoggingButton.grid(row=3, column=1, sticky=W)
stopLoggingButton['font'] = buttonFont

loggingBlankLabel = ttk.Label(mainframe, text="")
loggingBlankLabel.grid(row=4, column=0)

showSecondsGraphButton = tk.Button(mainframe, text='Show Last 15 Readings', command=graphSecondsInit)
showSecondsGraphButton.grid(row=5, column=0, columnspan=2)
showSecondsGraphButton['font'] = buttonFont

showTemperatureStatsButton = tk.Button(mainframe, text='Show Temperature Statistics', command=tempStatistics)
showTemperatureStatsButton.grid(row=6, column=0)
showTemperatureStatsButton['font'] = buttonFont

showHumidityStatsButton = tk.Button(mainframe, text='Show Humidity Statistics', command=humStatistics)
showHumidityStatsButton.grid(row=6, column=1)
showHumidityStatsButton['font'] = buttonFont

showAllStatsButton = tk.Button(mainframe, text='Show All Statistics', command=allStatistics)
showAllStatsButton.grid(row=7, column=0, columnspan=2)
showAllStatsButton['font'] = buttonFont

statsBlankLabel = ttk.Label(mainframe, text="")
statsBlankLabel.grid(row=8, column=0)

showHideTextButton = tk.Button(mainframe, text='Hide Raw Data', command=showHideText)
showHideTextButton.grid(row=9, column=0, columnspan=2)
showHideTextButton['font'] = buttonFont

endBlankLabel = ttk.Label(mainframe, text="")
endBlankLabel.grid(row=10, column=0)

resetFilesButton = tk.Button(mainframe, text='Reset Files', command=resetFiles)
resetFilesButton.grid(row=11, column=0, columnspan=2)
resetFilesButton['font'] = buttonFont

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)


# Data frame ---------------------------------------------------------------------------------------------------------------
dataFrame = ttk.Frame(root)
dataFrame.grid(row=11, column=0)

timeTitleLabel = ttk.Label(dataFrame, text="Last Time Read: ")
timeTitleLabel.grid(row=0, column=0)
timeTitleLabel['font'] = textFont

timeValueLabel = ttk.Label(dataFrame, text="00:00:00")
timeValueLabel.grid(row=0, column=1)
timeValueLabel['font'] = textFont

temperatureTitleLabel = ttk.Label(dataFrame, text="Current Temperature: ")
temperatureTitleLabel.grid(row=1, column=0)
temperatureTitleLabel['font'] = textFont

temperatureValueLabel = ttk.Label(dataFrame, text="0 °C")
temperatureValueLabel.grid(row=1, column=1)
temperatureValueLabel['font'] = textFont

humidityTitleLabel = ttk.Label(dataFrame, text="Current Humidity: ")
humidityTitleLabel.grid(row=2, column=0)
humidityTitleLabel['font'] = textFont

humidityValueLabel = ttk.Label(dataFrame, text="0 %")
humidityValueLabel.grid(row=2, column=1)
humidityValueLabel['font'] = textFont

for child in dataFrame.winfo_children(): 
    child.grid_configure(padx=5, pady=5)


# Serial output frame ---------------------------------------------------------------------------------------------------------------
serialOutputFrame = ttk.Frame(root)
serialOutputFrame.grid(column=1, row=0, rowspan=2)

rawText = tk.Text(serialOutputFrame, height=35, width=25)
rawText.pack(side="left", fill="both", expand=True)

verticalScrollBar = tk.Scrollbar(serialOutputFrame, orient="vertical", command=rawText.yview)
verticalScrollBar.pack(side="right", fill="y")

rawText.configure(yscrollcommand=verticalScrollBar.set)

root.mainloop()