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

import config
import clclasses
import cltkutils
import clSchedule
import imagemaker
import clAudio
import rebuild
import htmlgen

class Data_row:
	"""
	Base class for the various rows that gather data.  
	Basic layout is a row that has the name, a status cell,
	and some kind of a gadget that presents/gathers data.
	"""
	def __init__(self, parent, text, member):
		"""
		Set up the default values common to all rows...
		"""
		self.parent = parent
		self.text = text
		self.member = member
		# Basic row / cell management
		self.row = parent.row		# parent keeps track of row / column
		parent.row += 1				# move the  parent row down one...
		self.column = parent.column
		# initialization come to some / most / all
		self.label = None
		self.new = parent.new		# when true, items are ghosted / replaced on first key  
		self.ok = not self.new		# new items are assumed to be not good yet, and vice-versa
		
		self.content = ""
	
	def set(self, value):
		self.value = value
		self.new = False
		self.set_status(self.ok)
		self.post()
		
	def set_status(self, ok = None):
		"""
		Set the status of the widget - log the state, and update
		the status column, should work for most/all row classes...
		"""
		self.ok = ok
		if ok is None:
			color = '#a73'
			txt = ' - '
		if ok:
			color = '#2f2'	# bright green
			txt = 'OK'
		else:
			color = '#f11'	# bright red
			txt = ' X '
			
		self.status.configure(foreground=color)
		self.statusVar.set(txt)
	

			
class Entry_row(Data_row):
	"""
	A class for an entry row in an edit panel.  Holds the info specific to
	a row - implements posting the Text and the value in an entry field.
	Allows for "new" and "editable" fields (non-editable are displayed as
	labels).   Also handles validation based on the values put into the 
	class. Also marks the status and matching fields.
	"""
	def __init__(self, parent, text, member, width=15):
		Data_row.__init__(self, parent, text, member)
		
		self.width = width
		
		self.label = None				# have we been here before
		self.exclude_list = []		# a list of items not allowed (e.g., current file names)
		self.exclude_chars = '"'	# current implementation does not allow " n stored strings
		self.ignore_case = False	# Set to true for file names, etc.
		self.match = None	
		self.match_text = ''		# used to recall the last bad match (equiv. file name, e.g.)	
		self.match_color = '#666'
		#self.new = parent.new		# when true, items are ghosted / replaced on first key  
		self.editable = True		# occasionally we get one (existing file name) that we don't want to edit...
		
		
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
			self.label = ttk.Label(self.parent.edit_frame, text=self.text+":", justify=tk.RIGHT)
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
			self.status = ttk.Label(self.parent.edit_frame, textvariable=self.statusVar)
			self.status.grid(row=self.row, column=self.column + 1)
			if self.new:
				self.set_status(None)
			else:
				self.set_status(ok=True)
		else:
			self.widget.destroy()
		
		# if not editable - just display as a label...
		print "vobj - editable:", self.editable
		if not self.editable:
			self.widget = ttk.Label(self.parent.edit_frame, textvariable=self.nameVar, justify=tk.LEFT)
			self.widget.grid(row=self.row,column=self.column + 2, columnspan=3, sticky=tk.W)
			self.nameVar.set(self.value)
			#self.ok = True		# since we can't change it - it's good
			self.set_status(ok=True)
			print "non-edit _obj:", self.widget
		else:
			
			print "Ev_init: callback is:", self.callback
			# Build a list: the call back registery and the subcodes, 
			# then turn the list into a tuple to pass in...
			l = [ self.parent.edit_frame.register(self.callback) ]		# first part is the registration of the call back.
			#widget.destroy()
			for sc in self.subcodes:
				l.append(sc)
			self.validatecommand = tuple(l)	# make into a tuple
			print "vcmd ", self.validatecommand, "validate:", self.validate
			# set colors for edit (Black) and new (lt. gray) objects
			fg = '#000'		# black
			if self.new:
				fg = '#AAA'	# light gray
			
			self.widget = ttk.Entry(self.parent.edit_frame, textvariable=self.nameVar, width=self.width, foreground=fg,background='#e9e9e9', validate=self.validate, validatecommand=self.validatecommand )
			print "v-obj widget created:", self.widget
			self.widget.grid(row=self.row, column=self.column + 2, sticky=tk.W)
			self.nameVar.set(self.value)
						
			self.matchVar = tk.StringVar()
			self.match = tk.Label(self.parent.edit_frame, textvariable=self.matchVar, justify=tk.LEFT)
			self.match.grid(row=self.row, column=self.column + 3, rowspan=6, columnspan=2, sticky=tk.NW)		
	

		
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
			self.widget.configure(foreground=fg, validate=self.validate, validatecommand=self.validatecommand )
			self.new = False
			r_code = False		# Reject the character - we've already set it in, above
			
		print "Would is:", would
		#-- zero length?  
		if  len(would) == 0:
			self.set_status(ok = False)
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
					self.match_text += item + '\n'
					self.match_color = '#f11'
					good = False
					#break
				else:
					print "partial match:", item,  '/', would
					self.match_color = '#666'
					self.match_text += item + '\n'
		#
		# Post the status and the matching text, if any
		self.set_status(good)			
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
	
	def set(self, value):
		self.value = value
		self.new = False
		self.set_status(True)
		self.post()
		
