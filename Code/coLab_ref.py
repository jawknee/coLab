#!/usr/bin/env python
"""
	A attempt at...
	A initial GUI front-end interface to the various
	tasks required for creating and managing coLab.
"""

import os
import time

import Tkinter as tk
import tkFileDialog
import ttk


def task(obj,bar):
	bar.step(1.0)

	obj.after(50, task, obj,bar)

	

a = tk.Tk()

quitButton = tk.Button(a, text="Quit", command=a.quit)
quitButton.grid(column=3, row=3)

groupOptions = ( 'Catharsis', 'South Bay Philharmonic', 'Johnny' )

gOpt = tk.StringVar()
gOpt.set(groupOptions[0])

groupOption = tk.OptionMenu(a, gOpt, 'Catharsis', 'South Bay Philharmonic', 'Johnny')

groupOption.grid(column=1, row=1)

"""
screenshot = tkFileDialog.askopenfilename(initialdir="~/Desktop", title="Select a Screen Shot", parent=a)

print "Got Screenshot:", screenshot

audio = tkFileDialog.askopenfilename(initialdir="/Volumes/iMac 2TB/Music/JDJ", title="Select an audio file", parent=a)
print "Got audio file:", audio

"""



value = tk.IntVar()

progBar = ttk.Progressbar(a, length=500, maximum=30, mode='determinate', variable=value)

progBar["value"] = 20.0

progBar.grid(column=1, columnspan=3, row=2)

"""
for i in range(400):
	time.sleep(.1)
	progBar.step(1)
	print i
"""

#v.set(450)
#progBar.start(10)

a.after(20, task, a, progBar)

a.mainloop()



print  gOpt.get()





