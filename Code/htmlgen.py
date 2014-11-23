#!/usr/bin/env python
""" Create a Web dir based on the name passed.

Passed a simple name, creates a file <name>.html
and populates it with the necessary content to 
display the web page.

Creates a header, includes the apple specific head content,
body content including the media block and any comments.

"""

import os
import sys
import logging
import imp	# to input the data file
import shutil
import subprocess

import clutils
import cldate
import clclasses
import clColors
import locTagger

from headers import *
import imagemaker

fill = clColors.TAN

# 
# put these somewhere....
num_recent_entries = 5
num_project_entries = 10


def check_comments(obj):
	""" Make sure there's a comments file, if not, seed it. 

	Also touch the links.html to prevent include errors

	Obj can be a page or group - must have a .name 
	"""
	# if we don't yet have a comments file, seed it with enough helpful info (song, date)
	#
	file = 'Comments.log'
	if not os.path.isfile(file):
		try:
			f=open(file,'w+')
			f.write('<!-- Comments for ' + obj.name +
				' created on ' + cldate.now() + '-->\n' )
			f.close()
		except:
			logging.warning("Error creating", file, exc_info=True)
	else:
		logging.info("Comments exist")
	file = 'links.html'
	if not os.path.isfile(file):
		try:
			f = open(file, 'w+')	# just create a blank file for now
			f.close()
		except:
			logging.info("Error creating: %s", file)

def tagstrip(string,subs='\n',tag=''):
	""" Remove html tags 
	
	- and arbitrarily replace them with a
	new line (default).  tag var allows for specific tags
	to be removed.  e.g. 'a'

	Recursive - each call pulls out the next tag...
	"""

	i = string.find('<'+tag)	# is there a start tag?
	if i == -1:
		return(string)	# we're done
	closetag = string[i:].find('>') 
	if closetag == -1:		# not closing tag, return up to the start
		return(string[:i])
	next = closetag + i + 1	# set up for the recursive calll
	return ( string[:i] + subs + tagstrip(string[next:], subs) ) 
	
def smartsub(string,length):
	""" Return a substring that is based on the passed length,

	but modified up to 10% to find either a space, or period.

	Used to take arbitrary text and make a synopsis of the 
	approx. length
	"""

	slen = len(string)
	if slen <= length:
		return(string)

	limit = int(length * .7)
	#
	# Now, working backwards, find a '.'
	spot = string[length:limit:-1].find('.')
	if spot != -1:
		return(string[:length-spot+1] + ' (more...)')
	
	# No period, fine a space
	spot = string[length:limit:-1].find(' ')
	if spot != -1:
		return(string[:length-spot] + "...")
	else:
		return(string + "...")


def mk_dur_string(dur):
	"""  convert duration into a time string """
	try:
		dur = float(dur)
	except:
		logging.warning("Unexpected dur string: %s", exc_info=True)
		dur = 0.
	mins = int(dur / 60)
	seconds = dur - (mins * 60)
	secs = int(seconds)
	frac = int((seconds % 1) * 100)

	timestr = "%d:%02d.%02d" % (mins, secs, frac)

	return(timestr)

