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

import time		# rbf: unless needed....

import clclasses
import Tkinter as tk
import ttk


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
		self.editable = True
		
		self.exclude_list = []		# a list of items not allowed (e.g., current file names)
		self.exclude_chars = '"'	# current implementation does not allow " n stored strings
		self.ignore_case = False	# Set to true for file names, etc.
		self.match = None		
		self.new = parent.new		# when true, items are ghosted / replaced on first key  
		self.editable = True		# occasionally we get one (existing file name) that we don't want to edit...
		
		self.row = parent.row		# parent keeps track of row / column
		parent.row += 1				# move the  parent row down one...
		self.column = parent.column
				
		# Validation callback parameters
		self.callback = self.validate_entry	
		self.validate = 'key'
		self.subcodes =  ('%d', '%S', '%P')
		
		
	def post(self):
		"""
		Create a simple row with the text on the left (right just.), and the current value on the
		right (left justified).  An indicator sits in between (green check, orange ?, red X).
		If an exclude list is given, it can be used by the validation routine.
		"""
		# write the base label...
		self.label = tk.Label(self.parent.page_frame, text=self.text+":", justify=tk.RIGHT)
		self.label.grid(row=self.row,column=self.column, sticky=tk.E)
		
		# Now we build a string that is the name of the associated variable.   Then we use eval and exec to
		# deal with it.
		print "self.member", self.member
		self.value = eval("self.parent.obj." + self.member)	# convert the variable name to its value
		print "value", self.value
		#print "ept: new?:", self.new
		print "post:  my new is:", self.member, self.new
		self.nameVar = tk.StringVar()
		
		# if not editable - just display as a label...
		print "vobj - editable:", self.editable
		if not self.editable:
			self.widget = tk.Label(self.parent.page_frame, textvariable=self.nameVar, justify=tk.LEFT)
			self.widget.grid(row=self.row,column=self.column + 2, sticky=tk.W)
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
			
			self.statusVar = tk.StringVar()
			self.status = tk.Label(self.parent.page_frame, textvariable=self.statusVar, fg='#ca1')
			self.status.grid(row=self.row, column=self.column + 1)
			self.statusVar.set('-')
			
			self.matchVar = tk.StringVar()
			self.match = tk.Label(self.parent.page_frame, textvariable=self.matchVar, anchor=tk.NW)
			self.match.grid(row=self.row, column=self.column + 3, rowspan=6, sticky=tk.N)		
	
	def validate_entry(self, why, what, would):
	
		"""
		Do the actual validation - the entry object in self.widget
		Check for excluded characters - if any, beep and scoot (reject).
		Check for  zero-length, (bad), and for possible (ok) and exact
		(bad) matches in the exclude list.   
		
		Updates the status column based on what's 
		"""
		print "vld8_entry_base:", why, what
		
		if why == '-1':
			print"Focus: we don't need no stinkin' focus."
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
			
		#--are we new?   If so, blank what's there, update the color, and replace with any addition
		print "self.new:", self.new
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
			self.status.configure(fg='#f11')	# Red
			self.statusVar.set('X')
			print "Bad-==========-Zero length"
			return r_code
		
		#-- match?	set up a lambda function - lower the string to ignore, just return it, otherwise.
		if self.ignore_case:
			f = lambda x: x.lower()
		else:
			f = lambda x: x
			
		# Check for a match so far on any string - if so, just display 
		# it - if an exact match - flag as  Bad
		good = True
		for item in self.exclude_list:
			if f(item).find(f(would)) == 0:		# matches at the start
				if f(item) == f(would):
					print "BAD:  matches", item
					
					self.match.configure(fg='#f11')
					self.matchVar.set(item)
					good = False
					self.status.configure(fg='#f11')
					self.statusVar.set('X')
				else:
					print "partial match:", item,  '/', would
		if good:		# rbf:   this should be a call
			self.status.configure(fg='#2f2')
			self.statusVar.set('OK')
		else:
			self.status.configure(fg='#f11')
			self.statusVar.set('X')			
		print "evaL Return:", r_code
		return r_code			
	
