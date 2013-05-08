#!/usr/bin/env python
"""
	classes for defining the various data file fomrats

"""

import os
import sys
import imp
import cldate
import clutils
import cltkutils


def set_init_vars(obj, initdata):
	"""
	Take the var/value pairs passed as a list in initdata
	and put them into the object along with a varlist
	"""
	print "Entering set_init_vars..."
	print "Object:", obj.name

	obj.varlist = []
	for (varname, value) in initdata:
		x = value
		string = 'obj.' + varname + ' = x'
		exec(string)	# assign the value the var
		obj.varlist.append(varname)

	for var in obj.varlist:
		string= 'obj.' + var
		value = eval(string)
		print "init: var:", var, " is: ", value

def set_paths(obj,sub_dir):

	# load in the site data to get started...
	# coLab_url_head	- head to the ext web site (e.g., http://...)
	# coLab_root		- url to the local structure (e.g., /coLab )
	# coLab_home		- local fs location of coLab home
	#
	try:
		conf=clutils.get_config()
	except ImportError:
		print "Cannot find config."
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

def import_data(obj, path):
	"""
	used by the various load routines to import the data file
	in the "path" dir.  Import the values found in the data file,
	then, using the objects varlist, import them as found into the
	object (group, song, page, etc.)
	"""
	#
	datafile = os.path.join(path, 'data')

	p = ''
	print "Enter import_data for:", obj.name
	try:
		p = imp.load_source('',datafile)
		os.remove(datafile + 'c')
	except IOError, info:
		print "Import problem with", datafile, info
		#raise IOError

	#self.set_paths(conf)

	for var in obj.varlist:
		string = 'p.' + var	# var name from the file...
		try:
			val = eval(string)
		except AttributeError, info:
			print "No file value for:", var, info
			continue
		# value changed, deal with it...
		string = 'obj.' + var + ' = val'
		exec(string)	# this assigns the file var
		#print "updating value", var, val

		conversion = ""	# set if we need to do a conversion....

		# let's leave this out for now.   We'll just save
		# floats w/o quotes
		if var in obj.floatvars:
			#print 'Floating', var
			conversion = "float"
		if var in obj.timevars:
			print "Converting", var
			conversion = "cldate.string2utc"

		if conversion:
			string = "obj." + var + " = " + conversion + "(p." + var + ')'
			try:
				exec(string)
			except:
				print "import_data, problem with conversion:", conversion, var, val

