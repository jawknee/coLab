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
		logging.info("Searching %s", file)
		if os.path.isfile(file):
			logging.info("Found a config") 
			break
		else:
			continue

	if file.startswith(dnf):
		logging.warning("No config file found.")
		raise(ImportError)

	try:
		conf = imp.load_source('',file)
		conf.file = file
		return(conf)
	except (ImportError, info):
		logging.warning ("get_config: ImportError", exc_info=True)
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
		logging.warning("problem changing to: %s", path)
		return True

	try:
		htime = os.path.getmtime(file)
	except:
		htime = 0       # force a rebuild

	try:
		dtime = os.path.getmtime('data')
	except:
		#
		# Depending on 
		logging.info("Trouble getting mtime on data time...skipping", exc_info=True)
		return True

	if htime < dtime or opt == 'All':
		if opt == 'All':
			logging.info("Option All - regenerating all")
		else:
			logging.info("File data is newer, need to regenerate the file: %s", file)

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
		logging.error("ERROR:  string_to_filename - not a string %s", title)
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
		logging.error("Fatal error - string to unique, not a dir: %s", dir)
		sys.exit(1)
		
	basename = string_to_filename(title)
	
	basepath = os.path.join(dir, basename)
	extra = ''		# first try the base name...
	count = 1
	while os.path.isfile(basepath + extra):
		extra = "_%d" % count
		logging.info("extra: %s", extra)
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
		logging.info("problem changing to: %s", path)
		return False

	count = 0
	
	for file in os.listdir('.'):
		for type in typelist:
			if file.endswith(type):
				count += 1
	logging.info("has_filetype Found: %d", count)
	return count >= min


class FontLib:
	""" A repository for fonts
	
	Keeps track of them, can return the full path, and
	can generate an overview doc/web page.
	"""
	
	def __init__(self, conf=None):
		""" Read the font info and organize
		
		Builds a library of fonts that can be referenced 
		by name - flags any fonts that are not unique by base 
		name.
		"""
		
		if conf is None:
			logging.warning("FontLib called with no conf - check this.")
			conf = get_config()
			
		fontpath = os.path.join(conf.coLab_home, "Resources", "Fonts")
		if not os.path.exists(fontpath):
			logging.error("No such path: %s - cannot continue.", fontpath)	
			sys.exit(1)
			
		current_dir = os.path.abspath('.')
		try:
			os.chdir(fontpath)
		except:
			logging.warning("Cannot find fontpath, %s", fontpath, exc_info=True)
			return
		
		self.fontpath = fontpath
		logging.info("Greetings from: %s", fontpath)
		self.fontdict = {}
		
		for (here, dirlist, filelist) in os.walk(self.fontpath):
			for file in filelist:
				logging.info("Checking file: %s", file)
				if not file.endswith('.ttf') and not file.endswith('.otf'):
					continue
				logging.info("Found one - dir is: %s", here)
				try:
					self.fontdict[file]
				except:
					# don't have one - add it...
					self.fontdict[file] = os.path.join(here, file)
				else:
					logging.warning("Duplicate fonts: %s - %s and %s", file, self.fontdict[file], here)
				logging.info("Current entry: %s, %s", file, self.fontdict[file])

		os.chdir(current_dir)

	def return_fontpath(self,font=None):
		""" return the full path to the specified font
		
		NOTE: need to do something about the default - but if nothing passed, or 
		found, return the default.
		"""
		DEF_FONT = "Brentford.otf"	# we can do better - and define some where else?  RBF
		if font is None:
			font = DEF_FONT
			logging.info("No font passed - using default: %s", font)
			
		try:
			fontdir = self.fontdict[font]
		except:
			logging.warning("Did not find font: %s - using default %s", font, DEF_FONT)
			try:
				fontdir = self.fontdict[DEF_FONT]
			except:
				logging.error("Fatal: Fontlib - no default font: %s", DEF_FONT)
				sys.exit(1)
		return os.path.join(self.fontpath, fontdir)

	def list_fonts(self):
		""" list them out...   
		
		mostly for debugging
		"""
		for font in sorted(self.fontdict.keys(), key=lambda s: s.lower()):
			logging.info("Font: %s, path: %s", font, os.path.join(self.fontpath,self.fontdict[font]))

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	for name in ['This', 'is a space', '?,()#&*?what??']:
		print ("string_to_filename:", string_to_filename(name))
	print ("testing get_config")
	conf=get_config()
	print ("result:",  conf.coLab_url_head)
	print ("result:", conf.file, conf.coLab_root, conf.coLab_home)
	
	#fontclass = FontLib()
	fontclass = FontLib(conf)
	fontclass.list_fonts()
	print ("Font pass", fontclass.return_fontpath('DigitalDream.ttf'))
	print ("Font none", fontclass.return_fontpath())
	print ("Font bogo", fontclass.return_fontpath('bogofont'))