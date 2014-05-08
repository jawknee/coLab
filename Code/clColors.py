#!/usr/bin/env python
"""
Color definitions for coLab.
"""


# Colors....
XPARENT = (0,0,0,0)
HILITE = (255,255,255,32)    # mostly transparent white - to contrast black
LOLITE = (0, 0, 0, 64)        # mostly transparent black - etc....
WHITE = (255,255,255,255)
BLACK = (0,0,0,255)
MAIZE = (255, 225, 50, 255)
PART_BLACK = (0, 0, 0, 180)    # partly transparent black
TRANS_GRAY = (128, 128, 128, 128)   # middle gray, half transparent
DARK_X_GRAY = (64, 64, 64, 64)		# dark and mostly xprnt
GRAY_TEXT = (192, 192, 192, 255)
GREEN = (20, 255, 20, 255)    # a bright, opaque green
# 
# Waveform colors...  
BRIGHT_RED = (255, 48, 16, 255) # bright red - warnings and such
TAN = (196, 176, 160, 255)
# Cool..
EL_BLUE = (20, 20, 255, 255)    # electric blue
DEEP_BLUE = (10, 20, 128, 255)    # dark blue
DK_BLUE = (5, 10, 64, 255)    # dark blue
# Hot..
DK_RED = (90, 0, 0, 255)
ORANGE = (255, 80, 10, 255)
YELLOW = (255, 255, 0, 255)	
BRIGHT_YELLOW = (255,255,40,255)
# Cold..
ICE_BLUE1 = (0, 70, 150, 255)
ICE_BLUE2 = (70, 130, 200, 255)
# Desert  (courtesy, www.colorcombos.com)
#  http://www.colorcombos.com/color-schemes/386/combolibrary.html
DESERT_DARK = (42, 44, 5, 255)
DESERT_TAN = (239, 224, 185, 255)
DESERT_GOLD = (228, 176, 74, 255)
DESERT_BROWN = (100, 59, 15, 255)
DESERT_ORANGE = (183, 82, 30, 255)
# Nola
EGGPLANT = (97, 64, 81, 255)
#CLAY = (126, 60, 45, 255)
CLAY = (96, 40, 30, 255)
#CLAY = (166, 142, 115, 255)
OCHRE = (204, 119, 34, 255)
LIME = (191, 255, 0, 255)
AQUA = (0, 255, 255, 255)	# cyan

COLAB_BLUE = (0, 73, 141, 255)	# coLab Logo central color
COLAB_HILITE = (175, 198, 219, 255)	# logo highlight 
COLAB_SHADOW = (0, 25, 48, 255)		# and shadow

def htmlcolor(color=BLACK):
	'''
	Convert the passed color in an html string
	'''
	hcolor='#'
	for c in color[0:3]:	# skip the transparncy, if any
		hcolor += '%02x' % c
		
	return hcolor

class Themes:
	"""
	Define the colors for themes - for now, just wave forms
	"""
	def __init__(self, theme="Default"):
		"""
		Simply set the vars...
		"""
		DEFAULT_THEME = "Blue"
		if theme == "Default":
			theme = DEFAULT_THEME
		
		#	define the themes with:
		#	background, rms, wave, peak, cursor, cursor_offset (possibly text, lines, etc)
		#  I don't like the way I'm doing this - needs rework...
		themelist = [
					[ 'Blue', PART_BLACK, DEEP_BLUE, EL_BLUE, WHITE, MAIZE, LOLITE],
					[ 'Fire', PART_BLACK, DK_RED, ORANGE, BRIGHT_YELLOW, EL_BLUE, LOLITE],
					[ 'Iced', DK_BLUE,  ICE_BLUE1, ICE_BLUE2, WHITE, BRIGHT_RED, XPARENT],
					[ 'Beam', DARK_X_GRAY, DEEP_BLUE, GREEN, WHITE, YELLOW, XPARENT], 
					[ 'Desert', DESERT_GOLD, DESERT_BROWN, DESERT_ORANGE, DESERT_TAN, DESERT_DARK, LOLITE],
					[ 'Nola', CLAY, EGGPLANT, LIME, AQUA, BLACK, XPARENT]
					]
		
		self.theme_names = []
		valid = False
		for themeinfo in themelist:
			name = themeinfo[0]
			self.theme_names.append(name)
			if name == DEFAULT_THEME:
				default_vals = themeinfo[1:]
			if name == theme:
				values = themeinfo[1:]
				valid = True
				
		if not valid:
			values = default_vals	# just in case we get passed a bogus theme .. don't blow up
			print "ERROR:  invalid theme:", theme, " - using default:", DEFAULT_THEME
		
		self.theme = theme
		(self.background, self.rms, self.wave, self.peak, self.cursor, self.cursor_offset) = tuple(values)