class Group:
	"""
	Data associated with a group
	"""
	def __init__(self, name):
		"""
		Set the initial values for the group structure, using
		a varlist so we can keep track of what we've got.
		"""
		timenow=cldate.utcnow()
		#
		# varname, value pairs...
		#
		initdata = [
		('name', name),
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
		self.name = name
		set_init_vars(self, initdata)
		#
		# These are not saved to the file - don't add to the varlist...
		self.pagelist = []
		self.songlist = []

	def load(self):	
		"""
		Load the group data - starting at the local coLab root, 
		and also load all associated pages
		"""
		
		grp_dir = os.path.join('Group', self.name)
		set_paths(self, grp_dir)
		#
		# Load a generic object from the file, then transfer the items 
		# to the current Group object

		import_data(self, self.home)
			
		# Now, step into the pages dir and load up a list of pages
		pagedir = os.path.join(self.home, 'Page')

		try:
			os.chdir(pagedir)
		except:
			print "Cannot get to dir:", pagedir
			print "Fatal"
			raise ImportError()
			
		# Now step through the dirs  (and files - rejecting them...).
		
		for nextpage in (os.listdir('.')):
			
			# this is a bit week - our criteria for a new page
			# is a dir with a 'data' file in it...  ok for now...
			pagehome = os.path.join(pagedir, nextpage)
			datafile = os.path.join(pagehome, 'data')
			if not os.path.exists(datafile):
				continue	# not a page...

			page = Page(nextpage) # new page, current dir is the name
			set_paths(page, pagehome)
	
			try:
				page.load()
			except IOError:
				#print "problem with", dir
				continue
	
			page.url_head = os.path.join(self.url_head, 'Page', page.name)
			page.root = os.path.join(self.root, 'Page', page.name)
			page.home = os.path.join(self.home, 'Page', page.name)

			self.pagelist.append(page)

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
	
	def __init__(self, name):
		"""
		We create an initial set of variables from the variable, value pairs.
		This lets us also create a master variable list which we can use to 
		merge values from the data files
		"""
		
		timenow=cldate.utcnow()
		# varname, value pairs...
		initdata = [
		('name', name),
		('group', "<unset>"),
		('desc_title', "<unset>"),
		('fun_title', "<unset>"),
		('duration',  0.0),
		('screenshot', ""),
		('thumbnail', ""),
		('description', "\n<unset>\n"),
		# start and end of the piece on the graphic
		('xStart',  0),
		('xEnd',  0),
		# Frames per second, generally calculated from xEnd-xStart and duration
		('fps', 6),
		
		('project', "<unset>"),
		('assoc_projects', ''),
		('song', "<unset>"),
		('part', "All"),
		('prevlink', "<unset>"),
		('nextlink', "<unset>"),
		# initial value - as a datetime object 
		('createtime', timenow),
		('updatetime', timenow),
		]
		# A list of vars to be converted from strings to datetime objects
		self.timevars = [ 'createtime', 'updatetime' ]
		self.floatvars = [ 'duration' ]
		self.name = name

		set_init_vars(self, initdata)

	def dump(self):
		"""
		Output the data structure in data file ready output
		"""
		EOL = '"\n'


		return( 'name="' + self.name + EOL +
			'group="' + self.group + EOL +
			'desc_title="' + self.desc_title + EOL +
			'fun_title="' + self.fun_title + EOL +
			'duration=' + str(self.duration) + '\n' +
			'screenshot="' + self.screenshot + EOL +
			'thumbnail="' + self.thumbnail + EOL +
			'\n' +
			'project="' + self.project + EOL +
			'assoc_projects="' + self.assoc_projects + EOL +
			'song="' + self.song + EOL +
			'part="' + self.part + EOL +
			'description="""' + self.description +	
			'"""\n' +
			'\n' +
			'xStart=' + str(self.xStart) + '\n' +
			'xEnd=' + str(self.xEnd) + '\n' +
			'fps=' + str(self.fps) + '\n' +
			'\n' +
			'prevlink="' + self.prevlink + EOL +
			'nextlink="' + self.nextlink + EOL +
			'\n' +
			'createtime="' + cldate.utc2string(self.createtime) + EOL +
			'updatetime="' + cldate.utc2string(self.updatetime) + EOL +
			'\n'
			)

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

		if path == 'None':
			try:
				path = self.home
			except NameError, info:
				print "load: NE", info
				sys.exit(1)
		
		import_data(self, path)

		if self.group == '<unset>':
			self.group = cltkutils.getGroup()
			#self.group = "SBP"
			#self.group= "Johnny"
			print "Note: override: group =", self.group

		sub_dir = os.path.join('Group', self.group, 'Page', self.name)
		set_paths(self, sub_dir)



	def post(self):
		"""
			Post the object data into a 'data' file.  The path to it 
			is in the object, and it simply opens the file and 
			puts the output of dump() into it.

			Object variables presist.
		"""

		print "post: page path", self.home
		data = os.path.join(self.home, 'data')

		try: 
			dfile = open(data, 'w+')	
		except IOError, info:
			print "post: Problem opening", data, info
			raise

		dfile.write(self.dump())
		dfile.close()

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
		
		print "New init song - name:", name
		timenow=cldate.utcnow()
		# varname, value pairs...
		initdata = [
		('name', name),
		('group', "<unset>"),
		('desc_title', "<unset>"),
		('fun_title', "<unset>"),
		('duration',  0.0),

		('project', "<unset>"),
		('assoc_projects', ''),
		('song', "<unset>"),
		('partlist', ['All']),
		('partnames', ['All']), 
		('description', "\n<unset>\n"),

		('prevlink', "<unset>"),
		('nextlink', "<unset>"),
		
		# initial value - as a datetime object 
		('createtime', timenow),
		('updatetime', timenow),
		]
		# A list of vars to be converted from strings to datetime objects
		self.timevars = [ 'createtime', 'updatetime' ]
		self.floatvars = [ 'duration' ]
		self.name = name

		set_init_vars(self, initdata)
		#
		# items not stored in the data file
		self.list = []
		self.part_dict = {}

		# RBF
		print "******  init: name is:", self.name
		#
		# Create a dictionary of names of parts
		self.partname_dict = {}
		for i in range(len(self.partlist)):
			print "Insertng name:", i, self.partlist[i], self.partnames[i]
			self.partname_dict[self.partlist[i]] = self.partnames[i]
	

	def dump(self):
		"""
		Output the data structure in data file ready output
		"""
		EOL = '"\n'


		return( 'name="' + self.name + EOL +
			'group="' + self.group + EOL +
			'desc_title="' + self.desc_title + EOL +
			'fun_title="' + self.fun_title + EOL +
			'duration="' + str(self.duration) + EOL +
			'\n' +
			'project="' + self.project + EOL +
			'assoc_projects="' + self.assoc_projects + EOL +
			'partlist=' + str(self.partlist) + '\n' +
			'partnames=' + str(self.partnames) + '\n' +
			'description="""' + self.description +	
			'"""\n' +
		
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
			self.group = cltkutils.getGroup()
			#self.group = "SBP"
			#self.group= "Johnny"
			print "Note: override: group =", self.group

		song_dir = os.path.join('Group', self.group, 'Song', self.name)
		set_paths(self, song_dir)

		if path == 'None':
			try:
				path = self.home
			except NameError, info:
				print "load: NE", info
				sys.exit(1)
		
		import_data(self, path)


		for i in range(len(self.partlist)):
			print "Insertng name:", i, self.partlist[i], self.partnames[i]
			self.partname_dict[self.partlist[i]] = self.partnames[i]


	def post(self):
		"""
			Post the object data into a 'data' file.  The path to it 
			is in the object, and it simply opens the file and 
			puts the output of dump() into it.

			Object variables presist.
		"""

		print "post: page path", self.home
		data = os.path.join(self.home, 'data')

		try: 
			dfile = open(data, 'w+')	
		except IOError, info:
			print "post: Problem opening", data, info
			raise

		dfile.write(self.dump())
		dfile.close()

def main():
	print "Welcome to classes..."
	
	group = cltkutils.getGroup()

	p = Page()
	p.load('/Users/Johnny/dev/coLab/Group/' + group + '/Page/BeachFlute')
	print p.dump()

	
	g = Group()
	g.load(group)

	for p in g.pagelist:
		print "got page:", p.name, p.desc_title, p.fun_title


if __name__ == '__main__':
	main()
