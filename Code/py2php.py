#!/usr/local/bin/ython3
# -*- coding: utf-8 -*-
""" reads a passed file or stdin (if called from the command line)
	and converts python-style assignment statements into 
	php assignments - most interestingly: triple quoted strings
	become heredocs...
"""

import sys
""" can't use this until I can get a reasonable version of python working at Sonic.net
import subprocess
#"""
from distutils.version import StrictVersion

import logging

import locTagger

def py2php(filename="data", tagit=False, phpversion='4.0'):
	""" read the file as a series of python style
		assignment statements, and output a php 
		compatible eval string.
		
		If tagit is True - we first run the file through
		the locTagger...
		
		if php version is a placeholder - if older
		versions of php are extant - we need to NOT use
		a "NowDoc".
	
	"""
	logging.info("Reading from: %s", filename)
	if filename != '':
		try: 
			string = file(filename).read()
		except:
			string = ''
	else:
		logging.info("Reading from stdin:")
		string = sys.stdin.read()
		
	EOF_tag = "EOF"	# 
	END_tag = EOF_tag + ';\n'
	
	# If our php version is new enough, use a "NowDoc" 
	# rather than a "HereDoc"  - somewhat more secure...
	if StrictVersion(phpversion) >= StrictVersion('5.3.0'):		
		EOF_tag = "'" + EOF_tag + "'"	
	# Now, take that string, as a series of lines, 
	# and step through it, converting to php-style assignments
	# as we go...
	out = ''
	lines = string.split('\n')
	max = len(lines)
	logging.info("Number of Lines: %s", max)
	i = 0
	while i < max:
		l = lines[i]
		if len(l) == 0:
			logging.info("blank, line # %s", i)
			out += '// --- \n'
			i += 1
			continue
		if l[0] == '#':
			out += '//' + l[1:] + '\n'	 # comment - output and move on...
			i += 1
			continue
		eq_pos = l.find('=')
		if eq_pos == -1:
			out += "// -?- " + l + " -?- \n"	
			i += 1
			continue
		# if we get here, we've got an assignment statement...
		var = l[:eq_pos]
		val = l[eq_pos+1:]
		if val[0] == 'u':
			val = val[1:]	# remove the uni-code prefix...
		# convert triple quoted to here/nowdocs.. 
		if val[0:3] == '"""' or val[0:3] == "'''":	# is this a triple quote?
			out += '$' + var + " = <<<" + EOF_tag + '\n'
			endquote = val[0:3]
			val = val[3:]

			while val.find(endquote) == -1:
				# special case for the description var and  tagging...
				if var == "description" and tagit:
					logging.info("Running string through loctagger")
					val = locTagger.loctagger(val)
				out += val + '\n'
				i += 1
				val = lines[i]
			laststring = val[:val.find(endquote)] 
			if len(laststring) != 0:	# if the line line is blank - don't do it.
				out += val[:val.find(endquote)] + '\n'
			out += END_tag
			i += 1
		else:
			out += '$' + var + ' = ' + val + ';\n'
			i += 1
		
	return out	

if  __name__ == '__main__':
	# open a passed file - if not, use stdin.	
	filename = ''
	argc = len(sys.argv)
	if argc > 1:
			filename=sys.argv[1]

	""" sigh - no good until we get a newer version of python on Sonic.net.
	logging.basicConfig(level=logging.INFO)
	#logging.basicConfig(level=logging.WARNING)
	logging.info('Filename: %s', filename)
	try:
		version = subprocess.check_output(["php", "-v"]).split(' ')[1]
	except:
		version = "4.0.0"	# worst case?
	#"""
	version = '4.4.0'
	
	print py2php(filename, tagit=True, phpversion=version),
