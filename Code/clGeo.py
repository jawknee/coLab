#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
""" a command line interface into media info
	
	specifically designed to allow the php to have
	direct access to the size data structures, currently 
	encoded in the python.
"""

import sys
import logging

import config

def main():
	""" Return specific values based on the requested info.
	
		Runstring only - basically an interface to allow the php
		code to calculate sizes using the same code/values as 
		the older html generation.
	
		runstring is restricted - must include size and one option:
		clGeo.py size -o | -p | -f | -l | -r | -w | -h
		   where:
		   	-o	xOffset 
		   	-p  pageview width
		   	-f  adjust factor
		   	-l  left border
		   	-r	right border
		   	-w	media width
		   	-h  media height
		
		when in doubt, returns...   42  (why not?)
	"""
	argc = len(sys.argv)
	if argc > 2:
		media_size = sys.argv[1]	
		option = sys.argv[2]
	else:
		return 42

	sizes = config.Sizes()	
	try:
		(pgview_width, pgview_height) = sizes.sizeof(config.BASE_SIZE)
		(media_width, media_height) = sizes.sizeof(media_size)
	except:
		return 42
	
	if option == '-o':
		return config.MAIN_LEFT_EDGE 
	elif option == '-p':
		return pgview_width
	elif option == '-f':
		return  sizes.calc_adjust(media_height)
	elif option == '-l':
		return config.SG_LEFT_BORDER
	elif option == '-r':
		return config.SG_RIGHT_BORDER
	elif option == '-w':
		return media_width
	elif option == '-h':
		return media_height
	else:
		return 42
	
if __name__ == '__main__':
	print main(),