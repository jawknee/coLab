#!/usr/bin/env python
"""
	Some scripting to create a series of 
	images that will be the movie of the 
	scrolling line...
"""

import Image
import ImageDraw
import ImageFont

import sys
import os

import clclasses


def make_images(page):
	"""
	 for now - just create and display a time box...
	"""

	print "make_images: page.home:", page.home

	dir = os.path.join(page.home, 'coLab_local', 'Overlays' )
	os.system('rm -rfv ' + dir + '/')
	os.system('mkdir -pv ' + dir )

	fps = 6
	try:
		os.chdir(page.home)
	except OSError, info:
		print "Problem changing to :", page.home
		print info
		sys.exit(1)

	width = 640
	height = 480
	size = (width, height)

	tn_width = 160
	tn_height = 120
	tn_size = (tn_width, tn_height)

	# Colors....
	Xparent = (0,0,0,0)
	Hilite = (255,255,255,100)	# mostly transparent white - to contrast black
	black = (0,0,0,255)
	partBlack = (0, 0, 0, 180)	# partly transparent black
	Green = (20, 255, 20, 255)	# a bright, opaque green
	eBlue = (20, 20, 255, 255)	# electric blue

	box_width = 55
	box_height = 35
	box_size = (box_width, box_height)
	box_rect = [ (0,0), (box_width-1, box_height-1) ]
	box_rect2 = [ (2,2), (box_width-3, box_height-3) ]

	lbox_offset = (2, height - box_height - 2)
	rbox_offset = (width - box_width - 2, height - box_height - 2)

	# create basic box...
	box = Image.new('RGBA', box_size, color=partBlack)
	#boxdraw = ImageDraw.Draw(box)
	#boxdraw.rectangle(box_rect, outline=Green)


	# Set up the base image that will be copied and overlaid as needed...
	#
	orig_image = Image.open(page.screenshot)
	base_image = orig_image.resize( size, Image.ANTIALIAS ).convert('RGBA')
	tn_image = orig_image.resize(tn_size, Image.ANTIALIAS ).convert('RGB')

	tn_file = os.path.join(page.home, page.thumbnail)
	tn_image.save(tn_file, 'PNG')


	print "Keep current start/stop: ", page.xStart, page.xEnd
	ans = raw_input("OK? (y/N)")
	if  ans != 'y':
		base_image.show()
		print "Hit return for", page.xStart, page.xEnd
		(nuxStart, nuxEnd) = input("Enter xStart, xEnd: (" + str(page.xStart) + ', ' + str(page.xEnd) + '): ' )
		print "nux:", nuxStart, nuxEnd
		page.xStart = nuxStart
		page.xEnd = nuxEnd
		print "page:", page.xStart, page.xEnd
		page.post()
	else:
		print "Keeping:", page.xStart, page.xEnd


	# ********** RBF:   Hardcoded '/' in path... find a way to split and join the bites.

	#font = ImageFont.truetype('../Resources/Fonts/data-latin.ttf', 18)
	fontpath = os.path.join(page.coLab_home, 'Resources/Fonts/DigitaldreamFatSkewNarrow.ttf')

	font = ImageFont.truetype(fontpath, 12)

	lefttime = -1	# force a bild of the left box
	righttime = -1 	# ditto, right
	lastx = -1	# x-pos - force draw of the cursor

	xPos = page.xStart
	prevLine = -1

	# Now - loop through, generating images as we need...
	#
	frames = int(page.duration * fps) + 1
	print "duration, fps, frames:", page.duration, fps, frames
	xLen = page.xEnd - page.xStart

	frameIncr = float(xLen) / frames

	#while fr <= frames:
	for fr_num in range(frames):
		# create a new overlay
		overlay = Image.new( 'RGBA', size, color=Xparent)
		overlay_draw = ImageDraw.Draw(overlay)

		# Put the cursor into the overlay
		xLine = int(xPos)
		overlay_draw.line( [ (xLine-1,0), (xLine-1,479) ], fill=Hilite)
		overlay_draw.line( [ (xLine+1,0), (xLine+1,479) ], fill=Hilite)
		overlay_draw.line( [ (xLine,0), (xLine,479) ], fill=black)

		#
		# Build the left and right boxes...
		lbox = box.copy()
		lbox_draw = ImageDraw.Draw(lbox)	# draw object...
		if fr_num == 0:	# add a highlight
			lbox_draw.rectangle(box_rect, outline=eBlue)
			lbox_draw.rectangle(box_rect2, outline=eBlue)
		
		#
		# in the case of the last frame, with more than a second per frame, 
		# (longer than ~10 minutes) the final frame can came up short.   
		# force it...
		if fr_num != frames-1:	# if not the last frame
			time = float(fr_num) / fps	# normal...
		else:
			time = page.duration		# force to the end...
			
		seconds = int(time)
		tstring = "%01d:%02d" % divmod(seconds, 60)

		(twidth, theight) = lbox_draw.textsize(tstring, font=font)
		offset = ( (box_width - twidth) / 2, (box_height - theight) / 2)
		lbox_draw.text( offset, tstring, font=font, fill=Green)
		overlay.paste(lbox, lbox_offset)


		rbox = box.copy()
		rbox_draw = ImageDraw.Draw(rbox)
		if fr_num == frames-1:	# Outline last frame time.
			rbox_draw.rectangle(box_rect, outline=eBlue)
			rbox_draw.rectangle(box_rect2, outline=eBlue)


		seconds = int(page.duration - time)
		tstring = "-%01d:%02d" % divmod(seconds, 60)

		(twidth, theight) = rbox_draw.textsize(tstring, font=font)
		offset = ( (box_width - twidth) / 2, (box_height - theight) / 2)
		rbox_draw.text( offset, tstring, font=font, fill=Green)
		overlay.paste(rbox, rbox_offset)
		#
		# Now we gotta git a bit tricky since PIL doesn't support alpha compositing...
		r, g, b, a = overlay.split()
		overlay_rgb = Image.merge('RGB', (r,g,b))
		mask = Image.merge('L', (a,))

		frame_image = base_image.copy()		# new copy of the base...
		frame_image.paste(overlay_rgb, (0,0), mask)

		print "Frame", fr_num, "of", frames
		frame_image.save( dir + '/' + 'Frame-%05d.png' % fr_num, 'PNG')

		xPos += frameIncr


