#!/usr/bin/env python
"""
	coLab config: globals and such
	
"""


#--------------------------------------
# Resolution 
#--------------------------------------
# sizes and classes to define the various resolutions
# Define the graphical sizes

# size of the inline html
DISPLAY_SIZE = (640, 480)	

# a list of tuples, each member defines a size, starting at
# the largest, going to the smallest, then a 2-tuple of
# (width, height), the next size in the sequence. 
# The sequence is used to determine which sizes to 
# generate for multiple platforms by following a chain.
SIZE_LIST = [
			( '4k-Ultra-HD', (3840, 2160), "Super-HD"),
			( 'Super-HD', (2560, 1440), "HiDef"),
			( 'Super-HD-Letterbox', (1920, 1440), "HD-Letterbox"),
			( 'HiDef', (1920, 1080), "Large"),
			( 'HD-Letterbox', (1440, 1080), "Large"),
			( 'Large', (1280, 960), "Medium"),
			( 'Medium', (960, 720), "Small"),
			( 'Small', (640, 480), "Tiny"),
			( 'Tiny', (320, 240), "Micro"),
			( 'Micro', (160, 120), None)
			]

SMALLEST = 'Micro'		# the smallest size used 

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
if __name__ == '__main__':
	main()