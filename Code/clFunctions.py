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
import logging
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
import clutils
import cltkutils
import clGraphEdit
import clSchedule
import imagemaker
import clAudio
import clColors
import rebuild
import htmlgen

class Data_row:
	"""
	Base class for the various rows that gather data.  
	Basic layout is a row that has the name, a status cell,
	and some kind of a gadget that presents/gathers data.
	
	Classes are looking like:
	
	Data_row
		Entry_row
		Text_row
		Menu_row
			Theme_menu_row
			Resolution_menu_row
			Song_menu_row
			Graphic_row
			Graphic_menu_row
				Graphic_menu_row_soundfile
				Graphic_menu_row_screenshot
		
	"""
	def __init__(self, editor, text, member):
		"""
		Set up the default values common to all rows...
		"""
		self.editor = editor
		self.text = text
		self.member = member
		# install the current value...
		self.value = eval("self.editor.obj." + self.member)	# convert the variable name to its value# Basic row / cell management
		self.row = editor.row		# editor keeps track of row / column
		editor.row += 1				# move the  editor row down one...
		self.column = editor.column
		# initialization come to some / most / all
		self.label = None
		self.new = editor.new		# when true, items are ghosted / replaced on first key  
		self.ok = not self.new		# new items are assumed to be not good yet, and vice-versa
		self.editable = True		# occasionally we get one (existing file name) that we don't want to edit...
		
	def set(self, value):
		self.value = value
		self.new = False
		if self.editable:
			self.post_status()
		else:
			self.post_status(False)
		self.post()
		
	def post_status(self, ok=None):
		"""
		Set the status of the widget - log the state, and update
		the status column, should work for most/all row classes...
		If nothing / None is passed in, use the row's current status.
		"""
		print "Post_status: (name, self.ok, passed ok, editable):", self.member, self.ok, ok, self.editable
		if not self.editable:	# not editable, no status - takes prio
			ok = None
		elif ok is None:
			ok = self.ok
		else:
			self.ok = ok
		# None means don't display any, other Good/Bad
		if ok is None:
			color = '#a73'
			txt = ' - '
		elif ok:
			color = '#2f2'	# bright green
			txt = 'OK'
		else:
			color = '#f11'	# bright red
			txt = ' X '
			
		self.status.configure(foreground=color)
		self.statusVar.set(txt)
		
	def read(self):
		'''
		This may actually be an 'error' - this method needs to be
		implemented specifically to all sub classes...
		For now: return None and not ok...
		'''
		print ">>>>>>   Generic read: method needs to be replaced...", self.member
		return(None, False)	

	def return_value(self):
		"""
		Call read to update the values - and return them
		(some derived classes may do it differently)
		"""
		self.read()
		return (self.value, self.ok)
	
	
		
class Entry_row(Data_row):
	"""
	A class for an entry row in an edit panel.  Holds the info specific to
	a row - implements posting the Text and the value in an entry field.
	Allows for "new" and "editable" fields (non-editable are displayed as
	labels).   Also handles validation based on the values put into the 
	class. Also marks the status and matching fields.
	"""
	def __init__(self, editor, text, member, width=15):
		Data_row.__init__(self, editor, text, member)
		
		self.width = width
		
		self.label = None				# have we been here before
		self.exclude_list = []		# a list of items not allowed (e.g., current file names)
		self.exclude_chars = '"'	# current implementation does not allow " n stored strings
		self.ignore_case = False	# Set to true for file names, etc.
		self.match = None	
		self.match_text = ''		# used to recall the last bad match (equiv. file name, e.g.)	
		self.match_color = '#666'
		#self.new = editor.new		# when true, items are ghosted / replaced on first key  
		
		
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
			self.value_strVar = tk.StringVar()
			# write the base label...
			self.label = ttk.Label(self.editor.edit_frame, text=self.text+":", justify=tk.RIGHT)
			self.label.grid(row=self.row,column=self.column, sticky=tk.E)
			# Now we build a string that is the name of the associated variable.   Then we use eval and exec to
			# deal with it.
			print "self.member", self.member
			self.value = eval("self.editor.obj." + self.member)	# convert the variable name to its value
			print "value", self.value
			#print "ept: new?:", self.new
			print "post:  my new is:", self.member, self.new
			
			# set up a small label between the title and the value to 
			# display the status of the value...
			self.statusVar = tk.StringVar()
			self.status = ttk.Label(self.editor.edit_frame, textvariable=self.statusVar)
			self.status.grid(row=self.row, column=self.column + 1)
			if self.new:
				self.post_status(None)
			else:
				self.post_status(ok=True)
		else:
			self.widget.destroy()
		
		# if not editable - just display as a label...
		print "vobj - editable:", self.editable
		if not self.editable:
			self.widget = ttk.Label(self.editor.edit_frame, textvariable=self.value_strVar, justify=tk.LEFT)
			self.widget.grid(row=self.row,column=self.column + 2, columnspan=3, sticky=tk.W)
			self.value_strVar.set(self.value)
			#self.ok = True		# since we can't change it - it's good
			self.post_status()
			print "non-edit _obj:", self.widget
		else:
			
			print "Ev_init: callback is:", self.callback
			# Build a list: the call back registery and the subcodes, 
			# then turn the list into a tuple to pass in...
			l = [ self.editor.edit_frame.register(self.callback) ]		# first part is the registration of the call back.
			#widget.destroy()
			for sc in self.subcodes:
				l.append(sc)
			self.validatecommand = tuple(l)	# make into a tuple
			print "vcmd ", self.validatecommand, "validate:", self.validate
			# set colors for edit (Black) and new (lt. gray) objects
			fg = '#000'		# black
			if self.new:
				fg = '#AAA'	# light gray
			
			self.widget = ttk.Entry(self.editor.edit_frame, textvariable=self.value_strVar, width=self.width, foreground=fg,background='#e9e9e9', validate=self.validate, validatecommand=self.validatecommand )
			print "v-obj widget created:", self.widget
			self.widget.grid(row=self.row, column=self.column + 2, sticky=tk.W)
			self.value_strVar.set(self.value)
						
			self.matchVar = tk.StringVar()
			self.match = tk.Label(self.editor.edit_frame, textvariable=self.matchVar, justify=tk.LEFT)
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
				print "Would be:", would
				if self.ok:
					print "Setting ourselves to would."
					self.set(would)
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
			
		self.editor.changed = True	
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
			#would = ''
			#self.widget.configure(fg='#000')
			self.value_strVar.set(would)
			fg='#000'	# black
			#self.widget.configure(fg=fg)
			self.widget.configure(foreground=fg, validate=self.validate, validatecommand=self.validatecommand )
			self.widget.icursor(len(would))
			self.new = False
			r_code = False		# Reject the character - we've already set it in, above
			
		print "Would is:", would
		#-- zero length?  
		if  len(would) == 0:
			self.ok = False
			self.post_status()
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
		self.ok = good
		self.post_status()
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
				
	def read(self):
		"""
		Pull the value out of the widget...
		"""
		self.value = self.value_strVar.get()
		print "Entry read:", self.text, self.value, self.ok
		return 
	
