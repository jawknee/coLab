#!/usr/bin/env python
"""
	classes for defining the various data file fomrats

"""

import os
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
		self.create=cldate.string2utc("1970-01-24T09:23:45")
		self.update=cldate.string2utc("1970-01-24T09:23:45")
		
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
		self.url_head = os.path.join(conf.coLab_url_head, 'Group', name)
		self.root = os.path.join(conf.coLab_root, 'Group', name)
		self.home = os.path.join(conf.coLab_home, 'Group', name)

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
			raise ImportError
		

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
	return (self.update)	# return the update time as seconds for sorting
def createkey(self):
	return (self.create)	# ditto the create time
class Page:
	"""
	The data associated with a song, imported from 
	a raw file - at this point.
	"""
	
	def __init__(self):
		self.name="<unset>"
		self.desc_title="<unset>"
		self.fun_title="<unset>"
		self.screenshot="<unset>"
		self.description="<unset>"

		self.project="<unset>"
		self.assoc_projects=''

		self.prevlink="<unset>"
		self.nextlink="<unset>"

		# initial value close to the epoch
		self.create=cldate.string2utc("1970-01-24T09:23:45")
		self.update=cldate.string2utc("1970-01-24T09:23:45")

	def load(self,path):
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

		#
		# if path is passed in, use it - otherwise
		# look in the current dir...
		try:
			path
		except:
			path = '.'

		dfile = os.path.join(path, 'data')
		#print "dfile:",dfile

		#
		try:
			P = imp.load_source('',dfile)
			os.remove(dfile + 'c')
		except IOError, info:
			#print "Immport problem with", dfile, info
			raise IOError
		#
		# Step through them...
		try:
			self.name = P.name
			self.desc_title = P.desc_title
			self.fun_title = P.fun_title
			self.screenshot = P.screenshot
			self.description = P.description

			self.project = P.project
			self.assoc_projects = P.assoc_projects

			self.prevlink = P.prevlink
			self.nextlink = P.nextlink

			self.create = cldate.string2utc(P.create)
			self.update = cldate.string2utc(P.update)

		except (NameError, AttributeError), info:
			print "Note: unset var in data file", info



	def dump(self):
		"""
		Output in a format suitable for replacing the data file
		"""
		EOL = '"\n'

		return( 'name="' + self.name + EOL +
			'desc_title="' + self.desc_title + EOL +
			'fun_title="' + self.fun_title + EOL +
			'screenshot="' + self.screenshot + EOL +
			'\n' +
			'project="' + self.project + EOL +
			'assoc_projects="' + self.assoc_projects + EOL +
			'description="""' + self.description +
			'"""\n' +
			'\n' +
			'prevlink="' + self.prevlink + EOL +
			'nextlink="' + self.nextlink + EOL +
			'\n' +
			'create="' + cldate.utc2string(self.create) + EOL +
			'update="' + cldate.utc2string(self.update) + EOL )



def main():
	print "Welcome to clases..."
	
	
	g = Group()
	g.load('Catharsis')

	for p in g.pagelist:
		print "got page:", p.name, p.desc_title, p.fun_title


if __name__ == '__main__':
	main()