class Text_row(Data_row):
	"""
	A class for a text row in an edit panel.    Very simple
	"""
	def post(self):
		"""
		Just post the text...
		"""
		
		# write the base label...
		self.label = tk.Label(self.parent.edit_frame, text=self.text+":", justify=tk.RIGHT)
		self.label.grid(row=self.row,column=self.column, sticky=tk.E)
		
		# need a "sub-frame" to hold the desc. and scroll bar.
		self.subframe = tk.LabelFrame(self.parent.edit_frame, relief=tk.GROOVE)
		self.subframe.grid(row=self.row, column=self.column+2, columnspan=3, sticky=tk.W)
		
		self.widget = tk.Text(self.subframe, height=15, width=80, padx=5, pady=5, relief=tk.GROOVE, wrap=tk.WORD,bg='#ffffff', undo=True)
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
	
	
class Menu_row(Data_row):
	"""
	Just put up an OptionMenu from the provided list..)
	"""
	
	def __init__(self, parent, text, member):
		Data_row.__init__(self, parent, text, member)
		
		self.default = None
		self.titles = ('no-titles',)
		self.handler = self.handle_menu
		
	def post(self):
		print "Welcome menu-post"
		
		if self.default is None:
			self.default = self.titles[0]	# use the first as a default...
		
		if self.label is None:
		# write the base label...
			self.label = tk.Label(self.parent.edit_frame, text=self.text+":", justify=tk.RIGHT)
			self.label.grid(row=self.row,column=self.column, sticky=tk.E)

			self.gOpt = tk.StringVar()
		else:
			self.widget.destroy()
			
		self.gOpt.set(self.default)

		self.widget = tk.OptionMenu(self.parent.edit_frame, self.gOpt, *self.titles, command=self.handler)

		self.widget.grid(column=self.column+2, row=self.row,  columnspan=3,sticky=tk.W)
		
		self.statusVar = tk.StringVar()
		self.status = tk.Label(self.parent.edit_frame, textvariable=self.statusVar)
		self.status.grid(row=self.row, column=self.column + 1)
		if self.new:
			self.set_status(None)
		else:
			self.set_status(ok=True)
	
		
	def handle_menu(self, value):
		#new_name = self.gOpt.get()		# not needed here, name is what we want.
		
		# if the menu item starts with a "-", it is an unacceptable value
		self.set_status( value[0] != '-')
		self.parent.changed = True	
		
		#time.sleep(4)
		self.parent.read()
	
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

class Resolution_menu_row(Menu_row):
	def handle_menu(self, value):
		"""
		Reset the parent's size vars...
		"""
		self.parent.size = self.parent.size_class.sizeof(self.dict[value])	
	
class Song_menu_row(Menu_row):
	"""
	Derivative class - separate handler...
	"""
	def handle_menu(self, value):
		
		# if the menu item starts with a "-", it is an unacceptable value
		self.set_status(ok=value[0] != '-')
		self.parent.changed = True	
		
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
		
		# Special case a song with only the default part as "OK"
		print "testing the partlist..."
		if song_obj.partlist == [ 'All'	]:
			print "Partlist is just 'all'"
			self.set_status(ok=True)
			#time.sleep(2)
		# set the new dictiony in place...
		self.parent.part_obj.dict = self.parent.part_lookup
		self.parent.part_obj.post()
		self.parent.read()
		
