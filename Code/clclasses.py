#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" classes for defining the various colab data file formats """

import os
import sys
import logging
import imp
import copy

import config
import cldate
import clutils
import cltkutils

import imagemaker	# RBF:  remove once remake kludge is gone

def set_init_vars(obj, initdata):
	""" Process the var/value pairs

	Take the var/value pairs passed as a list in initdata
	and put them into the object along with a varlist
	"""
	logging.info("Entering set_init_vars...")
	logging.info("Object: %s", obj.name)

	obj.varlist = []
	for (varname, value) in initdata:
		x = value
		string = 'obj.' + varname + ' = x'
		exec(string)	# assign the value the var
		obj.varlist.append(varname)

	for var in obj.varlist:
		string = 'obj.' + var
		value = eval(string)
		#print "init: var:", var, " is: ", value

def set_paths(obj,sub_dir):
	""" set path variables for locations

	load in the site data to get started...
	 coLab_url_head	- head to the ext web site (e.g., http://...)
	 coLab_root		- url to the local structure (e.g., /coLab )
	 coLab_home		- local fs location of coLab home
	"""

	try:
		conf=clutils.get_config()
	except ImportError:
		logging.error("Cannot find config.")
		sys.exit(1)

	# populate the object's paths based on the subdir passed, 
	# (subdir is relative to the coLab root)
	# first - the site wide values	 - no need to config more than once..
	obj.coLab_url_head = conf.coLab_url_head
	obj.coLab_root = conf.coLab_root
	obj.coLab_home = conf.coLab_home
	# and the group specific locations
	obj.url_head = os.path.join(conf.coLab_url_head, sub_dir)
	obj.root = os.path.join(conf.coLab_root, sub_dir)
	obj.home = os.path.join(conf.coLab_home, sub_dir)

def import_data(obj, path=None):
	"""
	used by the various load routines to import the data file
	in the "path" dir.  Import the values found in the data file,
	then, using the objects varlist, import them as found into the
	object (group, song, page, etc.)
	
	By default, we load from the file 'data' in the current 
	object's home var.  If path is set, we use that instead.
	"""
	#
	if path is not None:
		datafile = os.path.join(path, 'data')
	else:
		datafile = os.path.join(obj.home, 'data')

	p = ''
	logging.info("Enter import_data for: %s, path: %s", obj.name,  datafile)
	try:
		p = imp.load_source('',datafile)
		os.remove(datafile + 'c')
	except IOError, info:
		logging.warning("Import problem with %s", datafile, exc_info=True)
		#raise IOError

	try:
		logging.info("name from import: %s", p.name)
	except:
		pass
	
	#self.set_paths(conf)
	# A few state vars...  are we "clean"?
	# RBF - maybe someday
	#obj.changed = False
	#obj.needs_rebuild = False
	# Convert the import data into actual vars in the object...
	for var in obj.varlist:
		string = 'p.' + var	# var name from the file...
		try:
			val = eval(string)
		except AttributeError, info:
			logging.info("No file value for: %s, %s, ", string, info, exc_info=True)
			continue
		# value changed, deal with it...
		string = 'obj.' + var + ' = val'
		exec(string)	# this assigns the file var
		#print "updating value", var, val
	convert_vars(obj)		# convert any floats, ints, etc...
	
def convert_vars(obj):
	"""
	When the vars are posted into a form, they get converted
	to strings - convert them back.
	"""
	for var in obj.varlist:
		conversion = ""	# set if we need to do a conversion....

		# let's leave this out for now.   We'll just save
		# floats w/o quotes
		if var in obj.floatvars:
			#print 'Floating', var
			conversion = "float"
		if var in obj.timevars:
			#logging.info("Converting %s", var)
			logging.info("Converting %s", var)		# RBF---------
			conversion = "cldate.string2utc"
		if var in obj.intvars:
			conversion = "int"

		if conversion:
			string = "obj." + var + " = " + conversion + "(obj." + var + ')'
			try:
				exec(string)
			except:
				logging.warning("import_data, problem with conversion: %s, var: %s", conversion, var, exc_info=True)
				
