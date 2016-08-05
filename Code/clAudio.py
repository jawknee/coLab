#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Audio utilities...

	Simple utilities:
	get_audio_len -- return the length in seconds of an audio file.
	make_movie -- create the html5 video files for the passed page
"""

import os
import logging
import subprocess
import fcntl
import select
import time
import aifc
import io

import config
import clclasses
import cldate

def get_audio_len(file):
	""" In this return the length of the file in seconds. """
	a = aifc.open(file)
	seconds = a.getnframes() / float(a.getframerate())
	a.close
	return(seconds)

def make_movie(page, prog_bar=None):
	""" Passed a Page, create the corresponding movie
	
	At the heart of it - passed a page, it builds a movie.
	This script basically writes a data file that is passed
	to the shell script that does the work.
	
	Most of the code is just to read the output of ffmpeg for
	updating of the progress bar.
	"""
	infofile = os.path.join(page.home, 'coLab_local', 'movie.info')
	outfile = io.open(infofile, 'w+', encoding='utf-8')
	#
	# Just some variable assignments used by the script.
	content = 'pagedir="' + page.home + '"\n' 
	content += 'imagedir="' + os.path.join(page.coLab_home, 'coLab_local', 'Frames', page.name) + '"\n'
	content += 'soundfile="' + page.localize_soundfile() + '"\n' 
	content += 'fps="' + str(page.fps) + '"\n'
	content += 'media_size="' + page.media_size + '"\n'
	if page.media_size != config.BASE_SIZE:
		content += 'generateMP3="no"\n'
	else:
		content += 'generateMP3="yes"\n'
		# ---  mp3 ID3 tags...
		# create a series of variables that match to ffpmeg -metadata tags for mp3	
		# variable names match the ffmpeg metadata tags, e.g., -metadata title="$title"
		# or the raw tag when not supported directly by ffmpeg, e.g., -metadata TIT3="$TIT3" 
		content += 'title="' + page.desc_title + '"\n'
	#
	# Get the group "title" ...
	try:
		page.group_obj
	except:
		page.group_obj = clclasses.Group(page.group)	# load the group whose name we have
		page.group_obj.load()
		
	grouptitle = page.group_obj.title 

	content += 'artist="' + grouptitle + '"\n'
	content += 'TIT3="' + page.fun_title + '"\n'

	year = cldate.format(page.createtime, '%Y')
	content += 'date="' + year + '"\n'
	content += 'TDAT="' + cldate.format(page.createtime, '%d%m') + '"\n'
	content += 'encoded_by="coLab"\n'
	rec_copyright = u'\u2117'	# recording copyright sign...
	#rec_copyright = "(P)"	# can't get the unicode to work yet...
	content += 'copyright="' + rec_copyright + ' ' + grouptitle + ' ' + year + '"\n'
	content += 'encoder="ffmpeg / LAME"\n'
	
	logging.warning("movie.info content: %s", content)
	outfile.write(content)
	outfile.close()
	
	media_script = os.path.join(page.coLab_home, 'Code', 'ffmpeg.sh')
	
	logging.info("running: %s with: %s", media_script, infofile)
	try:
		bufsize = 1	 # line buffered
		ffmpeg = subprocess.Popen([media_script, infofile], bufsize, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
	except:
		logging.warning("Video generation failed.", exc_info=True)
		sys.exit(1)
	"""
	# buffering info from Derrick Petzold: https://derrickpetzold.com/p/capturing-output-from-ffmpeg-python/
	fcntl.fcntl(
		ffmpeg.stdout.fileno(),
		fcntl.F_SETFL,
		fcntl.fcntl(ffmpeg.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
	)
	#   does not appear to be needed - the iter on the subprocess stdout works fine...
	#   though ffmpeg generates'\r' rather than '\n' so for any of this to work
	#   the output needs to be passed through: tr -u '\r' '\n'
	#"""
	prog_bar.update(0)	  # reset the start time...
	#
	# Read lines from the newly started ffmpeg... 
	# parse them and update the progress bar...
	read_delay=0.1	  # a bit of a delay so we don't slow down the encoding... (not clear if this is helping)
	frame_num = 0
	for line in iter(ffmpeg.stdout.readline, 'b'):
		logging.info(" Read a new ffmpeg line: %s", line)
		
		ffmpeg.poll()   # check the status....
		if ffmpeg.returncode is not None:
			logging.info("ffmpeg is done: %s", ffmpeg.returncode)
			break

		parms = line.split()
		try:
			if parms[0] == 'frame=':
				frame_num = parms[1]
				prog_bar.update(int(frame_num))
				logging.info(" Frame: %s", frame_num)
				time.sleep(read_delay)
		except:
			logging.warning("Something went wrong on the update... %s - possible last frame.", frame_num)
			pass
			#break
	logging.info("ffmpeg has completed.")