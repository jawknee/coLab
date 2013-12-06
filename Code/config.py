#!/usr/bin/env python
"""
	coLab config: globals and such
	
"""
import math

#--------------------------------------
# Resolution 
#--------------------------------------
# sizes and classes to define the various resolutions
# Define the graphical sizes

# size of the inline html
DISPLAY_SIZE = (640, 480)	
# base size of the time boxes
T_BOX_WIDE = 55
T_BOX_HIGH = 35
# Sound graphic borders:
SG_LEFT_BORDER = 30
SG_RIGHT_BORDER = 10
SG_TOP_BORDER = 25
SG_BOTTOM_BORDER = 25

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
			( 'HD-Letterbox', (1440, 1080), "Medium"),
			( 'Large', (1280, 960), "Medium"),
			( 'Medium', (960, 720), "Small"),
			( 'Small', (640, 480), "Tiny"),
			( 'Tiny', (320, 240), "Micro"),
			( 'Micro', (160, 120), None)
			]

BASE_SIZE = 'Small'		# what the main "page" is generated with...
SMALLEST = 'Tiny'		# the smallest size used 

class Sizes:
	def __init__(self):
		self.size_d = dict()
		self.next_d = dict()
		self.names = []
		for (name, size, next)  in SIZE_LIST:
			self.size_d[name] = size
			self.next_d[name] = next
			self.names.append(name)
			if name == SMALLEST:
				break
			
	def list(self):
		"""
		A simple generator of the size names
		"""
		for name in self.names:
			yield name
	def sizeof(self, name):
		""" Return the size tuple (width, height)
		"""
		return (self.size_d[name])
	def next_size(self, name):
		""" What's the next size down?
		"""
		return(self.next_d[name])
	def calc_scale(self, height):
		"""
		returns the ratio of the passed height to the
		BASE size (above)
		"""
		base_height = self.sizeof(BASE_SIZE)[1]	# we only care about the height...
		return(float(height)/base_height)
	
	def calc_adjust(self, height):
		"""
		returns a modified adjustment
		where a pure ratio is too much.
		Currently: sqrt of calc_scale
		"""
		
		return(math.sqrt(self.calc_scale(height)))
		
def main():
	print "Colab config"
	print "Display size:", DISPLAY_SIZE
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
if __name__ == '__main__':
	main()