class Text_row(Data_row):
	"""
	A class for a text row in an edit panel.    Very simple
	"""
	def post(self):
		"""
		Just post the text...
		"""
		
		# write the base label...
		self.label = tk.Label(self.editor.edit_frame, text=self.text+":", justify=tk.RIGHT)
		self.label.grid(row=self.row,column=self.column, sticky=tk.E)
		# set up a small label between the title and the value to 
		# display the status of the value...
		self.statusVar = tk.StringVar()
		self.status = ttk.Label(self.editor.edit_frame, textvariable=self.statusVar)
		self.status.grid(row=self.row, column=self.column + 1)
		# need a "sub-frame" to hold the desc. and scroll bar.
		self.subframe = tk.LabelFrame(self.editor.edit_frame, relief=tk.GROOVE)
		self.subframe.grid(row=self.row, column=self.column+2, columnspan=3, sticky=tk.W)
		
		self.widget = tk.Text(self.subframe, height=15, width=80, padx=5, pady=5, relief=tk.GROOVE, wrap=tk.WORD,bg='#ffffff', undo=True)
		self.widget.grid(row=0, column=0, sticky=tk.W)
		self.widget.insert('1.0', self.value)
		# vertical scroll bar...
		self.scrollY = tk.Scrollbar(self.subframe, orient=tk.VERTICAL, command=self.widget.yview)
		self.scrollY.grid(row=0, column=1, sticky=tk.N+tk.S)
		self.widget.configure(yscrollcommand=self.scrollY.set)
		
	def read(self):
		"""
		Just return the text.
		"""
		self.value = self.widget.get('1.0', 'end')
		self.ok = len(self.value) > 0 	# any non-null entry is ok....
	
	
class Menu_row(Data_row):
	"""
	Just put up an OptionMenu from the provided list..)
	"""
	
	def __init__(self, editor, text, member):
		Data_row.__init__(self, editor, text, member)
		
		self.default = None		# used o force a menu to a specific value
		self.value = None		# actual value - displayed if default is not set
		self.titles = ('no-titles',)
		self.handler = self.handle_menu
		
	def post(self):
		print "Welcome menu-post"
		
		# write the base label...
		if self.label is None:
			self.label = tk.Label(self.editor.edit_frame, text=self.text+":", justify=tk.RIGHT)
			self.label.grid(row=self.row,column=self.column, sticky=tk.E)
			# set up a small label between the title and the value to 
			# display the status of the value...
			self.statusVar = tk.StringVar()
			self.status = ttk.Label(self.editor.edit_frame, textvariable=self.statusVar)
			self.status.grid(row=self.row, column=self.column + 1)
		else:
			self.widget.destroy()
		self.post_menu()
		self.post_status()
			
	def post_menu(self):
		try:
			self.gOpt 
		except:
			self.gOpt = tk.StringVar()

		if self.default is not None:
			value = self.default
		else:
			if self.value is not None:
				value = self.value
			else:
				value = self.titles[0]	# use the first as a default...
		
		print "Setting gOpt to: ", value
		self.gOpt.set(value)

		self.widget = tk.OptionMenu(self.editor.edit_frame, self.gOpt, *self.titles, command=self.handler)

		self.widget.grid(column=self.column+2, row=self.row,  columnspan=3,sticky=tk.W)
		
		self.statusVar = tk.StringVar()
		self.status = tk.Label(self.editor.edit_frame, textvariable=self.statusVar)
		self.status.grid(row=self.row, column=self.column + 1)
	
	def lookup(self, value):
		'''
		Convert the value based on the dictionary...
		if none - or not known, return the passed value.
		'''
		# if there's a dictionary - do a lookup...
		try:
			value = self.dict[value]
		except:
			pass		# otherwise, just return the value
		return value
			
	def handle_menu(self, value):
		#value = self.gOpt.get()	 # should be equivalent
		
		value = self.lookup(value)	# convert from displayed to "actual"
		
		self.value = value
		# if the menu item starts with a "-", it is an unacceptable value
		self.post_status( value[0] != '-')
		self.editor.changed = True	
			
	def read(self):
		'''
		get the menu value.   At this point, it would 
		always just be self.value - since that's generally set
		by handle menu - but for now - let's just note if they
		don't match
		'''
		
		value = self.gOpt.get()
		value = self.lookup(value)	# convert from displayed to "actual"

		if value != self.value:
			print "Menu read - mismatch in values:", value, self.value
		self.value = value
		
	def return_value(self):
		"""
		Menu return - but force ok to true - we're always right
		"""
		self.post_status(True)
		self.read()
		return(self.value, self.ok)


class Theme_menu_row(Menu_row):
	def __init__(self, editor, text, member):
		Menu_row.__init__(self, editor, text, member)

		# we start with a theme object...
		theme_obj = clColors.Themes(editor.obj.graphic_theme)
			
		self.titles = theme_obj.theme_names
		self.value = theme_obj.theme
		self.ok = True				# always good...
		
	def handle_menu(self, value):
		"""
		Reset the editor's size vars...
		"""
		Menu_row.handle_menu(self, value)
		
		print "Rebuild the thumbnail(s) as appropriate..."
		page = self.editor.obj
		page.graphic_theme = self.value		# 
		popup = cltkutils.Popup('Rebuilding thumbnail...', 'Rebuilding to theme:\n'+self.value, geometry="+500+500")
		img_dest = os.path.join(page.home, page.soundgraphic)
		sound_file = os.path.join(page.home, page.localize_soundfile())
		imagemaker.make_sound_image(page, sound_file, img_dest, size='Tiny', max_samp_per_pixel=100)
		imagemaker.make_sub_images(page)
		popup.destroy()
		page.needs_rebuild = True
		page.changed = True
		self.editor.refresh()
		


class Resolution_menu_row(Menu_row):
	def __init__(self, editor, text, member):
		Menu_row.__init__(self, editor, text, member)

		l = []		# list of resolutions and their actual size
		d = {}		# dictionary of strings to media_size names...
		for resolution in editor.size_class.list():
			(width, height) = editor.size_class.sizeof(resolution)
			string = resolution + ' (' + str(width) + 'x' + str(height) + ')' 
			l.append(string)
			d[string] = resolution
			page = editor.obj
			if resolution == page.media_size:
				self.default = string
			
		self.titles = tuple(l)		# Convert to a tuple...
		self.dict = d
		self.ok = None				# calculated
		
	def handle_menu(self, value):
		"""
		Reset the editor's size vars...
		"""
		Menu_row.handle_menu(self, value)
		
		page = self.editor.obj
		prev_size = page.media_size 
		page.media_size = self.value
		if prev_size != page.media_size:
			print "Size has changed..."
			page.needs_rebuild = True
			page.changed = True
		
