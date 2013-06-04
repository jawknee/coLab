#!/usr/bin/env python
"""
	Helpful tools..
"""

import os
import sys
import imp

def get_config(debug=False):
	"""
		Look in the likely places for a .coLab.conf file - return 
		the contents as an object.
		
		This allows paths to be set different on different installations.
		return a conf object with these members:
		
		Current coLab vars:
		coLab_url_head		absolute URL   (e.g. http://localhost/coLab )
		coLab_root			how to get to here from local root (e.g. /coLab )
		coLab_home 			absolute file path (e.g. /Users/Johnny/dev/coLab )
	"""

	# locations in the order we want to search...
	dnf="DidNoTfIndaFile"
	locations=('.', os.path.expanduser("~/coLab"), "../coLab", "../../coLab", "~/coLab", dnf)

	for loc in locations:
		file = loc + "/.coLab.conf"
		if debug:
			print "Searching", file
		if os.path.isfile(file):
			if debug:
				print "Found it..."
			break
		else:
			#print "nope..."
			continue

	if file.startswith(dnf):
		raise(ImportError)

	try:
		conf = imp.load_source('',file)
		conf.file = file
		return(conf)
	except ImportError, info:
		print "get_config: ImportError", info
		sys.exit(1)	

def needs_update(path, file="index.shtml", opt='nope'):
	"""
	return True of False if the current directory 
	needs to be updated - e.g., the data file is
	newer than the index.shtml.  The flag allows
	the "All" flag to be passed in and returned,
	cleans up the code on the calling side
	"""
	if opt == 'All':
		return True

	try:
		os.chdir(path)
	except:
		print "problem changing to", path
		return False

	try:
		htime = os.path.getmtime(file)
	except:
		htime = 0       # force a rebuild

	try:
		dtime = os.path.getmtime('data')
	except:
		#
		# Depending on 
		print ("Trouble getting mtime on data time...skipping")
		return False

	if htime < dtime or opt == 'All':
		if opt == 'All':
			print "Option All - regenerating all"
		else:
			print "File data is newer, need to regenerate the", file, "file"

		return True
	else:
		return False

def touch(filename):
	f = file(filename, 'a')
	try:
		os.utime(filename, None)
	finally:
		f.close()

class fontlib:
	"""
	A collection of paths.   Mostly to return the path to a named font,
	but also can return the list of fonts / paths.
	"""
	def __init__(self):
		self.default = 'FoxboroScriptEBold'	# default font...
		self.fontdict = {
		'BaroqueScript': '/Users/Johnny/dev/coLab/Resources/Fonts/BaroqueScript.ttf',
		'TantrumTongue': '/Users/Johnny/dev/coLab/Resources/Fonts/TantrumTongue.ttf',
		'Neurochrome': '/Users/Johnny/dev/coLab/Resources/Fonts/Neurochrome/neurochr.ttf',
		'Daemones': '/Users/Johnny/dev/coLab/Resources/Fonts/DAEMONES.ttf',
		'TarantellaMF': '/Users/Johnny/dev/coLab/Resources/Fonts/TarantellaMF/Tarantella MF.ttf',
		'Minus': '/Users/Johnny/dev/coLab/Resources/Fonts/Minus.ttf',
		'Scretch': '/Users/Johnny/dev/coLab/Resources/Fonts/Scretch.ttf',
		'Radaern': '/Users/Johnny/dev/coLab/Resources/Fonts/RADAERN.ttf',
		'FoxboroScriptBold': '/Users/Johnny/dev/coLab/Resources/Fonts/SF Foxboro Script v1.0/SF Foxboro Script Bold.ttf',
		'FoxboroScriptEBold': '/Users/Johnny/dev/coLab/Resources/Fonts/SF Foxboro Script v1.0/SF Foxboro Script Extended Bold.ttf',
		'WorstveldSling': '/Users/Johnny/dev/coLab/Resources/Fonts/WorstveldSling/WorstveldSling.ttf',
		'Maxine': '/Users/Johnny/dev/coLab/Resources/Fonts/maxine.ttf',
		'JohnnyMacScrawl': '/Users/Johnny/dev/coLab/Resources/Fonts/JohnnyMacScrawl/jmacscrl.ttf',
		'Blippo': '/Users/Johnny/dev/coLab/Resources/Fonts/Blippo/BlippBlaD.ttf',
		'Metropolataines': '/Users/Johnny/dev/coLab/Resources/Fonts/Metropolitaines/MetroD.ttf',
		'Diskus': '/Users/Johnny/dev/coLab/Resources/Fonts/Diskus/DiskuDMed.ttf',
		'Coronet': '/Users/Johnny/dev/coLab/Resources/Fonts/Coronet/CoronI.ttf',
		'Blacklight': '/Users/Johnny/dev/coLab/Resources/Fonts/Blacklight/BlackD.ttf',
		'Freebooter': '/Users/Johnny/dev/coLab/Resources/Fonts/Freebooter/FreebooterUpdated.ttf',
		'Gillies': '/Users/Johnny/dev/coLab/Resources/Fonts/Gillies/GilliGotDLig.ttf',
		'Palette': '/Users/Johnny/dev/coLab/Resources/Fonts/Palette/PaletD.ttf',
		'DomCasual': '/Users/Johnny/dev/coLab/Resources/Fonts/Dom Casual/DomCasDReg.ttf',
		'RageJoi': '/Users/Johnny/dev/coLab/Resources/Fonts/Rage/RageJoiD.ttf',
		'Rage': '/Users/Johnny/dev/coLab/Resources/Fonts/Rage/RageD.ttf',
		'AenigmaScrawl': '/Users/Johnny/dev/coLab/Resources/Fonts/AenigmaScrawl/aescrawl.ttf'
		}

	def fontpath(self,font):
		"""
		Return the path to the passed font,
		return the default if no match.
		"""
		try:
			path=self.fontdict[font]
		except KeyError:
			print "No such font: '" + font + "' Using default: '" + self.default + "'"
			path=self.fontdict[self.default]
		return path

	def list(self):
		"""
		Return the list of fonts
		"""
		for name in self.fontdict:
			print name, self.fontdict[name]


if __name__ == "__main__":
	print "testing get_config"
	conf=get_config()
	print "result:",  conf.coLab_url_head, conf.coLab_rel_head
	print "result:", conf.file, conf.coLab_url_head, conf.coLab_rel_head