def make_text_graphic(string, output_file, fontfile, fontsize=45, border=2, fill=(196, 176, 160, 240), maxsize=(670,100) ):
	"""
	Since we're here with these imports - a simple enough 
	routine to return a PNG image of the passed text.  
	size is a (width, height) tuple.
	The fontfile var is the full path to a truetype font file.
	(for now, size=12)
	"""
	font = ImageFont.truetype(fontfile, fontsize)

	# create a temp image - just long enough to get the size of the text
	Xparent = (0,0,0,0)
	size = (10,10)
	box = Image.new('RGBA', size, color=Xparent)
	box_draw = ImageDraw.Draw(box)

	(w,h) = box_draw.textsize(string, font=font)

	print "Size is:", w, h
	# Let's see if we overflowed the size...
	# (There may be a more python way of doing this, 
	# but let's just return the largest of the returned
	# size divided by the max size - if more than one, 
	# rescale by that...
	#
	pad = border * 2

	maxw, maxh = maxsize
	print "maxsize, maxw, maxh", maxsize, maxw, maxh
	maxw = float(maxw - pad)	# account for the border (included in max)
	maxh = float(maxh - pad)	# and make a float for the division...
	factor = max ( w / maxw, h / maxh )
	if factor > 1.0:
		newfontsize=int(fontsize/factor)
		font = ImageFont.truetype(fontfile, newfontsize)
		print "Scale font by 1 /", factor, " from/to:", fontsize, newfontsize
		print "Factor = min( w/maxw, h/maxh):", factor, w, maxw, h, maxh
		w = int(w/factor)
		h = int(h/factor)
		print "New w,h:", w,h


		
	size = (w+pad, h+pad)
	offset = (border, border)
	
	box = Image.new('RGBA', size, color=Xparent)
	box_draw = ImageDraw.Draw(box)
	box_draw.text(offset, string, font=font, fill=fill)

	box.save(output_file, 'PNG')

	# start over with a new graphic the size of the

	
	

def main():
	make_image()


if __name__ == '__main__':
	main()

