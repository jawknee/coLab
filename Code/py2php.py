#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" reads a passed file or stdin (if called from the command line)
	and converts python-style assignment statements into 
	php assignments - most interestingly: triple quoted strings
	become heredocs...
"""

import sys

def py2php(filename="data"):
	""" read the file as a series of python style
		assignment statements, and output a php 
		compatible eval string.
	"""
	if filename != '':
		try: 
			print "# Reading from:", filename
			string = file(filename).read()
		except:
			pass
	else:
		print "# reading from stdin:"
		string = sys.stdin.read()
		
	#print " Parsing:", string
	#print "# =================================="

	# Now, take that string, as a series of lines, 
	# and step through it, converting to php-style assignments
	# as we go...
	out = ''
	lines = string.split('\n')
	max = len(lines)
	print "# Number of Lines:", max
	i = 0
	while i < max:
		l = lines[i]
		if len(l) == 0:
			print"// blank...", i
			i += 1
			continue
		if l[0] == '#':
			out += '//' + l[1:] + '\n'	 # comment - output and move on...
			i += 1
			continue
		eq_pos = l.find('=')
		if eq_pos == -1:
			out += "# <blankline> \n"	# RBF!
			i += 1
			continue
		# if we get here, we've got an assignment statement...
		var = l[:eq_pos]
		val = l[eq_pos+1:]
		if val[0] == 'u':
			val = val[1:]	# remove the uni-code prefix...
		# convert triple quoted to nowdocs.. 
		if val[0:3] == '"""' or val[0:3] == "'''":	# is this a triple quote?
			out += '$' + var + " = <<<'EOF'\n"
			endquote = val[0:3]
			val = val[3:]
			while val.find(endquote) == -1:
				out += val + '\n'
				i += 1
				val = lines[i]
			laststring = val[:val.find(endquote)] 
			if len(laststring) != 0:	# if the line line is blank - don't do it.
				out += val[:val.find(endquote)] + '\n'
			out += 'EOF;\n'
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

	print py2php(filename)