class Graphic_row(Data_row):
	"""
	Post a row with a title and a graphic...
	and something to let us deal with it ("Change" button?)
	"""
	def __init__(self, parent, text, member, graphic_path):
		Data_row.__init__(self, parent, text, member)

		self.graphic_path = graphic_path
		
		self.handler = self.button_handler
		
		self.parent.row += 1		# this one takes up 2 rows, one more than most
		
	def post(self):
		"""
		put the text and graphic on the screen...
		
		also post the "button")
		"""
		
		print "Graphic post"
		if self.label is None:
		# write the base label...
			self.frame = self.parent.edit_frame
			self.label = tk.Label(self.frame, text=self.text+":", justify=tk.RIGHT)
			self.label.grid(row=self.row,column=self.column, sticky=tk.E)

			self.gOpt = tk.StringVar()
			
			self.changeButton = ttk.Button(self.parent.edit_frame, text="Change " + self.text, command=self.button_handler).grid(column=self.column + 2, row=self.row + 1, sticky=tk.W )
			
			self.statusVar = tk.StringVar()
			self.status = tk.Label(self.parent.edit_frame, textvariable=self.statusVar)
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
			self.set_status(None)
			self.new = False
		else:
			self.set_status(True)
	
	def set(self, value):
		self.value = value
		self.new = False
		self.set_status(ok=True)
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
		page = self.parent.obj
		page.changed = True
		page.needs_rebuild = True
		initialPath = "/Users/Johnny/Desktop"
		file_path = tkFileDialog.askopenfilename(initialdir=initialPath, defaultextension='.png', title="Open screen shot...")
		if not file_path:
			return
		
		self.ok = True
		self.set_status( True)
		page.use_soundgraphic = False
		filename = os.path.split(file_path)[1]
		
		subdir = os.path.join('coLab_local', filename)
		page.screenshot = subdir
		dest = os.path.join(page.home, subdir)
						
		try:
			shutil.copy(file_path, dest)
		except Exception as e:
			print "Failure copying", file_path, "to", dest
			raise Exception
		#self.graphic_path = dest
		#
		# use "open" to schedule preview - seems to do what we need....
		try:
			open = '/usr/bin/open'		
			subprocess.call([open, '-W', '-a', 'Preview.app',  dest])
		except Exception as e:
			print "Ooops - Exception", e, sys.exc_info()[0]
			sys.exit(1)
			
		#message = 'Please crop the graphic and save in place.'
		#tkMessageBox.showinfo("Crop IT!", message, parent=self.parent.edit_frame, icon=tkMessageBox.ERROR)
		# 
		# Let's create the various bits...
		imagemaker.make_sub_images(self.parent.obj)
		#self.post()
		
		if tkMessageBox.askyesno('Select Limits',"Do you need to set the left and right limits?", icon=tkMessageBox.QUESTION):
			# Now - post the display sized object to let us enter the xStart, xEnd
			image_file = os.path.join(self.parent.obj.home, self.parent.obj.graphic)
			#image = Image.open(image_file)
			#image.show()
			try:
				open = '/usr/bin/open'	
				subprocess.call([open, '-W', '-a', 'Preview.app', image_file])
			except Exception as e:
				print "Problem opening the image for limits", e, sys.exc_info()[0]
				sys.exit(1)
			
				
			
		#self.parent.post_member('screenshot')
		self.graphic_path = os.path.join(self.parent.obj.home, self.parent.obj.thumbnail)
		self.post()
			
	def return_value(self):
		return(self.parent.obj.screenshot, self.ok)	# I know, a bit redundant...
	
	def sound_button(self):
		"""
		Put up a second button to allow using the sound graphic.
		"""
		self.changeButton = ttk.Button(self.parent.edit_frame, text="Use Sound Graphic", command=self.button2_handler).grid(column=self.column + 3, row=self.row + 1, sticky=tk.W )
	def size_menu(self):
		"""
		Offer up a menu of sizes...
		"""
			
	def button2_handler(self):
		"""
		Just use the sound graphic...
		"""
		page = self.parent.obj
		page.changed = True
		page.needs_rebuild = True
		page.screenshot = page.soundgraphic
		page.use_soundgraphic = True

		self.parent.set_member('xStart', 30)	#   RBF:  these need to be set elsewhere...
		width, height = self.parent.size
		end = width - 10
		self.parent.set_member('xEnd', end)

		self.parent.set_member('screenshot', page.soundgraphic)
		imagemaker.make_sub_images(page)
		self.graphic_path =  os.path.join(page.home, page.soundthumbnail)
		self.parent.post_member('screenshot')
		