def pagegen(group, page):
	""" Passed the name of the group and page, rebuilds the index.shtml """
	fonts = clutils.FontLib()	# this needs to be done at initialization   RBF

	try:
		os.chdir(page.home)
	except OSError,info:
		logging.error("Fatal Error: Cannot cd to ", page.home, exc_info=True)
		sys.exit(1)

	# make the title graphic...
	#  RBF   This needs a rewrite....      
	#fontpath = fonts.fontpath('DejaVuSans-BoldOblique')
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/VanDijAntD.ttf'
	fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
	logging.info("fontpath: %s", fontpath)
	if clutils.needs_update('.', file='Title.png'):
		imagemaker.make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=8, fill=fill, maxsize=(640,70) )
		logging.info("Updating Title.png")
	else:
		logging.info("Not updating Title.png")

	fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
	if clutils.needs_update('.', file='Header.png'):
		imagemaker.make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill)#, maxsize=(400,90) )
		logging.info("Updated Header.png")
	else:
		logging.info("Not updating Header.png")

	now = cldate.now()

	index='index.shtml'
	# for now - shuffle the current one to a temp location...
	if os.path.exists(index):
		try:
			os.remove(index)
		except OSError, info:
			logging.error("Fatal Error removing", index, exc_info=True)
			sys.exit(1)


	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except IOError, info:
		logging.error("Fatal Error: Failure opening ", index, exc_info=True)
		exit(1)

	html = Html()	# create an html object that contains the html strings...
	# 
	# output the pieces of the page...
	#
	outfile.write(html.emit_head(page, media=True))

	outfile.write(html.emit_body(group, page, media=True))

	# The part specific to this page...

	
	content = """
	<p>
	<! Start links...>
	<!--#include virtual="links.html" -->
	<! ...end links.>
	<div class="maintext">
	<br>
	<!-- gittin' a little tricky w/alignment... -->
	<table border=0 cellpadding=0 width=100%><tr>
	<td valign=top><img src="Header.png" align=left alt="page.desc_title"><br clear=all>
	<i>Created: """ + cldate.utc2long(page.createtime) + """</i></td>
	<td valign=center align=right><b>Duration: """ + mk_dur_string(page.duration) + """</b></td></tr></table>
	<p><font color=a0b0c0>"""  + locTagger.loctagger(page.description) + '<p>'

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()

def linkgen(group):
	""" set up prev / next links for the left side bar

	for the first and last links - cheat a bit - add a fake
	page to the end of the list named "Archive" 
	"""
	p = clclasses.Page('null')
	p.name = "Archive"
	p.root = os.path.join(group.root, 'Shared', 'Archive')
	p.home = os.path.join(group.home, 'Shared', 'Archive')
	p.Title = 'Archive'
	p.desc_title = "Archive"
	p.fun_title = "Archive - a place for everything"
	group.pagelist.append(p)

	# "dummy" current entry for the home...
	currName = "Home"
	currTitle = "Home"
	currFun = group.name + " Home"
	currPath = group.home
	currLink = group.root

	prevName = "not set yet"
	# step through the pages in order
	# Because we don't can't build the links until we've read
	# the next one, we loop through twice before we actually 
	# write the first file.  We write the link file for the
	# page in the previous iteration  (currLink, etc.)
	# The "current" page is 'q'
	for p in group.pagelist:

		if currName != 'Home':  # for "Home" the key is to execute the code at the bottom to load the pipeline
			#
			# Are these the links we saw last time?
			logging.info("Links for: %s, correct: prev: %s, name: %s, stored: prv%s, nxt%s ", q.name, prevName, p.name, q.prevlink, q.nextlink)
			#"""
			if prevName == q.prevlink and p.name == q.nextlink:
				logging.info("No link change for: %s",  q.name)
			else:
			#"""
			#if True:
				linkfile = os.path.join(currPath, 'links.html')
				logging.info("Creating linkfile: %s", linkfile)
				try:
					l = open(linkfile, 'w+')
				except IOError, info:
					logging.warning("problem opening", linkfile, exc_info=True)
					raise IOError

				# a little kludgy - should consider full path URLs from
				# the data structures

				l.write( '<div class="links" style="float: left;">' + 
					'<a href="' + prevLink + '" title="' + prevFun +
						'">&larr; ' + prevTitle + '</a></div>' +
					'<div class="links" style="float: right;">' +
					'<a href="' + p.root + '" title="' + p.fun_title +
						'">' + p.desc_title + ' &rarr;</a></div>' +
					'<br>' )
				l.close()
				# 
				# Update the pointers
				if q.name != 'Archive':
					logging.info("Updating links in: %s", p.name)
					q.prevlink = prevName
					q.nextlink = p.name
					q.post()
			

		prevName = currName
		prevTitle = currTitle
		prevFun = currFun
		prevPath = currPath
		prevLink = currLink

		currName = p.name
		currTitle = p.desc_title
		currFun = p.fun_title
		currPath = p.home
		currLink = p.root
		q = p		# save the page

	group.pagelist.pop()	# remove that fake "Archive" page

