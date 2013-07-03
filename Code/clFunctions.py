#!/usr/bin/env python
"""
	Various user interface functions for the coLab main app
	
	The main bits are the editing for pages, group, etc.   These
	use a series of classes that display text on one side, and an
	entry area on the other.  Each of these objects is stored in a 
	list on the edit_screen object so that when the "Enter" button
	is pressed - they're just stepped through and they update their
	particular item.
	
	Left to do at initial:  validation routines, at least. 
"""
import os
import sys
import shutil
import subprocess

import threading
import time		# rbf: unless needed....

import Tkinter as tk
import ttk
import tkFileDialog
import tkMessageBox
from PIL import Image

import clclasses
import cltkutils
import imagemaker
import clAudio
import rebuild

def set_status(obj, ok = None):
	"""
	Set the status of the widget - log the state, and update
	the status column, should work for most/all row classes...
	"""
	obj.ok = ok
	if ok is None:
		color = '#a73'
		txt = '-'
	if ok:
		color = '#2f2'	# bright green
		txt = 'OK'
	else:
		color = '#f11'	# bright red
		txt = 'X'
		
	obj.status.configure(fg=color)
	obj.statusVar.set(txt)
	

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
		"""
		# for now...
		self.value.set(new_value)
		self.v_string.set(str(new_value) + self.of_str)
		
		# time remaining:
		if new_value == 0:
			self.start_time=time.time()
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
		
	
	
		
class Entry_row():
	"""
	A class for an entry row in an edit panel.  Holds the info specific to
	a row - implements posting the Text and the value in an entry field.
	Allows for "new" and "editable" fields (non-editable are displayed as
	labels).   Also handles validation based on the values put into the 
	class. Also marks the status and matching fields.
	"""
	def __init__(self, parent, text, member, width=15):
		"""
		Set up the default values for the row object
		"""
		self.parent = parent
		self.text = text
		self.member = member
		self.width = width
		
		self.label = None				# have we been here before
		self.exclude_list = []		# a list of items not allowed (e.g., current file names)
		self.exclude_chars = '"'	# current implementation does not allow " n stored strings
		self.ignore_case = False	# Set to true for file names, etc.
		self.match = None	
		self.match_text = ''		# used to recall the last bad match (equiv. file name, e.g.)	
		self.match_color = '#666'
		self.new = parent.new		# when true, items are ghosted / replaced on first key  
		self.editable = True		# occasionally we get one (existing file name) that we don't want to edit...
		self.ok = not self.new		# new items are assumed to be not good yet, and vice-versa
		
		self.row = parent.row		# parent keeps track of row / column
		parent.row += 1				# move the  parent row down one...
		self.column = parent.column
				
		# Validation callback parameters
		self.callback = self.validate_entry	
		self.validate = 'all'
		self.subcodes =  ('%d', '%S', '%P', '%V')
		
	def post(self):
		"""
		Create a simple row with the text on the left (right just.), and the current value on the
		right (left justified).  An indicator sits in between (green check, orange ?, red X).
		If an exclude list is given, it can be used by the validation routine.
		"""
		if self.label is None:
			# write the base label...
			self.label = tk.Label(self.parent.page_frame, text=self.text+":", justify=tk.RIGHT)
			self.label.grid(row=self.row,column=self.column, sticky=tk.E)
			self.nameVar = tk.StringVar()
			# Now we build a string that is the name of the associated variable.   Then we use eval and exec to
			# deal with it.
			print "self.member", self.member
			self.value = eval("self.parent.obj." + self.member)	# convert the variable name to its value
			print "value", self.value
			#print "ept: new?:", self.new
			print "post:  my new is:", self.member, self.new
			
			# set up a small label between the title and the value to 
			# display the status of the value...
			self.statusVar = tk.StringVar()
			self.status = tk.Label(self.parent.page_frame, textvariable=self.statusVar)
			self.status.grid(row=self.row, column=self.column + 1)
			if self.new:
				set_status(self,None)
			else:
				set_status(self,ok=True)
		else:
			self.widget.destroy()
		
		# if not editable - just display as a label...
		print "vobj - editable:", self.editable
		if not self.editable:
			self.widget = tk.Label(self.parent.page_frame, textvariable=self.nameVar, justify=tk.LEFT)
			self.widget.grid(row=self.row,column=self.column + 2, columnspan=3, sticky=tk.W)
			self.nameVar.set(self.value)
			#self.ok = True		# since we can't change it - it's good
			set_status(self,ok=True)
			print "non-edit _obj:", self.widget
		else:
			
			print "Ev_init: callback is:", self.callback
			# Build a list: the call back registery and the subcodes, 
			# then turn the list into a tuple to pass in...
			l = [ self.parent.page_frame.register(self.callback) ]		# first part is the registration of the call back.
			#widget.destroy()
			for sc in self.subcodes:
				l.append(sc)
			self.validatecommand = tuple(l)	# make into a tuple
			print "vcmd ", self.validatecommand, "validate:", self.validate
			# set colors for edit (Black) and new (lt. gray) objects
			fg = '#000'		# black
			if self.new:
				fg = '#AAA'	# light gray
			
			self.widget = tk.Entry(self.parent.page_frame, textvariable=self.nameVar, width=self.width, fg=fg, validate=self.validate, validatecommand=self.validatecommand )
			print "v-obj widget created:", self.widget
			self.widget.grid(row=self.row, column=self.column + 2, sticky=tk.W)
			self.nameVar.set(self.value)
			

			
			self.matchVar = tk.StringVar()
			self.match = tk.Label(self.parent.page_frame, textvariable=self.matchVar, justify=tk.LEFT)
			self.match.grid(row=self.row, column=self.column + 3, rowspan=6, columnspan=2, sticky=tk.NW)		
	
	def set(self, value):
		self.value = value
		
		self.new = False
		set_status(self,ok=True)
		self.post()
		
	def validate_entry(self, why, what, would, how):
		"""
		Do the actual validation - the entry object in self.widget
		Check for excluded characters - if any, beep and scoot (reject).
		Check for  zero-length, (bad), and for possible (ok) and exact
		(bad) matches in the exclude list.   
		
		Updates the status column based on what's 
		"""
		print "vld8_entry_base:", why, what, how
		
		if why == '-1':
			if how == 'forced':
				print "Focus: we don't need no stinkin' forced focus"
			elif how == 'focusin':
				print "Focus In: restore Match", self.match_text
				if self.match_text:
					self.post_match()
					
			elif how == 'focusout':
				print "Focus Out: get rid of Match"
				self.matchVar.set('')
			return True
		try:
			val = self.widget.get()
		except:
			print "For some reason we're here without a widget:", self
			return True
			
		#-- bad character?
		for c in self.exclude_chars:
			if what.find(c) + 1:		# 0 and above: found
				print "Bad: found ", c
				self.widget.bell()
				return False
			
		self.parent.changed = True	
		#--are we new?   If so, blank what's there, update the color, and replace with any addition
		print "self.new:", self.new
		self.match_text = ''
		r_code = True	# from here on out, keep track of conditions that require an ultimate failure..
		if self.new:
			print "why:", why
			if why == '1':
				would = what
				print "would is what", what
			else:
				would = ''
			#self.widget.configure(fg='#000')
			self.nameVar.set(would)
			fg='#000'	# black
			#self.widget.configure(fg=fg)
			self.widget.configure(fg=fg, validate=self.validate, validatecommand=self.validatecommand )
			self.new = False
			r_code = False		# Reject the character - we've already set it in, above
			
		print "Would is:", would
		#-- zero length?  
		if  len(would) == 0:
			set_status(self, ok = False)
			print "Bad-==========-Zero length"
			self.match_text = ''
			self.post_match()
			return r_code
		
		#-- match?	set up a lambda function - lower the string to ignore, just return it, otherwise.
		if self.ignore_case:
			f = lambda x: x.lower()
		else:
			f = lambda x: x
			
		# Check for a match so far on any string - if so, just display 
		# it - if an exact match - flag as  Bad
		self.match_text = ''
		good = True
		for item in self.exclude_list:
			if f(item).find(f(would)) == 0:		# matches at the start
				if f(item) == f(would):
					print "BAD:  matches", item
					self.match_text = item
					self.match_color = '#f11'
					good = False
					break
				else:
					print "partial match:", item,  '/', would
					self.match_color = '#666'
					self.match_text += item + '\n'
		#
		# Post the status and the matching text, if any
		set_status(self, good)			
		self.post_match()
		return r_code	
			
	def post_match(self):
		"""
		Update the match text when refocused, or
		after handling validation
		"""
		self.match.configure(fg=self.match_color)
		self.matchVar.set(self.match_text)
		self.match.lift(aboveThis=None)
				
	def return_value(self):
		"""
		What it says: return the value of the Entry widget
		"""
		return(self.nameVar.get(), self.ok)
	
class Text_row():
	"""
	A class for a text row in an edit panel.    Very simple
	"""
	def __init__(self, parent, text, member):
		"""
		Set up the default values for the row object
		"""
		self.parent = parent
		self.text = text
		self.member = member
		self.content = ""
		
		self.row = parent.row		# parent keeps track of row / column
		parent.row += 1				# move the  parent row down one...
		self.column = parent.column
		
	def post(self):
		"""
		Just post the text...
		"""
		
		# write the base label...
		self.label = tk.Label(self.parent.page_frame, text=self.text+":", justify=tk.RIGHT)
		self.label.grid(row=self.row,column=self.column, sticky=tk.E)
		
		# need a "sub-frame" to hold the desc. and scroll bar.
		self.subframe = tk.LabelFrame(self.parent.page_frame, relief=tk.GROOVE)
		self.subframe.grid(row=self.row, column=self.column+2, columnspan=3, sticky=tk.W)
		
		self.widget = tk.Text(self.subframe, height=25, width=80, padx=5, pady=5, relief=tk.GROOVE, wrap=tk.WORD, undo=True)
		self.widget.grid(row=0, column=0, sticky=tk.W)
		self.widget.insert('1.0', self.content)
		# vertical scroll bar...
		self.scrollY = tk.Scrollbar(self.subframe, orient=tk.VERTICAL, command=self.widget.yview)
		self.scrollY.grid(row=0, column=1, sticky=tk.N+tk.S)
		self.widget.configure(yscrollcommand=self.scrollY.set)
		
	def return_value(self):
		"""
		Just return the text.
		"""
		return(self.widget.get('1.0', 'end'), True)
	
	def set(self):
		print "No 'set()' method for Text obj"
		return()
	
class Menu_row():
	"""
	Just put up an OptionMenu from the provided list..)
	"""
	
	def __init__(self, parent, text, member):
		
		self.parent = parent
		self.text = text
		self.member = member
		
		self.default = None
		self.label = None				# have we been here before
		self.titles = ('no-titles',)
		self.new = parent.new
		self.ok = not self.new		
		self.row = parent.row
		self.column = parent.column
		self.handler = self.handle_menu
		parent.row += 1	
		
	def post(self):
		print "Welcome menu-post"
		
		if self.default is None:
			self.default = self.titles[0]	# use the first as a default...
		
		if self.label is None:
		# write the base label...
			self.label = tk.Label(self.parent.page_frame, text=self.text+":", justify=tk.RIGHT)
			self.label.grid(row=self.row,column=self.column, sticky=tk.E)

			self.gOpt = tk.StringVar()
		else:
			self.widget.destroy()
			
		self.gOpt.set(self.default)

		self.widget = tk.OptionMenu(self.parent.page_frame, self.gOpt, *self.titles, command=self.handler)

		self.widget.grid(column=self.column+2, row=self.row,  columnspan=3,sticky=tk.W)
		
		self.statusVar = tk.StringVar()
		self.status = tk.Label(self.parent.page_frame, textvariable=self.statusVar)
		self.status.grid(row=self.row, column=self.column + 1)
		if self.new:
			set_status(self,None)
		else:
			set_status(self,ok=True)
	
		
	def handle_menu(self, value):
		#new_name = self.gOpt.get()		# not needed here, name is what we want.
		
		# if the menu item starts with a "-", it is an unacceptable value
		set_status(self, value[0] != '-')
		self.parent.changed = True	
		
		#time.sleep(4)
		self.parent.read_page()
		if self.member == 'song':
			# Special case for a song:  reload the part list..
			self.parent.obj.song = value
			try:
				group = self.parent.obj.group_obj
			except Exception as e:
				print "------- No such group found as part of", self.parent.obj.value
				print "---- fix  - for now, returning"
				return
			
			song_obj = group.find_song_title(value)
			if song_obj == None:
				print "No such song object found for:", value
				
			# build a part list...
			self.parent.song_obj = song_obj
			self.parent.obj.part = 'All'			# if a new song, use default part for now...
			self.parent.part_obj.titles = self.parent.build_part_list()
			
			self.parent.part_obj.post()
			
			#for i in song_obj.
			
			#self.post()
		else:
			print "Not a song........................."
		#self.parent.refresh()
		
	def return_value(self):
		"""
		Return the OptionMenu value...
		"""
		value = self.gOpt.get()
	
		# if there's a dictionary - do a lookup...
		try:
			value = self.dict[value]
		except:
			pass
		return(value, self.ok)
	def set(self, value):
		self.value = value
		self.ok = True
		self.post()
		
class Graphic_row():
	"""
	Post a row with a title and a graphic...
	and something to let us deal with it ("Change" button?)
	"""
	def __init__(self, parent, text, member, graphic_path):
		self.parent = parent
		self.text = text
		self.member = member
		self.graphic_path = graphic_path
		
		self.label = None			# have we been here...
		self.new = parent.new
		self.ok = not self.new		
		self.row = parent.row
		self.column = parent.column
		self.handler = self.button_handler
		
		self.parent.row += 2		# this one takes up 2 rows
		
	def post(self):
		"""
		put the text and graphic on the screen...
		
		also post the "button")
		"""
		
		print "Graphic post"
		if self.label is None:
		# write the base label...
			self.frame = self.parent.page_frame
			self.label = tk.Label(self.frame, text=self.text+":", justify=tk.RIGHT)
			self.label.grid(row=self.row,column=self.column, sticky=tk.E)

			self.gOpt = tk.StringVar()
			
			self.changeButton = tk.Button(self.parent.page_frame, text="Change " + self.text, command=self.button_handler).grid(column=self.column + 2, row=self.row + 1, sticky=tk.W )
			
			self.statusVar = tk.StringVar()
			self.status = tk.Label(self.parent.page_frame, textvariable=self.statusVar)
			self.status.grid(row=self.row, column=self.column + 1)
			
		else:
			try:
				self.widget.graphic.destroy()
			except:
				print "Widget.graphic.destroy failed."
				pass
		
		self.widget = cltkutils.graphic_element(self.frame)
		self.widget.filepath = self.graphic_path
		self.widget.row = self.row
		self.widget.column = self.column + 2
		self.widget.columnspan = 3
		self.widget.sticky = tk.W
		self.widget.post()	
		
		if self.new:
			set_status(self,None)
			self.new = False
		else:
			set_status(self,True)
	
	def set(self, value):
		self.value = value
		self.new = False
		set_status(self,ok=True)
		self.post()
	

				
	def button_handler(self):
		print "this is the button handler"
			
	def return_value(self):
		return("SomeScreenSht"), self.ok
	
class Graphic_row_screenshot(Graphic_row):
	"""
	Derived class - a button handler specific to the screenshot
	"""
	def button_handler(self):
		print "this is the button handler"
		self.parent.changed = True
		self.parent.needs_rebuild = True
		initialPath = "/Users/Johnny/Desktop"
		file_path = tkFileDialog.askopenfilename(initialdir=initialPath, defaultextension='.png', title="Open screen shot...")
		if not file_path:
			return
		
		self.ok = True
		set_status(self, True)
		filename = os.path.split(file_path)[1]
		
		subdir = os.path.join('coLab_local', filename)
		self.parent.obj.screenshot = subdir
		dest = os.path.join(self.parent.obj.home, subdir)
						
		try:
			shutil.copy(file_path, dest)
		except Exception as e:
			print "Failure copying", file_path, "to", dest
			raise Exception
		self.graphic_path = dest
		#
		# Kludge alert - let's find a better way to do this...
		try:
			open = '/usr/bin/open'		#os.path.join(self.parent.obj.coLab_home, 'Code', 'PhotoShopElements.scpt')
			options = '-a ' + dest
			subprocess.call([open, '-a', 'Preview.app', dest])
		except Exception as e:
			print "Ooops - Exception", e, sys.exc_info()[0]
			sys.exit(1)
			
		#message = 'Please crop the graphic and save in place.'
		#tkMessageBox.showinfo("Crop IT!", message, parent=self.parent.page_frame, icon=tkMessageBox.ERROR)
		# 
		# Let's create the various bits...
		imagemaker.make_sub_images(self.parent.obj)
		#self.post()
		
		if tkMessageBox.askyesno('Select Limits',"Do you need to set the left and right limits?", icon=tkMessageBox.QUESTION):
			# Now - post the display sized object to let us enter the xStart, xEnd
			image_file = os.path.join(self.parent.obj.home, self.parent.obj.graphic)
			image = Image.open(image_file)
			image.show()
			
		self.parent.post_member('screenshot')

			
	def return_value(self):
		return(self.parent.obj.screenshot, self.ok)	# I know, a bit redundant...
	
	def sound_button(self):
		"""
		Put up a second button to allow using the sound graphic.
		"""
		self.changeButton = tk.Button(self.parent.page_frame, text="Use Sound Graphic", command=self.button2_handler).grid(column=self.column + 3, row=self.row + 1, sticky=tk.W )
		
	def button2_handler(self):
		"""
		Just use the sound graphic...
		"""
		self.parent.changed = True
		self.parent.needs_rebuild = True
		self.parent.obj.screenshot = self.parent.obj.soundgraphic
		self.parent.set_member('xStart', 30)	#   RBF:  these need to be set elsewhere...
		self.parent.set_member('xEnd', 630)
		self.parent.set_member('screenshot', self.parent.obj.soundgraphic)
		imagemaker.make_sub_images(self.parent.obj)
		self.graphic_path =  os.path.join(self.parent.obj.home, self.parent.obj.soundthumbnail)
		self.parent.post_member('screenshot')
		
class Graphic_row_soundfile(Graphic_row):
	"""
	Derived class - a button handler specific to the soundfile
	"""
	def button_handler(self):
		print "this is the sound file button handler"
		self.parent.changed = True
		self.parent.needs_rebuild = True	
		initialPath = "/Volumes/iMac 2TB/Music/"
		file_path = tkFileDialog.askopenfilename(initialdir=initialPath, defaultextension='.aif', title="Open AIFF sound file...")
		if not file_path:
			return
		
		self.ok = True
		set_status(self, True)
		filename = os.path.split(file_path)[1]
		
		subdir = os.path.join('coLab_local', filename)
		self.parent.obj.soundfile = subdir
		sound_dest = os.path.join(self.parent.obj.home, subdir)
						
		try:
			shutil.copy(file_path, sound_dest)
		except Exception as e:
			print "Failure copying", file_path, "to", sound_dest
			raise Exception
		
		#self.parent.obj.duration = str(clAudio.get_audio_len(sound_dest))
		self.parent.set_member('duration', str(clAudio.get_audio_len(sound_dest)))
		#self.parent.duration_obj.nameVar.set(self.parent.obj.duration)
		
		img_dest = os.path.join(self.parent.obj.home, self.parent.obj.soundgraphic)
		#make_sound_image(self.parent.obj, sound_dest, img_dest)
		self.graphic_path =  os.path.join(self.parent.obj.home, self.parent.obj.soundthumbnail)
		page_thread=threading.Thread(target=make_sound_image, args=(self.parent, sound_dest, img_dest))
		page_thread.start()
		#rebuild_page_edit(self)

	def return_value(self):
		return(self.parent.obj.soundfile, self.ok)	# I know, a bit redundant...
	
def make_sound_image(page_edit, sound, image):
	print "Creating image...", image
	pageTop = tk.Toplevel()
	#pageTop.transient(page_edit)
	page_frame = tk.LabelFrame(master=pageTop, relief=tk.GROOVE, text="New Page Generation" , borderwidth=5)
	page_frame.lift(aboveThis=None)
	page_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
	
	f1 = tk.Frame(page_frame)
	f1.grid(row=0, column=0, sticky=tk.W)
	
	img_gen_progbar = Progress_bar(f1, 'Image Generation')
	img_gen_progbar.what = 'Line'
	img_gen_progbar.width = 500
	#img_gen_progbar.max = 600		# This needs to be calculated 
	#img_gen_progbar.post()		# initial layout...   called in Sound_image.build()
	
	snd_image = imagemaker.Sound_image(sound, image, img_gen_progbar)
	snd_image.build()	# separate - we may want to change a few things before the build...
	page_edit.obj.soundthumbnail = "SoundGraphic_tn.png"
	
	imagemaker.make_sub_images(page_edit.obj)
	page_edit.post_member('soundfile')
	pageTop.destroy()
		
class Page_edit_screen():
	"""
	A way of posting a screen that lets us enter
	or edit the variables associated with a page class.
	
	The new var if set to True allows the name to be set and
	populates the entry fields with temp strings that clear
	once a character is typed.
	
	Passed the parent structure of the entire session, works from
	the current group
	"""
	def __init__(self, parent, page, new=False):
		print "hello"
		if parent.edit_lock:
			print "locked"  # (obviously more, later)
			return
		#parent.edit_lock = True
		#new = False
		print "PES: new:",new
		self.parent = parent
		
		self.row=0
		self.column=0
		self.obj = page		# the object we're editing
		self.new = new
		self.ok = not new
		self.page_frame = None
		self.song_obj = None
		self.changed = False
		self.needs_rebuild = False
		
		page.page_type = 'html5'		# new pages use this..
		
		self.setup()
				
	def setup(self):		# RBF: at least check to see if we ever call  this - I'm guessing now...
		
		print "-----------Setup called!"
		if self.page_frame is not None:
			print "---------------Destroy All Page Frames...---------"
			self.page_frame.destroy()
	
		# Set up a dictionary listing the row objects, etc. that have the 
		# info we need.  By indexing by the "member" name - we can find the mas 
		# needed - or step through the whole list.
		self.editlist = dict()		
		if self.new:
			self.pageTop = tk.Toplevel()
			self.pageTop.transient(self.parent)
			self.page_frame = tk.LabelFrame(master=self.pageTop, relief=tk.GROOVE, text="New Page (Group: " + self.parent.current_groupname + ')', borderwidth=5)
			self.page_frame.lift(aboveThis=None)
			self.page_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
			
			# we first open, it it's new, with a simple window for the name...
			
			
			# get a little tricky - since we don't know the name yet - set a temp far in the 
			# page:  sub_dir so that we can pass this, plus the final name, to set_paths...
			self.obj.sub_dir = os.path.join('Group', self.parent.current_groupname, 'Page', )
			clclasses.set_paths(self.obj, self.obj.sub_dir)
			#================
			# Build page editor
			#================
			#
			# Build a list of basically name/value pairs
			# Each pair (e.g., title and entry widget), is added to a list, 
			# on "save" we retrieve each
			
			#---- name - this is a file name so we need to be somewhat strict about characters
			
			# gather the names of all the pages to exclude (dir name)
			row = Entry_row(self, "Name", "name", width=20)
			# build the list of excluded names: the existing page list of the parent group...
			print "PES: obj, group", self.obj.name, self.obj.group_obj.name
			for nextpage in self.obj.group_obj.pagelist:
				row.exclude_list.append(nextpage.name)
			row.exclude_chars=' "/:'	# characters we don't want in file names...
			row.ignore_case = True
			row.new = self.new				# as passed in
			row.editable = self.new		# don't edit a file name that's already been created...
			row.post()
			# cheat a little through u up quick descriptive label
			# later...  columnspan 2
			
			self.editlist[row.member] =  row 		# just process this one item...
			
			self.row = 8		# push these buttons down out of the way...
			self.saveButton = tk.Button(self.page_frame, text="Save", command=self.save_page).grid(column=3, row=self.row)	# add  command=
			self.quitButton = tk.Button(self.page_frame, text="Quit", command=self.my_quit).grid(column=4, row=self.row)
			
			# stop and wait for the above window to return...
			self.pageTop.wait_window(self.page_frame)
			
			if not self.ok:
				return()
		#
		# Basically start over - this time with the name preset...
		#time.sleep(1)		# Seems to be necessary for the window to die (is there a call for this?)
		self.pageTop = tk.Toplevel()
		self.pageTop.transient(self.parent)
		self.row=0
		self.column=0
		self.page_frame = tk.LabelFrame(master=self.pageTop, relief=tk.GROOVE, text=self.obj.name + " (Group: " + self.parent.current_groupname + ')', bd=100, padx=10, pady=10, borderwidth=5)
		self.page_frame.lift(aboveThis=None)
		self.page_frame.grid(ipadx=10, ipady=10, padx=15, pady=15)
		
		#---- Descriptive title, "unique", but flexible with case, spaces, etc...
		row = Entry_row(self, "Descriptive title", "desc_title", width=30)
		# exclude existing titles...
		for nextpage in self.obj.group_obj.pagelist:
			row.exclude_list.append(nextpage.desc_title)
		self.editlist[row.member] =  row
		row.post()
		
		#---- Fun title - just for fun...
		
		row = Entry_row(self, "Fun title", "fun_title", width=50)
		self.editlist[row.member] =  row
		row.post()
		
		#---- Description: text object
		row = Text_row(self, "Description", "description")
		self.editlist[row.member] =  row
		row.content = self.obj.description
		row.post()
		
		#---- Sound file...
		# 
		# is there such a file?
		screenshot_path = os.path.join(self.obj.home, self.obj.soundthumbnail)
		if not os.path.isfile(screenshot_path):		# we need a backup file...
			screenshot_path = os.path.join(self.obj.coLab_home, 'Resources', 'coLab-NoPageImage_tn.png')
			
		row = Graphic_row_soundfile(self, "Soundfile", 'soundfile', screenshot_path)
		self.editlist[row.member] =  row
		row.post()
		
		
		#---- Duration - display only ...
		row = Entry_row(self, "Duration", "duration", width=8)
		row.editable = False
		self.editlist[row.member] =  row
		row.post()
		self.duration_obj = row
		
		
		#---- Screen Shot
		# (for now, the name - later: the picture (thumbnail)
		try:	
			screenshot_path = os.path.join(self.obj.home, self.obj.thumbnail)
		except:				# in case something's not preset - we'll catch it in the test...
			pass
		if not os.path.isfile(screenshot_path):
			screenshot_path = os.path.join(self.obj.coLab_home, 'Resources', 'coLab-NoPageImage_tn.png')
			
		row = Graphic_row_screenshot(self, "Graphic", 'screenshot', screenshot_path)
		self.editlist[row.member] =  row
		row.post()
		row.sound_button()
		
		#----  x Start and Stop - eventually done with graphic input...
		row = Entry_row(self, "xStart", "xStart", width=5)
		self.editlist[row.member] =  row
		row.post()
		
		row = Entry_row(self, "xEnd", "xEnd", width=5)
		self.editlist[row.member] =  row
		row.post()
		
		#"""
		#----   fps: should be calculated...
		row = Entry_row(self, "fps", "fps", width=5)
		self.editlist[row.member] =  row
		row.editable = False
		row.post()
		#"""
		
		#--- Song

		#self.obj.song_obj = None
		menu = Menu_row(self, "Songs", "song")
		l = []		# list of song titles (desc_title)
		d = {}		# dictionary to convert desc_title to name
		if self.new:
			l = ['-select song-']		# build a list of song names...
		for i in self.obj.group_obj.songlist:
			l.append(i.desc_title)
			d[i.desc_title] = i.name
			if i.name == self.obj.song:
				self.song_obj = i		# remember this object
		l.append('-New song-')
			
		menu.titles = tuple (l)		# Convert to a tuple...
		
		try:
			menu.default = self.obj.song_obj.desc_title
		except:
			pass
		self.editlist[menu.member] =  menu
		menu.dict = d
		menu.post()
			
		#  Part - depends on the song selected.
		print "part time..."
		menu = Menu_row(self, "Part", "part")
		self.part_obj = menu		# save this for song changes (implying a new part list)
		menu.titles = self.build_part_list()
		self.editlist[menu.member] =  menu
		menu.dict = self.part_lookup
		
		menu.post()
		
		#"""
		self.saveButton = tk.Button(self.page_frame, text="Save", command=self.save_page).grid(column=3, row=self.row)	# add  command=
		self.quitButton = tk.Button(self.page_frame, text="Quit", command=self.my_quit).grid(column=4, row=self.row)
		
		
	def refresh(self):
		for i in self.editlist:
			self.editlist[i].post()
	
	def get_member(self, member):
		try:
			return(self.editlist[member])
		except Exception as e:
			print "Initialization Failed", sys.exc_info()[0], e
			print "member is:", member
			raise SystemError
				
	def set_member(self, member, value):
		"""
		use the editlist to set a specific value.		
		"""
		self.get_member(member).set(value)
			
		
	def post_member(self, member):
		"""
		Post the specified member...
		"""
		self.get_member(member).post()

			
	def build_part_list(self):
		"""
		Use the song object to build the part list
		and conversion dictionary (Long names are
		displayed, simple names are stored.)
		
		Returns a tuple ready to be assigned to an ObjectMenu..
		"""
		if self.song_obj is None:
			part_name_list = [ 'All' ]
			part_dict = { 'All': 'All' }	# build the one common part
		else:
			part_name_list = self.song_obj.partlist
			part_dict = self.song_obj.partname_dict		# convert short names to long
		
		# RBF:  Check: I think the whole / partname thing can reduce to the partname (can html # tags have spaces?)
		self.part_obj.default = part_dict[self.obj.part]
		l = []
		self.part_lookup = dict()
		for i in part_name_list:
			l.append(part_dict[i])
			self.part_lookup[part_dict[i]] = i
		return(tuple(l))
		
	def read_page(self):
		"""
		Read the current state of the edit list into the 
		object.
		"""
		print "Reading into obj.."
		self.ok = True		# until we hear otherwise...
		self.bad_list = []	# Keep trck of the names that are not set well..
		for item in self.editlist:
			row_obj = self.editlist[item]
			print "item.member:", row_obj.member
			(value, ok) = row_obj.return_value()
			if not ok:
				self.ok = ok
				self.bad_list.append(row_obj.text)
			
			# may not want to do this - but it likely doesn't matter as we 
			# will either correct it, or toss it.
			string = "self.obj." + item + ' = """' + str(value) + '"""'
			print "exec string:", string
			exec(string)
		
	def save_page(self):
		print
		print "------------------"
		print "Dump of page", self.obj.name
		self.read_page()
		print "Dump----------------"	
		#print self.obj.dump()
		print'---first home'
		try:
			sub_dir = os.path.join(self.obj.coLab_home, 'Group', self.obj.group, 'Page',  self.obj.name)
		except Exception as e:
			print "Cannot build new page subdir", e, sys.exc_info()[0]
			sys.exit(1)
	
		clclasses.set_paths(self.obj, sub_dir)		# Paths are now correct...
		print self.obj.home
		if not self.ok:
			print "Still something wrong - see above"
			message = "There were problems with the following fields:\n\n"
			spacer=' '
			for i in self.bad_list:
				message += spacer + i
				spacer = ', '
			message += '.\n\nPlease correct.'
			tkMessageBox.showerror("There were problems...", message, parent=self.page_frame, icon=tkMessageBox.ERROR)
			return
		
		else:
			if float(self.obj.duration) == 0.0:
				type = 'create'
			else:
				type = 'update'
			message = "This will " + type + " the page: " + self.obj.name
			message += "\n\nOK?"
			if not tkMessageBox.askquestion('OK to save?', message, parent=self.page_frame, icon=tkMessageBox.QUESTION):
				print "return"
	
	
			if type == 'create':
				# need to add this bit to the group's lists
				self.obj.group_obj.pagelist.append(self.obj)		# add the page name
				self.obj.group_obj.pagedict[self.obj.name] = self.obj	# name -> page obj
				self.obj.create()				# build the page dir structure, base data page.
				self.pageTop.destroy()
				return							# just create the dir and 1-entry data file - we only have the name so far
						
			# We're good - let's post this...
			clclasses.convert_vars(self.obj)
			self.obj.post()
			page_thread=threading.Thread(target=rebuild_page_edit, args=(self,))
			page_thread.start()
			#rebuild_page_edit(self)
			
			self.pageTop.destroy()
			
	def my_quit(self):
		if self.changed:
			message = "You've made changes, quiting now will lose them.\n\nDo you still want to quit?"
			if not tkMessageBox.askokcancel('OK to quit?', message, parent=self.page_frame, icon=tkMessageBox.QUESTION):
				return
		self.pageTop.destroy()
		

