#!/usr/loical/bin/python3
# -*- coding: utf-8 -*-
""" Some useful tools for dealing with graphic objects 

Some items like:
Progress_bar --  a class to ease setting up tkinter progress bars
graphic_element -- a function to put up an image
Popup	-- a class for Popups...
"""

import os
import sys
import logging
import time
import threading	# for the progbar lock

#import Tkinter as tk
#import tkFileDialog
#import ttk
#from tkinter import *
import tkinter as tk
from tkinter import ttk

#import tkinter as tk
#import tkinter.ttk

import tkinter.filedialog
import tkinter.messagebox

from PIL import Image, ImageTk

class Progress_bar():
	"""
	Build a generic progress bar.   Various items can
	be adjusted before calling post().  The update() 
	method handles both the bar and the remaining time.
	Creates a frame within the parent object, and grids
	out the title and 
	"""
	
	def __init__(self, parent, title, width=200, max=0, init=0):
		self.parent = parent
		self.title = title
		self.width = width
		self.max = max
		if self.max == 0:
			self.of_str = ' of ???'
		else:
			self.of_str = ' of ' + str(max)
		# value used to set the progress bard
		self.value = tk.DoubleVar()
		self.value.set(init)
		# string to show the progress status as text
		self.v_string = tk.StringVar()
		self.v_string.set(str(init) + self.of_str)
		# string to show remaining time..
		self.t_string = tk.StringVar()
		self.t_string.set('?:??')
		self.start_time = time.time()
		self.what = 'Item'	# what it is....
		self.mode = 'determinate'
		self.highest = 0	# what's the largest so far?
		self.lock = threading.Lock()	# let's threads lock access
		
		
	def post(self):
		"""
		Build a small grid, # items of items (0,0), time remaining (0,1),
		Progress bar, (1,0-1) (columnspan 2)
		"""
		self.start_time = time.time()
		
		self.frame = tk.Frame(self.parent)
		self.frame.grid(sticky=tk.W)
		
		
		tk.Label(self.frame, text=self.title).grid(row=0, column=0, columnspan=5, sticky=tk.W)
		if self.mode == 'determinate':
			tk.Label(self.frame, text=self.what + ':', justify= tk.LEFT).grid(row=1, column=0, sticky=tk.W)
			self.which = tk.Label(self.frame, textvariable=self.v_string, justify= tk.LEFT)
			self.which.grid(row=1, column=1, sticky=tk.W)
			
			tk.Label(self.frame, text='Time remaining: ', justify= tk.RIGHT).grid(row=1, column=3, sticky=tk.E)
			tk.Label(self.frame, textvariable=self.t_string, justify= tk.RIGHT).grid(row=1, column=4, sticky=tk.E)
		
		self.progBar = ttk.Progressbar(self.frame, length=self.width, maximum=self.max, mode=self.mode, variable=self.value)
		self.progBar.grid(row=2, column=0, columnspan=5, sticky=tk.W)
	

		   
	def set_max(self, new_max):
		self.max = new_max 
		self.of_str = ' of ' + str(self.max)
		self.progBar.configure(maximum=self.max)
	
			
	def update(self, new_value):
		"""
		Update the bits and pieces with the new value...
		Move the progress bar, display the new value and
		time remaining.
		
		Call with 0 to reset the starting time to now.
		"""
		# for now...
		if new_value < self.highest:
			logging.info("progbar.update() - value %s lower than highest %s.", new_value, self.highest)
			return
		self.value.set(new_value)
		self.highest = new_value
		self.v_string.set(str(new_value) + self.of_str)
		
		# time remaining:
		if new_value == 0:
			self.start_time=time.time()
			self.highest = 0 
			return
		
		elapsed = time.time() - self.start_time
		rem = elapsed / new_value * (self.max - new_value)	# remaining time in seconds...
		(minutes, seconds) = divmod(rem, 60)	# split (note: they are floats)

		# doesn't seem this should be necessary - but the %02.2f conversion is
		# not working as I expected...
		(isecs, frac) = divmod(seconds, 1)
		ifrac = int(frac*10)
		
		#rem_str =  ('%0d:%02d.%02d') % (minutes, isecs, frac)
		rem_str =  '%0d:%02d.%01d' % (minutes, isecs, ifrac)
		rem_str =  '%0d:%02d' % (minutes, isecs)
		self.t_string.set(rem_str)
		
	