def mk_page_synopsis(page, type='Default'):
	""" Create a short synopsis with the thumbnail, description, etc.

	Type can be used to alter the format a bit
	"""
	if page.thumbnail != '':
		shot=page.thumbnail
	else:
		shot=page.screenshot
		logging.info("no thumbnail")

	screenshot = os.path.join(page.root, shot)
	header = os.path.join(page.root, 'Header.png')
	timestr = mk_dur_string(page.duration)

	# cut to length....
	desc_text = tagstrip(smartsub(page.description, 350), tag='a', subs='')
	#
	# We need to link to a page...   derive the url from the page entry
	group_root = os.path.dirname(os.path.dirname(page.root))	# strip the 'Page/<pagename>' off the dir
	song_root = os.path.join(group_root, 'Song', page.song, '#' + page.part )	# song path, plus a part name

	# Build up the html content for this entry....  
	this_entry = '<table border=0 cellpadding=5 width=640>'		#  RBF: hard-coded width....
	this_entry += '<tr><td colspan=2>'
	this_entry += '<table border=0 cellpadding=5 width=100%><tr>'	# build another table inside these two cells..
	this_entry += '<td><a href="' + page.root + '" class="imglink"><img src="' + header + '"><br>'
	if page.createtime == page.updatetime or type == 'Archive':
		this_entry += 'Created: ' + cldate.utc2short(page.createtime)
	else:
		this_entry += 'Updated: ' + cldate.utc2short(page.updatetime)

	this_entry += '</a></td>'
	if type == 'Archive':
		this_entry += '<td align=center><a href="' + song_root + '">' +  page.song + '/' + page.part + '</a></td>\n'

	this_entry += '<td align=right>Duration: ' + timestr + '</td></tr></table>\n'	# end the header table
	this_entry += '</td></tr>\n'					# next row... (thumb, desc)
	this_entry += '<tr><td><a href="' + page.root + '" class="imglink"><img src="' + screenshot + '" width=160 height=140></a></td><td>'
	this_entry += '<span class="song">\n'
	this_entry += '<a href="' + page.root + '">\n'
	this_entry += desc_text 
	this_entry += '</a>\n'
	this_entry += '</span>\n'
	this_entry += '</td></tr></table>\n'


	return(this_entry)

