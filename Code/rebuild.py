#!/usr/bin/env python
"""
	Rebuild the links, side bar, and anything else
	needing routine maintenance.

	We're (currently) passed the name of a group and 
	rebuild the content found there.
"""

import os
import sys
import clutils
import cldate

import clclasses
from htmlgen import *

# 
# put these somewhere....
num_recent_entries = 5
num_project_entries = 10

def rebuild(group, opt):
	"""
	Create and populate group object, adding page and
	song objects, then create link, graphic text ad
	other related items.
	"""
	
	g = clclasses.Group(group)	# instantiate the group object

	# Load the group by traversing the file structure...
	try:
		g.load()
	except IOError, info:
		raise IOError

	#
	# At this point, we should have a populated group object, which includes
	# the group specific items as well as a list of pages, a
	# list of songs, (and eventually, probably projects)
	#
	# debug - print them out...	
	for s in g.pagelist:
		print s.name

	print "----------"
	#  sort pages by creation date - old to new...
	g.pagelist.sort(key=createkey)

	pagedir = os.path.join(g.coLab_home, 'Page')

	song_dict = {}	# a dictionary of songs we've created...


	# step through the pages in creation order, rebuilding link files and, 
	# as needed, index.shtml (data file change)
	for pg in g.pagelist:
		
		print pg.name
		# 
		# and rebuild the html in that case...
		newpage = clutils.needs_update(pg.home, file='index.shtml', opt=opt)
		if newpage:
			# Update this page
			pagegen(g, pg)

		#
		# Do we know this song yet...?
		# Create a new song if we need one, in any case
		# Append this page to the list...
		try:
			thissong = song_dict[pg.song]
		except KeyError:
			print "new song:", pg.song
			thissong = Song(pg.song)
			thissong.group = g.name
			thissong.load()
			song_dict[pg.song] = thissong
			g.songlist.append(thissong)
			print "----------------->Song name:", thissong.name

		datafile=os.path.join(thissong.home, 'data')
		if newpage:
			clutils.touch(datafile)		# touch the data file so we rebuild this song

		thissong.list.append(pg)

		# Do we know this part yet?
		try:
			thispart = thissong.part_dict[pg.part]
		except KeyError:
			print "new part:", pg.part
			thissong.part_dict[pg.part] = []

		thissong.part_dict[pg.part].append(pg)
		# RBF: hard coded part list.


	print "Songs found:"
	for songname in song_dict:
		print "Song:", songname
		song = song_dict[songname]
		song.list.sort(key=updatekey)
		for page in song.list:
			print "  Page:", page.name

		print "In part order"
		for part in song.part_dict:
			print "Part:", part
			for page in song.part_dict[part]:
				print "Page:", page.name


	# sort pages by update time... oldest to newest
	
	g.pagelist.sort(key=updatekey)

	"""
	Build the most recent list, typically included on the left sidebar...
	"""

	recent = os.path.join(g.home, 'Shared', 'mostrecent.html')
	try:
		f_recent = open(recent, 'w+')
	except IOError, info:
		print "Error opening file:", recent, info

	# a quick header...
	f_recent.write("""<!-- Shared "most-recent" list generated by """ + sys.argv[0] + \
		" on " + cldate.now() + 
		""" --> <h4>Recent Updates</h4> <ul> """)

	index = len(g.pagelist)	
	if num_recent_entries < index:
		index = -num_recent_entries 
	else:
		index = -index	

	pageURLbase = os.path.join(g.root, 'Page')
	for pg in g.pagelist[index:]:
		print "times:", pg.createtime, pg.updatetime

		flag = '<span style="font-size: smaller;'	# first part
		if pg.updatetime == pg.createtime:
			flag = flag + ' color: red;"> New!'
		else:
			flag = flag + '"> (u)'
		flag = flag + '</span>'

		localURL = os.path.join(pageURLbase, pg.name)
		f_recent.write('<li><a href="' + localURL + '/" title="' + pg.fun_title +
			'">' + pg.desc_title + '</a>' + 
			flag +
			'<br><i>' + cldate.utc2short(pg.updatetime) + 
			'</i></li>\n')

		print pg.name, '-', cldate.utc2short(pg.updatetime), flag

	f_recent.write('</ul>\n')
	f_recent.close()

	"""
	Similarly, build the Song/Project link
	"""

	project = os.path.join(g.home, 'Shared', 'projectlist.html')
	try:
		f_project = open(project, 'w+')
	except IOError, info:
		print "Error opening file:", project, info

	# a quick header...
	f_project.write("""<!-- Shared "project" list generated by """ + sys.argv[0] + \
		" on " + cldate.now() + 
		""" --> <h4>Current Projects</h4> <ul> """)

	index = len(g.songlist)	
	if num_project_entries < index:
		index = -num_project_entries
	else:
		index = -index

	songURLbase = os.path.join(g.root, 'Song')
	print "index is", index, "song list is", g.songlist
	for sg in g.songlist[index:]:
		#print "times:", sg.createtime, sg.updatetime

		localURL = os.path.join(songURLbase, sg.name)
		f_project.write('<li><a href="' + localURL + '/" title="' + sg.fun_title +
			'">' + sg.desc_title + '</a>' )
		if len(sg.part_dict) > 1:	# also list the parts
			f_project.write('<br><span style="font-size: smaller;">')
			dot = ''	# nothing for now...
			for pt in sg.partlist:
				title = sg.partname_dict[pt]
				f_project.write(dot + '<a href="' + 
					localURL + '/#' + pt + '" title="' + title + '">' +
					pt + '</a>')
				dot = ' &middot; '	# prepend the rest with dots
				
				
			f_project.write('<br></span>')


	f_project.write('</ul>\n')
	f_project.close()
	#
	# Generate the links from the list..
	g.pagelist.sort(key=createkey)
	linkgen(g)	# build the included links for the each page
	for song in g.songlist:
		print "precheck:", g.name, song.name

	songgen(g)	# build the song pages

	homegen(g)	# The pages associated with the banner links...
	newgen(g)
	navgen(g)
	archivegen(g)
	helpgen(g)

	sys.exit(0)


def main():
	# Name of the group...
	try:
		group = sys.argv[1]
	except IndexError, info:
		print "usage: use correctly:", info
		sys.exit(1)

	# optional option parm
	try:	
		opt = sys.argv[2]
	except:
		opt = 'none'

	rebuild(group, opt)

if __name__ == '__main__':
	main()
