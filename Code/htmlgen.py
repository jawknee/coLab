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

#
# font for the title graphic	 - these need to be group specific (at least)
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/WorstveldSling/WorstveldSling.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/Neurochrome/neurochr.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/TarantellaMF/Tarantella MF.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/Minus.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/Scretch.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/RADAERN.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/SF Foxboro Script v1.0/SF Foxboro Script Bold.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/SF Foxboro Script v1.0/SF Foxboro Script Extended Bold.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/maxine.ttf'
fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/JohnnyMacScrawl/jmacscrl.ttf'

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

def tagstrip(string,subs='\n'):
	"""
	Remove html tags - and arbitrarily replace them with a
	new line (default).

	Recursive - each call pulls out the next tag...
	"""

	i = string.find('<')	# is there a start tag?
	if i == -1:
		return(string)	# we're done
	closetag = string[i:].find('>') 
	if closetag == -1:		# not closing tag, return up to the start
		return(string[:i])
	next = closetag + i + 1	# set up for the recursive calll
	return ( string[:i] + subs + tagstrip(string[next:], subs) ) 
	
def smartsub(string,length):
	"""
	Return a substring that is basedj on the passed length,
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

def htmlgen(group, page):
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
        make_text_graphic(page.fun_title, 'Title.png', fontpath, fontsize=45, border=30, fill=fill )
        make_text_graphic(page.desc_title, 'Header.png', fontpath, fontsize=32, border=2, fill=fill )

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
	<td valign=top><img src="Header.png" align=left alt="page.desc_title"></td>
	<td valign=center align=right><b>Duration:""" + mk_dur_string(page.duration) + """</b></td></tr></table>
	<font color=a0b0c0>""" + page.description + "<p><i>" + cldate.utc2long(page.createtime) + """</i><p>
	<p>"""

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
	p = Page()
	p.name = "Archive"
	p.home = os.path.join(group.root, 'Shared', 'Archive')
	group.pagelist.append(p)

	# "dummy" current entry for the home...
	currName = "Home"
	currTitle = "Home"
	currFun = group.name + " Home"
	currLink = group.root

	prevName = "not set yet"
	# step through the pages in order
	for p in group.pagelist:
		if p.name == 'Archive':
			nextName = 'Archive'
			nextTitle = "Archive"
			nextFun = "Archive - a place for everything"
			nextLink = p.home
		else:
			nextName = p.name
			nextTitle = p.desc_title
			nextFun = p.fun_title
			nextLink = "../" + p.name	 # yeah, I know, cheating

		if currName != 'Home':
			linkfile = os.path.join(currPath, 'links.html')
			print "Creating linkfile", linkfile
			try:
				l = open(linkfile, 'w+')
			except IOError, info:
				print "problem opening", linkfile, info
				raise IOError

			l.write( '<div class="links" style="float: left;">' + 
				'<a href="' + prevLink + '" title="' + prevFun +
					'">&larr; ' + prevTitle + '</a></div>' +
				'<div class="links" style="float: right;">' +
				'<a href="' + nextLink + '" title="' + nextFun +
					'">' + nextTitle + ' &rarr;</a></div>' +
				'<br>' )

				
			l.close()
			

		prevName = currName
		prevTitle = currTitle
		prevFun = currFun
		prevLink = currLink

		currPath = p.home
		currName = nextName
		currTitle = nextTitle
		currFun = nextFun
		currLink = nextLink

	group.pagelist.pop()	# remove that fake "Archive" page