def rebuild_page_edit(obj):
		"""
		This is called as the run method of a thread object.
		The idea is to manage/monitor the creation of the web page
		data, in a distracting and entertaining way...
		
		Yeah, right.
		"""
		pageTop = tk.Toplevel()
		pageTop.transient(obj.parent)
		page_frame = tk.LabelFrame(master=pageTop, relief=tk.GROOVE, text="New Page Generation" , borderwidth=5)
		page_frame.lift(aboveThis=None)
		page_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
		#
		
		fps = imagemaker.calculate_fps(obj.obj)
		frames = int(float(obj.obj.duration) * fps) + 1
		if obj.needs_rebuild:
			f1 = tk.Frame(page_frame)
			f1.grid(row=0, column=0, sticky=tk.W)
			
			img_gen_progbar = Progress_bar(f1, 'Image Generation', max=frames)
			img_gen_progbar.what = 'Image'
			img_gen_progbar.width = 500
			img_gen_progbar.max = frames
			img_gen_progbar.post()		# initial layout...
			
			f2 = tk.Frame(page_frame)
			f2.grid(row=1, column=0, sticky=tk.W)
			
			vid_gen_progbar = Progress_bar(f2, 'Video Generation', max=frames)
			vid_gen_progbar.what = 'Frame'
			vid_gen_progbar.width = 500
			vid_gen_progbar.max = frames
			vid_gen_progbar.post()
		 
		 	
		f3 = tk.Frame(page_frame)
		f3.grid(row=2, column=0, sticky=tk.W)
		ftp_progbar = Progress_bar(f3, 'ftp mirror...')
		ftp_progbar.width = 500
		ftp_progbar.mode = 'indeterminate'
		ftp_progbar.post()
		
		f4 = tk.Frame(page_frame)
		f4.grid(row=3, column=0, sticky=tk.E)
		quitButton = tk.Button(f4, text="Quit", command=pageTop.quit)
		quitButton.grid()
		
		
		if obj.needs_rebuild:	
			imagemaker.make_images(obj.obj, img_gen_progbar)
			img_gen_progbar.progBar.stop()
			clAudio.make_movie(obj.obj, vid_gen_progbar)
		ftp_progbar.progBar.start()
		rebuild.rebuild(obj.obj.group_obj)		# currently the group name - change to the object...
		ftp_progbar.progBar.stop()
				
		pageTop.destroy()


		