def import_list(parent, type):
	"""
	Step through the "type" dirs... (Page, Song, etc.) 
	load an object for each, while also building a list (objects)
	and a dictionary to translate from the Page/Song name 
	(dir name) to a pointer to the object.
	"""
	# Now, step into the pages dir and load up a list of pages
	thisdir = os.path.join(parent.home, type)
	logging.info("import list dir: %s", thisdir)
	try:
		os.chdir(thisdir)
	except:
		logging.warning("Cannot get to dir: %s", thisdir, exc_info=True)
		logging.error("Fatal")
		raise ImportError()
		
	# Now step through the dirs  (and files - rejecting them...).
	logging.info("Import list: parent: %s, type: %s", parent.name, type)
	
	list = []
	dict = {}
	for item in (os.listdir('.')):
		
		# this is a bit weak - our criteria for a new page
		# is a dir with a 'data' file in it...  ok for now...
		nexthome = os.path.join(thisdir, item)
		datafile = os.path.join(nexthome, 'data')
		logging.info("import_list nexthome: %s, datafile: %s", nexthome, datafile)
		
		if not os.path.exists(datafile):
			continue	# not a page...
		
		if type == 'Page':
			obj = Page(item) # new page, current dir is the name
		elif type == 'Song':
			obj = Song(item)
			
		logging.info("Import_list: set_paths, type: %s, nexthome: %s", type, nexthome )
		
		obj.group = parent.name
		obj.group_obj = parent		# a pointer to the parent
		sub_dir = os.path.join('Group', parent.name, type, item)
		logging.info("Set_paths: %s %s", obj.name, sub_dir)
		set_paths(obj, sub_dir)	

		try:
			logging.info("Loading: obj: %s, gr.name: %s, objhome: %s",obj.name, obj.group_obj.name, obj.home)
			obj.load()
			
		except IOError:
			logging.warning("problem with %s", dir, exc_info=True)
			continue	# RBF: consider something serious here - exit even??
		if parent.name != obj.group:
			logging.warning("WARNING:  loading parent's name: %s, current group var: %s", parent.name, obj.group)
		list.append(obj)
		dict[obj.name] = obj
		#  RBF:   this appears that it should be replaced with sub_dir = os.path.join('Page', page.name) / set_paths(page, sub_dir)
		# check it...
		
		#item.url_head = os.path.join(parent.url_head, type, item.name)
		#item.root = os.path.join(parent.root, type, item.name)
		#item.home = os.path.join(parent.home, type, item.name)
	return(list, dict)

		
