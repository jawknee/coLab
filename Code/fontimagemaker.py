#!/usr/bin/env python
"""
	A quick, one-off to generate graphics of the current fonts...
"""
import sys
import os

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import imagemaker
import clutils

tan = (196, 176, 160, 255)
black = (0,0,0,255)
fill = black

fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/'
font_index_dir = '/Users/Johnny/coLab/Resources/FontIndex/'

html = font_index_dir + 'index.html'
try:
	file = open(html,'w')
except:
	print "Oops: no go on:", file
	sys.exit(1)


content = "<html><head><title>Current Font List</title></head>\n"
content += "<body bgcolor=#d0d0d0 text=#101010>\n"
content += "<h2>Current Font List</h2>\n"
file.write(content)

# No need to do this anymore - we now step through them....
#f = clutils.fontlib()	# create a font object
#fontlist=f.fontdict.items()	# convert to a list of tuples for sorting...
#fontlist.sort()

teststring = ": The Quick Brown Fox jumped over the Lazy Dog. AaBbCc 1lI O0"

try:
	os.chdir(fontpath)
except:
	print "Cannot get to dir:", fontpath
	print "Fatal"
	raise IOError()
	# build a dictionary of names to directory names.

for fontfile in (os.listdir('.')):
	print fontfile
	path = os.path.join(fontpath, fontfile)
	pngname = fontfile.replace('ttf', 'png')
	pngfile = font_index_dir  + pngname
	# Get the family and style....
	try:
		f = ImageFont.truetype(path, 1)
	except:
		print "Error: not a Truetype font:", path
		continue
	
	family = f.font.family
	style = f.font.style

	fontstring = family + '-' + style + teststring
	imagemaker.make_text_graphic(fontstring, pngfile, path, fontsize=60, fill=fill, maxsize=(1000,100))
	content = '<b>'
	content += family + ' ' + style
	content += '</b> <tt>'
	content += path
	content += '</tt><br>\n'
	content += '<img src="' + pngfile + '">\n'
	content += '<hr>\n'
	file.write(content)


file.write("</body></html>\n")
file.close()
