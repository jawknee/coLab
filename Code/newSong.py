#!/usr/bin/env python
""" Create a new song...

This is the old manual script, not used on coLab
"""

import os
import sys
import cldate
import clutils
import clclasses
import cltkutils

import imagemaker


def get_input(var, preprompt):
	"""
		Input something for the given far...
	"""

	if var == "<unset>" or var == "":
		prompt = preprompt + " (New): "
		default = ""
	else:
		prompt = preprompt + " (" + var + "): "
		default = var
	
	s = raw_input(prompt)
	if s == '':
		return(default)
	else:
		return(s)
	

def newSong(name):
	print "Creating song:", name

	conf = clutils.get_config()
	#group = cltkutils.getGroup()

	#songhome = os.path.join(conf.coLab_home, 'Group', group, 'Song', name)
	#songhome = os.path.join(conf.coLab_home, 'Group', 'SBP', 'Song', name)
	songhome = os.path.join(conf.coLab_home, 'Group', 'Johnny', 'Song', name)
	local = 'coLab_local'

	if os.path.isdir(songhome):
		print "Dir:", songhome, "exists.   Update?"
		print "For now... the answer is yes."
		# We want to implement an updatekoption...
	else:
		try:
			# Create the local subdir - get it all at once...
			localdir = os.path.join(songhome , local)
			os.makedirs(localdir)

		except OSError, info:
			print "Path:", localdir, "problem:", info
			print "Try again."
			sys.exit(1)

	song = clclasses.Song(name)	# new page...
	song.home = songhome

	# create a stub for the data file...
	datafile = os.path.join(songhome, 'data')
	f = open(datafile, 'a+')
	f.write('name="' + name + '"\n')
	f.close()

	song.load()
	print "songhome is ", songhome
	print "createtime is ", ' ' + cldate.utc2string(song.createtime)
	print "updatetime is ", ' ' + cldate.utc2string(song.updatetime)
	#song.update(songhome)	# maybe someday...

	song.desc_title = get_input(song.desc_title, "Short title")
	song.fun_title = get_input(song.fun_title, "Long title")
	
	print song.dump()

	song.post()	# put the data into file...

	print "newsong: song.name", song.name
	print "newsong: song.home", song.home



def main():
	try:
		name = sys.argv[1]

	except IndexError, info:
		print "%s: Must specify song name: %s" % (sys.argv[0], info)
		sys.exit(1)

	newSong(name)

if __name__ == '__main__':
	main()

