#!/usr/bin/env python
#
# Create a new page...
#
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
	

def newPage(name):
	print "Creating page:", name

	conf = clutils.get_config()
	group = cltkutils.getGroup()
	pagehome = os.path.join(conf.coLab_home, 'Group', group, 'Page', name)
	local = 'coLab_local'

	if os.path.isdir(pagehome):
		print "Dir:", pagehome, "exists.   Update?"
		print "For now... the answer is yes."
		# We want to implement an update option...
	else:
		try:
			# Create the local subdir - get it all at once...
			localdir = os.path.join(pagehome, local)
			os.makedirs(localdir)

		except OSError, info:
			print "Path:", localdir, "problem:", info
			print "Try again."
			sys.exit(1)

	page = clclasses.Page(name)	# new page...
	page.home = pagehome

	# create a stub for the data file...
	datafile = os.path.join(pagehome, 'data')
	f = open(datafile, 'a+')
	f.write('name="' + name + '"\n')
	f.close()

	page.load()
	print "pagehome is ", pagehome
	#page.update(pagehome)	# maybe someday...

	page.desc_title = get_input(page.desc_title, "Descriptive title")
	page.fun_title = get_input(page.fun_title, "Fun title")
	page.screenshot = os.path.join(local, "ScreenShot.png")
	page.duration = float(get_input(str(page.duration), "Duration (secs)"))
	
	page.song = get_input(page.song, "Song")
	page.project = page.song
	page.part = get_input(page.part, "Part (All)")

	page.screenshot = os.path.join(local, "ScreenShot.png")
	page.thumbnail = "ScreenShot_tn.png"
	print page.dump()

	page.post()	# put the data into file...

	print "Screenshot", page.screenshot
	print "newPage: page.name", page.name
	print "newPage: page.home", page.home

	screenpath = os.path.join(page.home, page.screenshot)
	if not os.path.exists(screenpath):
		print "Copy a screenshot to:"
		print screenpath
		a = raw_input("Hit return when ready...")


	imagemaker.make_images(page)	
	print "Page home:", pagehome

def main():
	try:
		name = sys.argv[1]

	except IndexError, info:
		print "%s: Must specify page name: %s" % (sys.argv[0], info)
		sys.exit(1)

	newPage(name)

if __name__ == '__main__':
	main()