class Song_menu_row(Menu_row):
	"""
	Derivative class - mostly for handling the changing part menu whenever
	the song changes...
	"""
	'''   
	# Not currently needed - using parent class init, but just in case...
	def __init__(self, editor, text, member):
		Menu_row.__init__(self, editor, text, member)
	#'''
	
	def post(self):
		#
		# We need to derive a list of songs by 
		# going into the page of the current editor, 
		# then stepping through its parent Group for
		# its song list..
		l = []		# list of song titles (desc_title)
		d = {}		# dictionary to convert desc_title to name
		page = self.editor.obj		# in this context it's always a page (may validate that)
		if self.editor.new:
			l = ['-select song-']		# build a list of song names...
		for i in page.group_obj.songlist:
			l.append(i.desc_title)
			d[i.desc_title] = i.name		# consider changing this to just the song object (i)
			if i.name == page.song:
				self.editor.song_obj = i		# remember this object
		# Perhaps some day we'll add the option to create a new song here...		
		#l.append('-New song-')		# maybe - but we're not ready for this yet...
			
		self.titles = tuple (l)		# Convert to a tuple...
		
		try:
			self.default = self.editor.song_obj.desc_title
		except:
			pass
		
		self.dict = d
		print "About to call Menu_row post with l / d:", l, d
		Menu_row.post(self)
		
	def handle_menu(self, value):
		"""
		Handle a change of the page's song - we need to mark\
		the current song, and the new one as changed (needs_rebuild) as
		well as rebuilding the part list and updating that.
		"""
		songname = self.dict[value]
		page = self.editor.obj
		if page.song == songname:
			print "Didn't really change..."
			# Didn't really change - all good...
			return
		# 
		# We need to do a bit of backtracking   get the page's parent 
		# group object, find the current song and mark it as needs rebuild...
		try:
			group = page.group_obj
		except Exception as e:
			print "------- No such group found as part of", self.editor.obj.value
			print "---- fix  - for now, returning"
			return
	
		song_obj = group.find_song_by_title(value)
		song_obj.needs_rebuild = True

		# if the menu item starts with a "-", it is an unacceptable value
		self.post_status(ok=value[0] != '-')	 # For now, if the song names doesn't start with '-', we're good to go 
		self.new = not self.ok
		self.editor.changed = True			# we may not need this....
		
		print "Song menu - handle_menu - songname, value", songname, value
		
		#page = self.editor.obj
		self.editor.set_member('song', songname)
		page.song = songname
		self.default = value
		print "self.default:", self.default
		self.post()
		
		song_obj = group.find_song_by_title(value)
		if song_obj == None:
			print "No such song object found for:", value
		song_obj.needs_rebuild = True		# mark the new song as needing rebuild too..
		# build a part list...
		self.editor.song_obj = song_obj
		self.editor.obj.part = 'All'			# if a new song, use default part for now...
		
		part_obj = self.editor.part_obj			# we saved this away for just such an occasion...
		part_obj.titles = self.editor.build_part_list()
		
		# Special case a song with only the default part as "OK"
		print "testing the partlist..."
		if song_obj.partlist == [ 'All'	]:
			print "Partlist is just 'all'"
			part_obj.post_status(ok=True)
			self.editor.set_member('part', 'All')
		else:
			part_obj.post_status(ok=False)
			print "Song object part list is vague:", song_obj.name, part_obj.ok
			#time.sleep(2)
		# set the new dictionary in place...
		self.editor.part_obj.dict = self.editor.part_lookup
		self.editor.part_obj.post()
		self.editor.read()
		
# a dictionary of menu options, short name mapped to longer name
# longer name can contain replaceable string, e.g.  !type! 
OPT_MENU_DICT = { 'Load': 'Load a new !type! file...', 
 				  'Reuse': 'Reuse a previous/existing !type! file...',
				  'UseSound': 'Use the Sound Graphic (above)',
				  'Adjust': 'Adjust start and end...'
				}
		
class Graphic_row(Data_row):
	"""
	Post a row with a title and a graphic...
	The member is a file name, and that file is displayed, if it exists,
	otherwise a default is shown. 
	Maybe associated with a graphic menu row that modifies the file and
	possibly other options.
	
	"""
	def __init__(self, editor, text, member, graphic_path):
		Data_row.__init__(self, editor, text, member)
 
		self.graphic_path = graphic_path
	       
	       
	def post(self):
		"""
		put the text and graphic on the screen...
		"""
	       
		print "Graphic post"
		if self.label is None:
			# write the base label...
			self.frame = self.editor.edit_frame
			self.label = tk.Label(self.frame, text=self.text+":", justify=tk.RIGHT)
			self.label.grid(row=self.row,column=self.column, sticky=tk.E)

			self.gOpt = tk.StringVar()
		       
			self.statusVar = tk.StringVar()
			self.status = tk.Label(self.editor.edit_frame, textvariable=self.statusVar)
			self.status.grid(row=self.row, column=self.column + 1)
		       
	
		else:
			try:
				self.graph_el.graphic.destroy()
			except:
				print "Graphic_el.graphic.destroy failed."
				pass

		self.graph_el = cltkutils.graphic_element(self.frame)
		self.graph_el.filepath = self.graphic_path
		self.graph_el.row = self.row
		self.graph_el.column = self.column + 2
		self.graph_el.columnspan = 3
		self.graph_el.sticky = tk.W
		self.graph_el.post()    
	       
		if self.new:
			self.new = False
		self.post_status()
       
	def set(self, value):
		self.value = value
		self.new = False
		self.post_status(ok=self.ok)
		self.post()
       

	def return_value(self):
		return(None, self.ok)
      
