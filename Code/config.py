#!/usr/bin/env python
"""
	coLab config: globals and such
	
"""

# Define the graphical sizes

# size of the inline html
DISPLAY_SIZE = (640, 480)	
# a list of tuples, each member defines a size, starting at
# the largest, going to the smallest - not all are used.

SIZE_LIST = [
			( 'Super-HD', (2560, 1440)),
			( 'Super-HD-Letterbox', (1920, 1440)),
			( 'HiDef', (1920, 1080)),
			( 'HD-Letterbox', (1440, 1080)),
			( 'Large', (1280, 960)),
			( 'Medium', (960, 720)),
			( 'Small', (640, 480)),
			( 'Tiny', (320, 240)),
			( 'Micro', (160, 120))
			]

SMALLEST = 'Small'		# the smallest size used 

class Sizes:
	def __init__(self):
		self.size_d = dict()
		self.names = []
		for (name, size)  in SIZE_LIST:
			self.size_d[name] = size
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
		return (self.size_d[name])
			
		
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
if __name__ == '__main__':
	main()