def songgen(group, song=None):
	""" rebuild a song page, or list of pages
	
	Using the passed song, or the song list in the passed group, rebuild those pages
	"""
	if song is None:
		songlist = group.songlist
	else:
		songlist = [ song ]
		
	# html horizontal rules...
	hr_half = '<hr width=50%>'
	hr_full = '<p><hr><p>'
	
	for song in songlist:
		logging.info("Writing song page: song: %s, group: %s", song.name, group.name)
		
		song_dir = os.path.join(group.home, 'Song', song.name)	

		try:
			os.chdir(song_dir)
		except OSError,info:
			logging.warning("Cannot cd to: %s ", song_dir, exc_info=True)
			continue
	
	
		index='index.shtml'
	
		# make the title graphics...
		fonts = clutils.FontLib()	# maybe put this in the group?
		fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
		#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/PaletD.ttf'
		if clutils.needs_update('.', file='Title.png'):
			imagemaker.make_text_graphic(song.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
		if clutils.needs_update('.', file='Header.png'):
			imagemaker.make_text_graphic(song.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )
	
		if not clutils.needs_update('.', file='index.shtml'):
			logging.info("Song %s oes not need update.", song.name)
			continue

		logging.info("------Updating: %s/%s", song_dir, index)

		# open the index file, dump the header, body, etc. into it...
		try:
			outfile = open(index, 'w+')
		except:
			logging.error("Failure opening ", index, exc_info=True)
			exit(1)

		logging.info("Updating: %s index.html", song.name)
		html = Html()	# create an html object that contains the html strings...
		# 
		# output the pieces of the page...
		#
		outfile.write(html.emit_head(song, media=False))
	
		outfile.write(html.emit_body(group, song, media=False))
	
		# The part specific to this page...
		content = """
			</center>
	
		<div class="maintext">
		<img src="Title.png"><br>
		""" + song.description + """
		<p>
		<i>""" + cldate.now() + """</i><br clear=all><p>"""
		
		multiparts = len(song.partlist) > 1	# do we have more than one part?
		if multiparts:	# just "All", skip this...
			content += "Part index:<ul>"
			for part in song.partlist:
				name = song.partname_dict[part]
				content += '<li><a href="#' + part + '">' + name + '</a>\n'
			content += '</ul><br><hr>\n'

		fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
		#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/ArabBruD.ttf'
		for part in song.partlist:
			# make the title graphics...
			# For now - just the part name - more when we datafy it....
			partPng = 'Part' + part + '.png'
			if clutils.needs_update('.', file=partPng):
				partname = song.partname_dict[part]
				imagemaker.make_text_graphic(partname, partPng, fontpath, fontsize=45, border=5, fill=fill )

			content += '<a name="' + part + '">\n'
			if multiparts:	# only include parts if there are 2 or more... (otherwise we get a separate "All")
				content += '<img src="' + partPng + '"></br>'
			#
			# The heart of it - create entries for each matching page
			try:
				num_pages = len(song.part_dict[part])
			except KeyError:
				num_pages = 0

			logging.info("for part %s, num is: %d", part, num_pages)

			if num_pages == 0:
				content += "(none)<p>"
				continue

			song.part_dict[part].sort(key=clclasses.updatekey, reverse=True)
			hr = ''	# cute trick to only put an <hr> tag "between" entries
			for pg in song.part_dict[part]:	#step though the pages


				if pg.thumbnail != '':
					shot=pg.thumbnail
				else:
					shot=pg.screenshot

				screenshot = os.path.join(pg.root, shot)
				timestr = mk_dur_string(pg.duration)

				# cut to length.... remove any tags
				desc_text = (smartsub(tagstrip(pg.description, '-'), 250))

				# Build up the html content for this entry....	
				content += hr	# set below - only shows up on 2+ entries...
				content += mk_page_synopsis(pg, type='Song')
				hr = hr_half
		

			content += hr_full
				
		if not content.endswith(hr_full):	# if a part has no songs, there won't be a horizontal rule
			content += hr_full				# add one...
		content += 'Song <u><i>' + song.desc_title + '</i></u>, created: ' + cldate.utc2long(song.createtime) + '<p>'

		outfile.write(content)
	
		outfile.write(html.emit_tail(song))
	
		outfile.close()
	
		check_comments(song)
		
	return()
	
def homegen(group):
	""" Generates the top group level home page... """
	try:
		os.chdir(group.home)
	except:
		logging.warning( "Cannot cd to: %s", group.home, exc_info=True)
		return()


	index='index.shtml'

	page = clclasses.Page('null')	# create a page structure - to pass in a title
	page.desc_title = group.title
	page.fun_title = group.subtitle
	page.name = group.name

	# make the title graphics...
	fonts = clutils.FontLib()	# maybe put this in the group?
	fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/ArabBruD.ttf'
	imagemaker.make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
	imagemaker.make_text_graphic(page.fun_title, 'Title_dk.png', fontpath, fontsize=45, border=10, fill=clColors.COLAB_BLUE )
	imagemaker.make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=45, border=2, fill=fill )
	imagemaker.make_text_graphic(page.desc_title, 'Header_dk.png', fontpath, fontsize=45, border=2, fill=clColors.COLAB_BLUE )
	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except:
		logging.error("Fatal Error: Failure opening ", index, exc_info=True)
		exit(1)

	html = Html()	# create an html object that contains the html strings...
	# 
	# output the pieces of the page...
	outfile.write(html.emit_head(page, media=False))

	outfile.write(html.emit_body(group, page, media=False))

	# The part specific to this page...

	content = """
		</center>

	<div class="maintext">
	<img src="Header.png"><br>
	<a href="Shared/SnapShot.png"><img src="Shared/SnapShot_tn.png" width=320 height=240 align=right></a>
	<font color=a0b0c0>""" + group.description + """<p>
	<i>""" + cldate.now() + """</i><br clear=all><p>"""

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()