class graphic_element:
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
		logging.info("ge-post: %s", self.filepath)
			
		try:	 # same thing, for the title
			img = Image.open(self.filepath)
			labelimage = ImageTk.PhotoImage(img)
			self.graphic = tk.Label(self.parent, image=labelimage)
			self.graphic.image = labelimage
			self.graphic.grid(column=self.column, row=self.row, rowspan=self.rowspan, columnspan=self.columnspan, sticky=self.sticky)
		except:
			logging.warning( "Title creation exception - file: %s", self.filepath, exc_info=True)
			#raise SystemError
	def destroy(self):		
		try:
			self.graphic.grid_forget()
			self.graphic.destroy()
		except:
			logging.warning("self.graphic.grid_forget / destroy excepted...", exc_info=True)
		   
class clOption_menu:
	"""
	creates a tk.OptionMenu as a child of the parent, from 
	the list - using the "eval_string" for the display
	(derivative classes can replace opt_string to change 
	the output)
	
	Builds a dictionary, and returns pointer to the member 
	of the list that was selected.
	
	"""
	def __init__(self, parent, list, eval_string, default='-Choose-', command=None, arg=None):
	
		self.parent = parent
		self.list = list
		self.eval_string = eval_string
		self.default = default
		self.command = command
		 
		# Create a list of strings and a dictionary to later convert
		# the return string back to a pointer to the list member
		self.namelist = []
		self.dictionary = dict()
		self.dictionary[default] = None # detect when there's no selection
	
		for member in self.list:
			string = self.opt_string(member, eval_string)
			logging.info("New member: %s", string)
			self.namelist.append(string)
			self.dictionary[string] = member
			 
		self.var = tk.StringVar()
		self.var.set(self.default)
		self.om = tk.OptionMenu(self.parent, self.var, *self.namelist, command=command)
		if arg is None:
			logging.info("OptionMenu: %s", self.var.get())
		else:
			logging.info("OptionMenu: %s, arg: %s", self.var.get(), arg)
		
	def return_value(self):
		""" which one is currently selected """
		string = self.var.get()
		logging.info("clOptionMenu return_value %s", string)
		if string == self.default:
			return None
		return self.dictionary[string]	# could "try" this... but a failure is pretty serious in any case
		
	def opt_string(self, member, eval_string):
		value = eval('member' + '.' + eval_string)
		#return(unicode(value))
		return(str(value))
 
class Popup:
	"""
	A very simple way to put something on the screen that will disappear soon.
	"""
	def __init__(self, label="Info...", text="Pop-up!", nobutton=True, geometry="+1800+80"):
		"""
		Pretty straight forward - the nobutton option is for pop ups 
		that out outside the loop and won't get cycles (like using 
		Preview to crop the graphics.
		"""
		logging.info("Popup: creating popup, label: %s, text: %s", label, text)
		self.t = tk.Toplevel()
		self.t.transient()
		self.t.title("File copy")
		self.t.geometry(geometry)
		self.t.lift(aboveThis=None)
		lf = tk.LabelFrame(master=self.t, relief=tk.GROOVE, text=label, borderwidth=5)
		lf.grid(ipadx=10, ipady=40, padx=5, pady=5)
		f = tk.Frame(lf)
		f.grid(row=0, column=0, sticky=tk.W)
		tk.Label(f, text=text).grid()
		if not nobutton:	# kinda dig the language here...
			ok_button = tk.Button(f, text='OK', command=self.destroy)
			ok_button.grid(row=1, column=0, sticky=tk.SE)
		self.t.update()	 # Get the pop-up on the screen...
		self.t.update_idletasks()
		
		 
	def destroy(self):
		""" Just make it go away..."""
		self.t.destroy()
		
		 
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
	my_obj_module = clOption_menu(t, l, 'a', 'one' )
	my_obj_module.om.grid()
	
	
	
import coLab
if __name__ == '__main__':
	#coLab.main()
	main()
	
	
	
