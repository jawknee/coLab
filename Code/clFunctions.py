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


def set_status(obj, ok = False):
	"""
	Set the status of the widget - log the state, and update
	the status column, should work for most/all row classes...
	"""
	obj.ok = ok
	if ok:
		color = '#2f2'	# bright green
		txt = 'OK'
	else:
		color = '#f11'	# bright red
		txt = 'X'
		
	obj.status.configure(fg=color)
	obj.statusVar.set(txt)


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
			self.nameVar.set(self.value)
			self.ok = True		# since we can't change it - it's good
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
			self.match = tk.Label(self.parent.page_frame, textvariable=self.matchVar, justify=tk.LEFT)
			self.match.grid(row=self.row, column=self.column + 3, rowspan=6, columnspan=2, sticky=tk.NW)		
	
	def validate_entry(self, why, what, would, how):
		"""
		Interface that calls the actual validation, then posts
		the resulting status.
		"""
		print "Validate!!!!!!"
		"""
		r_code = self.vld8_entry_base(why, what, would, how)
		self.post_match()
		return(r_code)
		
	def vld8_entry_base(self, why, what, would, how):
		#"""
		
		"""
		Do the actual validation - the entry object in self.widget
		Check for excluded characters - if any, beep and scoot (reject).
		Check for  zero-length, (bad), and for possible (ok) and exact
		(bad) matches in the exclude list.   
		
		Updates the status column based on what's 
		"""
		print "vld8_entry_base:", why, what, how
		self
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
	