def create_new_page(parent):
	"""
	Does the initial setup to call the edit screen and leaves.
	The rest is done there.
	"""
	
	print "New page"
	group_name = parent.current_groupname		# currently selected group
	this_group = parent.current_group
	print "My group is:", group_name, this_group.title
	
	print "Group info:", this_group.subtitle
	
	new_page = clclasses.Page(None)
	new_page.group_obj = this_group
	new_page.group = this_group.name
	new_page.coLab_home = this_group.coLab_home		# just enough path to get us stared...
	
	parent.page = Page_edit_screen(parent, new_page, new=True)
	
	
	
def edit_page(parent):
	print "edit Page"
	pagename='TestPage'
	pagename="NolaShort"
	#pagename="WaterMoonTomBass"
	#pagename="N-Drone"
	#pagename="JDJ-2-Jan2013"
	
	new_page = clclasses.Page(pagename)
	new_page.group_obj = parent.current_group
	new_page.group = parent.current_group.name
	
	
	# for now - build the path ...
	pagehome = os.path.join(parent.current_group.home, 'Page', pagename)
	new_page.home = pagehome
	new_page.load()
	
	new_page.song_obj = new_page.group_obj.find_song(new_page.song)
	
	parent.page = Page_edit_screen(parent, new_page, new=False)
def create_new_song(parent):
	print "new song"
def edit_song(parent):
	print "edit song"
	
	
#------ interface to main routine...
import coLab
def main():
	print "Colab Main"
	w=coLab.Colab()
	
if __name__ == '__main__':
	main()