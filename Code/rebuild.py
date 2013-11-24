#!/usr/bin/env python
"""
	Rebuild the links, side bar, and anything else
	needing routine maintenance.

	We're (currently) passed the name of a group and 
	rebuild the content found there.
"""

import os
import sys
import subprocess

import Tkinter as tk
import ttk

import config
import clutils
import cltkutils
import cldate
import clclasses
import clAudio
import imagemaker
import clSchedule
from htmlgen import *

# 
# put these somewhere....
num_recent_entries = 5
num_project_entries = 10

def render_page(page, media_size=None, max_samples_per_pixel=0):
	"""
	Interface to the routines to render a page.  By passing in size,
	it only renders that size - presumably for a preview.  Max samples/pixel
	can be set some number (100?) to speed up the generation of the 
	soundfile image - again, for previews. 
	
	This routine can be called from the interactive (clFunctions) section
	or the background task - so that multiple media types can be generated.
	"""
	
	if media_size is None:
		media_size = page.media_size
		
	size = config.Sizes().sizeof(media_size)
	print "render_page - size is:", size
	sound_dest = os.path.join(page.home, page.soundfile)
	img_dest = os.path.join(page.home, page.soundgraphic)
	#make_sound_image(page, sound_dest, img_dest, size, max_samples_per_pixel)
	
	# let's make sure mamp is running...
	
	clSchedule.start_mamp()
	progressTop = tk.Toplevel()
	progressTop.transient()
	render_frame = tk.LabelFrame(master=progressTop, relief=tk.GROOVE, text="New Page Generation" , borderwidth=5)
	render_frame.lift(aboveThis=None)
	render_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
	#
	
	fps = imagemaker.calc_fps_val(page)
	frames = int(float(page.duration) * fps) 
	f0 = tk.Frame(render_frame)
	f0.grid(row=0, column=0, sticky=tk.W)
	imagemaker.make_sound_image(f0, page, sound_dest, img_dest, size, max_samples_per_pixel)
	if page.needs_rebuild:
		f1 = tk.Frame(render_frame)
		f1.grid(row=1, column=0, sticky=tk.W)
		
		img_gen_progbar = cltkutils.Progress_bar(f1, 'Image Generation', max=frames)
		img_gen_progbar.what = 'Image'
		img_gen_progbar.width = 500
		img_gen_progbar.max = frames
		img_gen_progbar.post()		# initial layout...
		
		f2 = tk.Frame(render_frame)
		f2.grid(row=2, column=0, sticky=tk.W)
		
		vid_gen_progbar = cltkutils.Progress_bar(f2, 'Video Generation', max=frames)
		vid_gen_progbar.what = 'Frame'
		vid_gen_progbar.width = 500
		vid_gen_progbar.max = frames
		vid_gen_progbar.post()
	 
	"""
	f3 = tk.Frame(render_frame)
	f3.grid(row=2, column=0, sticky=tk.W)
	ftp_progbar = cltkutils.Progress_bar(f3, 'ftp mirror...')
	ftp_progbar.width = 500
	ftp_progbar.mode = 'indeterminate'
	ftp_progbar.post()
	"""

	f4 = tk.Frame(render_frame)
	f4.grid(row=3, column=0, sticky=tk.E)
	quitButton = ttk.Button(f4, text="Quit", command=progressTop.quit)
	quitButton.grid()
	
	try:
		if page.needs_rebuild:	
			imagemaker.make_images(page, img_gen_progbar, media_size)
			img_gen_progbar.progBar.stop()
			clAudio.make_movie(page, vid_gen_progbar)
	except:
		print "no page editor object - likely running free..."
		
	#ftp_progbar.progBar.start()
	rebuild(page.group_obj)		# currently the group name - change to the object...
	#ftp_progbar.progBar.stop()
			
	progressTop.destroy()
	local_url = "http://localhost/" + page.root
	clSchedule.browse_url(local_url)
	

def rebuild(g, mirror=False, opt="nope"):
	"""
	Create and populate group object, adding page and
	song objects, then create link, graphic text ad
	other related items.
	
	(Converting from rebuild_manual to no longer read the data -
	it's all loaded up).
	"""
	
	# For now...
	# Used to pass a group name - still do from the "Refresh" button.
	# A bit kludgy, but if the passed item does not have a coLab_home, 
	# let's assume we have a grup "name" and try to load it.
	try:
		g.coLab_home
	except:
		gname=g 
		g = clclasses.Group(gname)
		g.load()
		
	
	# Now that we have the paths, let's call the interarchy applescript
	# to update the mirror
	scriptpath = os.path.join(g.coLab_home, 'Code', 'Interarchy_coLab_mirror.scpt')
	osascript = "/usr/bin/osascript"
	if mirror:
		print "Mirror:", osascript, scriptpath
		try:
			subprocess.call([osascript, scriptpath])
		except:
			print "Mirror error: cannot continue."
			sys.exit(1)
		
	
	#
	# At this point, we should have a populated group object, which includes
	# the group specific items as well as a list of pages, a
	# list of songs, (and eventually, probably projects)
	#
	# debug - print them out...	
	for s in g.pagelist:
		print "group->page", s.name

	print "----------"
	#  sort pages by creation date - old to new...
	g.pagelist.sort(key=clclasses.createkey)

	pagedir = os.path.join(g.coLab_home, 'Page')

	song_dict = {}	# a dictionary of songs we've created:  song name -> song object


	# step through the pages in creation order, rebuilding link files and, 
	# as needed, index.shtml (data file change)
	for pg in g.pagelist:
		
		print pg.name
		thissong = g.songdict[pg.song]	# Song obj. for this page
		# 
		# and rebuild the html in that case...
		newpage = clutils.needs_update(pg.home, file='index.shtml', opt=opt)
		if newpage:
			# Update this page
			pagegen(g, pg)
			
			songdatafile=os.path.join(thissong.home, 'data')	# path to the song's data file
			clutils.touch(songdatafile)		# touch the data file so we rebuild this song

		
		# Create a dictionary for each song - each part points to a list of songs
		
		# Do we know this part yet?
		try:
			thispart = thissong.part_dict[pg.part]
		except KeyError:
			print "new part:", pg.part
			thissong.part_dict[pg.part] = []

		thissong.part_dict[pg.part].append(pg)

	"""
	print "Songs found:"
	for songname in song_dict:
		print "Song:", songname
		song = song_dict[songname]
		song.list.sort(key=clclasses.updatekey)
		for page in song.list:
			print "  Page:", page.name

		print "In part order"
		for part in song.part_dict:
			print "Part:", part
			for page in song.part_dict[part]:
				print "Page:", page.name
	#"""

	# sort pages by update time... oldest to newest
	
	g.pagelist.sort(key=clclasses.updatekey)

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
	g.songlist.sort(key=clclasses.createkey)
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
	g.pagelist.sort(key=clclasses.createkey)
	linkgen(g)	# build the included links for the each page
	for song in g.songlist:
		print "precheck:", g.name, song.name

	songgen(g)	# build the song pages

	homegen(g)	# The pages associated with the banner links...
	newgen(g)
	navgen(g)
	archivegen(g)
	helpgen(g)
	print "Rebuild done."
	
	
	if mirror:
		subprocess.call([osascript, scriptpath])
		print "Upload/Mirror done."
	#sys.exit(0)


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