class Entry_menu():
	"""
	Just put up a OptionMenu from the provided list..)
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

		self.widget.grid(column=self.column+2, row=self.row, sticky=tk.W)
		
		self.statusVar = tk.StringVar()
		self.status = tk.Label(self.parent.page_frame, textvariable=self.statusVar, fg='#ca1')
		self.status.grid(row=self.row, column=self.column + 1)
		self.statusVar.set('-')
		
		
	def handle_menu(self, name):
		#new_name = self.gOpt.get()		# not needed here, name is what we want.
		
		# if the menu item starts with a "-", it is an unacceptable value
		set_status(self, name[0] != '-')
		
		print "and now..."
		#time.sleep(4)
		self.parent.read_page()
		if self.member == 'song':
			# Special case for a song:  reload the part list..
			print "SETTING Song........", name, name
			
			self.parent.obj.song = name
			try:
				group = self.parent.obj.group_obj
			except Exception as e:
				print "------- No such group found as part of", self.parent.obj.name
				print "---- fix  - for now, returning"
				return
			
			song_obj = group.find_song(name)
			if song_obj == None:
				print "No such song object found for:", name
				
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
		return(self.gOpt.get(), self.ok)
	
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
		
		self.pageTop = tk.Toplevel()
		self.pageTop.transient(parent)
		self.row=0
		self.column=0
		self.obj = page		# the object we're editing
		self.new = new
		self.page_frame = None
		self.song_obj = None
		self.setup()
				
	def setup(self):		# RBF: at least check to see if we ever call  this - I'm guessing now...
		print "-----------Setup called!"
		if self.page_frame is not None:
			print "---------------Destroy All Page Frames...---------"
			time.sleep(2)
			self.page_frame.destroy()
			time.sleep(2)
			
		self.page_frame = tk.LabelFrame(master=self.pageTop, relief=tk.GROOVE, text="New Page (Group: " + self.parent.current_groupname + ')', borderwidth=5)

		self.page_frame.lift(aboveThis=None)
		self.page_frame.grid(ipadx=10, ipady=10, padx=25, pady=15)
		
		
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
		row = Entry_row(self, "Name", "name", width=20)
		# build the list of excluded names: the existing page list of the parent group...
		print "PES: obj, group", self.obj.name, self.obj.group_obj.name
		for nextpage in self.obj.group_obj.pagelist:
			row.exclude_list.append(nextpage.name)
		row.exclude_chars=' "/:'	# characters we don't want in file names...
		row.ignore_case = True
		row.new = self.new				# as passed in
		row.editable = self.new		# don't edit a file name that's already been created...
		
		self.editlist.append(row)
		row.post()
		
		#---- Descriptive title, "unique", but flexible with case, spaces, etc...
		row = Entry_row(self, "Descriptive title", "desc_title", width=30)
		# exclude existing titles...
		for nextpage in self.obj.group_obj.pagelist:
			row.exclude_list.append(nextpage.desc_title)
		self.editlist.append(row)
		row.post()
		
		#---- Fun title - just for fun...
		
		row = Entry_row(self, "Fun title", "fun_title", width=50)
		self.editlist.append(row)
		row.post()
		
		#---- Duration - display only ...
		row = Entry_row(self, "Duration", "duration", width=5)
		self.editlist.append(row)
		row.post()
		
		#---- Description: text object
		#self.editlist.append(edit_pair_text(self, "Description", "description", width=50))
		
		#---- Screen Shot
		# (for now, the name - later: the picture (thumbnail)
		row = Entry_row(self, "Screen Shot", "screenshot", width=20)
		self.editlist.append(row)
		row.post()
		
		#----  x Start and Stop - eventually done with graphic input...
		row = Entry_row(self, "xStart", "xStart", width=5)
		self.editlist.append(row)
		row.post()
		
		row = Entry_row(self, "xEnd", "xEnd", width=5)
		self.editlist.append(row)
		row.post()
		
		#"""
		#----   fps: should be calculated...
		row = Entry_row(self, "fps", "fps", width=5)
		self.editlist.append(row)
		row.editable = False
		row.post()
		#"""
		
		#--- Song
		#row = Entry_row(self, "Song", "song", width=10)
		#self.editlist.append(row)
		#row.post
		print "hello - time for a song list..."
		for i in self.obj.group_obj.songlist:
			print "Song name:", i.name
		self.obj.song_obj = None
		#self.obj.song = 'JDJ-5'
		menu = Entry_menu(self, "Songs", "song")
		l = []
		if self.new:
			l = ['-select song-']		# build a list of song names...
		for i in self.obj.group_obj.songlist:
			l.append(i.name)
			if i.name == self.obj.song:
				self.song_obj = i		# remember this object
		l.append('-New song-')
			
		menu.titles = tuple (l)		# Convert to a tuple...
		
		menu.default = self.obj.song
		self.editlist.append(menu)
		print "Posting that menu"
		menu.post()
			
		#  Part - depends on the song selected.
		print "part time..."
		menu = Entry_menu(self, "Part", "part")
		self.part_obj = menu		# save this for song changes (implying a new part list)
		menu.titles = self.build_part_list()
		self.editlist.append(menu)
		
		menu.post()
		
		#"""
		self.saveButton = tk.Button(self.page_frame, text="Save", command=self.save_page).grid(column=3, row=self.row)	# add  command=
		self.saveButton = tk.Button(self.page_frame, text="Quit", command=self.my_quit).grid(column=4, row=self.row)
		
		# get a little tricky - since we don't know the name yet - set a temp far in the 
		# page:  sub_dir so that we can pass this, plus the final name, to set_paths...
		self.obj.sub_dir = os.path.join('Group', self.parent.current_groupname, 'Page', )
	def refresh(self):
		for i in self.editlist:
			i.post()
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
		for item in self.editlist:
			print item.member, ":", item.return_value()
			(value, ok) = item.return_value()
			if not ok:
				self.ok = ok
				print "Value", value, "of", item.text, "is out of range."
			
			# may not want to do this - but it likely doesn't matter as we 
			# will either correct it, or toss it.
			string = "self.obj." + item.member + ' = "' + str(value) + '"'
			print "exec string:", string
			exec(string)
		
	def save_page(self):
		print
		print "------------------"
		print "Dump of page", self.obj.name
		self.read_page()
		print "Dump----------------"	
		print self.obj.dump()
		print'---first home'
		sub_dir = os.path.join(self.obj.sub_dir, self.obj.name)
		clclasses.set_paths(self.obj, sub_dir)
		print self.obj.home
		if self.ok:
			print "All good:  this would post"
		else:
			print "Still something wrong - see above"
			
			
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
	
	new_page = clclasses.Page(None)
	new_page.group_obj = this_group
	
	parent.page = Page_edit_screen(parent, new_page, new=True)
	
	
	
def edit_page(parent):
	print "edit Page"
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