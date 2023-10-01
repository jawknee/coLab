#!/usr/local/bin/python3
""" Convert "special" characters to meta

	Read from stdin, write to stdout, fixing various
	characters as needed...
	
	Rather than symbolic, number equivalents are used
	this simplifies the conversion back.  New lines
	are converted to '<br>'.
	
"""

import sys

def evalfix(s):

	#s=raw_input()	# input string
	l=len(s)
	i=0		# pointer into the string
	out = ''

	while i < l:
		c=s[i]
		if c == '<':
			out += '&#060;'
		elif c == '>':
			out += '&#062;'
		elif c == '$':
			out += '&#036;'
		elif c == '*':
			out += '&#042;'
		elif c == '@':
			out += '&#064;'
		elif c == '\\':
			out += '&#092;'
		elif c == '`':
			out += '&#096;'
		elif c == '\r':
			out += '<br>'
		else:
			out += c

		i+=1
	out += '\n'
	return out

if  __name__ == '__main__':
	s = sys.stdin.read()
	print (evalfix(s))