class Graphic_menu_row(Menu_row):
	"""
	Based on the menu class, so we can easily use the handler callback,
	this is a hybrid class that also does a graphical row.   The
	top graphic is a full row, though as a child class of this object.
	We get slightly tricky with the menu row, because we don't want
	the label and status.
	"""
	def __init__(self, editor, text, member, graphic_path=None):
		Menu_row.__init__(self, editor, text, member)

		self.graphic_path = graphic_path	# may be set by the derived class post method
		self.editor.row += 1		# this one takes up 2 rows, one more than most
		self.row = self.editor.row	# the menu part is the second row
		self.ok = None			# don't post a status for the menu
		
		self.graphic_row = Graphic_row(self.editor, text, member, graphic_path)	# create second row for the menu
		self.graphic_row.row = self.row - 1		# graphic appears in the row above.

	def post(self):
		"""
		put the text and graphic on the screen...
		
		also post the menu...
		"""
		# Build a list (and translation dict) from the menuitem list...
		l = []
		d = dict()

		for menuitem in self.menulist:
			title = OPT_MENU_DICT[menuitem].replace("!type!", self.type)
			l.append(title)
			d[title] = menuitem
			
		self.titles = tuple(l)
		self.dict = d

		self.post_menu()	# short cut to just the menu...
		self.statusVar.set('!!')
		print "Graphic post"
		self.graphic_row.graphic_path = self.graphic_path
		self.graphic_row.post()
		
		'''
		if self.new:
			self.post_status(ok=True)
			self.new = False
		else:
			self.post_status(ok=True)
		#'''
		self.post_status(None)	# the menu has no status
	
	def set(self, value):
		self.value = value
		self.new = False
		self.post_status(ok=None)
		self.post()
	

	def load(self):
		print "Graphic Menu Placeholder: load"
	def adjust(self):
		print "Graphic Menu Placeholder: adjust"
	def reuse(self):
		print "Graphic Menu Placeholder: reuse"
	def usesound(self):
		print "Graphic Menu Placeholder: usesound"
		
class Graphic_menu_row_soundfile(Graphic_menu_row):
	def post(self):
		self.type = 'Sound'	# I know, init - but here: it's one line
		# is there such a file?
		#self.widget = cltkutils.graphic_element(self.frame)
		page = self.editor.obj
		self.graphic_path = os.path.join(page.home, page.soundthumbnail)
		if not os.path.isfile(self.graphic_path):		# we need a backup file...
			self.graphic_path = os.path.join(page.coLab_home, 'Resources', 'coLab-NoPageSound_tn.png')
		
		# set up the menu...   we always include load...
		self.menulist = [ 'Load' ]
		# if there are any legit sound files in coLab_local, add "reuse"
		colab_local = os.path.join(page.home, 'coLab_local')
		if clutils.has_filetype(colab_local, ['.aif', '.aiff']):
			self.menulist.append('Reuse')	

		print "Graphic menu list:", self.menulist
		self.default = "Change Sound File"
		Graphic_menu_row.post(self)

	def handle_menu(self, menustring):

		action = self.dict[menustring]
		print "Soundfile menu handler", action
		if action is 'Load':
			self.load()
		elif action is 'Reuse':
			self.reuse()
		else:
			self.post()
			print "Time to relax - or panic s", action

	def load(self):
		"""
		Mostly just set up the initial path to the file...
		"""
		print "this is the sound file loader"
		page = self.editor.obj
		page.changed = True
		page.needs_rebuild = True	
		self.initialPath = "/Volumes/iMac 2TB/Music/"
		self.filetypes = [ ('AIFF', '*.aif'), ('AIFF', '*.aiff')]
		# We need to keep the latest file path...
		if page.soundfile.startswith(self.initialPath):
			init_file = page.soundfile[len(self.initialPath):]	# where we were within the starting path...
		else:
			init_file = os.path.split(page.soundfile)[1]	# just the file name
		self.initialfile = init_file
		self.copy_soundfile = True
		self.file_load()

	def reuse(self):
		"""
		Similar to load - but point to where we keep the local files
		"""
		print "this is the sound file reloader"
		page = self.editor.obj
		page.changed = True
		page.needs_rebuild = True	
		self.initialPath = os.path.join(page.home, "coLab_local")
		self.filetypes = [ ('AIFF', '*.aif'), ('AIFF', '*.aiff') ]
		self.initialfile = os.path.split(page.soundfile)[1]	# just the file name
		print"reuse: initial file:", self.initialfile
		self.copy_soundfile = False	# we already have it - just change the name...
		self.file_load()

	def file_load(self):
		"""
		Bring in the file we are pointing to in initialPath and initialfile...
		"""
		page = self.editor.obj
		print "----File load - initial file:", self.initialfile
		file_path = tkFileDialog.askopenfilename(initialdir=self.initialPath, defaultextension='.aif', title="Open AIFF sound file...", filetypes=self.filetypes, initialfile=self.initialfile)
		if not file_path:
			return
		
		self.graphic_row.post_status(True)
		page.soundfile = file_path
		self.editor.set_member('soundfile', file_path)

		filename = os.path.split(file_path)[1]
		destpath = os.path.join('coLab_local', filename)
		sound_dest = os.path.join(page.home, destpath)
		if self.copy_soundfile:
			popup = cltkutils.Popup("Sound file:" + filename, "Copying...")
			page = self.editor.obj
							
			try:
				shutil.copy(file_path, sound_dest)
			except Exception as e:
				print "Failure copying", file_path, "to", sound_dest
				raise Exception
			finally:
				popup.destroy()
			
		#  handle the duration...
		page.duration = clAudio.get_audio_len(sound_dest)
		self.editor.set_member('duration', str(page.duration))
		#self.editor.duration_obj.nameVar.set(self.editor.obj.duration)
		
		#page_thread=threading.Thread(target=rebuild.render_page, args=(page, media_size='Tiny', max_samples_per_pixel=100))
		self.size_save = page.media_size
		page.media_size = 'Tiny'	# for now - probably will define a "Preview" size
		
		
		'''   Let's try a simpler way...
		# Set up a few vars to only generate the sound graphic..
		use_save = page.use_soundgraphic
		page.use_soundgraphic = True
		page.needs_rebuild = False
		# 
		
		rendertop = rebuild.render_page(page, media_size='Tiny', max_samples_per_pixel=100)   # render as a preview...
		rendertop.destroy()		# yeah, not too keen on this, but destroying the top window in in the routine causes a hang...
		
		page.use_soundgraphic = use_save
		'''
		img_dest = os.path.join(page.home, page.soundgraphic)
		imagemaker.make_sound_image(page, sound_dest, img_dest, size='Tiny', max_samp_per_pixel=100)
		page.needs_rebuild = True
		page.changed = True
		
		if page.use_soundgraphic:		# note -this is probably duplicated -check that out    RBF
			self.editor.set_member('screenshot', page.soundgraphic)
			imagemaker.make_sub_images(page)
			self.graphic_path =  os.path.join(page.home, page.soundthumbnail)
			self.editor.post_member('screenshot')
		
		self.post()
		page.graphic_row.post()
		page.screenshot = page.soundgraphic     # probably not needed.
		#page.graphic_row.post()

	def return_value(self):
		return(self.editor.obj.soundfile, self.graphic_row.ok)	# I know, a bit redundant...	
		