class Group:
	"""
	Data associated with a group
	"""
	def __init__(self, name):
		""" Set the initial values for the group structure 
		
		set up the initial data - from a list,
		varlist, so we can keep track of what we've got.
		"""
		timenow=cldate.utcnow()
		#
		# varname, value pairs...
		#
		initdata = [
		('obj_type', 'Group'),
		('title', "<unset>"),
		('subtitle', "<unset>"),
		('collaborators', "<unset>"),
		('description', "\n<unset>\n"),
		# arbitrary date just after the epoch
		('createtime', timenow),
		('updatetime', timenow),
		]
		# vars that need to be converted to datetime objects
		self.timevars = [ 'createtime', 'updatetime' ]
		self.floatvars = []
		self.intvars = []
		try:
			logging.info("name, self. %s - %s", name, self.name)
		except:
			pass
		self.name = name
		try:
			logging.info("name, self. %s - %s", name, self.name)
		except:
			pass
		set_init_vars(self, initdata)
		try:
			logging.info("name, self. %s - %s", name, self.name)
		except:
			pass
		#
		# These are not saved to the file - don't add to the varlist...
		self.pagelist = []
		self.songlist = []
		# Create a "previous" version (possibly overwritten in "load") for comparisons
		self.prev = copy.copy(self)


	def load(self):	
		""" Load the group data from data file
		
		Starting at the local coLab root, 
		and also load all associated pages
		"""
		
		grp_dir = os.path.join('Group', self.name)
		set_paths(self, grp_dir)
		#
		# Load a generic object from the file, then transfer the items 
		# to the current Group object
		logging.info("self.name pre import: %s", self.name)
		import_data(self)
		logging.info("self.name post import: %s", self.name)
		
		# create translation dicts for 
		(self.pagelist, self.pagedict) = import_list(self, 'Page')
		for i in self.pagelist:
			logging.info("I've got a page in my list: %s", i.name)
			# RBF:   Rebuild the poster files - this needs to be a button /option at some point...
			'''  Uncomment (add "#") to rebuild all posters...
			if i.page_type == 'html5':
				logging.warning("Rebuilding poster images...")
				imagemaker.make_sub_images(i)
			#'''
		(self.songlist, self.songdict) = import_list(self, 'Song')
		for i in self.songlist:
			logging.info("I've got a song in my list: %s", i.name)
		# Make a copy for reference purposes (mostly to see what values have changed)
		self.prev = None	# (remove any previous "prev")
		self.prev = copy.copy(self)
	
	def find_song(self, song_name=None):
		"""
		return the song object whose name matches
		"""
		for song in self.songlist:
			if song.name == song_name:
				return(song) 
		return(None)	# none found...
	def find_song_by_title(self, song_title=None):
		"""
		Find by title...
		"""
		for song in self.songlist:
			if song.desc_title == song_title:
				return(song) 
		return(None)	# none found...
# 
# For sorting - return the appropriate time in seconds
def updatekey(self):
	return (self.updatetime)	# return the update time as seconds for sorting
def createkey(self):
	return (self.createtime)	# ditto the create time

