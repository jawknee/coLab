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


def make_image():
	"""
	 for now - just create and display a time box...
	"""

	dir="/Users/Johnny/dev/ScrollLine/Overlays"
	os.system('rm -rfv ' + dir + '/')
	os.system('mkdir -pv ' + dir )

	fps = 6
	duration = 147.012
	screenshot = "../Group/Catharsis/Page/StormLevelCheck/ScreenShot.png"
	
	width = 640
	height = 480
	size = (width, height)

	tn_width = 160
	tn_height = 120

	xStart = 73
	xEnd = 597

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
	orig_image = Image.open(screenshot)
	base_image = orig_image.resize( size, Image.ANTIALIAS ).convert('RGBA')


	print "Current start/stop: ", xStart, xEnd
	ans = raw_input("OK? (y/N)")
	if [ ans == 'y' ]:
		base_image.show()
		print "Hit return for", xStart, xEnd
		(nuxStart, nuxEnd) = input("Enter xStart, xEnd: (" + str(xStart) + ', ' + str(xEnd) + '): ' )
		print "nux:", nuxStart, nuxEnd
		xStart = nuxStart
		xEnd = nuxEnd
	else:
		print ("I was looking for 'y'.")


	#font = ImageFont.truetype('../Resources/Fonts/data-latin.ttf', 18)
	font = ImageFont.truetype('../Resources/Fonts/DigitaldreamFatSkewNarrow.ttf', 12)

	lefttime = -1	# force a bild of the left box
	righttime = -1 	# ditto, right
	lastx = -1	# x-pos - force draw of the cursor

	xPos = xStart
	prevLine = -1

	# Now - loop through, generating images as we need...
	frames = int(duration * fps)
	xLen = xEnd - xStart

	frameIncr = float(xLen) / frames

	#fr=1	# Frame number...
	#while fr <= frames:
	for fr in range(frames):
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
		if fr == 0:	# add a highlight
			lbox_draw.rectangle(box_rect, outline=eBlue)
			lbox_draw.rectangle(box_rect2, outline=eBlue)
		
		time = float(fr) / fps
		seconds = int(time)
		tstring = "%01d:%02d" % divmod(seconds, 60)

		(twidth, theight) = lbox_draw.textsize(tstring, font=font)
		offset = ( (box_width - twidth) / 2, (box_height - theight) / 2)
		lbox_draw.text( offset, tstring, font=font, fill=Green)
		overlay.paste(lbox, lbox_offset)


		rbox = box.copy()
		rbox_draw = ImageDraw.Draw(rbox)
		if fr == frames-1:	# Outline last frame time.
			rbox_draw.rectangle(box_rect, outline=eBlue)
			rbox_draw.rectangle(box_rect2, outline=eBlue)


		seconds = int(duration - time)
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

		print "Frame", fr, "of", frames
		frame_image.save( dir + '/' + 'Frame-%05d.png' % fr, 'PNG')

		xPos += frameIncr


	

def main():
	make_image()


if __name__ == '__main__':
	main()

