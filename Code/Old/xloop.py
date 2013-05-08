#!/usr/bin/env python
"""
	Test looping through a try...

"""

import sys

class Thing():
	def __init__(self):
		return
		
def main():
	
	X=Thing()
	print "Hello..."

	while True:
		try:	# a bunch of things...  all fail...
			X.a = a
			X.b = b
		except NameError, info:
			print "NameError:", info
			print sys.exc_info()[0]
			
			print "xfer_import: unset var in data file", info
			print sys.exc_info()[0]
			print (type(info))
			print (info.args)
			print (info)

			sys.exit(1)


if __name__ == '__main__':
	main()
