#!/usr/bin/env python
""" A tool to generate a graphic to show the available fonts """
import os
import sys
import logging

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import imagemaker
import clutils

def main():
	tan = (196, 176, 160, 255)
	black = (0,0,0,255)
	fill = black
	
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/'
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
	content += "<blockquote> End characters are: one-el-eye oh-zero (1lI O0)</blockquote><p><hr><p>"
	file.write(content)
	
	# No need to do this anymore - we now step through them....
	#f = clutils.fontlib()	# create a font object
	#fontlist=f.fontdict.items()	# convert to a list of tuples for sorting...
	#fontlist.sort()
	
	teststring = "The Quick Brown Fox jumped over the Lazy Dog. AaBbCc 1234567890 1lI O0"
	
	fonts = clutils.FontLib()
	
	for fontfile in sorted(fonts.fontdict.keys(), key=lambda s: s.lower()):
		print fontfile
		path = fonts.fontdict[fontfile]
		for ftype in 'ttf', 'TTF', 'otf', 'notafont':
			if fontfile.endswith(ftype):
				pngname = fontfile.replace(ftype, 'png')
				break
		if type == 'notafont':
			continue	# not a font....
			
		pngfile = font_index_dir + pngname
		# Get the family and style....
		try:
			f = ImageFont.truetype(path, 1)
		except:
			logging.warning("Error: not a TrueType/OpenType font: %s", path, exc_info=True)
			continue
		
		family = f.font.family
		style = f.font.style
	
		#fontstring = family + '-' + style + ': ' + teststring
		fontstring = teststring
		imagemaker.make_text_graphic(fontstring, pngfile, path, fontsize=60, fill=fill, maxsize=(1000,100))
		content = '<b>'
		content += family + ' ' + style
		content += '</b> <tt>'
		content += path
		content += '</tt><br>\n'
		content += '<img src="' + pngname + '">\n'
		content += '<hr>\n'
		file.write(content)
	
	file.write("</body></html>\n")
	file.close()

if __name__ == '__main__':
	main()	