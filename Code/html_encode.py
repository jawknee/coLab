#!/usr/local/bin/python3
""" convert cgi-bin info into assignments

	Convert the cgi-bin info on stdin to assignment statements 
	that can be used in most contexts
	
"""

import sys

def hencode(s):

	#s=raw_input()	# input string
	l=len(s)
	i=0		# pointer into the scring
	quoted=False
	ff = chr(12) 	# form feed
	out = ''

	xlatn_table = {			# a dictionary of conversions of special characters
		'&':  '&#038;',		# ampersand
		"'":  '&#039;',		# apostrophe
		'\\': '&#092;',		# backslash
		'"':  '&#034;',		# quote
		'#':  '&#035;',		# pound sign
		'+':  ' ',		# plus sign
		'=':  '&#061;'		# minus sign
		}

	alldone = False
	while i < l and not alldone:
		c=s[i]

		# and some extras..., put quotes around vars
		if c == '=' and not quoted:	# start of a variable assignment (unless quoted and we're inside of an assignment )
			out += '="'
			quoted=True
		elif c == '&':
			if quoted:
				out += '"\n'
				quoted = False
			else:
				out += '\n'

		elif c == ff:	# form feed - EOF
			if quoted:
				out += '"\n'
				
			alldone = True

		else:
			# first - convert any % hex characters...
			if c == '%':	
				c = chr(int(s[i+1:i+3],16))
				i+=2
			# 
			# Convert any special characters to their numeric equivalent...
			try:
				out += xlatn_table[c]
			except KeyError:
				out += c

		i+=1

	if quoted:
		out += '"'
	out += '\n'
	return out

if  __name__ == '__main__':
	""" Interface when called passing stdin... 
	"""
	s = sys.stdin.read()
	print (hencode(s))

