#!/usr/bin/env python
"""
	Create a Web dir based on the name passed.

	Passed a simple name, creates a file <name>.html
	and populates it with the necessary content to 
	display the web page.

	Creates a header, includes the apple specific head content,
	body content including the media block and any comments.

"""

import os
import sys
import imp	# to input the data file
import shutil

import clutils
import cldate

from clclasses  import *
from headers import *
from imagemaker import make_text_graphic

tan = (196, 176, 160, 255)
fill = tan

def check_comments(obj):
	"""
	Make sure there's a comments file, if not, seed it.
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
			print "Error creating", file
	else:
		print "Comments exist"
	file = 'links.html'
	if not os.path.isfile(file):
		try:
			f = open(file, 'w+')	# just create a blank file for now
			f.close()
		except:
			print "Error creating", file

def tagstrip(string,subs='\n',tag=''):
	"""
	Remove html tags - and arbitrarily replace them with a
	new line (default).  Suffix allows for specific tags
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
	"""
	Return a substring that is based on the passed length,
	but modified up to 10% to find either a space, or period.
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
	if dur != "":
		mins = int(dur / 60)
		seconds = dur - (mins * 60)
		secs = int(seconds)
		frac = int((seconds % 1) * 100)

		timestr = "%d:%02d.%02d" % (mins, secs, frac)
	else:
		timestr = "(?)"

	return(timestr)

def pagegen(group, page):
	"""
		Passed the name of the group and page, rebuilds
		the index.shtml 
	"""

	try:
		os.chdir(page.home)
	except OSError,info:
		print "Cannot cd to ", page.home
		print "fatal."
		sys.exit(1)

	# make the title graphic...
	fonts = clutils.fontlib()	# maybe put this in the group?
	fontpath = fonts.fontpath('AenigmaScrawl')
	if clutils.needs_update('.', file='Title.png'):
		make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=8, fill=fill, maxsize=(640,90) )
	else:
		print "Not updating Title.png"
	if clutils.needs_update('.', file='Header.png'):
		make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill)#, maxsize=(400,90) )
	else:
		print "Not updating Header.png"

	now = cldate.now()

	index='index.shtml'
	# for now - shuffle the current one to a temp location...
	if os.path.exists(index):
		try:
			os.remove(index)
		except OSError, info:
			print "Error removing", index, info
			sys.exit(1)


	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except IOError, info:
		print "Failure opening ", index, info
		exit(1)

	html = Html()	# create an html object that contains the html strings...
	# 
	# output the pieces of the page...
	#
	outfile.write(html.emit_head(page, media=True))

	outfile.write(html.emit_body(group, page, media=True))

	# The part specific to this page...

	
	content = """
		</center>
	<p>
	<!--#include virtual="links.html" -->
	<div class="maintext">
	<br>
	<!-- gittin' a little tricky w/alignment... -->
	<table border=0 cellpadding=0 width=100%><tr>
	<td valign=top><img src="Header.png" align=left alt="page.desc_title"><br clear=all>
	<i>Created: """ + cldate.utc2long(page.createtime) + """</i></td>
	<td valign=center align=right><b>Duration: """ + mk_dur_string(page.duration) + """</b></td></tr></table>
	<p><font color=a0b0c0>"""  + page.description + '<p>'

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()

def linkgen(group):
	# set up for the first and last links - cheat a bit - add a fake
	# page to the end of the list named "Archive" 
	#
	# A bit tricky...   append the list with a fake page: "Archive"
	p = Page('null')
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
			print "Links for", q.name, "correct", prevName, p.name, "stored:", q.prevlink, q.nextlink
			if prevName == q.prevlink and p.name == q.nextlink:
				print "No link change for",  q.name
			else:
				linkfile = os.path.join(currPath, 'links.html')
				print "Creating linkfile", linkfile
				try:
					l = open(linkfile, 'w+')
				except IOError, info:
					print "problem opening", linkfile, info
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
					print "Updating links in", p.name
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
	"""
	Create a short synopsis with the thumbnail, description, etc.)
	Type can be used to alter the format a bit
	"""
	if page.thumbnail != '':
		shot=page.thumbnail
	else:
		shot=page.screenshot
		print "no thumbnail"

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

def songgen(group):
	"""
	Using the song list in the passed group, rebuild those pages
	"""
	for song in group.songlist:
		print "Song found in group:", group.name, song.name

	for song in group.songlist:
		print "Writing song page:", song.name
		
		song_dir = os.path.join(group.home, 'Song', song.name)	

		try:
			os.chdir(song_dir)
		except OSError,info:
			print "Cannot cd to ", song_dir
			return()
	
	
		index='index.shtml'
	

		# RBF: hard coding  values that will be ext soon...
		#song.desc_title = "Eventual title of: " + song.name
		#song.fun_title = "Something funny here about " + song.name
	
		# make the title graphics...
		fonts = clutils.fontlib()	# maybe put this in the group?
		fontpath = fonts.fontpath('FoxboroScriptBold')
		if clutils.needs_update('.', file='Title.png'):
			make_text_graphic(song.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
		if clutils.needs_update('.', file='Header.png'):
			make_text_graphic(song.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )
	
		if not clutils.needs_update('.', file='index.shtml'):
			print "Song", song.name, "does not need update."
			return

		# open the index file, dump the header, body, etc. into it...
		try:
			outfile = open(index, 'w+')
		except IOError, info:
			print "Failure opening ", index, info
			exit(1)

		print "Updating", song.name, "index.shtml"
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

		if len(song.partlist) > 1:	# just "All", skip this...
			content += "Part index:<ul>"
			for part in song.partlist:
				name = song.partname_dict[part]
				content += '<li><a href="#' + part + '">' + name + '</a>\n'
			content += '</ul><br><hr>\n'

		fontpath = fonts.fontpath('Blacklight')
		for part in song.partlist:
			# make the title graphics...
			# For now - just the part name - more when we datafy it....
			partPng = 'Part' + part + '.png'
			if clutils.needs_update('.', file=partPng):
				partname = song.partname_dict[part]
				make_text_graphic(partname, partPng, fontpath, fontsize=45, border=5, fill=fill )

			content += '<a name="' + part + '">\n'
			content += '<img src="' + partPng + '"></br>'
			#
			# The heart of it - create entries for each matching page
			try:
				num_pages = len(song.part_dict[part])
			except KeyError:
				num_pages = 0

			print "for part", part, "num is", num_pages

			if num_pages == 0:
				content += "(none)<p>"
				continue

			song.part_dict[part].sort(key=updatekey, reverse=True)
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
				hr = "<hr width=50%>"
		

			content += '<p><hr><p>'	

		outfile.write(content)
	
		outfile.write(html.emit_tail(song))
	
		outfile.close()
	
		check_comments(song)
		
	return()
	
def homegen(group):
	"""
	Generates the top group level home page...
	"""


	try:
		os.chdir(group.home)
	except OSError,info:
		print "Cannot cd to ", group.home
		return()


	index='index.shtml'

	page = Page('null')	# create a page structure - to pass in a title
	page.desc_title = group.title
	page.fun_title = group.subtitle
	page.name = group.name

	# make the title graphics...
	fonts = clutils.fontlib()	# maybe put this in the group?
	fontpath = fonts.fontpath('FoxboroScriptBold')
	make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
        make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=45, border=2, fill=fill )
	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except IOError, info:
		print "Failure opening ", index, info
		exit(1)


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
	"""
	Generate a simple "what's new" page
	"""

	shared = os.path.join(group.home, 'Shared', 'WhatsNew')

	try:
		os.chdir(shared)
	except OSError,info:
		print "Cannot cd to ", shared
		return()


	index='index.shtml'
	if not clutils.needs_update('.', file=index):
		print "Skipping newgen..."
		return

	page = Page('null')	# create a page structure - to pass in a title
	page.desc_title = "What's New"
	page.fun_title = "What's new in " + group.title + " land"
	page.name = "WhatIsNew"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except IOError, info:
		print "Failure opening ", index, info
		exit(1)

	# make the title graphics...
	fonts = clutils.fontlib()	# maybe put this in the group?
	fontpath = fonts.fontpath('FoxboroScriptBold')
	make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
        make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )


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
	"""
	Generate a simple "navigation" 
	"""

	nav = os.path.join(group.home, 'Shared', 'Nav')

	try:
		os.chdir(nav)
	except OSError,info:
		print "Cannot cd to ", nav
		return()


	index='index.shtml'
	if not clutils.needs_update('.', file=index):
		print "Skipping nevgen..."
		return

	page = Page('null')	# create a page structure - to pass in a title
	page.desc_title = "Navigation"
	page.fun_title = "Navigation: " + group.title 
	page.name = "Navigation"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except IOError, info:
		print "Failure opening ", index, info
		exit(1)

	# make the title graphics...
	fonts = clutils.fontlib()	# maybe put this in the group?
	fontpath = fonts.fontpath('FoxboroScriptBold')
	make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
        make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )


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
	Not much for now - but feel free to comment.<p>
	There is this: <a href="http://jawknee.com/coLab/Resources/FontIndex/">Font List</a>
	<p><i>""" + cldate.now() + """</i><p>"""

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()



