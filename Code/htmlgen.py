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
		
	file = 'links.html'
	if not os.path.isfile(file):
		try:
			f = open(file, 'w+')	# just create a blank file for now
			f.close()
		except:
			print "Error creating", file


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


	now = cldate.now()

	index='index.shtml'
	# for now - shuffle the current one to a temp location...
	if os.path.exists(index):
		try:
			shutil.move(index, index + ".prev")
		except OSError, info:
			print "Error moving", index, index
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

	<!--#include virtual="links.html" -->
	<div class="maintext">
	<h2 class=fundesc>""" + page.desc_title + """</h2>
	<font color=a0b0c0>""" + page.description + "<p><i>" + cldate.utc2long(page.create) + """</i><p>
	<p>"""

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()
	
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
	<font color=a0b0c0>""" + group.description + """<p>
	<i>""" + cldate.now() + """</i><p>"""

	outfile.write(content)

	outfile.write(html.emit_tail(page))

	outfile.close()

	check_comments(page)
	
	return()


def newgen(group):
	"""
	Generate a simple "what's new" page
	"""

	shared = os.path.join(group.home, 'Shared', 'Whats')

	try:
		os.chdir(shared)
	except OSError,info:
		print "Cannot cd to ", shared
		return()


	new='new.shtml'

	page = Page()	# create a page structure - to pass in a title
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
	#group.pagelist.reverse()	# uncomment for newest first
	for pg in group.pagelist:
		print "archive:", pg.name

		screenshot = os.path.join(pg.root, pg.screenshot)
		outfile.write( '<tr><td colspan=2> <a href="' + pg.root + '"><h3 style="display: inline;">' + pg.desc_title + '</h3></a>' +
		' ~ ' + cldate.utc2long(pg.create) + '</td></tr>' +
		'<tr><td><a href="' + pg.root + '"><img src="' + screenshot + '" width=160 height=140></a></td><td>' +
		pg.description[:250] + """</td></tr>
		<tr><td colspan=2><hr></td></tr>"""
		)

	outfile.write('</table></center>\n')

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