class Graphic_menu_row_screenshot(Graphic_menu_row):
	"""
	Change the graphic - either load a new image, 
	or use the generated image from the sound.
	"""
	def post(self):
		self.type = 'Graphic'
		# is there such a file?
		#self.widget = cltkutils.graphic_element(self.frame)
		page = self.editor.obj
		self.graphic_path = os.path.join(page.home, page.thumbnail)
		if not os.path.isfile(self.graphic_path):		# we need a backup file...
			self.graphic_path = os.path.join(page.coLab_home, 'Resources', 'coLab-NoPageImage_tn.png')
		self.menulist = []	# build up the list of menu items based on context...
		if page.soundfile != '':
			self.menulist.append('UseSound')	# only offer this if a sound file is defined..
		self.menulist.append('Load')			# we always have this...	
		
		colab_local = os.path.join(page.home, 'coLab_local')
		if  clutils.has_filetype(colab_local, ['.png']):
			self.menulist.append('Reuse')
		
		if page.screenshot != '' and not page.use_soundgraphic:
			self.menulist.append('Adjust')
			
		print "Graphic menu list:", self.menulist
		self.default = "Change Graphic"
		
		Graphic_menu_row.post(self)
		
	def handle_menu(self, menustring):
		action = self.dict[menustring]
		print "Graphic file menu handler", action
		if action is 'Load':
			self.load()
		elif action is 'Reuse':
			self.reuse()
		elif action is 'Adjust':
			self.adjust()
		elif action is 'UseSound':
			self.usesound()
		else:
			self.post()
			print "Time to relax - or panic g", action
	def load(self):
		"""
		Load in a graphic - presumably a screen shot
		"""

		print "this is the screen shot loader..."
		page = self.editor.obj
		page.use_soundgraphic = False
		page.changed = True
		page.needs_rebuild = True	
		self.initialPath = "/Users/Johnny/Desktop"
		self.filetypes = [ ('PNG', '*.png'), ('JPEG', '*.jpg')]
		self.initialfile = os.path.split(page.screenshot)[1]
		#self.file_path = tkFileDialog.askopenfilename(initialdir=initialPath, defaultextension='.png', title="Open screen shot...", filetypes=filetypes, initialfile=initialfile)

		# We need to keep the latest file path...
		self.copy_graphicfile = True
		self.file_load()

	def reuse(self):
		print "this is the screen shot reloader..."
		page = self.editor.obj
		page.use_soundgraphic = False
		page.changed = True
		page.needs_rebuild = True	
		self.initialPath = os.path.join(page.home, "coLab_local")
		self.filetypes = [ ('PNG', '*.png'), ('JPEG', '*.jpg')]
		self.initialfile = os.path.split(page.screenshot)[1]

		#self.file_path = tkFileDialog.askopenfilename(initialdir=initialPath, defaultextension='.png', title="Open screen shot...", filetypes=filetypes, initialfile=initialfile)

		print"reuse: initial file:", self.initialfile
		self.copy_graphicfile = False	# we already have it - just change the name...
		self.file_load()

	def file_load(self):
		page = self.editor.obj
		print "----File load - initial file:", self.initialfile
		file_path = tkFileDialog.askopenfilename(initialdir=self.initialPath, defaultextension='.png', title="Select screen shot...", filetypes=self.filetypes, initialfile=self.initialfile)
		if not file_path:
			return
		
		orig_filename = os.path.split(self.initialfile)[1]	# used to determine if we have the same file...
		print "Graphic_menu_row_screenshot File path is:", file_path
		filename = os.path.split(file_path)[1]
		self.editor.set_member('screenshot', file_path)
		
		destpath = os.path.join('coLab_local', filename)
		
		graphic_dest = os.path.join(page.home, destpath)
		page.screenshot = graphic_dest
		if self.copy_graphicfile:
			popup = cltkutils.Popup("Sound file:" + filename, "Copying...") 
			page = self.editor.obj
							
			try:
				shutil.copy(file_path, graphic_dest)
			except Exception as e:
				print "Failure copying", file_path, "to", graphic_dest
				raise Exception
			finally:
				popup.destroy()
	
		# use "open" to schedule preview - seems to do what we need....
		prev_popup = cltkutils.Popup("Crop and Annotate", "Please crop to the size you want, add any annotations, then close and quit.")
		#prev_popup.t.geometry("-1-1")
		try:
				open = '/usr/bin/open'
				subprocess.call([open, '-W', '-a', 'Preview.app',  graphic_dest])
		except Exception as e:
				print "Ooops - Exception", e, sys.exc_info()[0]
				sys.exit(1)
		prev_popup.destroy()

		image = Image.open(graphic_dest)		# mostly we need the size....
		width = image.size[0]	# save the width...
		w_05 = int(width * 0.05)		# 5% of width - possible starting point
		w_95 = int(width - w_05)		# 95 % if width - possible ending poin

		# is this the same file?  (i.e., we just reselected it?)
		if filename == orig_filename and not self.copy_graphicfile:	
			print "Grhpic seems to be the same:  not changing...------------------", filename, orig_filename, self.copy_graphicfile
			xStart = page.xStart
			xEnd = page.xEnd
		else:		# set the start/end to a reasonable guess
			print "New graphic ------------------------", graphic_dest, w_05, w_95
			xStart = w_05	
			xEnd = w_95
			
	
		# In any case, the end point should not be more than the width
		if xEnd > width:
			xEnd = w_95
				
		# set into both the page values, and the editor (for now -editor will probably go away)
		page.xStart = xStart
		self.editor.set_member('xStart', xStart)
		page.xEnd = xEnd
		self.editor.set_member('xEnd', xEnd)
	
		#if tkMessageBox.askyesno('Select Limits',"Do you need to set the left and right limits?", icon=tkMessageBox.QUESTION):

		self.adjust(graphic_dest)	# Adjust the end points...

		#self.editor.post_member('screenshot')
		self.graphic_path = os.path.join(self.editor.obj.home, self.editor.obj.thumbnail)
		#
		# Let's create the poster size and thumbnails
		imagemaker.make_sub_images(self.obj)

		self.post()
		page.graphic_row.post()
		page.needs_rebuild = True
		page.changed = True
		self.graphic_row.post_status(ok=True)
		self.editor.refresh()
		#page.graphic_row.post()	# should be the same as the line above   RBF
		
	def adjust(self, graphic=None):	
		"""
		Use the graphic edit class to set the start and end points...
		"""
		page = self.editor.obj
		if graphic is None:
			graphic = page.localize_screenshot()
		# Now - post the display sized object to let us enter the xStart, xEnd
		graph_edit = clGraphEdit.GraphEdit(page, graphic)
		graph_edit.post()
		#page.xStart = graph_edit.start_x
		#page.xEnd = graph_edit.end_x
		self.editor.set_member('xStart', graph_edit.start_x)
		self.editor.set_member('xEnd', graph_edit.end_x)
				
		print "xStart, xEnd", self.editor.get_member('xStart'), self.editor.get_member('xEnd')

		self.post()
		page.needs_rebuild = True
		page.graphic_row.post()
		page.needs_rebuild = True
		page.changed = True
		self.graphic_row.post_status(ok=True)
		self.editor.refresh()
		

	def usesound(self):
		"""
		Use the graphic built from the sound...
		"""
		print "Using the sound graphic..."
		page = self.editor.obj
		page.use_soundgraphic = True
		#self.editor.set_member('graphic', page.soundgraphic)
		imagemaker.make_sub_images(page)
		#self.graphic_path =  os.path.join(page.home, page.soundthumbnail)
		#page.graphic = page.soundgraphic		# this *shouldn't be necessary, right?
		#self.editor.post_member('graphic')
		self.post()
		page.graphic_row.post()
		page.needs_rebuild = True
		page.changed = True
		self.graphic_row.post_status(ok=True)
		self.editor.refresh()
		
	def return_value(self):
		return(self.editor.obj.screenshot, self.graphic_row.ok)

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
		
		frame = tk.LabelFrame(master=self.tmpBox, relief=tk.GROOVE, text="Select " + self.name + " to Edit (Group: " + self.parent.current_grouptitle + ')', borderwidth=5)
		frame.lift(aboveThis=None)
		frame.grid(ipadx=10, ipady=40, padx=15, pady=15)
		# return the list...
		plist = eval("self.parent.current_group." + self.list)
		plist.sort(key=clclasses.createkey, reverse=True)
		
		self.my_option_menu = cltkutils.clOption_menu(frame, plist, self.member, command=self.menu_callback )
		self.my_option_menu.om.grid(column=1, row=1)
		#self.my_option_menu.om.configure(command=self.menu_callback)
		
		self.button = ttk.Button(frame, text="Edit", command=self.edit_select).grid(column=2, row=2)	
		self.tmpBox.wait_window(frame)
	
	def edit_select(self):
		"""
		Called when the "Edit" button is pushed
		"""
		print "edit_select called."
		selected_str = self.my_option_menu.var.get()
		if selected_str is None:
			print "Got a Null selection."
		print self.my_option_menu.var.get()
		self.selected = self.my_option_menu.dictionary[selected_str]
		self.tmpBox.destroy()
		
	def menu_callback(self, value):
		print "called back we were", value

					
