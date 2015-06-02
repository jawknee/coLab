#!/usr/bin/env python
"""
	Any html numeric codes to the ascii equiv.
"""

import sys

def hdecode(s):

	l=len(s)
	i=0		# pointer into the scring
	out = ''

	while i < l:	# step through the chars...
		c=s[i]

		# if we see an ampersand, look for a "#" (we don't do symbolics here....)
		if c == '&':
			if s[i+1] == '#':
				# Why we're here - convert the number...
				numstr = ''	# start from nothing....

				i += 1
				while s[i+1] in '0123456789':
					numstr += s[i+1]
					i += 1
				i += 1	# skip over the semi-colon...
				try:
					out += chr(int(numstr))
				except:
					out += numstr	# for what ever reason, not an actual num-string...
				# print ">>", numstr, "<<<>>>", out,  "<<<"
			else:
				out += '&'
		else:
			out += c

		i+=1

	out += '\n'
	return out

if  __name__ == '__main__':
	s = sys.stdin.read()
	print hdecode(s)

