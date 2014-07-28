#!/usr/bin/env python
""" Helpful tools.. """

import os
import sys
import logging
import string
import imp
import six

def get_config(debug=False):
	""" Get the colab config...

	Look in the likely places for a .coLab.conf file - return 
	the contents as an object.
	
	This allows paths to be set differently on different installations.

	Returns a conf object with these members:
	
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
	""" return True of False if the current directory needs to be updated 
	
	- e.g., the data file is newer than the index.shtml.  The flag allows
	the "All" flag to be passed in and returned, cleans up the code on the 
	calling side
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
	""" touch the file..."""
	f = file(filename, 'a')
	try:
		os.utime(filename, None)
	finally:
		f.close()

def string_to_filename(title):
	""" Convert a passed string to a legal filename

	This is overly strict.  We only allow alphanumeric,
	'-', '_', and '.'.  Of all others, spaces are changed 
	to '_' all others to '-'.  We toss any additional substitutions, 
	and force the first char to be an alphanum, unless an
	explicit '-', '_', or '.'. 
	
	Likely to be used by string_to_unique to append a
	number as needed to create a legal and unique 
	file name.
	"""
	filename = ''	# start here - add chars as we go...
	
	if not isinstance(title, six.string_types):
		print "ERROR:  string_to_filename - not a string", title
		sys.exit(1)
		
	alnum_chars = "%s%s" % (string.ascii_letters, string.digits)
	other_valid = "-_."		# valid, after the first character
	valid_chars = alnum_chars

	blank_subst = '_'
	other_subst = '-'
	skip_subs = True		# used to prevent multiple subs, or starting with one...

	for c in title:
		# regular character (alphanumeric?)
		if valid_chars.find(c) != -1:
			filename += c
			skip_subs = False
			if other_valid:		# was this the first?
				valid_chars += other_valid
				other_valid = False
			continue
		# at this point, it's not a valid char, skip or sub
		if skip_subs:
			continue
		skip_subs = True
		if c.isspace():
			filename += blank_subst
		else:
			filename += other_subst

	if len(filename) == 0:
		filename = 'GenName'	# generated/generic name - fail "safe"
	return filename

def string_to_unique(title, dir=None):
	""" Turn any arbitrary string into a legal and unique file name.
	
	Use string_to_filename, then look in dir
	to see if it exists, if so - start adding
	numbers to the end until it is unique.
	"""
	if not os.path.isdir(dir):
		print "Fatal error - string to unique, not a dir:", dir
		sys.exit(1)
		
	basename = string_to_filename(title)
	
	basepath = os.path.join(dir, basename)
	extra = ''		# first try the base name...
	count = 1
	while os.path.isfile(basepath + extra):
		extra = "_%d" % count
		print "extra:", extra
		count += 1
		
	return basename + extra

	
		
def has_filetype(path, typelist=[], min=1):
	""" return true if the given path has at least "min" matchin files

	Matches the patterns in typelist 
	Used to determine if we need look in a dir for a graphic (.png)
	or audio (.aif, .aiff).
	"""
	try:
		os.chdir(path)
	except:
		print "problem changing to", path
		return False

	count = 0
	
	for file in os.listdir('.'):
		for type in typelist:
			if file.endswith(type):
				count += 1
	print "has_filetype Found:", count
	return count >= min

class fontlib:
	""" A class to let us manage our fonts

	A collection of paths.   Mostly to return the path to a named font,
	but also can return the list of fonts / paths.
	Needs a rewrite to actually scan the library and build the list.
	"""
	def __init__(self, conf=None):
		self.conf = conf
		if self.conf is None:
			self.conf = get_config()
		
		self.default = 'FoxboroScriptEBold'	# default font...
		self.fontdict = {
		'BaroqueScript': 'Resources/Fonts/BaroqueScript.ttf',
		'TantrumTongue': 'Resources/Fonts/TantrumTongue.ttf',
		'Neurochrome': 'Resources/Fonts/Neurochrome/neurochr.ttf',
		'Daemones': 'Resources/Fonts/DAEMONES.ttf',
		'TarantellaMF': 'Resources/Fonts/TarantellaMF/Tarantella MF.ttf',
		'Minus': 'Resources/Fonts/Minus.ttf',
		'Scretch': 'Resources/Fonts/Scretch.ttf',
		'Radaern': 'Resources/Fonts/RADAERN.ttf',
		'FoxboroScriptBold': 'Resources/Fonts/SF Foxboro Script v1.0/SF Foxboro Script Bold.ttf',
		'FoxboroScriptEBold': 'Resources/Fonts/SF Foxboro Script v1.0/SF Foxboro Script Extended Bold.ttf',
		'WorstveldSling': 'Resources/Fonts/WorstveldSling/WorstveldSling.ttf',
		'Maxine': 'Resources/Fonts/maxine.ttf',
		'JohnnyMacScrawl': 'Resources/Fonts/JohnnyMacScrawl/jmacscrl.ttf',
		'Blippo': 'Resources/Fonts/Blippo/BlippBlaD.ttf',
		'Metropolataines': 'Resources/Fonts/Metropolitaines/MetroD.ttf',
		'Diskus': 'Resources/Fonts/Diskus/DiskuDMed.ttf',
		'Coronet': 'Resources/Fonts/Coronet/CoronI.ttf',
		'Blacklight': 'Resources/Fonts/Blacklight/BlackD.ttf',
		'Freebooter': 'Resources/Fonts/Freebooter/FreebooterUpdated.ttf',
		'Gillies': 'Resources/Fonts/Gillies/GilliGotDLig.ttf',
		'Palette': 'Resources/Fonts/Palette/PaletD.ttf',
		'DomCasual': 'Resources/Fonts/Dom Casual/DomCasDReg.ttf',
		'RageJoi': 'Resources/Fonts/Rage/RageJoiD.ttf',
		'Rage': 'Resources/Fonts/Rage/RageD.ttf',
		'AenigmaScrawl': 'Resources/Fonts/AenigmaScrawl/aescrawl.ttf',
		'DejaVuSans-BoldOblique': 'Resources/Fonts/dejavu-fonts-ttf-2.34/ttf/DejaVuSans-BoldOblique.ttf'
		}

	def fontpath(self,font):
		""" Return the path to the passed font,

		return the default if no match.
		"""
		try:
			path= os.path.join(self.conf.coLab_home, self.fontdict[font])
		except KeyError:
			print "No such font: '" + font + "' Using default: '" + self.default + "'"
			path=self.fontdict[self.default]
		return path

	def list(self):
		""" prints the list of fonts """
		# is this used??? - doesn't look like it...
		for name in self.fontdict:
			print name, self.fontdict[name]

if __name__ == "__main__":
	for name in ['This', 'is a space', '?,()#&*?what??']:
		print "string_to_filename:", string_to_filename(name)
	print "testing get_config"
	conf=get_config()
	print "result:",  conf.coLab_url_head, conf.coLab_rel_head
	print "result:", conf.file, conf.coLab_url_head, conf.coLab_rel_head