class Check_button():
	"""
	A class to display a check button - simpler than the Row classes, 
	this is presumed to drop into an existing row somewhere.
	
	As the others, supplies  return_vakue, and set methods.
	Does not supply "post", the self.widget opject can be 
	
	if text is a list, two values:  [ unpressed-text, pressed-text ]
	(Not yet implemented)
	
	Returns: True or False (is button pressed?)
		
	"""
	def __init__(self, parent, text='Button', member='unsetbutton', value=False):
		
		self.parent = parent
		self.text = text
		self.member = member
		self.value = value
		
		self.row = 1			# default - leaves room  in row/column 0
		self.column = 1
		self.sticky = tk.NW
		
		self.new = True		# button pressed or changed?
		self.editable = True
		
		self.controlvar = tk.IntVar()
		self.widget = ttk.Checkbutton(parent, text=self.text, variable=self.controlvar)

	def post(self):
		"""
		Simply use grid to post it, 
		then set the var
		"""
		self.widget.grid(row=self.row, column=self.column, sticky=self.sticky)
		self.controlvar.set(self.value)
		
	def set(self, value):
		self.value = value
		self.new = False
		#self.post()
		
	def read(self):
		'''
		read the button
		'''
		self.value = self.controlvar.get()
		return

	def return_value(self):
		self.read()
		return(self.value, True)
	
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
		print "Edit Screen: new:",new
		self.parent = parent		# at this point, coLab_top
		self.object_type = 'Unset'
		self.new = new
		# let's do some verb determination now...
		if self.new:
			self.action = 'create'
		else:
			self.action = 'update'

		
		self.row=0
		self.column=0
		self.obj = object		# the object we're editing
		self.ok = not new
		self.edit_frame = None
		self.song_obj = None
		self.obj.changed = False
		self.obj.needs_rebuild = False
		
		object.editor = self	# so we can get back to the parent

		return
	
	
	def make_new(self):
	    """
	    Create a new page or song - basically just returns a legal dir name
	    Needs to not match anything in the exclusion list.   Limits characters
	    to a small set.  
	    """
	    """
	    self.editor = editor
	    self.object = object
	    self.sub_dir = sub_dir
	    #"""
	
	    type = os.path.split(self.sub_dir)[1]           # last part of the sub_dir (Page, Song) is the type...
	
	    self.editTop = tk.Toplevel()
	    self.editTop.transient(self.parent.top)
	    self.editTop.title("coLab: New " + type)
	    self.edit_frame = tk.LabelFrame(master=self.editTop, relief=tk.GROOVE, text=self.new_text, borderwidth=5)
	    self.edit_frame.lift(aboveThis=None)
	    self.edit_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
	    self.edit_frame.grab_set()              # we are the only game in town...
	
	    # we first open, it it's new, with a simple window for the name...
	
	
	    # get a little tricky - since we don't know the name yet - set a temp var in the 
	    # object:  sub_dir so that we can pass this, plus the final name, to set_paths...
	    self.obj.sub_dir = self.sub_dir
	    clclasses.set_paths(self.obj, self.obj.sub_dir)
	    #
	    # Just a simple "one-row" page - the "name"
	    row = Entry_row(self, "Name", "name", width=20)
	    self.name_row = row
	    # build the list of excluded names: the existing page list of the parent group...
	    print "PES: obj, group", self.obj.name, self.obj.group_obj.name
	
	    row.exclude_list = self.exclude_list
	    row.exclude_chars=' "/:'        # characters we don't want in file names...
	    row.ignore_case = True
	    row.new = self.new                              # as passed in
	    row.editable = self.new         # don't edit a file name that's already been created...
	    row.post()
	    row.widget.focus_set()
	    # cheat a little through u up quick descriptive label
	    # later...  columnspan 2
	
	    self.row = 8            # push these buttons down out of the way...
	    self.saveButton = ttk.Button(self.edit_frame, text="Save", command=self.save_new).grid(column=3, row=self.row)  # add  command=
	    self.quitButton = ttk.Button(self.edit_frame, text="Quit", command=self.quit).grid(column=4, row=self.row)
	
	    # stop and wait for the above window to return...
	    self.editTop.wait_window(self.edit_frame)
                

	def save_new(self):
		"""
		Simplified save - just receives the page/song name, creates the 
		directory, corrects the previously partial paths, and returns
		to allow the rest of the edit to begin...
		"""
		row_obj = self.name_row		# recall the one row...

		(value, ok) = row_obj.return_value()
		if not ok:
			self.quit_new()
			
		self.ok = ok
		self.obj.name = value
		print
		print "------------------"
		print "Creation of song/page", self.obj.name, self.ok
	
		print "Dump----------------"	
		#print self.obj.dump()
		print'---first home'
		# Add the new name to the so far partial paths...
		try:
			sub_dir = os.path.join(self.obj.sub_dir,  self.obj.name)
			home_dir = os.path.join(self.obj.coLab_home, sub_dir)
		except Exception as e:
			print "Cannot build new page sub_dir", e, sys.exc_info()[0]
			sys.exit(1)
	
		clclasses.set_paths(self.obj, sub_dir)		# Paths are now correct...
		print "Pagehome:", self.obj.home
		print "Pageroot:", self.obj.root

		self.object_type = self.obj.object_type
		print "Save new - object type:", self.object_type
		
		# 
		# A bit klunky for now but....
		# need to add this bit to the group's lists
		if self.object_type == 'Page':
			self.obj.group_obj.pagelist.append(self.obj)		# add the page name
			self.obj.group_obj.pagedict[self.obj.name] = self.obj	# name -> page obj
		elif self.object_type == 'Song':
			self.obj.group_obj.songlist.append(self.obj)		# add the song name
			self.obj.group_obj.songdict[self.obj.name] = self.obj	# name -> song obj
		self.obj.create()				# build the page dir structure, base data page.
		self.editTop.destroy()
		#self.new = False
		return							
	
	def quit_new(self):
		"""
		Handle the quit button from creating a new entity...
		"""
		self.editTop.destroy()
		self.ok = False
		return				
		
	def setup(self):	
		'''
		Handle initial setup duties for an edit object,
		open the top-level edit frame, etc....
		arguably could be part of __init__
		'''
		
		print "-----------Setup called!"
		if self.edit_frame is not None:
			print "---------------Destroy All Page Frames...---------"
			self.edit_frame.destroy()

		# Set up a dictionary listing the row objects, etc. that have the 
		# info we need.  By indexing by the "member" name - we can find the mas 
		# needed - or step through the whole list.
		self.editlist = dict()		
			
		#
		# Basically start over - this time with the name preset...
		self.editTop = tk.Toplevel()
		self.obj.top = self.editTop.winfo_toplevel()
		self.editTop.transient(self.parent.top)
		self.row=0
		self.column=0

		rowtext = self.obj.name + " (Group: " + self.parent.current_grouptitle + ')'
		self.edit_frame = tk.LabelFrame(master=self.editTop, relief=tk.GROOVE, text=rowtext, bd=100, padx=10, pady=10, borderwidth=5)
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
		for item in self.editlist:		# editlist is a dictionary of member names -> edit row objects
			row_obj = self.editlist[item]	# convert to a row object
			(value, ok) = row_obj.return_value()
			print "item.member:", row_obj.member, value, ok
			#  prev  value - have we changed...?
			try:	# this is not working yet....
				prev_value = eval ("self.obj.prev." + row_obj.member)
			except:
				logging.warning("No .prev member object:  %s." % row_obj.member)
			else:
				logging.info("previous value: " + prev_value)
				
			if row_obj.editable and not ok:
				self.ok = False
				self.bad_list.append(row_obj.text)
			
			# may not want to do this - but it likely doesn't matter as we 
			# will either correct it, or toss it.
			string = "self.obj." + item + ' = """' + str(value) + '"""'
			print "exec string:", string
			exec(string)
				
		
	def refresh(self):
		for i in self.editlist:
			self.editlist[i].read()
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
		
		Returns a tuple of long names ready to be assigned to an ObjectMenu for display
		"""
		if self.song_obj is None:
			part_name_list = [ 'All' ]
			partname_dict = { 'All': 'All' }	# build the one common part
		else:
			part_name_list = self.song_obj.partlist
			partname_dict = self.song_obj.partname_dict		# convert short names to long
		
		# map short and long names...
		self.part_obj.default = partname_dict[self.obj.part]
		l = []
		self.part_lookup = dict()
		for i in part_name_list:
			l.append(partname_dict[i])
			self.part_lookup[partname_dict[i]] = i
		return(tuple(l))
		
	def quit(self):
		'''
		Quit button handler - 
		if no changes, just quit.   If changes, or new,
		then return 
		'''
		
		if self.obj.changed or self.new:
			message = "You've made changes, quitting now will lose them.\n\nDo you still want to quit?"
			if not tkMessageBox.askokcancel('OK to quit?', message, parent=self.edit_frame, icon=tkMessageBox.QUESTION):
				return

		self.editTop.destroy()
		
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
		
		#'''
		if self.new:
			self.new_text = "New Page (Group: " + self.parent.current_grouptitle + ')'
			self.sub_dir = os.path.join('Group', self.parent.current_group.name, 'Page', )
			self.exclude_list = []	# names to not allow for a new page
			for nextpage in self.obj.group_obj.pagelist:
				self.exclude_list.append(nextpage.name)
			self.make_new()	
			if not self.ok:
				return
		#'''
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
		row.value = self.obj.description
		row.post()
		
		#--- Resolution
		#self.obj.song_obj = None
		menu = Resolution_menu_row(self, "Resolution", "media_size")

		self.editlist[menu.member] =  menu
		menu.post()
		menu.ok = None		# always good....
		menu.post_status()	
		"""  RBF:  Major Kludge Alert - this is just get create page working...  track this down!!!!!!!"""
		self.res_obj = menu

		#---- Sound file...
		# (new version, menu based)
		row = Graphic_menu_row_soundfile(self, "Soundfile", 'soundfile')
		self.editlist[row.member] =  row
		row.post()
		
		#---- Strict Mode
		bonus_frame = ttk.Frame(self.edit_frame)
		bonus_frame.grid(row=self.row-2, column=3, sticky=tk.NW)

		button = Check_button(bonus_frame, text='Strict Graphics (slower)', member='strict_graphic', value=self.obj.strict_graphic)
		button.post()
		self.editlist[button.member] = button
		
		#---- Duration - display only ...
		row = Entry_row(self, "Duration", "duration", width=8)
		row.editable = False
		self.editlist[row.member] =  row
		row.post()
		self.duration_obj = row
		
		#----- graphic theme (color scheme)
		menu = Theme_menu_row(self, 'Theme', 'graphic_theme')		
		self.editlist[menu.member] = menu
		menu.post()
		
		#---- graphic file...
		# (new version, menu based)
		row = Graphic_menu_row_screenshot(self, "Graphic", 'screenshot')
		self.editlist[row.member] =  row
		row.post()
		self.obj.graphic_row = row      # we'll want this later....
		
		#----  x Start and Stop - eventually done with graphic input...
		row = Entry_row(self, "xStart", "xStart", width=5)
		row.editable = False
		self.editlist[row.member] =  row
		row.post()
		
		row = Entry_row(self, "xEnd", "xEnd", width=5)
		row.editable = False
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
		
		self.editlist[menu.member] =  menu
		if self.action == 'update':
			menu.default = page.song	# RBF: This is wrong  it gets fixed later, but....
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

		imagemaker.make_sub_images(page)
			

	def save(self):
		print
		print "------------------"
		print "Dump of page", self.obj.name
		
		#print "Dump----------------"	
		#print self.obj.dump()
		print'---first home'
		try:
			sub_dir = os.path.join('Group', self.obj.group, 'Page',  self.obj.name)
			home_dir = os.path.join(self.obj.coLab_home, sub_dir)
		except Exception as e:
			print "Cannot build new page sub_dir", e, sys.exc_info()[0]
			sys.exit(1)
	
		clclasses.set_paths(self.obj, sub_dir)		# Paths are now correct...
		print "Pagehome:", self.obj.home
		print "Pageroot:", self.obj.root
		
		self.read()
		
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
		
		message = "This will " + self.action + " the page: " + self.obj.name
		message += "\n\nOK?"
		if u'no' == tkMessageBox.askquestion('OK to save?', message, parent=self.edit_frame, icon=tkMessageBox.QUESTION):
			print "return"
			return

		if self.action == 'create':
			# need to add this bit to the group's lists
			self.obj.group_obj.pagelist.append(self.obj)		# add the page name
			self.obj.group_obj.pagedict[self.obj.name] = self.obj	# name -> page obj
			self.obj.create()				# build the page dir structure, base data page.
			self.editTop.destroy()
					
		# We're good - let's post this...
		clclasses.convert_vars(self.obj)
		self.obj.post()
		# Now build the frames and video in the background...
		#page_thread=threading.Thread(target=rebuild_page_edit, args=(self,))
		page = self.obj
		page.editor = None
		htmlgen.pagegen(page.group_obj, page)
		if page.needs_rebuild:
			self.parent.render_engine.add_render(sub_dir)
		#page.editor = self	# pass in the page, but reference this editor obj.
		#page_thread=threading.Thread(target=rebuild.render_page, args=(page,))
		#page_thread.start()
		#rebuild_page_edit(self)
		
		self.editTop.destroy()
			
		'''
	def quit(self):
		if self.obj.changed:
			message = "You've made changes, quitting now will lose them.\n\nDo you still want to quit?"
			if not tkMessageBox.askokcancel('OK to quit?', message, parent=self.edit_frame, icon=tkMessageBox.QUESTION):
				return(None)
		self.editTop.destroy()
		'''

		
def create_new_page(coLab_top):
	"""
	Does the initial setup to call the edit screen and leaves.
	The rest is done there.
	"""
	
	print "New page"
	group_name = coLab_top.current_grouptitle		# currently selected group
	this_group = coLab_top.current_group
	
	print "My group is:", group_name, this_group.title
	
	print "Group info:", this_group.subtitle
	
	new_page = clclasses.Page(None)
	new_page.group_obj = this_group
	new_page.group = this_group.name
	new_page.coLab_home = this_group.coLab_home		# just enough path to get us started..
	
	new_page.master = coLab_top.master
	coLab_top.editor = Page_edit_screen(coLab_top, new_page, new=True)
	
	
def edit_page(coLab_top):
	print "edit Page"
	
	selector = Select_edit(coLab_top, "pagelist", "desc_title", "Page")	# pick a page...
	print "ep hello"
	selector.post()
	print "ep post post"
	try:
		page = selector.selected
	except:
		page = None
	if page is None:
		return
	print "Selected:", page.name, page.locked
	#if page.locked:
	#	coLab_top.master.beep()
	#	return
	page.master = coLab_top.master
	coLab_top.editor = Page_edit_screen(coLab_top, page, new=False)


def create_new_song(coLab_top):
	print "new song"
	"""
	Does the initial setup to call the edit screen and leaves.
	The rest is done there.
	"""
	
	print "New song"
	group_name = coLab_top.current_grouptitle		# currently selected group
	this_group = coLab_top.current_group
	
	print "My group is:", group_name, this_group.title
	
	print "Group info:", this_group.subtitle
	
	new_song = clclasses.Song(None)
	new_song.group_obj = this_group
	new_song.group = this_group.name
	new_song.coLab_home = this_group.coLab_home		# just enough path to get us stared..
	
	coLab_top.editor = Song_edit_screen(coLab_top, new_song, new=True)
	
	
def edit_song(coLab_top):

	print "edit Song"
	
	selector = Select_edit(coLab_top, "songlist", "desc_title", "Song")	# pick a song...
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
	
	coLab_top.editor = Song_edit_screen(coLab_top, song, new=False)	

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
			self.new_text = "New Song (Group: " + self.parent.current_grouptitle + ')'
			self.sub_dir = os.path.join('Group', self.parent.current_group.name, 'Song', )
			self.exclude_list = []	# names to not allow for a new page
			for nextsong in self.obj.group_obj.songlist:
				self.exclude_list.append(nextsong.name)
			self.make_new()	
			if not self.ok:
				return
				
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
		row.value = self.obj.description
		row.post()
		
		#"""
		self.saveButton = ttk.Button(self.edit_frame, text="Save", command=self.save).grid(column=3, row=self.row)	# add  command=
		self.quitButton = ttk.Button(self.edit_frame, text="Quit", command=self.quit).grid(column=4, row=self.row)
		
		
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
			print "Cannot build new page sub_dir", e, sys.exc_info()[0]
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
			message = "This will " + self.action + " the song: " + self.obj.name
			message += "\n\nOK?"
			if not tkMessageBox.askquestion('OK to save?', message, parent=self.edit_frame, icon=tkMessageBox.QUESTION):
				print "return"
				return
	
	
			if self.action == 'create':
				# need to add this bit to the group's lists
				self.obj.group_obj.songlist.append(self.obj)		# add the page name
				self.obj.group_obj.songdict[self.obj.name] = self.obj	# name -> page obj
				self.obj.create()				# build the page dir structure, base data page.
				self.editTop.destroy()
				self.new = False
				return							# just create the dir and 1-entry data file - we only have the name so far
						
			# We're good - let's post this...
			song = self.obj
			clclasses.convert_vars(song)
			song.post()

			# Now rebuild the song...
			song.editor = None
			htmlgen.songgen(song.group_obj, song)
			if song.needs_rebuild:
				self.parent.render_engine.add_render(sub_dir)
			#page.editor = self	# pass in the page, but reference this editor obj.
			#page_thread=threading.Thread(target=rebuild.render_page, args=(page,))
			#page_thread.start()
			#rebuild_page_edit(self)
			
			self.editTop.destroy()		


	
#------ interface to main routine...
import coLab
def main():
	print "Colab Main"
	coLab.main()
	
if __name__ == '__main__':
	main()