def newgen(group):
	""" Generate a simple "what's new" page """

	shared = os.path.join(group.home, 'Shared', 'WhatsNew')

	try:
		os.chdir(shared)
	except:
		logging.warning("Cannot cd to: %s ", shared, exc_info=True)
		return()


	index='index.shtml'
	if not clutils.needs_update('.', file=index):
		logging.info("Skipping newgen...")
		return

	page = clclasses.Page('null')	# create a page structure - to pass in a title
	page.desc_title = "What's New"
	page.fun_title = "What's new in " + group.title + " Land"
	page.name = "WhatIsNew"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except:
		logging.error("Fatal Error: Failure opening ", index, exc_info=True)
		exit(1)

	# make the title graphics...
	fonts = clutils.FontLib()	# maybe put this in the group?
	fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/ArabBruD.ttf'
	imagemaker.make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
	imagemaker.make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )


	html = Html()	# create an html object that contains the html strings...
	# 
	# output the pieces of the page...
	#
	outfile.write(html.emit_head(page, media=False))

	outfile.write(html.emit_body(group, page, media=False))

	# The part specific to this page...

	content = """
		</center>

	<div class="maintext">
	<img src="Title.png"><br>
	<font color=a0b0c0>
	For now, just a running comment log of what's new...
	<p><i>""" + cldate.now() + """</i><p>"""

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()


def navgen(group):
	""" Generate a simple "navigation" """
	nav = os.path.join(group.home, 'Shared', 'Nav')

	try:
		os.chdir(nav)
	except:
		logging.warning("Cannot cd to: %s", nav, exc_info=True)
		return()


	index='index.shtml'
	if not clutils.needs_update('.', file=index):
		logging.info("Skipping nevgen...")
		return

	page = clclasses.Page('null')	# create a page structure - to pass in a title
	page.desc_title = "Navigation"
	page.fun_title = "Navigation: " + group.title 
	page.name = "Navigation"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except:
		logging.error("Fatal Error: Failure opening ", index, exc_info=True)
		exit(1)

	# make the title graphics...
	fonts = clutils.FontLib()	# maybe put this in the group?
	fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/ArabBruD.ttf'
	imagemaker.make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
	imagemaker.make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )


	html = Html()	# create an html object that contains the html strings...
	# 
	# output the pieces of the page...
	#
	outfile.write(html.emit_head(page, media=False))

	outfile.write(html.emit_body(group, page, media=False))

	# The part specific to this page...

	content = """
		</center>

	<div class="maintext">
	<img src="Title.png"><br>
	<font color=a0b0c0>
	A few Catharsis related links you might find interesting:  (these open in a new tab/window)
	<ul>
		<li><a href="http://jawknee.com/iWeb/Catharsis_Log/Clog/Clog.html" target=_blank>The Clog</a><br>
			the one that started us down this web collaboration path... our private area
		<li><a href="http://jawknee.com/iWeb/Catharsis/Music/Music.html" target=_blank>The Catharsis Cast</a><br>
			stuff we were willing to share including photos and The Basement.
		<li><a href="http://jawknee.com/iWeb/Catharsis_Friends/Music_for_Friends/Music_for_Friends.html" target=_blank>Catharsis Friends</a><br>	
			music we sort of shared...   added to the complexity that helped spawn coLab.
		<li><a href="http://jawknee.com/coLab/Group/Johnny/" target=_blank>Johnny's coLab Page</a><br>
			What it says...
			
		<li><a href="http://jawknee.com/iWeb/Johnnys_Sandbox/Welcome_to_the_Sandbox.html" target=_blank>Johnny's Sandbox</a><br>
			Johnny's iWeb based sharing...
	</ul>		
		
	And in the category of just because I can, here are the fonts currently available in coLab:<p>
	 <a href="http://jawknee.com/coLab/Resources/FontIndex/">Font List</a>
	<p><i>""" + cldate.now() + """</i><p>"""

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()



