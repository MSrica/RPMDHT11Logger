# Todo --------------------------------------------------------------------------------------------------------------------
# 1 value doesn't show up in graph


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
import datetime
from datetime import datetime, date, time, timedelta
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

import numpy as np
import pandas as pd
import re

global serialThreadBoolean
serialThreadBoolean = False

# Functions ---------------------------------------------------------------------------------------------------------------
# Tkinter -------------------
def selectionClear(*args):
	root.focus()
	pass

def onClosing():
	root.destroy()
	pass

def error(i):
	if i == 0:
		messagebox.showinfo(title="Error", message="COM port not chosen")
	elif i == 1:
		messagebox.showinfo(title="Error", message="Arduino comunication not started")

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

def startOrStop():
	if serialConnectButton.cget('text') == "Connect to Arduino":
		if startSerialThread():
			serialConnectButton.configure(text="Disconnect from Arduino")
	elif serialConnectButton.cget('text') == "Disconnect from Arduino":
		stopSerialThread()
		serialConnectButton.configure(text="Connect to Arduino")

def startSerialThread():
	global serialThreadBoolean
	if not serialThreadBoolean and not (COMPortCombobox.get() == 'None' or COMPortCombobox.get() == ''):
		serialThreadBoolean = True
		serialThread = Thread(target=serialInit, daemon=True)
		serialThread.start()
		return True
	else:
		error(0)
		return False

def stopSerialThread():
	global serialThreadBoolean
	global serialPort
	serialThreadBoolean = False
	serialPort.close()

def serialPortToLine():
	line = str(serialPort.readline())
	line = line[2:len(line)-5]
	return line


# Main functions ------------
secondsTimeArray = [1000 for x in range(30)]
minutesTimeArray = [1000 for x in range(60)]

global currentSecondsIndex
currentSecondsIndex = 0
twoSecondsTemperature = [1000 for x in range(30)]
twoSecondsHumidity = [1000 for x in range(30)]

global currentMinutesIndex
currentMinutesIndex = 0
minuteAverageTemperature = [1000 for x in range(60)]
minuteAverageHumidity = [1000 for x in range(60)]
minuteSDTemperature = [1000 for x in range(60)]
minuteSDHumidity = [1000 for x in range(60)]

def showMinuteStats():
	global currentSecondsIndex
	try:
		if serialPort:
			serialPort.write(bytes("1", 'utf-8'))
			line = serialPortToLine()
			twoSeconds = re.split(';|,', line)
			y = 0
			for x in range(0, 60, 2):
				twoSecondsTemperature[y] = int(twoSeconds[x])
				twoSecondsHumidity[y] = int(twoSeconds[x+1])
				y += 1
			currentSecondsIndex = int(twoSeconds[60])

			g = rearangeMinutes()
			minuteStats(g)
			graphMinutes()
	except:
		error(1)

def showHourStats():
	global currentMinutesIndex
	try:
		if serialPort:
			serialPort.write(bytes("2", 'utf-8'))
			line = serialPortToLine()
			sixtySeconds = re.split(';|,', line)
			y = 0
			for x in range(0, 240, 4):
				minuteAverageTemperature[y] = float(sixtySeconds[x])
				minuteAverageHumidity[y] = float(sixtySeconds[x+1])
				minuteSDTemperature[y] = float(sixtySeconds[x+2])
				minuteSDHumidity[y] = float(sixtySeconds[x+3])
				y += 1
			currentMinutesIndex = int(sixtySeconds[240])

			g = rearangeHours()
			hourStats(g)
			graphHours()
	except:
		error(1)

def minuteStats(g):
	mStatsWin = tk.Toplevel()

	title = ttk.Label(mStatsWin, text="Minute Statistics")
	title.grid(row=0, column=0, columnspan=3)
	title['font'] = toplevelTitleFont

	l = ttk.Label(mStatsWin, text="Time")
	l.grid(row=1, column=0)
	l['font'] = textFont

	l = ttk.Label(mStatsWin, text="Temperature")
	l.grid(row=1, column=1)
	l['font'] = textFont

	l = ttk.Label(mStatsWin, text="Humidity")
	l.grid(row=1, column=2)
	l['font'] = textFont

	for x in range(g):
		l = ttk.Label(mStatsWin, text=secondsTimeArray[x])
		l.grid(row=x+2, column=0)
		l['font'] = textFont

		t = ttk.Label(mStatsWin, text=newTwoSecondsTemperature[x])
		t.grid(row=x+2, column=1)
		t['font'] = textFont

		h = ttk.Label(mStatsWin, text=newTwoSecondsHumidity[x])
		h.grid(row=x+2, column=2)
		h['font'] = textFont

	for child in mStatsWin.winfo_children(): 
		child.grid_configure(padx=5, pady=3)

