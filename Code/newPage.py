#!/usr/bin/env python
#
# Create a new page...
#
import os
import sys
import cldate
import clutils
import clclasses

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
	pagehome = os.path.join(conf.coLab_home, 'Group', 'Catharsis', 'Page', name)

	if os.path.isdir(pagehome):
		print "Dir:", pagehome, "exists.   Update?"
		print "For now... the answer is yes."
		# We want to implement an update option...
	else:
		try:
			os.makedirs(pagehome)

		except OSError, info:
			print "Path:", pagehome, "problem:", info
			print "Try again."
			sys.exit(1)

	page = clclasses.Page()	# new page...
	datafile = os.path.join(pagehome, 'data')
	f = open(datafile, 'a+')
	f.write('name="' + name + '"\n')
	f.close()

	page.load(pagehome)
	print "pagehome is ", pagehome
	#page.update(pagehome)	# maybe someday...

	page.desc_title = get_input(page.desc_title, "Descriptive title")
	page.fun_title = get_input(page.fun_title, "Fun title")
	page.screenshot = "ScreenShot.png"
	page.duration = float(get_input(str(page.duration), "Duration (secs)"))

	page.project = get_input(page.project, "Project")

	print page.dump()

	f = open(datafile, 'w')
	f.write(page.dump())
	f.close()

	imagemaker.make_images(page)	
	



def main():
	try:
		name = sys.argv[1]

	except IndexError, info:
		print "%s: Must specify page name: %s" % (sys.argv[0], info)
		sys.exit(1)

	newPage(name)

if __name__ == '__main__':
	main()

