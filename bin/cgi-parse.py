#!/usr/bin/env python
"""
	Convert the cgi-bin info on stdin to assignment statements 
	that can be used in most contexts
"""

import sys

def cgiparse():

	#s=raw_input()	# input string
	s = sys.stdin.read()
	l=len(s)
	i=0		# pointer into the scring
	quoted=False
	ff = chr(12) 	# form feed
	out = ''


	while i < l:
		c=s[i]
		# first - convert any % hex characters...
		if c == '%':	
			c = chr(int(s[i+1:i+3],16))
			i+=2

		if c == '+':
			out = ' '	# space
		elif c == '=':
			out = '="'
			quoted=True
		elif c == '&':
			if quoted:
				out = '"\n'
				quoted = False
			else:
				out = '\n'
			
		elif c == "'":	# apostrophe
			out='&#039;'
		elif c == '\\':	# backslash
			out='&#092;'
		elif c == '"':	# quote
			out='&#034;'
		elif c == ff:
			break

		else:
			out = c

		sys.stdout.write(out)			
		i+=1
	if quoted:
		sys.stdout.write('"')
	sys.stdout.write('\n')

if  __name__ == '__main__':
	cgiparse()

