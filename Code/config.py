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
			( 'Medium', (960, 720)),
			( 'Small', (640, 480)),
			( 'Tiny', (320, 240))
			]
SMALLEST = 'Small'		# the smallest size used 

def main():
	print "Colab config"
	print "Display size:", DISPLAY_SIZE
	for size in SIZE_LIST:
		print "Size", size[0], 'is:', size[1]
	
if __name__ == '__main__':
	main()