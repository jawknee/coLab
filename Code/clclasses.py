#!/usr/bin/env python
"""
	classes for defining the various data file fomrats

"""

import os
import sys
import imp
import cldate
import clutils

class Group:
	"""
	Data associated with a group
	"""
	def __init__(self):
		self.name = "<unset>"
		self.title = "<unset>"
		self.subtitle = "<unset>"
		self.collaborators = "<unset>"
		self.description = "\n<unset>\n"
		# arbitrary date just after the epoch
		self.createtime=cldate.string2utc("1970-01-24T09:23:45")
		self.updatetime=cldate.string2utc("1970-01-24T09:23:45")
		
		self.pagelist = []
		self.songlist = []


	def load(self,name):	
		"""
		Load the group data - starting at the local coLab root, 
		and also load all associated pages
		"""
		try:
			name
		except NameError, info:
			print "Group load - no name passed.", info
			raise NameError

		self.name = name

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

		# populate the group paths/locations
		# first - the site wide values	 - no need to config more than once..
		self.coLab_url_head = conf.coLab_url_head
		self.coLab_root = conf.coLab_root
		self.coLab_home = conf.coLab_home
		# and the group specific locations
		grp_dir = os.path.join('Group', name)
		self.url_head = os.path.join(conf.coLab_url_head, grp_dir)
		self.root = os.path.join(conf.coLab_root, grp_dir)
		self.home = os.path.join(conf.coLab_home, grp_dir)

		#
		# Load a generic object from the file, then transfer the items 
		# to the current Group object

		try:
			data = os.path.join(self.home, 'data')
			d = imp.load_source('', data)
			os.remove(data + 'c')	# compiled...
		except (ImportError, IOError), info:
			print "Group,load - cannot access:", data
			print info
			print "Trying an update..."
			self.update(data)
			

		# populate the group data from the imported data file...
		try:
			self.title = d.title
			self.subtitle = d.subtitle
			self.collaborators = d.collaborators
			self.description = d.description

		except AttributeError, info:
			print "group.load - import error", info
			raise ImportError
			
		# Now, step into the pages dir and load up a list of pages
		pagedir = os.path.join(self.home, 'Page')

		try:
			os.chdir(pagedir)
		except:
			print "Cannot get to dir:", pagedir
			print "Fatal"
			raise ImportError()
			
		# Now step through the dirs  (and files - rejecting them...).
		
		for dir in (os.listdir('.')):
			#print "dir is:", dir

			page = Page() # instance
	
			try:
				page.load(dir)
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
	A Page object contains the data associated with posted page.
	Also contains methods for:
		load	- load the data from a file 
		update  - handle exceptions from older data files,
			  adds any new vars to the data file. 
		dump	- return the object's data in file format
		post	- puts the output of dump into the data file

	"""
	
	def __init__(self):
		self.name="<unset>"
		self.group="<unset>"
		self.desc_title="<unset>"
		self.fun_title="<unset>"
		self.duration = 0.0
		self.screenshot=""
		self.thumbnail=""
		self.description="\n<unset>\n"

		self.xStart = 0
		self.xEnd = 0

		self.project="<unset>"
		self.assoc_projects=''
		self.song="<unset>"
		self.part="All"

		self.prevlink="<unset>"
		self.nextlink="<unset>"

		# initial value - now as a datetime object
		self.createtime = cldate.utcnow()
		self.updatetime = self.createtime

	def xfer_import(self, file):
		"""
		 	Transfer the items from the file object into the 
			page object.   Careful - this is called from both 
			load and update. 
		"""
		#
		# Step through them...
		try:
			# These first few should always happen and should be first.
			# Needed to set up default path to the data file..
			self.name = file.name
			self.group = file.group

			#
			self.desc_title = file.desc_title
			self.fun_title = file.fun_title
			self.duration = float(file.duration)
			self.screenshot = file.screenshot
			self.thumbnail = file.thumbnail
			self.description = file.description

			self.xStart = file.xStart
			self.xEnd = file.xEnd

			self.project = file.project
			self.assoc_projects = file.assoc_projects
			self.song = file.song
			self.part = file.part

			self.prevlink = file.prevlink
			self.nextlink = file.nextlink

			self.createtime = cldate.string2utc(file.createtime)
			self.updatetime = cldate.string2utc(file.updatetime)

		except (NameError, AttributeError) as info:
			print "xfer_import: unset var in data file", info
			raise NameError

	def set_paths(self, conf):
		"""
		populate the page paths/locations from the conf object. expects self.name
		and self.group to be set. Will return invalid paths if they are not.
		"""

		#
		# RBF: Remove Before Flight
		# 	for debugging, we hard code the group  - needs to come out before
		# 	"production"
		try:
			if self.group == "<unset>":
				raise NameErrror	
		except (NameError, TypeError), info:
			self.group = "Catharsis" 
			print "load: group Force:", self.group, info

		if self.name == "<unset>":
			raise NameError

		# first - the site wide values   - no need to config more than once..
		self.coLab_url_head = conf.coLab_url_head
		self.coLab_root = conf.coLab_root
		self.coLab_home = conf.coLab_home
		# and the page specific locations
		page_dir = os.path.join('Group', self.group, 'Page',  self.name)
		self.url_head = os.path.join(conf.coLab_url_head, page_dir)
		self.root = os.path.join(conf.coLab_root, page_dir)
		self.home = os.path.join(conf.coLab_home, page_dir)
		print "set_paths: self.home:", self.home
		return

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


		# load in the site data to get started...
		# coLab_url_head        - head to the ext web site (e.g., http://...)
		# coLab_root            - url to the local structure (e.g., /coLab )
		# coLab_home            - local fs location of coLab home
		#
		try:
			conf=clutils.get_config()
		except ImportError:
			print "Cannot find config."
			sys.exit(1)
		

		if path == 'None':
			try:
				path = self.home
			except NameError as info:
				print "load: NE", info
				sys.exit(1)
		
		dfile = os.path.join(path, 'data')
		#print "dfile:",dfile

		#
		try:
			P = imp.load_source('',dfile)
			os.remove(dfile + 'c')
		except IOError, info:
			print "Import problem with", dfile, info
			raise IOError

		#self.set_paths(conf)

		try:
			self.xfer_import(P)
		except NameError, info:
			self.set_paths(conf)
			print "load: import problems:", info
			print "Calling self.update() with self.home, group, name  as:", self.home, self.group, self.name
			self.update()

		"""   Ugly - this is a kluge - need to tighten this up:   RBF
		self.post()
		"""
		self.set_paths(conf)


	def dump(self):
		"""
		Update the data file
		"""
		EOL = '"\n'


		print "dump- self: xStart, xEnd", self.xStart, self.xEnd
		return( 'name="' + self.name + EOL +
			'group="' + self.group + EOL +
			'desc_title="' + self.desc_title + EOL +
			'fun_title="' + self.fun_title + EOL +
			'duration="' + str(self.duration) + EOL +
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
			'\n' +
			'prevlink="' + self.prevlink + EOL +
			'nextlink="' + self.nextlink + EOL +
			'\n' +
			'createtime="' + cldate.utc2string(self.createtime) + EOL +
			'updatetime="' + cldate.utc2string(self.updatetime) + EOL +
			'\n'
			)

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

	def update(self):
		"""
			A bit of a kluge to let me retain a python/shell/etc.
			flat data file.  Dumps the passed object to a temp file,
			concatenates the passed file to it, then imports that.
			Can be called from the exception in load.

			Object variables do NOT persist if already specified in the
			data file.  Use post() in that case
	
		"""
		print "page path", self.home
		data = os.path.join(self.home, 'data')
		tmp = data + '.temp'
		print "data, tmp", data, tmp 
		print "update path file:", tmp
		try:
			tfile = open(tmp, 'w+')		
		except IOError, info:
			print "update: Problem opening", tmp, info
			sys.exit(1)

		tfile.write(self.dump())

		try: 
			dfile = open(data, 'rw+')
		except IOError, info:
			print "update: Problem opening", data, info
			raise

		tfile.write(dfile.read())

		tfile.close()
		dfile.close()


		try:
			P = imp.load_source('',tmp)
		except IOError, info:
			print "Immport problem with", dfile, info
			raise IOError

		try:
			os.remove(tmp + 'c')
			os.remove(tmp)
		except:
			print "Couldn't remove", tmp

		try:
			self.xfer_import(P)
		except NameError, info:
			print "update: problems:", info
			raise ImportError

		self.post()

class Song:
	"""
	Information specific to a song
	"""

	def __init__(self,name):
		self.name = name
		self.list = []
		self.part_dict = {}

	""" May want a new __append__ to check the new item's 
	    update time and if newer, make it ours
	"""

def main():
	print "Welcome to classes..."
	
	p = Page()
	p.load('/Users/Johnny/dev/coLab/Group/Catharsis/Page/BeachFlute')
	print p.dump()

	
	g = Group()
	g.load('Catharsis')

	for p in g.pagelist:
		print "got page:", p.name, p.desc_title, p.fun_title


if __name__ == '__main__':
	main()