class Page:
	"""
	A Page object contains the data associated with a posted page.
	Also contains methods for:
		load	- load the data from a file 
		dump	- return the object's data in file format
		post	- puts the output of dump into the data file

	"""
	
	def __init__(self, name=None):
		"""
		We create an initial set of variables from the variable, value pairs.
		This lets us also create a master variable list which we can use to 
		merge values from the data files
		"""

		if name is None:
			self.name = 'ProtoPage'
		else:
			self.name = name
		timenow=cldate.utcnow()
		# varname, value pairs...
		initdata = [
		('obj_type', 'Page'),
		('page_type', 'orig'),
		('locked', False),
		('group', "<unset>"),
		('desc_title', "(Descriptive title - should be unique)"),
		('fun_title', "(Fun title - whatever feels right)"),
		('duration',  0.0),
		('media_size', "Small"),
		('screenshot', ""),
		('graphic', "ScreenShot.png"),
		('thumbnail', "ScreenShot_tn.png"),
		('use_soundgraphic', False),
		('strict_graphic', False),
		('graphic_theme', 'Default'),
		('soundfile', ""),
		('soundgraphic', os.path.join("coLab_local", "SoundGraphic.png")),
		('soundthumbnail', "SoundGraphic_tn.png"),
		('description', ""),
		# start and end of the piece on the original graphic
		('xStart',  0),
		('xEnd',  0),
		('screenshot_width', 0),
		# Frames per second, generally calculated from xEnd-xStart and duration
		('fps', '6'),
		
		('project', "<unset>"),
		('assoc_projects', ''),
		('song', "<unset>"),			# name (parent dir)  of the current song..
		('part', "All"),
		('prevlink', "<unset>"),
		('nextlink', "<unset>"),
		('soundinfo', "<unset>"),
		# initial value - as a datetime object 
		('createtime', timenow),
		('updatetime', timenow),
		]
		# A list of vars to be converted from strings to datetime objects
		self.timevars = [ 'createtime', 'updatetime' ]
		self.floatvars = [ 'duration' ]
		self.intvars = [ 'xStart', 'xEnd', 'screenshot_width' ]
		
		# set up a number of buttons
		# add to the init data, and the floatvars
		numbut = config.NUM_BUTS
		initdata.append( ("numbuts", numbut) )
		for i in range(1, numbut+1):
			locvar = "Loc_%d" % i
			initdata.append( (locvar, 0.0) )	# var, val tuple
			self.floatvars.append(locvar)
			initdata.append( (locvar+'_desc', 'Unset'))

		set_init_vars(self, initdata)
		# Create a "previous" version (possibly overwritten in "load") for comparisons
		self.prev = copy.copy(self)

	def dump(self):
		"""
		Output the data structure in data file ready output
		"""
		EOL = '"\n'
		encoding = "# -*- coding: utf-8 -*-"		# probably belongs as a config value...
		return( encoding + '\n' +
			'name="' + self.name + EOL +
			'page_type="' + self.page_type + EOL +
			'locked=' + str(self.locked) + '\n' +
			'group="' + self.group + EOL +
			'desc_title=u"' + self.desc_title.strip() + EOL +
			'fun_title=u"' + self.fun_title.strip() + EOL +
			'duration=' + str(self.duration) + '\n' +
			'media_size="' + str(self.media_size) + EOL +
			'screenshot="' + self.screenshot + EOL +
			'graphic="' + self.graphic + EOL +
			'thumbnail="' + self.thumbnail + EOL +
			'use_soundgraphic=' + str(self.use_soundgraphic) + '\n' +
			'\n' +
			'soundfile="' + self.soundfile + EOL +
			'strict_graphic=' + str(self.strict_graphic) + '\n' +
			'graphic_theme="' + self.graphic_theme + EOL +
			'soundgraphic="' + self.soundgraphic + EOL +
			'soundthumbnail="' + self.soundthumbnail + EOL +
			'\n' +
			'project="' + self.project + EOL +
			'assoc_projects="' + self.assoc_projects + EOL +
			'song="' + self.song + EOL +
			'part="' + self.part + EOL +
			'description=u"""' + self.description.strip() + '"""\n' +
			'\n' +
			'xStart=' + str(self.xStart) + '\n' +
			'xEnd=' + str(self.xEnd) + '\n' +
			'screenshot_width=' + str(self.screenshot_width) + '\n' +
			'fps=' + str(self.fps) + '\n' +
			'\n' +
			'soundinfo="""' + self.soundinfo + '\n"""'
			'\n' +
			'prevlink="' + self.prevlink + EOL +
			'nextlink="' + self.nextlink + EOL +
			'\n' +
			'createtime="' + cldate.utc2string(self.createtime) + EOL +
			'updatetime="' + cldate.utc2string(self.updatetime) + EOL +
			'\n' + self.dump_locs()
			)
	def dump_locs(self):
		""" Output the button info...
		"""
		but_str = "numbuts=%d\n" % self.numbuts
		for i in range(1, self.numbuts+1):
			locvar = "Loc_%d" % i
			locval = eval("self." + locvar)
			but_str += locvar + "=" + str(locval) + '\n'
			but_str += locvar + '_desc="' + eval("self." + locvar + "_desc") + '"\n'
		
		return but_str

	def load(self, path=None):
		"""
		This is a bit kludgy right now, 
		we read the file, then populate
		the song object with the data.

		We could just create a list of the imported
		objects, but we'd have no idea what 
		vars were involved and no methods.   Pickling
		could work - if we want to commit to Python.

		For now, this is generic and flexible
		"""
		
		if path is None:
			try:
				page_dir = os.path.join('Group', self.group, 'Page', self.name)
				set_paths(self, page_dir)
			except Exception as e:
				logging.warning("Cannot build page paths %s", page_dir,  exc_info=True)
		else:
			logging.info("Page load path passed in: %s", path)
			set_paths(self, path)
			
			# Kludge alert:  this is not OS independent - should use sys calls...
			# the second piece of "path" should be the group
			logging.info("About to split: %s", path)
			self.group = path.split('/')[1]
			self.name = path.split('/')[3]
			# probably running offline - load the object too...
			#self.group_obj = Group('self.group')
			#self.group_obj.load()
			
		import_data(self)

		# Make a copy for reference purposes (mostly to see what values have changed)
		self.prev = None	# (remove any previous "prev")
		self.prev = copy.copy(self)

	def post(self):
		"""
			Post the object data into a 'data' file.  The path to it 
			is in the object, and it simply opens the file and 
			puts the output of dump() into it.

			Object variables persist.
		"""

		logging.info("post: page path: %s", self.home)
		data = os.path.join(self.home, 'data')

		try: 
			dfile = open(data, 'w+')	
		except IOError, info:
			logging.info("post: Problem opening: %s", data, exc_info=True)
			raise

		dfile.write(self.dump())
		dfile.close()
		
	def create(self):
		"""
		This could be part of post - but I want to 
		restrict directory creation to when I'm specifically
		creating a new page.
		"""
		local = 'coLab_local'
	
		if not os.path.isdir(self.home):
			try:
				# Create the local subdir - get it all at once...
				localdir = os.path.join(self.home, local)
				os.makedirs(localdir)
	
			except OSError, info:
				logging.warning("Path: %s", localdir, exc_info=True)
				logging.warning("Try again.")
				sys.exit(1)
	
		# create a stub for the data file...
		datafile = os.path.join(self.home, 'data')
		f = open(datafile, 'a+')
		f.write('name="' + self.name + '"\n')
		f.close()

	def localize_soundfile(self):
		"""
		Return the path to the local sound file - 
		we store the full path to the original so we
		can later find or highlight it
		"""
		return self.localize(self.soundfile)

	def localize_screenshot(self):
		"""
		Return the local path to the screenshot...
		"""
		return self.localize(self.screenshot)

		
	def localize(self, fullpath):
		"""
		Take a local value, and return the page local
		path to it...
		"""
		# split it...
		filename = os.path.split(fullpath)[1]
		return os.path.join(self.home, 'coLab_local', filename)
		