class Graphic_row_soundfile(Graphic_row):
	"""
	Derived class - a button handler specific to the soundfile
	"""
	def button_handler(self):
		print "this is the sound file button handler"
		page = self.parent.obj
		page.changed = True
		page.needs_rebuild = True	
		initialPath = "/Volumes/iMac 2TB/Music/"
		file_path = tkFileDialog.askopenfilename(initialdir=initialPath, defaultextension='.aif', title="Open AIFF sound file...")
		if not file_path:
			return
		
		
		self.ok = True
		self.set_status( True)
		filename = os.path.split(file_path)[1]
		popup = cltkutils.Popup("Sound file:" + filename, "Copying...")
		page = self.parent.obj
		
		filepath = os.path.join('coLab_local', filename)
		
		page.soundfile = filepath
		sound_dest = os.path.join(page.home, filepath)
						
		try:
			shutil.copy(file_path, sound_dest)
		except Exception as e:
			print "Failure copying", file_path, "to", sound_dest
			raise Exception
		finally:
			popup.destroy()
		
		page.duration = clAudio.get_audio_len(sound_dest)
		self.parent.set_member('duration', str(page.duration))
		#self.parent.duration_obj.nameVar.set(self.parent.obj.duration)
		
		page.editor = self.parent	# the editor object we're in rigt now...
		#page_thread=threading.Thread(target=rebuild.render_page, args=(page, media_size='Tiny', max_samples_per_pixel=100))
		self.size_save = page.media_size
		page.media_size = 'Tiny'	# for now - probably will define a "Preview" size
		# 
		page_thread=threading.Thread(target=self.render_and_post, args=(page, 'Tiny', 100))
		page_thread.start()
		
		#rebuild.render_page(page, media_size='Tiny', max_samples_per_pixel=100)   # render as a preview...
		"""
		img_dest = os.path.join(self.parent.obj.home, self.parent.obj.soundgraphic)
		#make_sound_image(self.parent.obj, sound_dest, img_dest)
		self.graphic_path =  os.path.join(self.parent.obj.home, self.parent.obj.soundthumbnail)
		max = 100 	# overview -no more than 100 sound frames (samples) per vertical pixel
		page_thread=threading.Thread(target=make_sound_image, args=(self.parent, sound_dest, img_dest, self.parent.size, max))
		page_thread.start()
		#rebuild_page_edit(self)
		"""
	def render_and_post(self, page, media_size, max_samples_per_pixel):
		"""
		A routine to handle the last bit of the rendering - in the background, 
		so we can see it (i.e. so we return to the main loop while building)
		"""
		#rebuild.render_page(page, 'Tiny', 100)	# probably always... but:
		rebuild.render_page(page, media_size, max_samples_per_pixel)
		self.parent.post_member('soundfile')
		page.media_size = self.size_save 	# restore what was saved before we were called.
		if page.use_soundgraphic:
			page.graphic_row.button2_handler()
			page.graphic_row.post()
		
	def return_value(self):
		return(self.parent.obj.soundfile, self.ok)	# I know, a bit redundant...
	

class Select_edit():
	"""
	A simple class to hold the pieces we need to 
	determine which Page/Song/etc. we want to edit...
	"""
	def __init__(self, parent, list="pagelist", member="desc_title", name="Page"):
		
		self.parent = parent
		self.member = member 	# text: name of the member that is the list (e.g., "pagelist")
		self.list = list
		self.name = name		# text: what to print... (e.g., "Page")
	
	def post(self):
		self.tmpBox = tk.Toplevel()
		#self.tmpBox.transient(self.parent.top)
		
		frame = tk.LabelFrame(master=self.tmpBox, relief=tk.GROOVE, text="Select " + self.name + " to Edit (Group: " + self.parent.current_groupname + ')', borderwidth=5)
		frame.lift(aboveThis=None)
		frame.grid(ipadx=10, ipady=40, padx=15, pady=15)
		# return the list...
		plist = eval("self.parent.current_group." + self.list)
		plist.sort(key=clclasses.createkey, reverse=True)
		
		self.my_obj_module = cltkutils.clOption_menu(frame, plist, self.member )
		self.my_obj_module.om.grid(column=1, row=1)
		
		self.button = ttk.Button(frame, text="Edit", command=self.edit_select).grid(column=2, row=2)	
		self.tmpBox.wait_window(frame)
	
	def edit_select(self):
		"""
		Called when the "Edit" button is pushed
		"""
		print "edit_select called."
		selected_str = self.my_obj_module.var.get()
		if selected_str is None:
			print "Got a Null selection."
		print self.my_obj_module.var.get()
		self.selected = self.my_obj_module.dictionary[selected_str]
		self.tmpBox.destroy()