def archivegen(group):
	"""
	Generate an archive of the various pages...
	"""

	archive = os.path.join(group.home, 'Shared', 'Archive')

	try:
		os.chdir(archive)
	except OSError,info:
		print "Cannot cd to ", archive
		return()


	index='index.shtml'

	page = Page('null')	# create a page structure - to pass in a title
	page.desc_title = group.title + " Archive"
	page.fun_title = group.title + " Archive"
	page.name = "Archive"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except IOError, info:
		print "Failure opening ", index, info
		exit(1)



	html = Html()	# create an html object that contains the html strings...
	# 
	# output the pieces of the page...
	#
	outfile.write(html.emit_head(page, media=False))

	outfile.write(html.emit_body(group, page, media=False))

	# The part specific to this page...
	
	# make the title graphics...
	fonts = clutils.fontlib()	# maybe put this in the group?
	fontpath = fonts.fontpath('FoxboroScriptBold')
	make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
        make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )

	content = """
		</center>

	<div class="maintext">
	<img src="Title.png"><br>
	<font color=a0b0c0>
	Here are the collected pages, listed chronologically by creation time,
	most recent first.  Unless otherwise stated, all times are US/Pacific.
	<p><i>""" + cldate.now() + """</i><p><hr><p>
	<center>
	"""
	outfile.write(content)


	group.pagelist.sort(key=createkey)
	group.pagelist.reverse()
	hr = ''		# no horizontal rule on the first pass...
	for pg in group.pagelist:
		print "archive:", pg.name

		outfile.write(hr + mk_page_synopsis(pg, type='Archive'))
		hr = '<hr>'

	outfile.write('</center>\n')

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()



