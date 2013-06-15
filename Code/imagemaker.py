#!/usr/bin/env python
"""
	Some scripting to create a series of 
	images that will be the movie of the 
	scrolling line...
"""

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
#import Image
#import ImageDraw
#import ImageFont

import sys
import os

import clclasses

def calculate_fps(page):
	"""
	Return a "legal" frames per second based on the number
	of pixels covered by the cursor (xEnd - xStart) and the 
	length of the song (duration)

	Basically the philosophy is that we would like the cursor
	line to never skip a pixel position, but not be any more 
	often then necessary beyond that (i.e, an occassional 'no-move'
	frame.)   We start at the slowest and work our way up until
	we find the value we want and return it.
	"""

	# frames per second is represented as a tuple, literally
	# (frames, seconds) to prevent any rounding error when fps < 1
	# from slowest to fastest )
	# spf:  10 5 4 3 2 1
	# fps:  2 6 10 12 15 24 25 30 50 60 
	# (we skip the fractional ones for now...)
	fps_values = [ (1,10), (1,5), (1,4), (1,3), (1,2), (1,1),
	      (2,1), (6,1), (10,1), (12,1), (15,1), (24,1), 
	      (25,1), (30,1) ]  #  not using:   (50,1), (60,1) 
	try:
		secs_long = float(page.duration)
		start = float(page.xStart)
		end = float(page.xEnd)
	except NameError,info:
		print "oops: must have vars!!", info
		sys.exit(1)
	pixels = end - start + 1 
	# 
	pps =  pixels / secs_long	# pixels per second required
	print "calculate_fps, pps:", pps

	for (frames, seconds) in fps_values:
		fps = float(frames) / seconds
		if fps >= pps:
			break	# this is the one.
	page.post()	# seems like I think you'd want to remember..
	return(fps)	# should account for max fps being enough...

width = 640
height = 480
size = (width, height)

tn_width = 160
tn_height = 120
tn_size = (tn_width, tn_height)		

def make_sub_images(page):
	"""
	Create the main graphic and thumbnail for a page.
	Could/should be generalized for other objects.
	"""
	
	screenshot = os.path.join(page.home, page.screenshot)
	graphic = os.path.join(page.home, page.graphic)
	thumbnail = os.path.join(page.home, page.thumbnail)
	#
	orig_image = Image.open(screenshot)
	base_image = orig_image.resize( size, Image.ANTIALIAS ).convert('RGBA')
	tn_image = orig_image.resize(tn_size, Image.ANTIALIAS ).convert('RGB')

	base_image.save(graphic, 'PNG')
	tn_image.save(thumbnail, 'PNG')
	
def make_images(page):
	"""
	 for now - just create and display a time box...
	"""

	print "make_images: page.home:", page.home

	directory = os.path.join(page.home, 'coLab_local', 'Overlays' )
	os.system('rm -rfv ' + directory + '/')
	os.system('mkdir -pv ' + directory )

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
	"""		RBF:should not be needed.
	tn_image = orig_image.resize(tn_size, Image.ANTIALIAS ).convert('RGB')

	tn_file = os.path.join(page.home, page.thumbnail)
	tn_image.save(tn_file, 'PNG')
	#"""
	
	"""
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
	"""
	
	# use the pixels and duration to determine frames per second...
	#
	page.fps = calculate_fps(page)
	

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
	frames = int(float(page.duration) * page.fps) + 1
	print "duration, fps, frames:", page.duration, page.fps, frames
	xLen = page.xEnd - page.xStart

	frameIncr = float(xLen) / frames

	#while fr <= frames:
	last_fr_num = frames - 1
	for fr_num in range(frames):
		last_frame = fr_num == last_fr_num # Boolean
		# create a new overlay
		overlay = Image.new( 'RGBA', size, color=Xparent)
		overlay_draw = ImageDraw.Draw(overlay)

		#
		# at slower frame rates the final frame can be short of the mark,
		# make sure we're at the end if this is the final frame.
		if last_frame:
			xPos = page.xEnd
			time = page.duration		# force to the end...
		else:
			time = float(fr_num) / page.fps	# normal...

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
		
			
		seconds = int(time)
		tstring = "%01d:%02d" % divmod(seconds, 60)

		(twidth, theight) = lbox_draw.textsize(tstring, font=font)
		offset = ( (box_width - twidth) / 2, (box_height - theight) / 2)
		lbox_draw.text( offset, tstring, font=font, fill=Green)
		overlay.paste(lbox, lbox_offset)


		rbox = box.copy()
		rbox_draw = ImageDraw.Draw(rbox)
		if last_frame:		# Outline last frame time.
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

		print "Frame", fr_num, "of", last_fr_num
		frame_image.save( directory + '/' + 'Frame-%05d.png' % fr_num, 'PNG')

		xPos += frameIncr

	print "Done: ",
	if page.fps < 1:
		print "Seconds per frame:", 1/page.fps
	else:
		print "Frames per second:", page.fps

def make_text_graphic(string, output_file, fontfile, fontsize=45, border=2, fill=(196, 176, 160, 55), maxsize=(670,100) ):
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
	maxw = float(maxw - pad)	# account for the border (included in max)
	maxh = float(maxh - pad)	# and make a float for the division...
	print "maxsize, maxw, maxh", maxsize, maxw, maxh
	factor = max ( w / maxw, h / maxh )
	if factor > 1.0:
		factor = factor * 1.1	# kludge - but accounts for variability in actual font sizes...
		newfontsize=int(fontsize/factor)
		font = ImageFont.truetype(fontfile, newfontsize)
		#print "Scale font by 1 /", factor, " from/to:", fontsize, newfontsize
		#print "Factor = min( w/maxw, h/maxh):", factor, w, maxw, h, maxh
		w = int(w/factor)
		h = int(h/factor)
		print "New w,h:", w,h, "font/new:", fontsize, newfontsize, " factor:", factor
		(w,h) = box_draw.textsize(string, font=font)
		print "New width/height:", w, h

	size = (w+pad, h+pad)
	offset = (border, border)
	
	# start over with a new graphic, this time with the text at the corrected (if necessary) font size
	box = Image.new('RGBA', size, color=Xparent)
	box_draw = ImageDraw.Draw(box)

	(fw,fh) = box_draw.textsize(string, font=font)	# how big is it really?
	offset = ( (size[0] - fw) / 2, ( size[1] - fh) / 2 )
	box_draw.text(offset, string, font=font, fill=fill)

	box.save(output_file, 'PNG')


	
	

def main():

	p = clclasses.Page('imagemakerTest')
	p.xStart = 10
	p.xEnd = 630


	p.duration = .01	# start small (seconds) but get big fast...

	print "xStart, xEnd:", p.xStart, p.xEnd
	while p.duration < 100000:
		fps = calculate_fps(p)
		print "For duration:", p.duration, "- fps:", fps
		p.duration += p.duration * 0.3	# funny boy


if __name__ == '__main__':
	main()