class Edit_screen:
	"""
	Base class for the Page, Song and whatever future
	classes.   Does the barebones setup of a frame, ready
	for edit rows, or what ever else shows up.
	"""
	def __init__(self, parent, object, new=False):
		"""
		Set up for the base object (Page, Song, etc.).  
	
		If new is True, we're likely creating a new object
		including a dir (no spaces, etc.).   In any case,
		not to be called directly - set up for the derivative
		class
		"""
		print "hello"
		if parent.edit_lock:
			print "locked"  # (obviously more, later)
			return
		#parent.edit_lock = True
		#new = False
		print "PES: new:",new
		self.parent = parent
		self.object_type = 'Unset'
		
		self.row=0
		self.column=0
		self.obj = object		# the object we're editing
		self.new = new
		self.ok = not new
		self.edit_frame = None
		self.song_obj = None
		self.obj.changed = False
		self.obj.needs_rebuild = False
		
		
		
	def setup(self):		# RBF: at least check to see if we ever call  this - I'm guessing no...
		
		print "-----------Setup called!"
		if self.edit_frame is not None:
			print "---------------Destroy All Page Frames...---------"
			self.edit_frame.destroy()
	
		# Set up a dictionary listing the row objects, etc. that have the 
		# info we need.  By indexing by the "member" name - we can find the mas 
		# needed - or step through the whole list.
		self.editlist = dict()		
		if self.new:
			self.editTop = tk.Toplevel()
			self.editTop.transient(self.parent.top)
			self.editTop.title("coLab Edit")
			self.edit_frame = tk.LabelFrame(master=self.editTop, relief=tk.GROOVE, text=self.new_text, borderwidth=5)
			self.edit_frame.lift(aboveThis=None)
			self.edit_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
			
			# we first open, it it's new, with a simple window for the name...
			
			
			# get a little tricky - since we don't know the name yet - set a temp var in the 
			# object:  sub_dir so that we can pass this, plus the final name, to set_paths...
			self.obj.sub_dir = self.sub_dir
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

			row.exclude_list = self.exclude_list
			row.exclude_chars=' "/:'	# characters we don't want in file names...
			row.ignore_case = True
			row.new = self.new				# as passed in
			row.editable = self.new		# don't edit a file name that's already been created...
			row.post()
			# cheat a little through u up quick descriptive label
			# later...  columnspan 2
			
			self.editlist[row.member] =  row 		# just process this one item...
			
			self.row = 8		# push these buttons down out of the way...
			self.saveButton = ttk.Button(self.edit_frame, text="Save", command=self.save).grid(column=3, row=self.row)	# add  command=
			self.quitButton = ttk.Button(self.edit_frame, text="Quit", command=self.quit).grid(column=4, row=self.row)
			
			# stop and wait for the above window to return...
			self.editTop.wait_window(self.edit_frame)
		
		#
		# Basically start over - this time with the name preset...
		#time.sleep(1)		# Seems to be necessary for the window to die (is there a call for this?)
		self.editTop = tk.Toplevel()
		self.editTop.transient(self.parent.top)
		self.row=0
		self.column=0
		self.edit_frame = tk.LabelFrame(master=self.editTop, relief=tk.GROOVE, text=self.obj.name + " (Group: " + self.parent.current_groupname + ')', bd=100, padx=10, pady=10, borderwidth=5)
		self.edit_frame.lift(aboveThis=None)
		self.edit_frame.grid(ipadx=10, ipady=10, padx=15, pady=15)
		
		return	
	
	def read(self):
		"""
		Read the current state of the edit list into the 
		object.
		"""
		print "Reading into obj.."
		self.ok = True		# until we hear otherwise...
		self.bad_list = []	# Keep track of the names that are not set well..
		for item in self.editlist:
			row_obj = self.editlist[item]
			print "item.member:", row_obj.member
			(value, ok) = row_obj.return_value()
			if not ok:
				self.ok = False
				self.bad_list.append(row_obj.text)
			
			# may not want to do this - but it likely doesn't matter as we 
			# will either correct it, or toss it.
			string = "self.obj." + item + ' = """' + str(value) + '"""'
			print "exec string:", string
			exec(string)
				
		
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
		
