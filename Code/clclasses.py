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
		self.description = "<unset>"
		# arbitrary date just after the epoch
		self.createtime=cldate.string2utc("1970-01-24T09:23:45")
		self.updatetime=cldate.string2utc("1970-01-24T09:23:45")
		
		self.pagelist = []



	def load(self,name):	
		"""
		Load the group data - starting at the local coLab root, 
		and also load all the related data, e.g., pages.
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
			print "Tring an update..."
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
	The data associated with a song, imported from 
	a raw file - at this point.
	"""
	
	def __init__(self):
		self.name="<unset>"
		self.group="<unset>"
		self.desc_title="<unset>"
		self.fun_title="<unset>"
		self.duration = 0.0
		self.screenshot=""
		self.thumbnail=""
		self.description="<unset>"

		self.xStart = 0
		self.xEnd = 0

		self.project="<unset>"
		self.assoc_projects=''

		self.prevlink="<unset>"
		self.nextlink="<unset>"

		# initial value - now as a datetime object
		self.createtime = cldate.utcnow()
		self.updatetime = self.createtime

	def xfer_import(self, file):
		"""
		 	Transfer the items from the file object into the 
			page object.   Careful - ths is called from both 
			load and update. 
		"""
		#
		# Step through them...
		try:
			self.name = file.name
			self.desc_title = file.desc_title
			self.fun_title = file.fun_title
			self.duration = float(file.duration)
			self.screenshot = file.screenshot
			self.description = file.description
			self.group = file.group

			self.xStart = file.xStart
			self.xEnd = file.xEnd

			self.project = file.project
			self.assoc_projects = file.assoc_projects

			self.prevlink = file.prevlink
			self.nextlink = file.nextlink

			self.createtime = cldate.string2utc(file.createtime)
			self.updatetime = cldate.string2utc(file.updatetime)

		except (NameError, AttributeError) as info:
			print "xfer_import: unset var in data file", info

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
				print info
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
		try:
			self.xfer_import(P)
		except NameError, info:
			print "load: import problems:", info
			self.update(path)

		# populate the group paths/locations
		# first - the site wide values   - no need to config more than once..
		self.coLab_url_head = conf.coLab_url_head
		self.coLab_root = conf.coLab_root
		self.coLab_home = conf.coLab_home
		# and the group specific locations
		page_dir = os.path.join('Group', self.group, 'Page',  self.name)
		self.url_head = os.path.join(conf.coLab_url_head, page_dir)
		self.root = os.path.join(conf.coLab_root, page_dir)
		self.home = os.path.join(conf.coLab_home, page_dir)

	def dump(self):
		"""
		Update the data file
		"""
		EOL = '"\n'

		print "dump- self:", self.xStart, self.xEnd
		return( 'name="' + self.name + EOL +
			'group="' + self.group + EOL +
			'desc_title="' + self.desc_title + EOL +
			'fun_title="' + self.fun_title + EOL +
			'duration="' + str(self.duration) + EOL +
			'group="Catharsis' + EOL +	# ******* RBF:  Hardcoded group ***
			'screenshot="' + self.screenshot + EOL +
			'thumbnail="' + self.thumbnail + EOL +
			'\n' +
			'project="' + self.project + EOL +
			'assoc_projects="' + self.assoc_projects + EOL +
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

	def update(self):
		"""
			A bit of a kluge to let me retain a python/shell/etc.
			flat data file.  Dumps the passed object to a temp file,
			concatenates the passed file to it, then imports that.
			Can be from the exception in load.
			then dumps the passed object to it, 
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
			os.remove(tmp + 'c')
		except IOError, info:
			print "Immport problem with", dfile, info
			raise IOError

		try:
			self.xfer_import(P)
		except NameError, info:
			print "update: problems:", info
			raise ImportError

		dfile = open(data, 'w+')
		dfile.write(self.dump())
		dfile.close()


def main():
	print "Welcome to classes..."
	
	
	g = Group()
	g.load('Catharsis')

	for p in g.pagelist:
		print "got page:", p.name, p.desc_title, p.fun_title


if __name__ == '__main__':
	main()
