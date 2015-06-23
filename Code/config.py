#!/usr/bin/env python
""" coLab config: globals and such """

import logging
import math

#--------------------------------------
# Interface descriptions
#--------------------------------------
NUM_BUTS = 10	# number of locator buttons
#--------------------------------------
# Resolution 
#--------------------------------------
# sizes and classes to define the various resolutions
# Define the graphical sizes

# base size of the time boxes
T_BOX_WIDE = 55
T_BOX_HIGH = 23
# box size of the marker boxes
M_BOX_WIDE = 18
M_BOX_HIGH = 18
# Sound graphic borders:
SG_LEFT_BORDER = 30
SG_RIGHT_BORDER = 10
SG_TOP_BORDER = 25
SG_BOTTOM_BORDER = 25

#--------------------------------------
# Coordinates 
#--------------------------------------
# These are "constants" that are related to formatting
# that is in the current .css files (currently:
# /coLab/Resources/Style_VidAutoTest.css - soon to 
# change).
# RBF:  This should probably change  - the 175 is the 
# left margin of the Content block, plus the
# 5px margin of the mainsection - these should be
# discernable directly from the html ?
#MAIN_LEFT_EDGE = 228	# 204 + 208 ?
MAIN_LEFT_EDGE = 175	
MAIN_WIDTH = 700

#
#--------------------------------------
# Size Definitions
#--------------------------------------
# a list of tuples, each member defines a size, starting at
# the largest, going to the smallest, then a 2-tuple of
# (width, height), the next size in the sequence. 
# The sequence is used to determine which sizes to 
# generate for multiple platforms by following a chain.
SIZE_LIST = [
			( '4k-Ultra-HD', (3840, 2160), "HiDef"),
			( 'Super-HD', (2560, 1440), "HiDef"),
			( 'Super-HD-Letterbox', (1920, 1440), "Large"),
			( 'HiDef', (1920, 1080), "Medium"),
			( 'HD-Letterbox', (1440, 1080), "Small"),
			( 'Large', (1280, 720), "Small"),
			( 'Medium', (960, 540), "Small"),
			( 'Small', (640, 360), "Tiny"),
			( 'Tiny', (320, 180), "Micro"),
			( 'Micro', (160, 90), None)
			]

BASE_SIZE = 'Small'		# what the main "page" is generated with...
SMALLEST = 'Tiny'		# the smallest size used 

class Sizes:
	""" A class to let us manage the various media sizes """
	def __init__(self):
		self.size_d = dict()
		self.next_d = dict()
		self.names = []
		for (name, size, next) in SIZE_LIST:
			self.size_d[name] = size
			self.next_d[name] = next
			self.names.append(name)
			if name == SMALLEST:
				break
			
	def list(self):
		""" A simple generator of the size names """
		for name in self.names:
			yield name

	def sizeof(self, name):
		""" Return the size tuple (width, height) """
		return (self.size_d[name])

	def next_size(self, name):
		""" What's the next size down? """
		return(self.next_d[name])

	def calc_scale(self, height):
		""" returns the ratio of the passed height to the BASE size (above) """
		base_height = self.sizeof(BASE_SIZE)[1]	# we only care about the height...
		return(float(height)/base_height)
	
	def calc_adjust(self, height):
		""" returns a modified adjustment where a pure ratio is too much.

		Currently: sqrt of calc_scale
		"""
		return(math.sqrt(self.calc_scale(height)))
	
	def is_smaller_than(self, s1, s2):
		""" Method of returning if a size, s1, is smaller than another, s2.  
		
		Since the sizes are stored largest first, the logic is reversed.
		"""
		try:
			return self.names.index(s1) > self.names.index(s2)
		except ValueError:
			logging.warning("Sizes class invalid sizes: %s, %s", s1, s2, exc_info=True)
			raise ValueError('Invalid Size')
	def is_larger_than(self,s1,s2):
		""" Convenient notation for the reverse... """
		return not self.is_smaller_than(s1, s2)			
	
	def get_screensize(self):
		""" This won't work yet - it's a reference for later """
		screen_width = root.winfo_screenwidth()
		screen_height = root.winfo_screenheight() 	
		
def main():
	print "Colab config"
	print "Base size:", BASE_SIZE
	for size in SIZE_LIST:
		print "Size", size[0], 'is:', size[1]
	s = Sizes()
	print "List:"
	s.list()
	
	print "Sizes:"
	for name in s.names:
		print "Size of", name, "is", s.sizeof(name)
		print "next size would be:", s.next_size(name)
		
	print "Scale of 960:", s.calc_scale(960)
	print "Adjst of 960:", s.calc_adjust(960)
	
	if s.is_smaller_than('Large', 'Small'):
		print "oops.   Large is not smaller than Small"
	else:
		print "Larger than Small"
		
	if s.is_smaller_than('Medium','Medium'):
		print "oops  medium is not smaller"
	else:
		print "Medium is"
		
	if s.is_smaller_than('Tiny', 'HiDef'):
		print "Tiny is smaller than HiDef"
	else:
		print "ooooops Tiny is not not smaller than HiDef"
	try:
		if s.is_smaller_than('Tiny', 'Bogus'):
			print "No good - not smaller than Bogus"
	except ValueError:
		print "Good: detected Bogus"
		
	if s.is_larger_than('Tiny', 'HiDef'):
		print "oooops,  Tiny is not larger than HiDef"
	else:
		print "is larger than looks good"
if __name__ == '__main__':
	main()