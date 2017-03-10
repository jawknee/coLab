#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" coLab - a music collaboration tool.
	
	This tool is the front end used to create the coLab web site.
	It takes input of audio files (currently .aiff) and optionally
	graphics (typically a screen shot) and builds the web various pages
	and links to allow for musical collaboration.
	
	Makes extensive use of the Tkinter and PIL (Python Imaging Library)
	functions.
	
	It is currently designed to be a single program - starting with this module.
"""

import os
import sys
import logging
import time

import Tkinter as tk
import tkFileDialog
import ttk
import tkMessageBox
import imp

from PIL import Image, ImageTk

import clutils
import clFunctions
import clclasses
import cltkutils
import clSchedule
import rebuild
import imagemaker

class Colab():
	""" Basic class for the colab front end - holder of the main window and basic methods. 
	
	It all starts here.  The "top" element is the root of the Tkinter GUI.
	It holds the graphic elements, as well as the basic methods for performing
	the basic tasks.
	
	This tool is the interface to the coLab data structure, consisting
	of a hierarchy:  Groups, Projects (nyi), Songs, and Pages.  
	
	Basic functions include creating and editing (eventually
	projects), songs, and pages, and updating the external web
	site. 
	"""
	
	def __init__(self, master=None):
		""" Create a frame instance, populate it with the various gadgets.
		
		We step through the data structure, finding the groups, and loading the 
		current one (groups are currently loaded when first referenced). 
		The group data are then added or modified as directed by the buttons.
		
		As each group is selected, we update the title and snapshot graphics, 
		and the corresponding data and editing objects...
		"""
		# Get the system wide config - find the local config file and 
		# set the basic paths to content, code, etc.

		self.master = master
		
		try:
			self.conf=clutils.get_config()
			logging.info ("conf shows: %s", self.conf.coLab_home)
		except ImportError:
			logging.error("Cannot find config.")
			sys.exit(1)		# fatal...
		
		self.home = self.conf.coLab_home   # can be overridden - not currently anticipated
			
		try:
			option_file = os.path.join(self.conf.coLab_home, ".coLab_tkOptions")
			#self.winfo_toplevel().option_readfile(option_file, 20)
			self.master.option_readfile(option_file, 80)
			#self.top.option_add('background', '#66a') 
		except:
			logging.error("Error reading optionfile: %s", option_file)
			sys.exit(1)
			
			
		# call the parent class init - initializes ourselves
		self.top = tk.Frame(self.master)
 
		self.master.geometry('+80+80')
		self.master.grid()	
		self.top.grid()
		
		# load the initial table of lists
		# a dictionary indexed by name, pointing dir name 
		# The "name" is what's returned from the menu - thus the need for translation
		self.load_group_list()
		self.edit_lock = False
		
		self.render_engine = rebuild.Render_engine(self.master)
			   
	   
		# let's make sure mamp is running...
		#clSchedule.start_mamp()	 # (let's not)

		self.get_last_group()	# set the initial group, and load it...
		#self.set_group()		# update the internal group structure
		self.createMainWidgets()	# put the initial widgets up...
		self.set_group_from_menu(menu_grouptitle="None")
		#self.place_group_shot()
		self.master.mainloop()

		# some sort of a GUI loop here...
		
	def get_last_group(self):
		""" returns the name of the last used group
		
		 Retrieve the "current" group name from 
		... some data structure... - for now, 
		we just hard code it until we have the data laid out.
		"""
		self.current_grouptitle = "Catharsis"
		#self.current_grouptitle = "Johnny's Music"
		#self.current_grouptitle = "Test Group"
		#self.current_grouptitle = "South Bay Philharmonic"

		logging.info("Default group:  %s", self.current_grouptitle)
		
	def set_group_from_menu(self, menu_grouptitle='None'):
		""" Retrieve the menu value and set that as the current group name """
		logging.info("!  Click !---------------------------")
		# Called with menu_grouptitle = None for initial setup...
		if menu_grouptitle == "None":
			menu_grouptitle = self.gOpt.get()
		self.current_grouptitle = menu_grouptitle
	
		logging.info("set_group_from_menu - setting current_grouptitle to %s", self.current_grouptitle)
		self.set_group()
		
	def set_group(self):
		""" point to the group object
		
		Make sure the group specified in self.current_grouptitle
		is loaded and displayed.   If we haven't yet, 
		load the group.	
		
		We keep a list of groups, which we load as they're referenced
		and a dictionary of groups by dir name (group name).
		"""
		try:
			thisname = self.current_grouptitle
		except:
			logging.error("Fatal error: set_group called with no current_grouptitle set.")
			sys.exit(1)
		
		group_dir = self.grouplistdict[thisname]
		logging.info("set_group: group_dir %s, group name: %s", group_dir, thisname)

		# Do we know about this group yet - i.e., is it loaded?
		try:	# do we even have the list yet?
			self.group_list
		except:
			logging.info("New group list")
			self.group_list = dict()	# new dictionary...		#RBF   this is a dict, not a list
		 
		logging.info("group_dir pre list test %s", group_dir)
		try:
			self.current_group = self.group_list[thisname]
		except KeyError:
			logging.info("Nope - don't know group %s loading now...", thisname)
			#try:
			logging.info("group_dir pre pre group inst: %s", group_dir)
			self.current_group = clclasses.Group(group_dir)
			logging.info("group_dir post group Inst - dir: %s, name %s", group_dir, self.current_group.name)
			self.current_group.load()				
			logging.info("group_dir post group load - dir: %s, name: %s", group_dir, self.current_group.name)
			self.group_list[thisname] = self.current_group
			logging.info("This group name: %s", self.current_group.name)
			#except Exception as e:
			#	print "Internal Failure: cannot load ", thisname, sys.exc_info()[0], e
			#	sys.exit(0)
		self.place_group_shot()
		self.function_buttons()
        
	def createMainWidgets(self):
		""" Put up the main, initial set of widgets """
		self.master.title('coLab')
		#self.master.configure(bg=self.bg)
		self.master.lift(aboveThis=None)
		
		self.main_frame=tk.LabelFrame(self.top, text='coLab')
		self.main_frame.grid(padx=10, pady=10, ipadx=10, ipady=10)

		try:
			self.display_group_list()
			self.place_logo()
		except TypeError, info:
			logging.warning("TypeError", exc_info=True)
		except Exception as e:
			logging.warning( "Initialization Failed", exc_info=True)
			raise SystemError

		# do a few of the simpler ones here...
		self.menuBar = tk.Menubutton(self.top)
		#self.configure(bg='#8cf')		#--- RBF - consider this as a background for everything...
		#self.top['menu'] = self.menuBar
		
		# Menu bar...
		self.subMenu = tk.Menu(self.menuBar)
		#self.subMenu.add_cascade(label='Help', menu=self.subMenu)
		self.subMenu.add_command(label='About coLab...', command=self.__aboutHandler)
		
		# Just the word: "Group:"
		tk.Label(self.main_frame, text="Group:", justify=tk.RIGHT).grid(row=2, column=0, sticky=tk.E)
		
		self.subtitle_str = tk.StringVar()	 # put text into self.subtitle.set("new string")
		self.subtitle_str.set("Not set yet")
		self.subtitle=tk.Label(self.main_frame, textvariable=self.subtitle_str, anchor=tk.NE, justify=tk.CENTER).grid(row=1, column=1, columnspan=3, sticky=tk.E)

		#self.function_buttons()
		# refresh button...
		self.refreshButton = ttk.Button(self.main_frame, text="Refresh", command=self.refresh_group).grid(column=4, row=3)
		# quit button...
		self.quitButton = ttk.Button(self.main_frame, text="Quit", command=self.my_quit).grid(column=9, row=9)
		
	def __aboutHandler(self):
		""" Let's do a nice little pop-up saying who we are and what we do....
		
		(eventually)
		"""
		msg = "Welcome to coLab\nThis is a music collaboration tool created by Johnny Klonaris.\n\n"
		msg += "Note: 'coLab' is a trademark or other property of various entities.\n\n"
		msg += "I'm just using it for now.   Stay tuned for MusiCoLab."
		tkMessageBox.showinfo("About coLab...", msg)
		logging.info("how's this?")
	
	def load_group_list(self):
		""" Load up the names of the groups...  
		
		we don't actually load the groups until they're called.
		"""
		group_dir = os.path.join(self.conf.coLab_home, 'Group')
		logging.info("new cd: %s", group_dir)
		try:
			os.chdir(group_dir)
		except:
			logging.error("Cannot get to dir: %s", group_dir)
			logging.error("Fatal")
			raise IOError()
		# build a dictionary of names to directory names.
		self.grouplistdict = dict()		# clean dictionary..
		for dir in (os.listdir('.')):
			# Step through each, try to import from a data file -if it works, 
			# and there's a tile - we're in - otherwise skip
			if dir == '.DS_Store':	# yeah, mac specific, but just skipp it...
				continue
			datapath = os.path.join(dir, 'data')
			logging.info("Checking: %s", datapath)
			
			try:
				data = imp.load_source('', datapath)
				#os.remove(datafile + 'c')
			except:			# if any thing goes wrong - just skip ahead...
				logging.warning("no good - skipping %s", datapath,exc_info=True)
				continue		
				
			if not data.title:		# no title - no play...
				continue
			# ok - we've got a dir and a title - setup the next entry.
			self.grouplistdict[data.title] = dir	# for converting a title to a dir name
			logging.info("self.grouplistdict of %s is %s", data.title, self.grouplistdict[data.title])
		
	def display_group_list(self):
		""" Update the menu to display lists...
		 
		We want to display the title, but return the directory name.   
		We create a dictionary as we go, which will convert the title
		to the dir name.
		"""
		
		try:
			groupTitles = tuple(self.grouplistdict.keys())
		except:
			logging.warning("got no titles", exc_info=True)
			
		self.gOpt = tk.StringVar()
		self.gOpt.set(self.current_grouptitle)

		self.groupOption = tk.OptionMenu(self.main_frame, self.gOpt, *groupTitles,command=self.set_group_from_menu)

		self.groupOption.grid(column=1, row=2, columnspan=2, sticky=tk.W)
		
		
	
	def function_buttons(self):
		""" Place the buttons (and now, menus)  that drive the main process """
		logging.info("function buttons")
		# Do we have a local frame, if so, destroy it, other 
		try:
			self.function_frame.destroy()   
		except:
			logging.info("musta not been a function_frame...")
			pass

		#parent = self.main_frame

		# setup a simple frame to hold everything - so that we can rebuild it when ever we want...
		f_frame = tk.Frame(self.main_frame, bg="#e9e9e9", borderwidth=2, padx=10, pady=5) 
		f_frame.grid(column=0, row=4, columnspan=4)
		self.function_frame = f_frame
		new_page_button = ttk.Button(f_frame, text="New Page", command=lambda: clFunctions.create_new_page(self))
		new_page_button.grid(column=0, row=4)
		#edit_page_button = ttk.Button(f_frame, text="Edit Page", command=lambda: clFunctions.edit_page(self))
		#edit_page_button.grid(column=1, row=4)
		# RBF: put a test in here - if no pages yet in this group, replace with a label. (are we refreshing? - I think not)
		pagelist=self.current_group.pagelist
		logging.info("pagelist sort")
		pagelist.sort(key=clclasses.createkey, reverse=True)
		if len(pagelist) == 0:
			self.pg_option_menu = tk.Label(f_frame, text="-No Pages Yet-")
			self.pg_option_menu.grid(column=1, row=4)
		else:
			self.pg_option_menu = cltkutils.clOption_menu(f_frame, pagelist, 'desc_title', default='Edit Page', command=self.edit_page)
			self.pg_option_menu.om.grid(column=1, row=4)

		new_song_button = ttk.Button(f_frame, text="New Song", command=lambda: clFunctions.create_new_song(self))
		new_song_button.grid(column=2, row=4)
		#edit_song_button = ttk.Button(f_frame, text="Edit Song", command=lambda: clFunctions.edit_song(self))
		#edit_song_button.grid(column=3, row=4)
		songlist = self.current_group.songlist
		logging.info("songlist sort")
		songlist.sort(key=clclasses.createkey, reverse=True)
		if len(songlist) == 0:
			self.pg_option_menu = tk.Label(f_frame, text="-No Song Yet-")
			self.pg_option_menu.grid(column=3, row=4)
		else:
			self.sg_option_menu = cltkutils.clOption_menu(f_frame, songlist, 'desc_title', default='Edit Song', command=self.edit_song)
			self.sg_option_menu.om.grid(column=3, row=4)
		
	def edit_page(self, selection):
		"""
		Handler for the function menus, above.   Call the right thing...
		"""
		
		logging.info("Greetings from page editor... our selection: %s", selection)

		page = self.pg_option_menu.return_value()
		self.function_buttons()	
		if page is None:
			logging.info("None selected.")
			return
		logging.info("page is: %s", page)
		logging.info("Selection, type: %s", page.name)
		#clFunctions.edit_page(self)
		logging.info("edit Page")
		
		logging.info("Selected: name: %s locked: %s", page.name, page.locked)
		#if page.locked:
		#	coLab_top.master.beep()
		#	return
		page.master = self.master
		self.editor = clFunctions.Page_edit_screen(self, page, new=False)


	def edit_song(self, selection):
		"""
		Handler for song edit - create a song editor...
		"""
		logging.info("Greetings from song editor... our selection: %s", selection)

		song = self.sg_option_menu.return_value()
		self.function_buttons()	
		if song is None:
			return	# changed their mind

		song.master = self.master
		self.editor = clFunctions.Song_edit_screen(self, song, new=False)

			
			
	def place_group_shot(self):
		"""
		Place a photo/graphic specific to the currently selected 
		group.   Passed the group name, places the current snapshot
		into the window.   If that window (img)
		"""
		
		snapshot_name = 'SnapShot_tn.png'
		
		logging.info("Current group.name: %s", self.current_group.name)
		imgpath = os.path.join(self.current_group.home, "Shared", snapshot_name)
		if not os.path.exists(imgpath):
			imgpath = os.path.join(self.conf.coLab_home, 'Resources', "coLab-NoGroupSnap.png")

			
		logging.info("Image path: %s", imgpath)
		try:
			self.snapshot.destroy()
		except:
			pass
		
		self.snapshot = cltkutils.graphic_element(self.main_frame)
		self.snapshot.filepath = imgpath
		self.snapshot.row=0
		self.snapshot.column=5
		self.snapshot.rowspan=5
		self.snapshot.columnspan=4
		self.snapshot.post()

		# and again - for the header (Title)
		try:
			self.header.destroy()
		except:
			pass
		
		headerpath = os.path.join(self.current_group.home, "Header_dk.png")
		logging.info("Title path: %s", headerpath)
		self.header = cltkutils.graphic_element(self.main_frame)
		self.header.filepath = headerpath
		self.header.row=0
		self.header.column=0
		self.header.columnspan=3
		self.header.post()
		
		self.subtitle_str.set(self.current_group.subtitle)
			
	def place_logo(self):
		""" Place the logo on the frame """
		logo_name = 'CoLab_Logo3D_sm.png'	# let's extract this at some point...

		logo_path = os.path.join(self.conf.coLab_home, 'Resources', logo_name)
		logging.info("logo path: %s", logo_path)
		self.logo = cltkutils.graphic_element(self.main_frame)
		self.logo.filepath = logo_path
		self.logo.row=0
		self.logo.column=9
		self.logo.post()
		
	def refresh_group(self):
		""" Simple interface to the rebuild scripting... """
		logging.info("Refresh: %s", self.current_grouptitle)
		rebuild.rebuild(self.current_group.name, mirror=True)
		clSchedule.browse_url(self.current_group.url_head)
		"""	Code to regenerate posters, thumbnails
		for page in self.current_group.pagelist:
			imagemaker.make_sub_images(page)
		#"""
		logging.info("Refresh complete.")
		
	def my_quit(self):
		""" handle user quit
		
		Let's check to see what's left hanging if/when someone quits.
		"""
		logging.info("Time to quit.")

		self.master.quit()
		
def task(obj,bar):
	bar.step(1.0)

	obj.after(50, task, obj,bar)



def main():
	""" Just enough to get us started...  
	 
	Create the root and pass it into the Colab class (master)
	"""
	#logging.basicConfig(level=logging.INFO)
	logging.info("Colab Main")
	print "Colab"
	print "Python:", sys.version
	print "Tcl revision:", tk.Tcl().eval('info patchlevel')
	root = tk.Tk()
	
	w=Colab(root)
	
if __name__ == '__main__':
	main()
   