def helpgen(group):
	"""
	Generate a simple help page place holder (for now)
	"""

	help = os.path.join(group.home, 'Shared', 'Help')

	try:
		os.chdir(help)
	except OSError,info:
		print "Cannot cd to ", help
		return()

	index='index.shtml'
	if not clutils.needs_update('.', file=index):
		print "Skipping helpgen..."
		return

	page = Page('null')	# create a page structure - to pass in a title
	page.desc_title = "Help"
	page.fun_title = "Help"
	page.name = "Help"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(index, 'w+')
	except IOError, info:
		print "Failure opening ", index, info
		exit(1)

	# make the title graphics...
	fonts = clutils.fontlib()	# maybe put this in the group?
	fontpath = fonts.fontpath('FoxboroScriptBold')
	make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=10, fill=fill )
        make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=30, border=2, fill=fill )


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
	Some highlights:
	<ul>
		<li><b>Recent Updates</b><br>
		The top of the left side bar shows the 
		most recent activity.  The most recent
		is at the bottom of the list.  
		Pages marked <span style="color: ff2020; size: smaller;">New!</span>
		have not been commented on.  Those marked <span style="size: smaller;">(u)</span>
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
		Archve link in the top nav bar (interestingly 
		or not - the "Nav" link in the nav bar is easily the
		least useful feature).  The Archive page will show 
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
		print "Usage:", sys.argv[0], "page name"
		exit(1)

	name=sys.argv[1]



