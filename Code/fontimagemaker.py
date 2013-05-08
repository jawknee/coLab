#!/usr/bin/env python
"""
	A quick, one-off to generate graphics of the current fonts...
"""
import sys
import imagemaker
import clutils

tan = (196, 176, 160, 255)
black = (0,0,0,255)
fill = black

font_index_dir="/Users/Johnny/coLab/Resources/FontIndex/"

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

f = clutils.fontlib()	# create a font object

teststring = ": The Quick Brown Fox jumped over the Lazy Dog. AaBbCc 1lI O0"
fontlist=f.fontdict.items()	# convert to a list of tuples for sorting...
fontlist.sort()
for font, path in fontlist:
	print font
	#path = f.fontpath(font)
	pngfile = font_index_dir  + font + '.png'
	imagemaker.make_text_graphic(font + teststring, pngfile, path, fontsize=60, fill=fill, maxsize=(1000,100))
	content = '<b>'
	content += font
	content += '</b> <tt>'
	content += path
	content += '</tt><br>\n'
	content += '<img src="' + font + '.png">'
	content += '<hr>\n'
	file.write(content)


file.write("</body></html>\n")
file.close()
