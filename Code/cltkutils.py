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
    def destroy(self):        
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


import coLab
if __name__ == '__main__':
    coLab.main()
    
    
    
    