class Page_edit_screen(Edit_screen):
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
		Edit_screen.__init__(self, parent, page, new)

		page.object_type = 'Page'
		page.page_type = 'html5'		# new pages use this..
		
		# convert the media size (e.g., small, medium, etc) to (width, height)
		self.size_class = config.Sizes()
		self.size = self.size_class.sizeof(page.media_size)	
		
		if self.new:
			self.new_text = "New Page (Group: " + self.parent.current_groupname + ')'
			self.sub_dir = os.path.join('Group', self.parent.current_groupname, 'Page', )
			self.exclude_list = []	# names to not allow for a new page
			for nextpage in self.obj.group_obj.pagelist:
				self.exclude_list.append(nextpage.name)
				
		self.setup()
		
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
		
		#--- Resolution
		#self.obj.song_obj = None
		menu = Resolution_menu_row(self, "Resolution", "media_size")
		l = []		# list of resolutions and their actual size
		d = {}		# dictionary of strings to media_size names...
		for resolution in self.size_class.list():
			string = resolution + " " + str(self.size_class.sizeof(resolution))
			l.append(string)
			d[string] = resolution
			if resolution == page.media_size:
				menu.default = string
			
		menu.titles = tuple(l)		# Convert to a tuple...
		
		self.editlist[menu.member] =  menu
		menu.dict = d
		menu.post()
		menu.set_status(True)	# It's always good...
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
		self.obj.graphic_row = row	# we'll want this later....
		
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
		menu = Song_menu_row(self, "Song", "song")
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
			menu.default = self.song_obj.desc_title
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
		self.saveButton = ttk.Button(self.edit_frame, text="Save", command=self.save).grid(column=3, row=self.row)	# add  command=
		self.quitButton = ttk.Button(self.edit_frame, text="Quit", command=self.quit).grid(column=4, row=self.row)
	
			
	def build_part_list(self):
		"""
		Use the song object to build the part list
		and conversion dictionary (Long names are
		displayed, simple names are stored.)
		
		Returns a tuple of long names ready to be assigned to an ObjectMenu for display
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
		
	def save(self):
		print
		print "------------------"
		print "Dump of page", self.obj.name
		self.read()
		print "Dump----------------"	
		#print self.obj.dump()
		print'---first home'
		try:
			sub_dir = os.path.join('Group', self.obj.group, 'Page',  self.obj.name)
			home_dir = os.path.join(self.obj.coLab_home, sub_dir)
		except Exception as e:
			print "Cannot build new page subdir", e, sys.exc_info()[0]
			sys.exit(1)
	
		clclasses.set_paths(self.obj, sub_dir)		# Paths are now correct...
		print "Pagehome:", self.obj.home
		print "Pageroot:", self.obj.root
		
		
		
		if not self.ok:
			print "Still something wrong - see above"
			message = "There were problems with the following fields:\n\n"
			spacer=' '
			for i in self.bad_list:
				message += spacer + i
				spacer = ', '
			message += '.\n\nPlease correct.'
			tkMessageBox.showerror("There were problems...", message, parent=self.edit_frame, icon=tkMessageBox.ERROR)
			return
		
		else:
			# I don't like this - I want a better method to determine if this is new or not...
			if float(self.obj.duration) == 0.0:
				action = 'create'
			else:
				action = 'update'
			message = "This will " + action + " the page: " + self.obj.name
			message += "\n\nOK?"
			if not tkMessageBox.askquestion('OK to save?', message, parent=self.edit_frame, icon=tkMessageBox.QUESTION):
				print "return"
				return
	
			if action == 'create':
				# need to add this bit to the group's lists
				self.obj.group_obj.pagelist.append(self.obj)		# add the page name
				self.obj.group_obj.pagedict[self.obj.name] = self.obj	# name -> page obj
				self.obj.create()				# build the page dir structure, base data page.
				self.editTop.destroy()
				return							# just create the dir and 1-entry data file - we only have the name so far
						
			# We're good - let's post this...
			clclasses.convert_vars(self.obj)
			self.obj.post()
			# Now build the frames and video in the background...
			#page_thread=threading.Thread(target=rebuild_page_edit, args=(self,))
			page = self.obj
			page.editor = None
			htmlgen.pagegen(page.group_obj, page)
			self.parent.render_engine.add_render(sub_dir)
			#page.editor = self	# pass in the page, but reference this editor obj.
			#page_thread=threading.Thread(target=rebuild.render_page, args=(page,))
			#page_thread.start()
			#rebuild_page_edit(self)
			
			self.editTop.destroy()
			
			
	def quit(self):
		if self.obj.changed:
			message = "You've made changes, quitting now will lose them.\n\nDo you still want to quit?"
			if not tkMessageBox.askokcancel('OK to quit?', message, parent=self.edit_frame, icon=tkMessageBox.QUESTION):
				return(None)
		self.editTop.destroy()
'''

def rebuild_page_edit(obj):
		"""
		This is called as the run method of a thread object.
		The idea is to manage/monitor the creation of the web page
		data, in a distracting and entertaining way...
		
		Yeah, right.
		
		Specifically: the generation of the image frames, followed by the generation of
		the video from those frames plus the audio.
		"""
		# let's make sure mamp is running...
		
		clSchedule.start_mamp()
		progressTop = tk.Toplevel()
		progressTop.transient(obj.parent.top)
		edit_frame = tk.LabelFrame(master=progressTop, relief=tk.GROOVE, text="New Page Generation" , borderwidth=5)
		edit_frame.lift(aboveThis=None)
		edit_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
		#
		
		fps = imagemaker.calc_fps_val(obj.obj)
		frames = int(float(obj.obj.duration) * fps) 
		if obj.needs_rebuild:
			f1 = tk.Frame(edit_frame)
			f1.grid(row=0, column=0, sticky=tk.W)
			
			img_gen_progbar = cltkutils.Progress_bar(f1, 'Image Generation', max=frames)
			img_gen_progbar.what = 'Image'
			img_gen_progbar.width = 500
			img_gen_progbar.max = frames
			img_gen_progbar.post()		# initial layout...
			
			f2 = tk.Frame(edit_frame)
			f2.grid(row=1, column=0, sticky=tk.W)
			
			vid_gen_progbar = cltkutils.Progress_bar(f2, 'Video Generation', max=frames)
			vid_gen_progbar.what = 'Frame'
			vid_gen_progbar.width = 500
			vid_gen_progbar.max = frames
			vid_gen_progbar.post()
		 
		""" 	
		f3 = tk.Frame(edit_frame)
		f3.grid(row=2, column=0, sticky=tk.W)
		ftp_progbar = cltkutils.Progress_bar(f3, 'ftp mirror...')
		ftp_progbar.width = 500
		ftp_progbar.mode = 'indeterminate'
		ftp_progbar.post()
		#"""
		
		f4 = tk.Frame(edit_frame)
		f4.grid(row=3, column=0, sticky=tk.E)
		quitButton = ttk.Button(f4, text="Quit", command=progressTop.quit)
		quitButton.grid()
		
		
		if obj.needs_rebuild:	
			imagemaker.make_images(obj.obj, img_gen_progbar)
			img_gen_progbar.progBar.stop()
			clAudio.make_movie(obj.obj, vid_gen_progbar)
		#ftp_progbar.progBar.start()
		rebuild.rebuild(obj.obj.group_obj)		# currently the group name - change to the object...
		#ftp_progbar.progBar.stop()
				
		progressTop.destroy()
		local_url = "http://localhost/" + obj.obj.root
		clSchedule.browse_url(local_url)
