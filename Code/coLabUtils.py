#!/usr/bin/env python
"""
	Helpful tools..
"""

import os
import imp

def get_config():
	"""
		Look in the likely places for a .coLab.conf file - return 
		the contents as an object.
	"""

	# locations in the order we want to search...
	dnf="DidNoTfIndaFile"
	locations=('.', os.path.expanduser("~/coLab"), "../coLab", "../../coLab", "~/coLab", dnf)

	for loc in locations:
		file = loc + "/.coLab.conf"
		print "Searching", file
		if os.path.isfile(file):
			#print "Found it..."
			break
		else:
			#print "nope..."
			continue

	if file.startswith(dnf):
		raise(ImportError)

	conf = imp.load_source('',file)
	conf.file = file
	return(conf)





if __name__ == "__main__":
	print "testing get_config"
	conf=get_config()
	print "result:",  conf.coLab_url_head, conf.coLab_rel_head
	print "result:", conf.file, conf.coLab_url_head, conf.coLab_rel_head