class Entry_vld8():
	"""
	create a container for the bits we need to validate a specific
	entry - create a reasonable default otherwise.   
	Passed into edit_pair_text (or invoked from there if not passed).
	"""
	def __init__(self, validate='key', callback=None, subcodes=('%d', '%S', '%P')):
		self.validate=validate
		
		widget = tk.Frame()	# RBF: don't want to accum. widgets - assoc. with a parent?
		
		# ever so slightly trick - the parms for validate command are the call back 
		# and substitution calls - create a tuple of those to pass all at once
		if not callback:
			callback = self.vld8_entry_base
		
		print "Ev_init: callback is:", callback
		l = [ widget.register(callback) ]		# first part is the registration of the call back.
		#widget.destroy()
		for sc in subcodes:
			l.append(sc)
		self.validatecommand = tuple(l)	# make into a tuple
		
		self.exclude_list = []	# a list of items not allowed (e.g., current file names)
		self.exclude_chars = '"'	# current implementation does not allow " n stored strings
		self.ignore_case = False	# Set to true for file names, etc.
		self.match = None		
		self.new = None			# when true, items are ghosted / replaced on first key  
		self.editable = True		# occasionally we get one (existing file name) that we don't want to edit...
		
	def vld8_entry_base(self, why, what, would):
		"""
		Do the actual validation - the entry object in self.widget
		Check for excluded characters - if any, beep and scoot (reject).
		Check for  zero-length, (bad), and for possible (ok) and exact
		(bad) matches in the exclude list.
		"""
		print "vld8_entry_base:", why, what
		
		if why == '-1':
			print"Focus: we don't need no stinkin' focus."
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
			
		#--are we new?   If so, blank what's there, update the color, and replace with any addition
		print "self.new:", self.new
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
			self.widget.configure(fg=fg, validate=self.validate, validatecommand=self.validatecommand )
			self.new = False
			r_code = False	# 
			
		print "Would is:", would
		#-- zero length?  
		if  len(would) == 0:
			self.status.configure(fg='#f11')
			self.statusVar.set('X')
			print "Bad-==========-Zero length"
			return r_code
		
		#-- match?	set up a lambda function - lower the string to ignore, just return it, otherwise.
		
		if self.ignore_case:
			f = lambda x: x.lower()
		else:
			f = lambda x: x
			
		# Check for a match so far on any string - if so, just display 
		# it - if an exact match - flag as  Bad
		good = True
		for item in self.exclude_list:
			if f(item).find(f(would)) == 0:		# matches at the start
				if f(item) == f(would):
					print "BAD:  matches", item
					
					self.match.configure(fg='#f11')
					self.matchVar.set(item)
					good = False
					self.status.configure(fg='#f11')
					self.statusVar.set('X')
				else:
					print "partial match:", item,  '/', would
		if good:		# rbf:   this should be a call
			self.status.configure(fg='#2f2')
			self.statusVar.set('OK')
		else:
			self.status.configure(fg='#f11')
			self.statusVar.set('X')			
		print "evaL Return:", r_code
		return r_code			