'''

		
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
	new_page.coLab_home = this_group.coLab_home		# just enough path to get us stared..
	
	parent.page = Page_edit_screen(parent, new_page, new=True)
	
	
def edit_page(parent):
	print "edit Page"
	
	selector = Select_edit(parent, "pagelist", "desc_title", "Page")	# pick a page...
	print "ep hello"
	selector.post()
	print "ep post post"
	try:
		page = selector.selected
	except:
		page = None
	if page is None:
		return
	print "Selected:", page.name
	
	parent.page = Page_edit_screen(parent, page, new=False)


	
def create_new_song(parent):
	print "new song"
	"""
	Does the initial setup to call the edit screen and leaves.
	The rest is done there.
	"""
	
	print "New song"
	group_name = parent.current_groupname		# currently selected group
	this_group = parent.current_group
	
	print "My group is:", group_name, this_group.title
	
	print "Group info:", this_group.subtitle
	
	new_song = clclasses.Song(None)
	new_song.group_obj = this_group
	new_song.group = this_group.name
	new_song.coLab_home = this_group.coLab_home		# just enough path to get us stared..
	
	parent.song = Song_edit_screen(parent, new_song, new=True)
	
	
def edit_song(parent):

	print "edit Song"
	
	selector = Select_edit(parent, "songlist", "desc_title", "Song")	# pick a song...
	print "ep hello"
	selector.post()
	print "ep post post"
	try:
		song = selector.selected
	except:
		song = None
	if song is None:
		return
	print "Selected:", song.name
	
	parent.page = Song_edit_screen(parent, song, new=False)	

class Song_edit_screen(Edit_screen):
	"""
	A way of posting a screen that lets us enter
	or edit the variables associated with a song class.
	
	The new var if set to True allows the name to be set and
	populates the entry fields with temp strings that clear
	once a character is typed.
	
	Passed the parent structure of the entire session, works from
	the current group
	"""
	def __init__(self, parent, song, new=False):
		Edit_screen.__init__(self, parent, song, new)
		
		print "hello"
		if parent.edit_lock:
			print "locked"  # (obviously more, later)
			return
		#parent.edit_lock = True
		#new = False
		print "SES: new:",new
		
		song.object_type = 'Song'
		
		if self.new:
			self.new_text = "New Song (Group: " + self.parent.current_groupname + ')'
			self.sub_dir = os.path.join('Group', self.parent.current_groupname, 'Song', )
			self.exclude_list = []	# names to not allow for a new page
			for nextsong in self.obj.group_obj.songlist:
				self.exclude_list.append(nextsong.name)
				
		self.setup()

		
		#---- Descriptive title, "unique", but flexible with case, spaces, etc...
		row = Entry_row(self, "Descriptive title", "desc_title", width=30)
		# exclude existing titles...
		for nextsong in self.obj.group_obj.songlist:
			row.exclude_list.append(nextsong.desc_title)
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
		
		#"""
		self.saveButton = ttk.Button(self.edit_frame, text="Save", command=self.save).grid(column=3, row=self.row)	# add  command=
		self.quitButton = ttk.Button(self.edit_frame, text="Quit", command=self.quit).grid(column=4, row=self.row)
		

	def build_part_list(self):
		"""
		Use the song object to build the part list
		and conversion dictionary (Long names are
		displayed, simple names are stored.)
		
		Returns a tuple of long names ready to be assigned to an ObjectMenu for display
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
		
	def save(self):
		print
		print "------------------"
		print "Dump of page", self.obj.name
		self.read()
		print "Dump----------------"	
		#print self.obj.dump()
		print'---first home'
		try:
			sub_dir = os.path.join('Group', self.obj.group, 'Song',  self.obj.name)
			home_dir = os.path.join(self.obj.coLab_home, sub_dir)
		except Exception as e:
			print "Cannot build new page subdir", e, sys.exc_info()[0]
			sys.exit(1)
	
		clclasses.set_paths(self.obj, sub_dir)		# Paths are now correct...
		print "Pagehome:", self.obj.home
		print "Pageroot:", self.obj.root
		
		if not self.ok:
			print "Still something wrong - see above"
			message = "There were problems with the following fields:\n\n"
			spacer=' '
			for i in self.bad_list:
				message += spacer + i
				spacer = ', '
			message += '.\n\nPlease correct.'
			tkMessageBox.showerror("There were problems...", message, parent=self.edit_frame, icon=tkMessageBox.ERROR)
			return
		
		else:
			if self.new:
				action = 'create'
			else:
				action = 'update'
			message = "This will " + action + " the song: " + self.obj.name
			message += "\n\nOK?"
			if not tkMessageBox.askquestion('OK to save?', message, parent=self.edit_frame, icon=tkMessageBox.QUESTION):
				print "return"
				return
	
	
			if action == 'create':
				# need to add this bit to the group's lists
				self.obj.group_obj.songlist.append(self.obj)		# add the page name
				self.obj.group_obj.songdict[self.obj.name] = self.obj	# name -> page obj
				self.obj.create()				# build the page dir structure, base data page.
				self.editTop.destroy()
				self.new = False
				return							# just create the dir and 1-entry data file - we only have the name so far
						
			# We're good - let's post this...
			clclasses.convert_vars(self.obj)
			self.obj.post()
			#page_thread=threading.Thread(target=rebuild_page_edit, args=(self,))
			#page_thread.start()
			#rebuild_page_edit(self)
			htmlgen.rebuild(self.obj.group_obj)		
			self.editTop.destroy()
			
	def quit(self):
		if self.obj.changed:
			message = "You've made changes, quitting now will lose them.\n\nDo you still want to quit?"
			if not tkMessageBox.askokcancel('OK to quit?', message, parent=self.edit_frame, icon=tkMessageBox.QUESTION):
				return
		self.editTop.destroy()
		

	
#------ interface to main routine...
import coLab
def main():
	print "Colab Main"
	coLab.main()
	
if __name__ == '__main__':
	main()