def archivegen(group):
	""" Generate an archive of the various pages... """ 
	archive = os.path.join(group.home, 'Shared', 'Archive')

	try:
		os.chdir(archive)
	except:
		logging.warning("Cannot cd to: %s", archive, exc_info=True)
		return()


	index='index.shtml'

	page = clclasses.Page('null')	# create a page structure - to pass in a title
	page.desc_title = group.title + " Archive"
	page.fun_title = group.title + " Archive"
	page.name = "Archive"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except:
		logging.error("Fatal Error: Failure opening ", index, exc_info=True)
		exit(1)



	html = Html()	# create an html object that contains the html strings...
	# 
	# output the pieces of the page...
	#
	outfile.write(html.emit_head(page, media=False))

	outfile.write(html.emit_body(group, page, media=False))

	# The part specific to this page...
	
	# make the title graphics...
	fonts = clutils.FontLib()	# maybe put this in the group?
	fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/ArabBruD.ttf'
	imagemaker.make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
	imagemaker.make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )

	content = """
		</center></center>

	<div class="maintext">
	<img src="Title.png"><br>
	<font color=a0b0c0>
	Here are the collected pages, listed chronologically by creation time,
	most recent first.  Unless otherwise stated, all times are US/Pacific.
	<p><i>""" + cldate.now() + """</i><p><hr><p>
	<center>
	"""
	outfile.write(content)


	group.pagelist.sort(key=clclasses.createkey)
	group.pagelist.reverse()
	hr = ''		# no horizontal rule on the first pass...
	for pg in group.pagelist:
		logging.info("archive: %s", pg.name)

		outfile.write(hr + mk_page_synopsis(pg, type='Archive'))
		hr = '<hr>'

	outfile.write('</center>\n')

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()



def helpgen(group):
	""" Generate a simple help page place holder (for now) """

	help = os.path.join(group.home, 'Shared', 'Help')

	try:
		os.chdir(help)
	except:
		logging.warning("Cannot cd to: %s ", help, exc_info=True)
		return()

	index='index.shtml'
	if not clutils.needs_update('.', file=index):
		logging.info("Skipping helpgen...")
		return

	page = clclasses.Page('null')	# create a page structure - to pass in a title
	page.desc_title = "Help"
	page.fun_title = "Help"
	page.name = "Help"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except:
		logging.error("Fatal Error: Failure opening ", index, exc_info=True)
		exit(1)

	# make the title graphics...
	fonts = clutils.FontLib()	# maybe put this in the group?
	fontpath = fonts.return_fontpath('ProximaFontauriItalic.otf')
	#fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/ArabBruD.ttf'
	imagemaker.make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
	imagemaker.make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )


	html = Html()	# create an html object that contains the html strings...
	# 
	# output the pieces of the page...
	#
	outfile.write(html.emit_head(page, media=False))

	outfile.write(html.emit_body(group, page, media=False))

	# The part specific to this page...

	content = """
		</center>

	<div class="maintext">
	<img src="Title.png"><br>
	<font color=a0b0c0>
	Hopefully the interface is reasonbly intuitive.  If something
	doesn't make sense, you have a question or a comment, feel
	free to enter something below.
	<p>
	<h4>Issues with Internet Explorer?</h4>
	As far as I know - I've resolved the problem with newer
	versions of IE - it was a configuration issue with my ISP.
	<p>
	If you have a problem playing the media files on <i>any platform</i>,
	<a href="mailto:coLab_dude@jawknee.com?subject=coLab Playback Issues">I'm interested in hearing about it.</a>
	
	<p>
	<h4>Some highlights:</h4>
	<ul>
		<li><b>Recent Updates</b><br>
		The top of the left side bar shows the 
		most recent activity.  The most recent
		is at the bottom of the list.  
		Pages marked 
		<span style="color: #ff2020; size: smaller;">New!</span>
		are "new" (currently less than two weeks old) and
		have not been commented on.  Those marked 
		<span style="color: #14ff14; size: smaller;">(u)</span>
		have been recently commented on (updated).
		<li><b>Current Projects</b><br>
		Below that are the current projects - presently 
		these are songs - project support is planned.
		You can link directly to a song, or part of one
		by clicking there.
		<li><b>Links</b><br>
		Each content page is linked in a chain to all the other
		pages.   These are currently chronological by creation
		date.
		<li><b>Archive</b><br>
		Beyond that - the most useful item is probably the 
		Archive link in the top nav bar. The Archive page will show 
		every page, in chronological order, most recent first.
	</ul>
	<p>
	Hope that helps.
	<p><hr>
	<p><i>""" + cldate.now() + """</i><p>"""

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()

				
if __name__ == "__main__":

	if len(sys.argv) < 2:
		logging.error("Fatal Error: Usage: %s page name", sys.argv[0])
		exit(1)

	name=sys.argv[1]