def hourStats(g):
	hStatsWin = tk.Toplevel()

	title = ttk.Label(hStatsWin, text="Hour Statistics")
	title.grid(row=0, column=0, columnspan=10)
	title['font'] = toplevelTitleFont

	time1 = ttk.Label(hStatsWin, text="Time")
	time1.grid(row=1, column=0)
	time1['font'] = textFont

	aTemp1 = ttk.Label(hStatsWin, text="Average\ntemperature")
	aTemp1.grid(row=1, column=1)
	aTemp1['font'] = textFont

	aHum1 = ttk.Label(hStatsWin, text="Average\nhumidity")
	aHum1.grid(row=1, column=2)
	aHum1['font'] = textFont

	SDTemp1 = ttk.Label(hStatsWin, text="Standard\ndeviation\ntemperature")
	SDTemp1.grid(row=1, column=3)
	SDTemp1['font'] = textFont

	SDHum1 = ttk.Label(hStatsWin, text="Standard\ndeviation\nhumidity")
	SDHum1.grid(row=1, column=4)
	SDHum1['font'] = textFont

	col = 0
	row = 0
	cnt = 1

	for x in range(g):
		if x > 29 and cnt == 1:
			cnt = 0
			col = 5
			row = 30

			time2 = ttk.Label(hStatsWin, text="Time")
			time2.grid(row=1, column=5)
			time2['font'] = textFont

			aTemp2 = ttk.Label(hStatsWin, text="Average\ntemperature")
			aTemp2.grid(row=1, column=6)
			aTemp2['font'] = textFont

			aHum2 = ttk.Label(hStatsWin, text="Average\nHumidity")
			aHum2.grid(row=1, column=7)
			aHum2['font'] = textFont

			SDTemp2 = ttk.Label(hStatsWin, text="Standard\ndeviation\ntemperature")
			SDTemp2.grid(row=1, column=8)
			SDTemp2['font'] = textFont
			

			SDHum2 = ttk.Label(hStatsWin, text="Standard\ndeviation\nhumidity")
			SDHum2.grid(row=1, column=9)
			SDHum2['font'] = textFont
			

		l = ttk.Label(hStatsWin, text=minutesTimeArray[x])
		l.grid(row=x+2-row, column=0+col)
		l['font'] = textFont

		l = ttk.Label(hStatsWin, text=newMinuteAverageTemperature[x])
		l.grid(row=x+2-row, column=1+col)
		l['font'] = textFont

		l = ttk.Label(hStatsWin, text=newMinuteAverageHumidity[x])
		l.grid(row=x+2-row, column=2+col)
		l['font'] = textFont

		l = ttk.Label(hStatsWin, text=newMinuteSDTemperature[x])
		l.grid(row=x+2-row, column=3+col)
		l['font'] = textFont

		l = ttk.Label(hStatsWin, text=newMinuteSDHumidity[x])
		l.grid(row=x+2-row, column=4+col)
		l['font'] = textFont

	for child in hStatsWin.winfo_children(): 
		child.grid_configure(padx=5, pady=3)

def circularArray(a, l, ind):
    b = [None]*2*l
    out = [None]*2*l
    i = 0
     
    while i < l: 
        b[i] = b[l + i] = a[i]
        i += 1
     
    i = ind
    j = 0

    while i < l + ind :
        out[j] = b[i]
        i += 1
        j += 1

    return out

def rearangeMinutes():
	global newTwoSecondsTemperature
	global newTwoSecondsHumidity
	global secondsTimeArray
	secondsTimeArray = [1000 for x in range(30)]
	tmp = [1000 for x in range(30)]
	g = 0
	t = 0

	tmp = circularArray(twoSecondsTemperature[::-1], 30, 29-currentSecondsIndex)
	newTwoSecondsTemperature = tmp[0:30]
	tmp = circularArray(twoSecondsHumidity[::-1], 30, 29-currentSecondsIndex)
	newTwoSecondsHumidity = tmp[0:30]
	
	if int(format(datetime.now(), '%S')) % 2 == 1:
		t = 1
	while g < 30 and newTwoSecondsTemperature[g] != 1000:
		secondsTimeArray[g] = format(datetime.now() - timedelta(seconds=g*2 - t), '%M:%S')
		g += 1
		
	if g == 30:
		g = 29

	if secondsTimeArray[g] == 1000:
		secondsTimeArray = secondsTimeArray[:g]
		newTwoSecondsTemperature = newTwoSecondsTemperature[:g]
		newTwoSecondsHumidity = newTwoSecondsHumidity[:g]
	else:
		secondsTimeArray = secondsTimeArray[:g+1]
		newTwoSecondsTemperature = newTwoSecondsTemperature[:g+1]
		newTwoSecondsHumidity = newTwoSecondsHumidity[:g+1]

	return g

