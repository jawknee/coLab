#!/usr/bin/env python
""" Create images for video

    Some scripting to create a series of 
	images that will be the movie of the 
	scrolling line.
	
	Can crate an overview image from a sound file, 
	or use a screen capture.
"""

import os
import sys
import logging

import aifc
import math
import threading
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
#import Image
#import ImageDraw
#import ImageFont

import Tkinter as tk
import ttk
import tkFileDialog
import tkMessageBox

#from coLab import main
import config
import clclasses
import cltkutils
import clSchedule
import clAudio
import clColors
import clutils	# for fonts - pull if fonts move to their own module

#size = (width, height)
poster_width = 640
poster_height = 480
poster_size = (poster_width, poster_height)
tn_width = 160
tn_height = 120
tn_size = (tn_width, tn_height)

def calc_fps_val(page):
	"""
	returns the fps value as a real number
	"""
	(f,s) = calculate_fps(page)
	return(float(f)/s)

def calc_fps_string(page):
	"""
	Return the frames per second as a fractional
	string:  frames/second  (if seconds ! 1, else just seconds.)  
	"""
	(f,s) = calculate_fps(page)
	
	if s == 1:
		return(str(f))
	else:
		return(str(f) + '/' + str(s))
def calculate_fps(page):
	"""
	Return a "legal" frames per second based on the number
	of pixels covered by the cursor (xEnd - xStart) and the 
	length of the song (duration)

	Basically the philosophy is that we would like the cursor
	line to never skip a pixel position, but not be any more 
	often then necessary beyond that (i.e, an occasional 'no-move'
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
	      (2,1), (3,1), (4,1), 
	      (6,1), (10,1), (12,1), (15,1), (24,1), 
	      (25,1), (30,1) ]  #  not using:   (50,1), (60,1) 
	
	size_class = config.Sizes()
	(width, height) = size_class.sizeof(page.media_size)
	if page.use_soundgraphic:
		factor = size_class.calc_adjust(height)
		start = int(config.SG_LEFT_BORDER * factor)
		end = width - int(config.SG_RIGHT_BORDER * factor)
	else:
		# we need to know the correction factor for this page size.
		try:
			factor = float(width) / page.screenshot_width
		except:
			factor = 1
		start = page.xStart * factor
		end = page.xEnd * factor
	

	secs_long = float(page.duration)
	pixels = end - start + 1 
	# 
	pps =  pixels / secs_long	# pixels per second required
	print "Size:", width, height
	print "start, end:",  start, end, factor
	print "calculate_fps, pixels/sec:", pps

	"""   At this time - there are no fractional fps,
	      ffmpeg does not support it - so let's eliminate
	      the calculation (may have been a bit of error 
	      anyway...
	"""     
	for (frames, seconds) in fps_values:
		fps = float(frames) / seconds
		#fps = frames
		if fps >= pps:
			break	# this is the one.
	
	#page.post()	# seems like I think you'd want to remember..
	print "Derived fps is:", fps
	return( (frames, seconds) )	# should account for max fps being enough...

def make_sound_image(page,  sound, image, size, prog_bar=None, max_samp_per_pixel=0):
	print "Creating image...", image
	"""
	soundimageTop = tk.Toplevel()
	
	soundimage_frame = tk.LabelFrame(master=soundimageTop, relief=tk.GROOVE, text="New Page Generation" , borderwidth=5)
	soundimage_frame.lift(aboveThis=None)
	soundimage_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
	"""
	
	#img_gen_progbar.max = 600		# This needs to be calculated 
	#img_gen_progbar.post()		# initial layout...   called in Sound_image.build()
	
	# is we're not strict (and didn't pass in an alternate value)
	# skip most samples....
	if not page.strict_graphic and max_samp_per_pixel == 0:
		max_samp_per_pixel = 250	# 
	snd_image = Sound_image(sound, image, size, prog_bar, page.graphic_theme, max_samp_per_pixel)
	snd_image.build()	# separate - we may want to change a few things before the build...
	page.soundthumbnail = "SoundGraphic_tn.png"
	
	make_sub_images(page)
	try:
		page.editor.get_member('soundfile').post()
	except:
		print "Free running..."
		pass
	
	#soundimageTop.destroy()

def make_sub_images(page, size=None):
	"""
	Create the main graphic and thumbnail for a page.
	Could/should be generalized for other objects.
	"""
	#  Screen shot
	if page.use_soundgraphic:
		baseimage = os.path.join(page.home, page.soundgraphic)
	else:
		baseimage = page.localize_screenshot()
	graphic = os.path.join(page.home, page.graphic)
	thumbnail = os.path.join(page.home, page.thumbnail)
	if size is None:
		#size = config.Sizes().sizeof(page.media_size)
		size = poster_size
	#
	# "Screenshot" / Poster image
	# Either a screen shot or a generated image, make a pair
	# of poster images for the video tag
	try:
		orig_image = Image.open(baseimage)
		page.screenshot_width = orig_image.size[0]	# save the width...
	except:
		print "Error opening:", baseimage
	else:
		base_image = orig_image.resize( size, Image.ANTIALIAS ).convert('RGBA')
		tn_image = orig_image.resize(tn_size, Image.ANTIALIAS ).convert('RGB')
		base_image.save(graphic, 'PNG')
		tn_image.save(thumbnail, 'PNG')
		print "make_sub_images:", graphic, thumbnail
		
		resourcedir = os.path.join(page.coLab_home, 'Resources')
		for postertype in [ 'Start', 'Pressed', 'Waiting']:
			overlayname = 'Poster' + postertype + "Overlay.png"
			poster_path = os.path.join(page.home, 'Poster_' + postertype + '.png')
			overlaypath = os.path.join(resourcedir, overlayname)
			try:
				over_image = Image.open(overlaypath).convert('RGBA')
			except IOError, info:
				print "Cannot open poser image", overlaypath, info
			else:
				# could resize here - but I'd rather see it something changes...
				#
				# Now we gotta git a bit tricky since PIL doesn't support alpha compositing...
				r, g, b, a = over_image.split()
				overlay_rgb = Image.merge('RGB', (r,g,b))
				mask = Image.merge('L', (a,))

				poster_image = base_image.copy()		# new copy of the base...
				poster_image.paste(overlay_rgb, (0,0), mask)
				poster_image.save(poster_path, 'PNG')

		
		del orig_image
		
	soundgraph = os.path.join(page.home, page.soundgraphic)
	soundthumb = os.path.join(page.home, page.soundthumbnail)
	try:
		snd_image = Image.open(soundgraph)
	except:
		print "Error opening:", soundgraph
	else:
		tn_image = snd_image.resize(tn_size, Image.ANTIALIAS ).convert('RGB')
		tn_image.save(soundthumb, 'PNG')
		print "make_sub_images:", soundgraph, soundthumb
		del snd_image

def make_images(page, prog_bar=None, media_size=None):
	"""
	Starting with the audio and an image (either a cropped screenshot
	or an image generated from the sound), create a series of images
	that will be turned into a movie by adding a moving cursor
	and elapsed and remaining time counters.  Also the size of the
	boxes and internal fonts should scale to the size being generated.
	
	The time boxes are adjusted to some non-linear relationship
	to the factor - based on the "BASE_SIZE":
	square root of the ratio.
	"""
	
	fontclass = clutils.FontLib()	# this needs to be done at initialization   RBF

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
	if media_size is None:
		media_size = page.media_size
	
	
	
	# the scale factor (below) is the ratio of the target size to
	# the original.   The adjust factor is for 
	# the time boxes.
	#"""
	
	size_class = config.Sizes()
	size = size_class.sizeof(media_size)
	(width, height) = size
	
	adjust_factor = size_class.calc_adjust(height)
	print "adjust_factor:", adjust_factor

	box_width = int(config.T_BOX_WIDE * adjust_factor) 
	box_height = int(config.T_BOX_HIGH * adjust_factor)
	
	box_size = (box_width, box_height)
	box_rect = [ (0,0), (box_width-1, box_height-1) ]
	box_rect2 = [ (2,2), (box_width-3, box_height-3) ]

	h_adj = int(math.ceil(2 * adjust_factor))
	lbox_offset = (2, height - box_height - h_adj)
	rbox_offset = (width - box_width - 2, height - box_height - h_adj)

	# create basic box...
	box = Image.new('RGBA', box_size, color=clColors.PART_BLACK)
	boxdraw = ImageDraw.Draw(box)
	boxdraw.rectangle(box_rect, outline=clColors.GREEN)


	# Set up the base image that will be copied and overlaid as needed...
	#
	if page.use_soundgraphic:
		image = page.soundgraphic
	else:
		image = page.screenshot

	orig_image = Image.open(image)
	base_image = orig_image.resize( size, Image.ANTIALIAS ).convert('RGBA')

	# use the pixels and duration to determine frames per second...
	page.fps = calc_fps_val(page)
	#page.editor.set_member('fps', page.fps)	#rbf ? for now, update the screen?
	

	# ********** RBF:   Hardcoded '/' in path... find a way to split and join the bites.

	#font = ImageFont.truetype('../Resources/Fonts/data-latin.ttf', 18)
	#fontpath = os.path.join(page.coLab_home, 'Resources/Fonts/DigitaldreamFatSkewNarrow.ttf')
	#fontpath = fontclass.return_fontpath('DigitaldreamFatSkewNarrow.ttf')
	#fontpath = os.path.join(page.coLab_home, 'Resources/Fonts/QuartBolD.ttf')
	#fontpath = fontclass.return_fontpath('DigitaldreamFatSkewNarrow.ttf')
	fontpath = fontclass.return_fontpath('DigitaldreamFatSkew.ttf')
	fontsize = int(12 * adjust_factor)
	font = ImageFont.truetype(fontpath, fontsize)

	lefttime = -1	# force a build of the left box
	righttime = -1 	# ditto, right
	lastx = -1	# x-pos - force draw of the cursor
	
	# set the initial line x position and end point,  based
	# either on the known sound graphic dimensions, or a 
	# scaled version of the enter start and end for screen captures, etc.
	if page.use_soundgraphic:
		xPos = int(config.SG_LEFT_BORDER * adjust_factor)
		xEnd = int(width - config.SG_RIGHT_BORDER * adjust_factor)
	else:	# compensate for the actual size of the screenshot image...
		scale_factor = float(width) / page.screenshot_width		
		xPos = int(page.xStart * scale_factor)
		xEnd = int(page.xEnd * scale_factor)
	
	secs_long = float(page.duration)
	xLen = xEnd - xPos
		
	prev = -1	# force

	# Now - loop through, generating images as we need...
	#
	frames = int(float(page.duration) * page.fps) 

	print "duration, fps, frames:", page.duration, page.fps, frames
	if frames != prog_bar.max:
		print "------FRAME MISMATCH---------", frames, prog_bar.max
		prog_bar.max = frames
		#prog_bar.post()
		#sys.exit(0)
	
	
	# change the colors of the cursor and 
	# and the contrasting surround (mostly transparent)
	if page.use_soundgraphic:
		theme_colors = clColors.Themes(page.graphic_theme)
		linecolor=theme_colors.cursor
		offsetcolor=theme_colors.cursor_offset
	else:
		linecolor=clColors.BLACK
		offsetcolor=clColors.HILITE
	# set the width of the offset based on the scale adjustment
	offsetwidth = 1 + int(adjust_factor) 
	print "color, offset, width", linecolor, offsetcolor, offsetwidth
	
	overlay_master = Image.new( 'RGBA', size, color=clColors.XPARENT)
	master_draw = ImageDraw.Draw(overlay_master)
	add_res_text(master_draw, size, adjust_factor)
	
	frameIncr = float(xLen) / frames
	# for generated graphics, don't let the cursor go over the text
	if page.use_soundgraphic:
		cursor_top = int(config.SG_TOP_BORDER * adjust_factor)
		cursor_bot = height - int(config.SG_BOTTOM_BORDER * adjust_factor)
	else:	#cursor is top to bottom
		cursor_top = 0
		cursor_bot = height - (1 / adjust_factor)

	prog_bar.update(0)		# Reset the time to now...
	#while fr <= frames:
	last_fr_num = frames - 1
	for fr_num in range(frames):
		last_frame = fr_num == last_fr_num # Boolean
		# create a new overlay
		overlay = overlay_master.copy()
		overlay_draw = ImageDraw.Draw(overlay)

		#
		# at slower frame rates the final frame can be short of the mark,
		# make sure we're at the end if this is the final frame.
		if last_frame:
			xPos = xEnd
			time = page.duration		# force to the end...
		else:
			time = float(fr_num) / page.fps	# normal...

		# Put the cursor into the overlay
		xLine = int(xPos)
		# add to "rectangles" that are mostly transparent but help offset the cursor on similar colors
		overlay_draw.rectangle( [ (xLine-1,cursor_top), (xLine-offsetwidth,cursor_bot) ], outline=offsetcolor, fill=offsetcolor)
		overlay_draw.rectangle( [ (xLine+1,cursor_top), (xLine+offsetwidth,cursor_bot) ], outline=offsetcolor, fill=offsetcolor)
		overlay_draw.line( [ (xLine,cursor_top), (xLine,cursor_bot) ], fill=linecolor)

		#
		# Build the left and right boxes...
		lbox = box.copy()
		lbox_draw = ImageDraw.Draw(lbox)	# draw object...
		if fr_num == 0:	# add a highlight
			lbox_draw.rectangle(box_rect, outline=clColors.EL_BLUE)
			lbox_draw.rectangle(box_rect2, outline=clColors.EL_BLUE)
		
			
		seconds = int(time)
		tstring = "%01d:%02d" % divmod(seconds, 60)

		(twidth, theight) = lbox_draw.textsize(tstring, font=font)
		offset = ( (box_width - twidth) / 2, (box_height - theight) / 2)
		lbox_draw.text( offset, tstring, font=font, fill=clColors.GREEN)
		overlay.paste(lbox, lbox_offset)


		rbox = box.copy()
		rbox_draw = ImageDraw.Draw(rbox)
		if last_frame:		# Outline last frame time.
			rbox_draw.rectangle(box_rect, outline=clColors.EL_BLUE)
			rbox_draw.rectangle(box_rect2, outline=clColors.EL_BLUE)


		seconds = int(page.duration - time)
		tstring = "-%01d:%02d" % divmod(seconds, 60)

		(twidth, theight) = rbox_draw.textsize(tstring, font=font)
		offset = ( (box_width - twidth) / 2, (box_height - theight) / 2)
		rbox_draw.text( offset, tstring, font=font, fill=clColors.GREEN)
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
		#print "Saved:", directory + '/' + 'Frame-%05d.png' % fr_num

		xPos += frameIncr
		try:
			prog_bar.update(fr_num+1)
		except:
			pass
		
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
	
	We convert the string from what could be utf-8 (check this - other formats are possible)
	to the ascii equivalent since most TrueType fonts don't support them.
	"""
	print "Font file is:", fontfile
	font = ImageFont.truetype(fontfile, fontsize, encoding='unic')	# utf-8 is not working yet...
	string = string.encode('ascii', 'ignore')	# decode any utf-8 chars - not handled well in mo
	# create a temp image - just long enough to get the size of the text
	size = (10,10)
	box = Image.new('RGBA', size, color=clColors.XPARENT)
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
	box = Image.new('RGBA', size, color=clColors.XPARENT)
	box_draw = ImageDraw.Draw(box)

	(fw,fh) = box_draw.textsize(string, font=font)	# how big is it really?
	offset = ( (size[0] - fw) / 2, ( size[1] - fh) / 2 )
	box_draw.text(offset, string, font=font, fill=fill)

	box.save(output_file, 'PNG')
	return (font.font.family, font.font.style)

def add_res_text(draw, size, adjust_factor=1.0):
	"""
	Put a simple (elegant?) bit of text in the lower right
	of the graphic showing the resolution
	"""
	
	(width, height) = size
	
	fontclass = clutils.FontLib()	# this needs to be done at initialization   RBF
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/Dom Casual/DomCasDReg.ttf'
	#fontpath = os.path.join(page.coLab_home, 'Resources/Fonts/ArabBruD.ttf')
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/ArabBruD.ttf'
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/DigitalDream.ttf'
	#fontpath = fontclass.return_fontpath('DigitaldreamFatSkewNarrow.ttf')
	#fontpath = fontclass.return_fontpath('DigitaldreamFatSkew.ttf')
	fontpath = fontclass.return_fontpath('Berrington.otf')
	font_size = int(10 * adjust_factor)
	font = ImageFont.truetype(fontpath, font_size)
	res_string = str(width) + " x " + str(height)
	(t_width, t_height) = draw.textsize(res_string, font=font)
	print "Text size is :", t_width, t_height
	
	
	print "build sound file"
	lborder = config.SG_LEFT_BORDER
	rborder = config.SG_RIGHT_BORDER 
	tborder = int(config.SG_TOP_BORDER * adjust_factor)
	bborder = int(config.SG_BOTTOM_BORDER * adjust_factor)
	print "Border constants set."
	xmin = lborder
	xmax = width - rborder 
	ymin = bborder
	ymax = height - tborder
	box_width = int(config.T_BOX_WIDE * adjust_factor) 
	
	r_text_x = xmax - box_width - int(10 * adjust_factor) - t_width
	r_text_y = ymax + int(10 * adjust_factor)
	
	print "rx,ry, ", r_text_x, r_text_y
	
	# Draw with hi/lo lights so it should show up on many any background
	# (and look cool!)
	
	#for (offset, color) in [ (+1, clColors.BLACK), (-1, clColors.GRAY_TEXT), (0, clColors.PART_BLACK)]:
	for (offset, color) in [ (+1, clColors.PART_BLACK), (-1, clColors.GRAY_TEXT), (0, clColors.TRANS_GRAY)] :
		draw.text((r_text_x+offset, r_text_y+offset), res_string, font=font, fill=color)
	
	

def signed2int(s):
        """
        take an signed byte string
        and return a signed floating point.
        """
        value = 0
        l = len(s)
        for i in range(l): # keep it byte width flexible...
                value = (value << 8) + ord(s[i])

        max = 1 << (l * 8)
        offset = max >> 1
        if value < offset:
                value = value
        else:
                value = value - max

        #if value >= 65536:
        #        print "OOops - toobig:", value
        #        raise ValueError
        return(value)

class Sound_image():
	""" Take a sound file and convert into a base image

	Take an arbitary sound file (well - .aiff for now) and turn it into a base image for the page.

	Should handle:
	 - 1 or more channels, 8, 16, or 24 bit (whatever sample size the file has)
	 - arbitrary bit depth
	 - arbitrary sample rate (not quite yet)

	Generates a standard (or other) sized png file.
	"""
	def __init__(self, sound_file, image_file, media_size, prog_bar=None, theme='Default', max_samp_per_pixel=0):
		""" open the sound file and set the various internal vars. """
		print "Beginning Sound file open..."
		
		try:
			self.aud = aifc.open(sound_file)
		except:
			logging.warning("Sound file problems: %s", sound_file, exc_info=True)
			raise Exception
		
		self.sound_file = sound_file
		self.image_file = image_file
		self.media_size = media_size
		self.prog_bar = prog_bar
		"""
		max samp/pixel let's us process hour long audio quickly for preview. 
		Setting to some value (e.g., 100) approximates that many sample per
		vertical line (horizontal pixel) vs, the 60,000 or so in the hour recording.
		For preview, it can reduce the render time from 20 minutes to less than 5 seconds
		with reasonable accuracy, but should be set to 0 for final versions in order to
		get accurate clipping, rms and other values.
		"""
		self.max_samp_per_pixel = max_samp_per_pixel	# set to zero for no skipping.
		
		self.nchannels = self.aud.getnchannels()
		self.sampwidth = self.aud.getsampwidth()
		self.nframes = self.aud.getnframes()
		self.framerate = self.aud.getframerate()
		
		self.samp_max = 1 << (self.sampwidth * 8 - 1)	# -1 because we're signed.  range is -samp_max(-1?) - +samp_max; 3 => -8388607 - 8388608
		
		self.theme_colors = clColors.Themes(theme)
				
	# Adjust the amount of content in the top and bottom strings, based
	# on the size..	
	def upTickText(self, text, xcenter, y, font, fill=clColors.GREEN):
		""" create an string with an "up tick"
		
		centers the text and puts a corresponding height
		tick up from the current line.
		"""
		
		tick_height = 5 * self.adjust_factor
		
		(twidth, theight) = self.graphic_draw.textsize(text, font=font)
		self.graphic_draw.text((xcenter-(twidth/2), self.top), text, font=font, fill=clColors.GREEN)
		self.graphic_draw.line([(xcenter,y), (xcenter,y-tick_height)], fill=clColors.GREEN)


	def build(self):
		""" Build the image based on what we know...
		
		Using the size and borders, plus the attributes of the 
		audio file (# chan, sample size, length) we map a number
		of sample and sample levels to x and y coordinates, respectively.
		
		The first pass reads a clump of samples corresponding to the next
		vertical line in the graphic, detects the min and max of that group
		for each sample (and overall) and stores those in a set of arrays.
		Currently min_tab and max_tab - tables of min and max.  Each is a list
		of lists.  The number of lists is the number of channels in the audio.
		
		Once we've built the table, we can calculate the headroom and adjust the 
		values to full scale, so we do.
		
		Note: values internal to this are basically Cartesian: +y is up, but the actual
		file coordinates are reversed in the y-axis.   This is dealt with by negating
		the sample values as we assemble them, and dealing with Left/Right issues 
		when we build the graphic.
		
		"""
		# Set up min and max based on border size,
		# and various factors and values

		fontclass = clutils.FontLib()	# this needs to be done at initialization   RBF

		self.size_class = config.Sizes()	# new size class for size fun...
		size = self.size_class.sizeof(self.media_size)
		(width, height) = size
		
		adjust_factor = self.size_class.calc_adjust(height)
		print "adjust_factor:", adjust_factor
		
		print "build sound file"
		lborder = int(config.SG_LEFT_BORDER * adjust_factor)
		rborder = int(config.SG_RIGHT_BORDER * adjust_factor)
		tborder = int(config.SG_TOP_BORDER * adjust_factor)
		bborder = int(config.SG_BOTTOM_BORDER * adjust_factor)	
		print "Border constants set."
		xmin = lborder
		xmax = width - rborder 
		ymin = bborder
		ymax = height - tborder
		
		# how "tall" is each sample in the range of values - account for the number of channels
		levels_per_pixel = ( float(self.samp_max * 2) / (ymax - ymin + 1) ) * self.nchannels
		
		colors = self.theme_colors
		#graphic = Image.new('RGBA', (width, height), color=clColors.PART_BLACK)
		graphic = Image.new('RGBA', (width, height), color=colors.background)
		graphic_draw = ImageDraw.Draw(graphic)
		
		# Draw the limit lines...
		graphic_draw.line([(xmin,ymin), (xmax,ymin)], fill=clColors.GREEN)
		# A little tricky here - account for the time boxes:
		box_width = int(config.T_BOX_WIDE * adjust_factor)
		graphic_draw.line([(2+box_width,ymax), (width-box_width-2, ymax)], fill=clColors.GREEN )
		
		
		num_xpix = xmax - xmin		# number of available x pixels
	
		# seems a bit odd - but we post before setting the max...
		try:
			self.prog_bar.post()
			self.prog_bar.set_max(num_xpix)			# how many for the progress bar...
		except:
			pass
	
	
		aud_frames_per_pixel = float(self.nframes) / num_xpix
		
		print "Frames_per_pixel", aud_frames_per_pixel
		# variables for keeping track of the range..
		max = -self.samp_max
		min = self.samp_max
		#
		# A bit of shorthand for readablity....
		nchan = self.nchannels
		w = self.sampwidth
		
		"""
		Build the min_tab, max_tab, and rms_tab "arrays".   

		These tables are lists of lists - by channel, and then by vertical line.
		The number of lists for each is the number of channels in the audio.    Each of 
		those list entries is a list of num_xpix values, min or max for that channel.
		"""
		
		# tables are lists of min/max/etc pre channel, per line
		min_tab = []
		max_tab = []
		rms_tab = []	# actually the avg of squares, (sqrt later...)
		# values per channell
		chan_min = []
		chan_max = []
		run_count = []
		sum_sqrs = []
		
		#	c is channel
		
		for c in range(nchan):
			min_tab.append([])	# one list per channel
			max_tab.append([])
			rms_tab.append([])
			chan_min.append(self.samp_max)	#seed min/max with the other...
			chan_max.append(-self.samp_max)
			run_count.append(0)	# A running average for each
			sum_sqrs.append(0.0)
		
		
		# v is vertical line
 		print "reading frames...", self.nframes

		aud_frame_data = self.aud.readframes(self.nframes)
	
		print "Done reading.", len(aud_frame_data)
		p = 0	# pointer into the frame data
		# for previews, we can seet sample_skip to some value 
		# (e.g. 100) to 
		if self.max_samp_per_pixel == 0:
			aud_frame_skip = 1
		else:
			aud_frame_skip = int(aud_frames_per_pixel / self.max_samp_per_pixel) + 1
		
		clip_count = 0
		aud_frame_count = 0				# how many are we really reading?
		last_samp = 0					# where were we last?
		for v in range(num_xpix):		# Calculate min/max for each line in the graphic
			try:
				self.prog_bar.update(v)
			except:
				pass	# if there's no bar, there's no problem

			next_samp_num = int((v+1) * aud_frames_per_pixel)	# where are we reading to next?
			for c in range(nchan):
				min_tab[c].append(self.samp_max)	# seed with max value
				max_tab[c].append(-self.samp_max)	# seed with min...
				rms_tab[c].append(0.0)
				
			"""
			aud_frame_data is a string of characters:  the number 
			of samples x sample width(w) (bytes) x # channels
			We turn group of "w" sample bytes into a signed
			int and do the math...
			"""
			num_samps = next_samp_num - last_samp
			chunk_offset = last_samp * w * nchan		# where does the next chunk (vertical line) start
			#aud_frame_data = self.aud.readframes(num_samps)
				
			for i in range(0, num_samps, aud_frame_skip):		# for the samples we just read..
				aud_frame_count += 1
				offset = i * nchan * w + chunk_offset
				for c in range(nchan):
					p = offset +  c * w
					ep = p + w  	# end pointer
					value = signed2int( aud_frame_data[p:ep] )
					if value == self.samp_max -1 or value == -self.samp_max:
						clip_count += 1
						print "-------Found Clip:", value, aud_frame_count, c, v
					#p = ep
					#aud_frame_data = aud_frame_data[w:]		# strip what we just read off the front
					run_count[c] += value
					val_squared = value * value
					sum_sqrs[c] += val_squared	# squares

					rms_tab[c][v] += ( val_squared / num_samps ) * aud_frame_skip	# average of squares for this line 
					if value < min_tab[c][v]:
						min_tab[c][v] = value

						if value < chan_min[c]:
							chan_min[c] = value
							if value < min:
								min = value

					if value > max_tab[c][v]:
						max_tab[c][v] = value

						if value > chan_max[c]:
							chan_max[c] = value
							if value > max:
								max = value
								
			last_samp = next_samp_num 	# and so it goes, round and round...
		print "----Max, min:", max, min
		print " ----------Samp Max:", self.samp_max
		try:
			self.prog_bar.update(num_xpix)
		except:
			pass
			
		self.aud.close()
		"""
		At this point we have the min and max arrays, and an overall
		min and max.   Calculate the ratio of max to full scale, calculate
		in dBFS and emit the graphics, normalized.
		
		Might want this to be per channel - for now it's global
		We want the furthest excursion, min or max
		"""
	
		max_xcrsn = max		# maximum excursion
		if -min > max+1:	# '+1' prevents -0.0
			max_xcrsn = -min
			
		# Calculate what we now know...
		# headroom ratio and headroom in dBFS
		hr_ratio = float(max_xcrsn) / self.samp_max	# ratio of highest peak to max value - headroom as a ratio
		# create an "effective headroom" - do we do any correction or not?
		if hr_ratio < 0.9:
			eff_ratio = hr_ratio * 1.1	# make the end points just short of the limits
		else:
			eff_ratio = 1	# close enough - show the wave form as is
			
		headroom = 20 * math.log10(hr_ratio)
		
		
		chan_ht = ( ymax - ymin ) / nchan
		centers = []
		separators = []	# note  there n-1 - we skip 0 later
		for c in range(nchan):		# Build the center lines,  bottom up..
			# This is where we do the next bit of reversal - so that left or 1 is 
			# at the top, we build the list bottom up
			centers.append(ymin + c * chan_ht + chan_ht / 2)
			separators.append(ymin + c * chan_ht )
			# and add separaters
			if c != 0:	# we do n-1 separators
				y = separators[c]
				graphic_draw.line([(xmin,y), (xmax, y)], fill=clColors.HILITE)
		
		x = xmin
		for s in range(num_xpix):	
			# step through, scaling the samples as we go
			# and emitting the graphics 
			# the minus is to flip the value of the sample - the second bit of the
			# reversal
			for c in range(nchan):
				top = int(centers[c] - ( float(max_tab[c][s]) / levels_per_pixel ) / eff_ratio ) + 1
				bot = int(centers[c] - ( float(min_tab[c][s]) / levels_per_pixel ) / eff_ratio ) + 1
				rms = math.sqrt(rms_tab[c][s])	
				rms_offset = (rms / levels_per_pixel) / eff_ratio
				rms_center = (top + bot) / 2
				# or...
				rms_center = centers[c]
				
				t_rms = int(rms_center - rms_offset)
				b_rms = int(rms_center + rms_offset)
				# or...
				
				# temp - may make this an option at some point...
				rms_display = True
				
				if rms_display:
					# as three - rms "middle" is darker
					graphic_draw.line([(x,t_rms), (x,b_rms)], fill =  colors.rms)
					graphic_draw.line([(x,top), (x,t_rms)], fill = colors.wave)
					graphic_draw.line([(x,b_rms), (x,bot)], fill = colors.wave)
				else:
					# as one line...
					graphic_draw.line([(x,top), (x,bot)], fill = colors.wave)
					
				"""
				Draw the end points - mark any likely clip points
				(Note - we can only detect max values - they may or may
				not be a clip.   
				
				Future:  if there is only one "clip" per channel, we
				may want to assume it's a normalized clip and not get
				quite so excited.
				"""
				
				clip_stretch = 1 + int(adjust_factor*adjust_factor)
				#if eff_ratio == 1 and top == centers[c] - chan_ht / 2:
				if max_tab[c][s] == self.samp_max-1:
					fill = clColors.BRIGHT_RED
					tip_stretch = clip_stretch
					#print "=====Clip!", s, c, max_tab[c][s], min_tab[c][s], max, min
				else:
					fill = colors.peak
					tip_stretch	= 0
				#graphic_draw.point([(x,top)], fill = fill)
				graphic_draw.line([(x-tip_stretch,top), (x+tip_stretch,top)], fill = fill)
				
				tip_stretch	= 0
				#if eff_ratio == 1 and bot == centers[c] + chan_ht / 2 + 1:
				if min_tab[c][s] == -self.samp_max:
					fill = clColors.BRIGHT_RED
					tip_stretch = clip_stretch	# allows us to highliging...
					#print "-----Clip!", s, c, max_tab[c][s], min_tab[c][s], max, min
				else:
					fill = colors.peak
				
				#graphic_draw.point([(x,bot)], fill = fill)
				graphic_draw.line([(x-tip_stretch,bot), (x+tip_stretch,bot)], fill = fill)
			x += 1 		# Next vertical line
			
			
		#fontpath = os.path.join(page.coLab_home, 'Resources/Fonts/DigitaldreamFatSkewNarrow.ttf')
		#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/DigitaldreamFatSkewNarrow.ttf'
		#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/Dom Casual/DomCasDReg.ttf'
		#fontpath = os.path.join(page.coLab_home, 'Resources/Fonts/DomCasDReg.ttf')
		#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/DomCasDReg.ttf'
		# RBF: Convert this to not have a full path
		#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/DigitaldreamNarrow.ttf'
		#fontpath = fontclass.return_fontpath('DomCasDReg.ttf')
		fontpath = fontclass.return_fontpath('ComicSenseCond.otf')
		font_size = int( 18 * adjust_factor)
		font = ImageFont.truetype(fontpath, font_size)	
	
		# Build the text strings for the graphic
		#
		clist = self.chan_list()	# what do we call these things called channels?
		#------- Pretty much aren't doing this now --- rip out eventually.
		# First - the bits that are channel based
		comma = ''
		rms = 'rms(dB): '
		offset = 'Bias(%): '
		for c in range(nchan):
			rms_avg = math.sqrt( sum_sqrs[c] / (self.nframes / aud_frame_skip ) )
			rms_val = 20. * math.log10( rms_avg / self.samp_max  )
			
			rms += comma + clist[c] +': %0.1f' % rms_val
			#offset_val = 20 * math.log10( float(run_count[c]) / self.samp_max )
			offset_val = (( float(run_count[c]) / self.samp_max ) / self.nframes ) * 100.
			offset += comma + clist[c] +': %.2f' %  offset_val 
			comma = ', '
			# while we're at it, let's label the channels

			# Channel name:
			graphic_draw.text((xmin/2, centers[c]-10), clist[c], font=font, fill=clColors.GREEN)
		
		#------------------------
		# Top Text Line
		#------------------------
		self.top = 5		# yeah, I know - but it basically works everything else falls out of the equation

		size_class = config.Sizes()
		size = size_class.sizeof(self.media_size)
		(width, height) = size
	
		self.adjust_factor = size_class.calc_adjust(height)

		self.graphic_draw = graphic_draw		# UGLY!!!! Fix this    RBF
		self.xPos = int(config.SG_LEFT_BORDER * adjust_factor)
		self.xEnd = int(width - config.SG_RIGHT_BORDER * adjust_factor)
		self.upTickText('Start', self.xPos, ymin, font=font)
		#start_string = 'Start'
		#(twidth, theight) = graphic_draw.textsize(start_string, font=font)
		#graphic_draw.text((xPos-(twidth/2), top), start_string, font=font, fill=clColors.GREEN)
		#graphic_draw.line([(xPos,ymin), (xPos,ymin-tick_height)], fill=clColors.GREEN)
		
		self.upTickText('End', self.xEnd, ymin, font=font)
		
		# So now....
		# we need to figure out where to put the time markers
		# Base the number of markers on the scale, and then find 
		# the closest time increment to use.
		adjust_scale = size_class.calc_scale(height)
		num_time_incs = int(5 * adjust_scale)
		
		seconds = float(self.nframes) / self.framerate
		time_incr =  seconds / (num_time_incs + 1)
		logging.info("upTickTime incr...")
		time = time_incr
		while  time < seconds:
			#string = '%05.3f' % time
			string = str(time)
			time_factor = time / seconds

			x = (self.xEnd - self.xPos) * time_factor + self.xPos
			logging.info("time intr: %3f time factor time / seconds: %3f / %3f ", time_incr, time , seconds)
			self.upTickText(string, x, ymin, font=font)
			time += time_incr


		#------------------------
		# Bottom Text Line
		#------------------------
		left = box_width + 5
		(dir, filename) = os.path.split(self.sound_file)
		bot_string = '   File: '
		bot_string += filename 
		if self.size_class.is_larger_than(self.media_size, 'Tiny'):
			seconds = float(self.nframes) / self.framerate
			minutes = int(seconds / 60)
			secs = seconds - minutes * 60
			bot_string += ' / Length: %d:%06.3f' % (minutes, secs)
			bot_string += ' / Headroom: '
			if aud_frame_skip != 1 and headroom != 0:
				bot_string += '~'
			bot_string += ' %0.1fdB' % -headroom
			if self.size_class.is_larger_than(self.media_size, 'Medium'):
				bot_string += ' / %0.1fkHz' % (self.framerate / 1000.)
				bot_string += ' /  %dbits' % (self.sampwidth * 8)
			if self.size_class.is_larger_than(self.media_size, 'Large'):
				bot_string += ' Clipping: ' + str(clip_count)
		
		graphic_draw.text((left, ymax+3), bot_string, font=font, fill=clColors.GREEN)

		#if clip_count > 0 and self.size_class.is_larger_than(self.media_size, 'Large'):
		if clip_count:
			# add in a string about clipping
			# --- let's try to make this smarter about clips vs. likely normalization
			string = 'Clipping: ' + str(clip_count)
			(bwidth, bheight) = graphic_draw.textsize(bot_string, font=font)
			right = left + bwidth + 15
			print "Right text fun:", right, width, bwidth, 15
			graphic_draw.text((right, ymax+3), string, font=font, fill=clColors.BRIGHT_RED)
		
		#add_res_text(graphic_draw, size, adjust_factor)

	#"""
		
		graphic.save(self.image_file, 'PNG')
		
		print "Got min/max and actual max of:", min, max, max_xcrsn
		print "Computed headroom of:", hr_ratio, '/', headroom, 'dBFS'
		print "Expected vs. processed audioframes:", self.nframes, aud_frame_count
		print "Clip count:", clip_count
	

	def chan_list(self):
		"""
		Return a list of channel names: if mono, 'All', 
		if stereo, L and R, otherwise a list of channel numbers.
		"""
		if self.nchannels == 1:
			return( ['All'])
		elif self.nchannels == 2:
			return(['L', 'R'])
		else:
			return([ str(x+1) for x in range(self.nchannels) ])
		
import coLab		
def main():
	""" Some old, now obsolete tests are below - for now - just run the top level. """

	#------ interface to main routine...

	"""
	print "Colab Main"
	w=coLab.Colab()
	sys.exit(0)
	"""
	
	
	snd = '/Users/Johnny/coLab/Group/Johnny/Page/TestPage2/coLab_local/4-channel.aiff'
	snd = '/Users/Johnny/dev/CoLab/Group/Johnny/Page/Hello_AHH/coLab_local/Hello_AHH!.aif'
	#snd = '/Users/Johnny/dev/CoLab/Group/Johnny/Page/Boyars/coLab_local/Boyars.aif'
	pdir = 'Group/Johnny/Page/Boyars'
	pdir = 'Group/Johnny/Page/Hello_AHH'
	#pic = '/Users/Johnny/coLab/Group/Johnny/Page/AudioTest/coLab_local/TestSoundGraphic.png'
	#pic = '/Users/Johnny/dev/coLab/Group/Catharsis/Page/FullStormMIDI/coLab_local/soundgraphic.png'
	

	#"""
	# what the hell - make a bunch...
	s = config.Sizes()
	img_base = snd[:snd.rfind('/')+1]
	
	main = tk.Tk()
	f1 = tk.Frame(main)
	f1.grid()

	"""
	#for media_size in s.names:
	#for media_size in [ 'Small', 'Medium', 'Large', 'HiDef', '4k-Ultra-HD']:
	for media_size in [ 'Small']:
		print "Media size:", media_size
		
		pic = img_base + 'TestImage-' + media_size + ".png"
		print "Image file:", pic
		
		prog_bar = cltkutils.Progress_bar(f1, 'Image Generation', max=100)
		prog_bar.what = 'Image'
		prog_bar.width = 500
		prog_bar.max = s.sizeof(media_size)[0]
		prog_bar.post()		# initial layout...
		Sound_image(snd, pic, media_size, prog_bar, max_samp_per_pixel=0).build()
	#"""
	# now create and load a page so we can have some images....

	page = clclasses.Page()
	page.load(pdir)
	
	
	media_size = 'Large'
	#media_size = '4k-Ultra-HD'
	#media_size = 'HiDef'
	#media_size = 'Small'
	
	prog_bar = cltkutils.Progress_bar(f1, 'Image Generation', max=100)
	prog_bar.what = 'Image'
	prog_bar.width = 500
	prog_bar.max = s.sizeof(media_size)[0]
	prog_bar.post()		# initial layout...
	
	page.media_size = media_size
	pic = img_base + "SoundGraphic.png"
	Sound_image(snd, pic, media_size, prog_bar, page.graphic_theme).build()

	page.use_soundgraphic = True
	
	try:
		page.screenshot_width
	except:
		page.screenshot_width = 0
	if page.screenshot_width == 0:
		page.screenshot_width = prog_bar.max
		
	make_images(page, prog_bar)
	
	sys.exit(0)
	
	p = clclasses.Page('imagemakerTest')
	p.xStart = 10
	p.xEnd = 470

	p.duration = .01	# start small (seconds) but get big fast...

	print "xStart, xEnd:", p.xStart, p.xEnd
	while p.duration < 100000:
		fps = calculate_fps(p)
		print "For duration:", p.duration, "- fps:", fps
		p.duration += p.duration * 0.3	# funny boy


if __name__ == '__main__':
	#coLab.main()
	main()