class Song:
	"""
	A Song object contains the data associated with a generate song page
	Also contains methods for:
		load	- load the data from a file 
		dump	- return the object's data in file format
		post	- puts the output of dump into the data file
	"""


	""" May want a new __append__ to check the new item's 
		update time and if newer, make it ours
	"""
	
	def __init__(self, name):
		"""
		We create an initial set of variables from the variable, value pairs.
		This lets us also create a master variable list which we can use to 
		merge values from the data files
		"""
		
		logging.info("New init song - name: %s", name)
		timenow=cldate.utcnow()
		# varname, value pairs...
		initdata = [
		('name', name),
		('obj_type', 'Song'),
		('group', "<unset>"),
		('desc_title', "<unset>"),
		('fun_title', "<unset>"),

		('project', "<unset>"),
		('assoc_projects', ''),
		('song', "<unset>"),
		('partlist', ['All']),
		('partnames', ['All']), 
		('description', ""),

		('prevlink', "<unset>"),
		('nextlink', "<unset>"),
		
		# initial value - as a datetime object 
		('createtime', timenow),
		('updatetime', timenow),
		]
		# A list of vars to be converted from strings to datetime objects
		self.timevars = [ 'createtime', 'updatetime' ]
		self.floatvars = [ ]
		self.intvars = []
		self.name = name

		set_init_vars(self, initdata)
		#
		# items not stored in the data file
		self.list = []			# not clear this is used...   check it.
		self.part_dict = {}		# used later to keep lists of pages, organized by what part they're associated with
		# Create a "previous" version (possibly overwritten in "load") for comparisons
		self.prev = copy.copy(self)


	def dump(self):
		"""
		Output the data structure in data file ready output
		"""
		EOL = '"\n'

		encoding = "# -*- coding: utf-8 -*-"		# probably belongs as a config value...
		return( encoding + '\n' +
			'name="' + self.name + EOL +
			'group="' + self.group + EOL +
			'desc_title=u"' + self.desc_title.strip() + EOL +
			'fun_title=u"' + self.fun_title.strip() + EOL +
			'\n' +
			'project="' + self.project + EOL +
			'assoc_projects="' + self.assoc_projects + EOL +
			'partlist=' + str(self.partlist) + '\n' +
			'partnames=' + str(self.partnames) + '\n' +
			'description=u"""' + self.description.strip() + '"""\n' +
		
			'prevlink="' + self.prevlink + EOL +
			'nextlink="' + self.nextlink + EOL +
			'\n' +
			'createtime="' + cldate.utc2string(self.createtime) + EOL +
			'updatetime="' + cldate.utc2string(self.updatetime) + EOL +
			'\n' )

	def load(self, path='None'):
		"""
		This is a bit kludgy right now, 
		we read the file, then populate
		the song object with the data.

		We could just create a list of the imported
		objects, but we'd have no idea what 
		vars were involved and no methods.   Pickling
		could work - if we want to commit to Python.

		For now, this is generic and flexible
		"""

		if self.group == '<unset>':
			raise(ValueError)
			self.group_obj = cltkutils.getGroup()
			self.group = self.group_obj.name
			self.group="Test"
			#self.group = "SBP"
			#self.group= "Catharsis"
			#self.group= "Johnny"
			logging.info("Note: override: group = %s - %s", self.group_obj, self.group)

		song_dir = os.path.join('Group', self.group, 'Song', self.name)
		set_paths(self, song_dir)

		if path == 'None':
			try:
				path = self.home
			except NameError, info:
				logging.warning("load: NE", exc_info=True)
				sys.exit(1)
		
		import_data(self, path)

		self.partname_dict = {}
		# build a part dictionary   shortname ->  longer name...
		for i in range(len(self.partlist)):
			logging.info("Inserting name: inx: %d, list: %s name:%s", i, self.partlist[i], self.partnames[i])
			self.partname_dict[self.partlist[i]] = self.partnames[i]
		# make a copy so we can tell if we've been changed, etc...
		self.prev = None	# (remove any previous "prev")
		self.prev = copy.copy(self)
	def create(self):
		"""
		This could be part of post - but I want to 
		restrict directory creation to when I'm specifically
		creating a new page.
		"""
		local = 'coLab_local'
	
		if not os.path.isdir(self.home):
			try:
				# Create the local subdir - get it all at once...
				localdir = os.path.join(self.home, local)
				os.makedirs(localdir)
	
			except OSError, info:
				logging.warning("Path: %s", localdir, exc_info=True)
				logging.error("Try again.")
				sys.exit(1)
	
		# create a stub for the data file...
		datafile = os.path.join(self.home, 'data')
		f = open(datafile, 'a+')
		f.write('name="' + self.name + '"\n')
		f.close()

	def post(self):
		"""
			Post the object data into a 'data' file.  The path to it 
			is in the object, and it simply opens the file and 
			puts the output of dump() into it.

			Object variables presist.
		"""

		logging.info("post: page path: %s", self.home)
		data = os.path.join(self.home, 'data')

		try: 
			dfile = open(data, 'w+')	
		except IOError, info:
			logging.warning("post: Problem opening: %s", data, exc_info=True)
			raise

		dfile.write(self.dump())
		dfile.close()

def main():
	logging.info("Welcome to classes...")
	
	"""
	
	g = Group()
	g.load(group)

	for p in g.pagelist:
		logging.info("got page: %s, %s, %s", p.name, p.desc_title, p.fun_title)
	"""

if __name__ == '__main__':
	main()