def songgen(group):
	"""
	Using the song list in the passed group, rebuild those pages
	"""
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
		song.desc_title = "Eventual title of: " + song.name
		song.fun_title = "Something funny here about " + song.name

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
		outfile.write(html.emit_head(song, media=False))
	
		outfile.write(html.emit_body(group, song, media=False))
	
		# The part specific to this page...
	
		content = """
			</center>
	
		<div class="maintext">
		<h2 class=fundesc>""" + song.desc_title + """</h2>
		Here are the current versions of """ + song.desc_title + """.
		They are shown by part, if any, and most recently updated first.<p>
		<i>""" + cldate.now() + """</i><br clear=all><p>"""

		if len(song.partlist) > 1:	# just "All", skip this...
			content += "Part index:<ul>"
			for part in song.partlist:
				content += '<li><a href="#' + part + '">' + part + '</a>\n'
			content += '</ul><br><hr>\n'

		for part in song.partlist:
			content += '<a name="' + part + '">\n'
			content += '<h2>' + part + '</h2>\n' 
			#
			# The heart of it - create entries for each matching page
			try:
				num_pages = len(song.part_dict[part])
			except KeyError:
				num_pages = 0

			print "for part", part, "num is", num_pages

			if num_pages == 0:
				content += "(none)"
				continue

			song.part_dict[part].sort(key=updatekey)
			song.part_dict[part].reverse()
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
				content += '<a href="' + pg.root + '"><h3 style="display: inline;">' + pg.desc_title + '</h2></h3></a>'
				content += ' ~ ' + cldate.utc2long(pg.createtime) + ' / Duration: ' + timestr + '<br>\n'
				content += '<span class="song">\n'
				content += '<a href="' + pg.root + '">' + desc_text + '</a>\n'
				content += '</span>\n'
				
				hr = "<hr width=50%>"
		

			content += "<p><hr><p>"	
			
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

	page = Page()	# create a page structure - to pass in a title
	page.desc_title = group.title
	page.fun_title = group.subtitle
	page.name = group.name

	
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
	<h2 class=fundesc>""" + group.title + """</h2>
	<img src="Shared/DSCF4212.png" width=320 height=240 align=right>
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


	new='index.shtml'

	page = Page()	# create a page structure - to pass in a title
	page.desc_title = "What's New"
	page.fun_title = "What's new in " + group.title + " land"
	page.name = "WhatIsNew"

	
	# open the index file, dump the header, body, etc. into it...
	try:
		outfile = open(new, 'w+')
	except IOError, info:
		print "Failure opening ", new, info
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
	<h2 class=fundesc>""" + page.fun_title + """</h2>
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

	page = Page()	# create a page structure - to pass in a title
	page.desc_title = "Navigation"
	page.fun_title = "Navigation: " + group.title 
	page.name = "Navigation"

	
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
	<h2 class=fundesc>""" + page.fun_title + """</h2>
	<font color=a0b0c0>
	Nothing for now - but feel free to comment.
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

	page = Page()	# create a page structure - to pass in a title
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


	content = """
		</center>

	<div class="maintext">
	<h2 class=fundesc>""" + page.fun_title + """</h2>
	<font color=a0b0c0>
	Here are the submitted pages, in chronological order of creation.
	<p><i>""" + cldate.now() + """</i><p><hr><p>
	<center>
	<table cellpadding=10 border=0 width=640>\n"""

	outfile.write(content)


	group.pagelist.sort(key=createkey)
	group.pagelist.reverse()
	for pg in group.pagelist:
		print "archive:", pg.name

		if pg.thumbnail != '':
			shot=pg.thumbnail
		else:
			shot=pg.screenshot
			print "no thumbnail"

		screenshot = os.path.join(pg.root, shot)
		timestr = mk_dur_string(pg.duration)

		# cut to length....
		desc_text = (smartsub(pg.description, 250))

		# Build up the html content for this entry....	
		content = '<tr><td colspan=2> <a href="' + pg.root + '"><h3 style="display: inline;">' 
		content += pg.desc_title + '</h3></a>' + ' ~ ' + cldate.utc2long(pg.createtime) + ' / Duration: ' + timestr + '</td></tr>' 
		content += '<tr><td><a href="' + pg.root + '"><img src="' + screenshot + '" width=160 height=140></a></td><td>' 
		content += desc_text + '</td></tr> <tr><td colspan=2><hr></td></tr>'

		outfile.write(content)

	outfile.write('</table></center>\n')

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

	page = Page()	# create a page structure - to pass in a title
	page.desc_title = "Help"
	page.fun_title = "Help"
	page.name = "Help"

	
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
	<h2 class=fundesc>""" + page.fun_title + """</h2>
	<font color=a0b0c0>
	Nothing for now - but feel free to comment.
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

	htmlgen('Catharsis', name)


