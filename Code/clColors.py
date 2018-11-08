#!/usr/bin/env python
""" Color definitions for coLab. 

Various color definitions both specific and symbolic (e.g., WHITE, HILITE).

Colors are 4-tuples:  (red, green, blue, alpha)   where each is 0-255
A routine (html_color) to emit the html rgb string
A Themes class to let us create a number of color schemes
"""

import logging

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
DK_GRAY_BIAS = (32, 32, 32, 0)
MED_GRAY_BIAS = (96, 96, 96, 0)
# 
# Waveform colors...  
BRIGHT_RED = (255, 48, 16, 255) # bright red - warnings and such
TAN = (196, 176, 160, 255)
# Cool..
EL_BLUE = (20, 20, 255, 255)    # electric blue
DEEP_BLUE = (10, 20, 128, 255)    # dark blue
DK_BLUE = (5, 10, 64, 255)    # dark blue
TRANS_BLUE = (0, 0, 64, 32)
BLUE_BIAS = (15, 30, 0, 0)
DK_BROWN_BIAS = (40, 20, 0, 0)
ORANGE_BIAS = (50, 20, 0, 0)


# Hot..
DEEP_RED = (60, 0, 0, 90)
DK_RED = (90, 0, 0, 255)
ORANGE = (255, 80, 10, 255)
YELLOW = (255, 255, 0, 255)	
BRIGHT_YELLOW = (255,255,40,255)
# Cold..
ICE_BLUE1 = (0, 70, 150, 255)
ICE_BLUE2 = (70, 130, 200, 255)
# Gold
DARK_GOLD = (184, 103, 21, 255)
MED_GOLD =  (225, 135, 35, 255)
LT_GOLD = (251, 176, 39, 255)
GLINT_GOLD = (254, 233, 118, 255)
# Desert  (courtesy, www.colorcombos.com)
#  http://www.colorcombos.com/color-schemes/386/combolibrary.html
DESERT_DARK = (42, 44, 5, 255)
DESERT_TAN = (239, 224, 185, 255)
DESERT_GOLD = (228, 176, 74, 255)
DESERT_BROWN = (100, 59, 15, 255)
DESERT_ORANGE = (183, 82, 30, 255)
# Nola
EGGPLANT = (35, 5, 30, 255)
#CLAY = (126, 60, 45, 255)
CLAY = (100, 10, 0, 255)
#CLAY = (166, 142, 115, 255)
OCHRE = (204, 119, 34, 255)
LIME = (191, 255, 0, 255)
AQUA = (0, 255, 255, 255)	# cyan
# Tree / Leaf
DK_BROWN = (40, 20, 0, 255)
DK_GREEN = (0, 32, 0, 255)
MED_GREEN = (20, 160, 20, 255)
LT_GREEN = (64, 255, 96, 255)
GREEN_WHITE = (128, 255, 192, 255)
SKY_BLUE = (128, 128, 255, 255)

COLAB_BLUE = (0, 73, 141, 255)	# coLab Logo central color
COLAB_HILITE = (175, 198, 219, 255)	# logo highlight 
COLAB_SHADOW = (0, 25, 48, 255)		# and shadow

def htmlcolor(color=BLACK):
	'''
	Convert the passed color in an html string
	'''
	hcolor='#'
	for c in color[0:3]:	# skip the transparency, if any
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
		
		"""
		define the themes with:
		  name,	background, rms, wave, peak, cursor, cursor_offset (possibly text, lines, etc)

		I don't like the way I'm doing this - needs rework... 
		"""
		themelist = [
					[ 'Blue', PART_BLACK, DEEP_BLUE, EL_BLUE, WHITE, MAIZE, LOLITE, BLUE_BIAS ],
					[ 'Fire', DEEP_RED, DK_RED, ORANGE, BRIGHT_YELLOW, EL_BLUE, LOLITE, DK_GRAY_BIAS],
					[ 'Iced', DK_BLUE,  ICE_BLUE1, ICE_BLUE2, WHITE, BRIGHT_RED, XPARENT, DK_GRAY_BIAS],
					[ 'Beam', DARK_X_GRAY, DEEP_BLUE, GREEN, WHITE, YELLOW, XPARENT, ORANGE_BIAS], 
					[ 'Sand', DESERT_GOLD, DESERT_BROWN, DESERT_ORANGE, DESERT_TAN, DESERT_DARK, LOLITE, DK_GRAY_BIAS],
					[ 'Nola', EGGPLANT, CLAY, LIME, AQUA, AQUA, XPARENT, DK_GRAY_BIAS],
					[ 'Tree', DK_BROWN, DK_GREEN, MED_GREEN, GREEN_WHITE, EL_BLUE, XPARENT, ORANGE_BIAS],
					[ 'Leaf', DK_GREEN, LT_GREEN, MED_GREEN, GREEN_WHITE, EL_BLUE, XPARENT, ORANGE_BIAS],
					[ 'Gold', TRANS_BLUE, MED_GOLD, LT_GOLD, GLINT_GOLD, EL_BLUE, XPARENT, ORANGE_BIAS],
					[ 'Vivid', PART_BLACK, DK_BLUE, ORANGE, SKY_BLUE, GREEN, XPARENT, MED_GRAY_BIAS],
					[ 'LeftRightIce', DK_BLUE, ICE_BLUE1, BRIGHT_RED, WHITE, GREEN, XPARENT, DK_GRAY_BIAS],
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
			logging.warning("ERROR:  invalid theme: %s,- using default: %s", theme, DEFAULT_THEME)
		
		self.theme = theme
		(self.background, self.rms, self.wave, self.peak, self.cursor, self.cursor_offset, self.bias) = tuple(values)