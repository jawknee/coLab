#!/usr/bin/env python
"""
	Read from stdin, write to stdout, fixing various
	charcters as needed...
"""

import sys

def evalfix():

	#s=raw_input()	# input string
	s = sys.stdin.read()
	l=len(s)
	i=0		# pointer into the scring
	out = ''

	while i < l:
		c=s[i]
		if c == '<':
			out = '&#060;'
		elif c == '>':
			out = '&#062;'
		elif c == '$':
			out = '&#036;'
		elif c == '*':
			out = '&#042;'
		elif c == '@':
			out = '&#064;'
		elif c == '\\':
			out = '&#092;'
		elif c == '`':
			out = '&#096;'
		elif c == '\r':
			out = '<br>'
		else:
			out = c

		sys.stdout.write(out)			
		i+=1
	sys.stdout.write('\n')

if  __name__ == '__main__':
	evalfix()