def rearangeHours():
	global newMinuteAverageTemperature
	global newMinuteAverageHumidity
	global newMinuteSDTemperature
	global newMinuteSDHumidity
	global minutesTimeArray
	minutesTimeArray = [1000 for x in range(60)]
	tmp = [1000 for x in range(60)]
	g = 0

	tmp = circularArray(minuteAverageTemperature[::-1], 60, 59-currentMinutesIndex)
	newMinuteAverageTemperature = tmp[0:60]
	tmp = circularArray(minuteAverageHumidity[::-1], 60, 59-currentMinutesIndex)
	newMinuteAverageHumidity = tmp[0:60]
	tmp = circularArray(minuteSDTemperature[::-1], 60, 59-currentMinutesIndex)
	newMinuteSDTemperature = tmp[0:60]
	tmp = circularArray(minuteSDHumidity[::-1], 60, 59-currentMinutesIndex)
	newMinuteSDHumidity = tmp[0:60]

	while g < 60 and newMinuteAverageTemperature[g] != 1000:
		minutesTimeArray[g] = format(datetime.now() - timedelta(minutes=g), '%M')
		g += 1

	if g == 60:
		g = 59

	if minutesTimeArray[g] == 1000:
		minutesTimeArray = minutesTimeArray[:g]
		newMinuteAverageTemperature = newMinuteAverageTemperature[:g]
		newMinuteAverageHumidity = newMinuteAverageHumidity[:g]
		newMinuteSDTemperature = newMinuteSDTemperature[:g]
		newMinuteSDHumidity = newMinuteSDHumidity[:g]
	else:
		minutesTimeArray = minutesTimeArray[:g+1]
		newMinuteAverageTemperature = newMinuteAverageTemperature[:g+1]
		newMinuteAverageHumidity = newMinuteAverageHumidity[:g+1]
		newMinuteSDTemperature = newMinuteSDTemperature[:g+1]
		newMinuteSDHumidity = newMinuteSDHumidity[:g+1]

	return g

def graphMinutes():
	figureSeconds = plt.figure("Last minute", figsize=(18, 7))
	axisSeconds = figureSeconds.add_subplot()
	axisSeconds.set_xlabel('Time')
	axisSeconds.set_ylabel('Values')
	axisSeconds.plot(secondsTimeArray[::-1], newTwoSecondsTemperature[::-1], label='Temperature')
	axisSeconds.plot(secondsTimeArray[::-1], newTwoSecondsHumidity[::-1], label='Humidity')
	figureSeconds.subplots_adjust(top=0.97, left=0.043, right=0.971, bottom=0.079)
	axisSeconds.legend(loc='best', shadow=True)
	plt.show()

def graphHours():
	figureMinutes = plt.figure("Last hour", figsize=(18, 8))
	axisMinutes = figureMinutes.add_subplot()
	axisMinutes.set_xlabel('Time')
	axisMinutes.set_ylabel('Values')
	axisMinutes.plot(minutesTimeArray[::-1], newMinuteAverageTemperature[::-1], label='Average temperature')
	axisMinutes.plot(minutesTimeArray[::-1], newMinuteAverageHumidity[::-1], label='Average humidity')
	axisMinutes.plot(minutesTimeArray[::-1], newMinuteSDTemperature[::-1], label='Standard deviation temperature')
	axisMinutes.plot(minutesTimeArray[::-1], newMinuteSDHumidity[::-1], label='Standard deviation humidity')
	figureMinutes.subplots_adjust(top=0.97, left=0.095, right=0.95, bottom=0.076)
	axisMinutes.legend(loc='best', shadow=True)
	plt.show()

# Tkinter window ---------------------------------------------------------------------------------------------------------------
root = tk.Tk()
root.title("DH11 data logger")
root.geometry("300x300")
root.columnconfigure(1, weight=1)
root.protocol("WM_DELETE_WINDOW", onClosing)

# Fonts ----------------------------------------------
buttonFont = font.Font(family='Helvetica', size='15')
textFont = font.Font(family='Helvetica', size='12')
titleFont = font.Font(family='Helvetica', size='25')
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

serialConnectButton = tk.Button(mainframe, text='Connect to Arduino', command=startOrStop)
serialConnectButton.grid(row=2, column=0, columnspan=2)
serialConnectButton['font'] = buttonFont

connectBlankLabel = ttk.Label(mainframe, text="")
connectBlankLabel.grid(row=3, column=0)

showMinuteButton = tk.Button(mainframe, text='Show Last Minute', command=showMinuteStats)
showMinuteButton.grid(row=4, column=0, columnspan=2)
showMinuteButton['font'] = buttonFont

showHourButton = tk.Button(mainframe, text='Show Last Hour', command=showHourStats)
showHourButton.grid(row=5, column=0, columnspan=2)
showHourButton['font'] = buttonFont

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

root.mainloop()