#!/usr/bin/env python
"""
	Rebuild the links, side bar, and anything else
	needing routine maintenance.

	We're (currently) passed the name of a group and 
	rebuild the content found there.
"""

import os
import sys
import coLabUtils
import cLdate
import imp
import cLdate

# 
# For sorting - return the appropriate time in seconds
def updatekey(self):
	return (self.update)	# return the 
class Song:
	"""
	The data associated with a song, imported from 
	a raw file - at this point.
	"""
	
	def __init__(self):
		self.name="<unset>"
		self.desc_title="<unset>"
		self.fun_title="<unset>"
		self.description="<unset>"
		self.project="<unset>"
		self.assoc_projects=False

		self.create="1776.07.02T12:32:18"
		self.update="1776.07.04T18:23:29"

	def load(self):
		"""
		This is a bit kludgy right now, 
		we read the file, then populate
		the song object with the data.

		We could just create a list imported
		objects, but we'd have no idea what 
		vars were involved.
		"""

		# for now, assume we're here, read "data" and 
		# populate ourselves (where legal)
		S = imp.load_source('','data')
		#
		# Step through them...
		try:
			self.name = S.name
			self.desc_title = S.desc_title
			self.fun_title = S.fun_title
			self.description = S.description
			self.project = S.project
			self.assoc_projects = S.assoc_projects

			self.create = cLdate.string2utc(S.create)
			self.update = cLdate.string2utc(S.update)

		except NameError, info:
			print "Note: unset var in data file", info


	def dump(self):
		"""
		Output in a format suitable for replacing the data file
		"""
		EOL = '"\n'

		return( 'name="' + self.name + EOL +
			'desc_title="' + self.desc_title + EOL +
			'fun_title="' + self.fun_title + EOL +
			'\n' +
			'project="' + self.project + EOL +
			'assoc_projects="' + self.assoc_projects + EOL +
			'description="""' + self.description +
			'"""\n' +
			'create="' + cLdate.utc2string(self.create) + EOL +
			'update="' + cLdate.utc2string(self.update) + EOL )



def main():
	print "Welcome to main...."
	
	songdata = Song()
	songdata.load()
	print songdata.dump()



if __name__ == '__main__':
	main()
