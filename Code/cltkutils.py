#!/usr/bin/env python
"""
    A attempt at...
    A initial GUI front-end interface to the various
    tasks required for creating and managing coLab.
"""

import os
import sys
import time

import Tkinter as tk
import tkFileDialog
import ttk

from PIL import Image, ImageTk

class graphic_element():
    """
    Used to place a generic image on the grid.
    """
    def __init__(self, parent):
        self.parent = parent
        self.row = 0
        self.column = 0
        self.rowspan = 1
        self.columnspan = 1
        self.filepath = "unset"
        self.sticky = tk.W
        
    def post(self):
        """
        build a tk image and post it - the values should have been filled in above.
        """
        print "ge-post:", self.filepath
            
        try:     # same thing, for the title
            img = Image.open(self.filepath)
            labelimage = ImageTk.PhotoImage(img)
            self.graphic = tk.Label(self.parent, image=labelimage)
            self.graphic.image = labelimage
            self.graphic.grid(column=self.column, row=self.row, rowspan=self.rowspan, columnspan=self.columnspan, sticky=self.sticky)
        except Exception as e:
            print "Title creation exception", sys.exc_info()[0], e
            raise SystemError
    def clear(self):        
        try:
            self.graphic.grid_forget()
            self.graphic.destroy()
        except Exception as e:
            print "self.graphic.grid_forget / destroy excepted...", e, sys.exc_info()[0]
           
def task(obj,bar):
    
    val = raw_input('Next Spot')
    
    obj.value.set(val)

    val = raw_input('Max val')
    
    bar.configure(maximum=val)

    obj.after(50, task, obj,bar)


# This one is likely going away soon...   still used in the scripted version
def getGroup():
    
    a = tk.Tk()
    
    quitButton = tk.Button(a, text="Quit", command=a.quit)
    quitButton.grid(column=3, row=3)
    
    groupOptions = ( 'Catharsis', 'SBP', 'Johnny' )
    
    gOpt = tk.StringVar()
    gOpt.set(groupOptions[0])
    
    groupOption = tk.OptionMenu(a, gOpt, 'Catharsis', 'SBP', 'Johnny')
    
    groupOption.grid(column=1, row=1)
    
    """
    screenshot = tkFileDialog.askopenfilename(initialdir="~/Desktop", title="Select a Screen Shot", parent=a)
    
    print "Got Screenshot:", screenshot
    
    audio = tkFileDialog.askopenfilename(initialdir="/Volumes/iMac 2TB/Music/JDJ", title="Select an audio file", parent=a)
    print "Got audio file:", audio
    
    """
    
    
    
    a.value = tk.IntVar()
    
    progBar = ttk.Progressbar(a, length=500, maximum=800, mode='determinate', variable=a.value)
    
    
    progBar.grid(column=1, columnspan=3, row=2)
    
    """
    for i in range(400):
        time.sleep(.1)
        progBar.step(1)
        print i
    """
    
    #v.set(450)
    #progBar.start(10)
    a
    a.after(20, task, a, progBar)
    
    a.mainloop()
    
    a.destroy()    

    group = gOpt.get()

    print "cltkutils.getGroup:", group

    return(group)
    
if __name__ == '__main__':
    getGroup()
    
    
    
    