class edit_pair_text():
	"""
	Simple text - an "Entry" widget
	"""
	def __init__(self, parent, text, member, width=15, validate_obj=None):	
		"""
		Create a simple row with the text on the left (right just.), and the current value on the
		right (left justified).  An indicator sits in between (green check, orange ?, red X).
		If an exclude list is given, it can be used by the validation routine.
		"""
		# write the base label...
		self.label = tk.Label(parent.page_frame, text=text+":", justify=tk.RIGHT).grid(row=parent.row,column=parent.column, sticky=tk.E)
		
		# Now we build a string that is the name of the associated variable.   Then we use eval and exec to
		# deal with it.
		self.varName = member
		print "self.varName", self.varName
		value = eval("parent.obj." + self.varName)
		print "value", value
		#print "ept: new?:", self.new
		#
		# normal: set up an entry object...
		if validate_obj is None:	# create a generic entry validation
			print "Creating stock vld8 obj"
			validate_obj=Entry_vld8()		# default entry validation class
		
		# get a little tricky here - if the object doesn't know if it's new, 
		# pull that from the parent object...
		if validate_obj.new is None:
			validate_obj.new = parent.new
			print "ept: setting v-obj.new to:", validate_obj.new
			
		print "We have val-obj"
		
		validate_obj.nameVar = tk.StringVar()
		
		vcommand=validate_obj.validatecommand
		print "we have v-cmd:", vcommand
		
		# Now we build a string that is the name of the associated variable.   Then we use eval and exec to
		# deal with it.
		self.varName = member
		print "self.varName", self.varName
		
		
		
		# if not editable - just display as a label...
		print "vobj - editable:", validate_obj.editable
		if not validate_obj.editable:
			validate_obj.widget = tk.Label(parent.page_frame, textvariable=validate_obj.nameVar, justify=tk.LEFT).grid(row=parent.row,column=parent.column + 2, sticky=tk.W)
			print "non-edit validate_obj:", validate_obj.widget
		else:
		
			print "vcmd ", vcommand, "validate:", validate_obj.validate
			fg = '#000'		# black
			if validate_obj.new:
				fg = '#AAA'	# light gray
			
			validate_obj.widget = tk.Entry(parent.page_frame, textvariable=validate_obj.nameVar, width=width, fg=fg, validate=validate_obj.validate, validatecommand=validate_obj.validatecommand )
			print "v-obj widget created:", validate_obj.widget
			validate_obj.widget.grid(row=parent.row, column=parent.column + 2, sticky=tk.W)
			
			validate_obj.statusVar = tk.StringVar()
			validate_obj.status = tk.Label(parent.page_frame, textvariable=validate_obj.statusVar)
			validate_obj.status.grid(row=parent.row, column= parent.column + 1)
			validate_obj.statusVar.set('-')
			
			validate_obj.matchVar = tk.StringVar()
			validate_obj.match = tk.Label(parent.page_frame, textvariable=validate_obj.matchVar, anchor=tk.NW)
			validate_obj.match.grid(row=parent.row, column=parent.column + 3, rowspan=6, sticky=tk.N)
	
		value = eval("parent.obj." + self.varName)
		print "value", value

		print "Setting name Var", value
		validate_obj.nameVar.set(str(value))

		print "set"

		validate_obj.nameVar.set(str(value))
		parent.row += 1
		
		
	
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
		self.pageTop = tk.Toplevel()
		self.pageTop.transient(parent)
		self.page_frame = tk.LabelFrame(master=self.pageTop, relief=tk.GROOVE, text="New Page (Group:" + parent.current_groupname + ')', borderwidth=5)

		self.page_frame.lift(aboveThis=None)
		self.page_frame.grid(ipadx=10, ipady=10, padx=25, pady=15)
		
		self.row=0
		self.column=0
		self.obj = page		# the object we're editing
		self.new = new
		
		self.editlist = []	# becomes a list of edit pair objects
		
		#================
		# Build page editor
		#================
		#
		# Build a list of basically name/value pairs
		# Each pair (e.g., title and entry widget), is added to a list, 
		# on "save" we retrieve each
		
		#---- name - this is a file name so we need to be somewhat strict about characters
		# gather the names of all the pages to exclude (dir name)
		
		thisrow = Entry_row(self, "Name", "name", width=15)
		# build the list of excluded names: the existing page list of the parent group...
		for nextpage in self.obj.group_obj.pagelist:
			thisrow.exclude_list.append(nextpage.name)
		thisrow.exclude_chars=' "/:'	# characters we don't want in file names...
		thisrow.ignore_case = True
		thisrow.new = new				# as passed in
		thisrow.editable = new		# don't edit a file name that's already been created...
		
		self.editlist.append(thisrow)
		thisrow.post()
		
		thisrow = Entry_row(self, "Descriptive title", "desc_title", width=30)

		for nextpage in self.obj.group_obj.pagelist:
			thisrow.exclude_list.append(nextpage.desc_title)
		self.editlist.append(thisrow)
		thisrow.post()
		"""
		self.editlist.append(edit_pair_text(self, "Fun title", "fun_title", width=50))
		
		vld8_obj = Entry_vld8()
		vld8_obj.editable = False
		self.editlist.append(edit_pair_text(self, "Duration", "duration", width=5, validate_obj=vld8_obj))
		
		#self.editlist.append(edit_pair_text(self, "Description", "description", width=50))
		self.editlist.append(edit_pair_text(self, "ScreenShot", "screenshot", width=20))
		self.editlist.append(edit_pair_text(self, "Thumbnail", "thumbnail", width=20))
		self.editlist.append(edit_pair_text(self, "xStart", "xStart", width=5))
		self.editlist.append(edit_pair_text(self, "xEnd", "xEnd", width=5))
		self.editlist.append(edit_pair_text(self, "fps", "fps", width=5))
		self.editlist.append(edit_pair_text(self, "Projects", "project", width=10))
		self.editlist.append(edit_pair_text(self, "Associated", "assoc_projects", width=30))
		self.editlist.append(edit_pair_text(self, "Song", "song", width=10))
		self.editlist.append(edit_pair_text(self, "Part", "part", width=10))
		#"""
		self.saveButton = tk.Button(self.page_frame, text="Save", command=self.save_page).grid(column=3, row=self.row)	# add  command=
		self.saveButton = tk.Button(self.page_frame, text="Quit", command=self.my_quit).grid(column=4, row=self.row)
		
		# get a little tricky - since we don't know the name yet - set a temp far in the 
		# page:  sub_dir so that we can pass this, plus the final name, to set_paths...
		self.obj.sub_dir = os.path.join('Group', parent.current_groupname, 'Page', )
	
	def save_page(self):
		print
		print "------------------"
		print "Dump of page", self.obj.name
		for item in self.editlist:
			print item.varName, ":", item.nameVar.get()
			string = "self.obj." + item.varName + ' = "' + str(item.nameVar.get()) + '"'
			print "exec string:", string
			exec(string)
		print "Dump----------------"	
		print self.obj.dump()
		print'---first home'
		sub_dir = os.path.join(self.obj.sub_dir, self.obj.name)
		clclasses.set_paths(self.obj, sub_dir)
		print self.obj.home
			
			
	def my_quit(self):
		self.pageTop.destroy()
		
		
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
	
	new_page = clclasses.Page("new-page")
	new_page.group_obj = this_group
	
	parent.page = Page_edit_screen(parent, new_page, new=True)
	
	
	
def edit_page(parent):
	print "edit Page"
def create_new_song(parent):
	print "new song"
def edit_song(parent):
	print "edit song"