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
           
class clOption_menu():
    """
    creates a tk.OptionMenu as a child of the parent, from 
    the list - using the "eval_string" for the display
    (derivative classes can replace opt_string to change 
    the output)
    
    Builds a dictionary, and returns pointer to the member 
    of the list that was selected.
    
    """
    def __init__(self, parent, list, eval_string, default='-Choose-'):
    
        self.parent = parent
        self.list = list
        self.eval_string = eval_string
        self.default = default
         
        # Create a list of strings and a dictionary to later convert
        # the return string back to a pointer to the list member
        self.namelist = []
        self.dictionary = dict()
        self.dictionary[default] = None # detect when there's no selection
    
        for member in self.list:
            string = self.opt_string(member, eval_string)
            print "New member", string
            self.namelist.append(string)
            self.dictionary[string] = member
             
        self.var = tk.StringVar()
        self.var.set(self.default)
        self.om = tk.OptionMenu(self.parent, self.var, *self.namelist)
        
        print self.var.get()
        
    def return_value(self):
        """ which one is currently selected """
        string = self.var.get()
        if string == '-Choose-':
            return None
        return self.dict[string]    # could "try" this... but a failure is pretty serious in any case
        
    def opt_string(self, member, eval_string):
        value = eval('member' + '.' + eval_string)
        return(str(value))
 
""" for debugging.... """
class Thingy():
    def __init__(self):
        self.a = 'string'
        self.b = 1
              
def main():
    t = tk.Tk() # base object
    t.grid()
    l = []
    a = Thingy()
    a.a = 'zero'
    a.b = 0
    b = Thingy()
    b.a = "one"
    b.b = 1
    c = Thingy()
    c.a = 'two'
    c.b = 2
    l = [ a, b, c]
    myom = clOption_menu(t, l, 'a', 'one' )
    myom.om.grid()
    
    
    
import coLab
if __name__ == '__main__':
    #coLab.main()
    main()
    
    
    
