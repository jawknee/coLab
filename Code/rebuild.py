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
# temp?
import time

import Tkinter as tk
import ttk
import threading

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

class Render_engine():
	"""
	A class to allow us to render pages in the background.
	A file contains a list of page dirs that need to be
	rendered (relative to home / colab_home).  The rebuild_page method then calls render_page
	for each page - and each resolution needed.
	"""
	
	def __init__(self, master, render_list_file=None):
		"""
		Open the initial window if not already set.  
		Note this is a separate loop from the main edit
		as it can run offline.
		
		Process the waiting pages.
		"""
		self.master = master
		self.busy = False
		try:
			self.conf=clutils.get_config()
			print "conf shows:", self.conf.coLab_home
		except ImportError:
			print "Cannot find config."
			sys.exit(1)		# fatal...
			
		self.home = self.conf.coLab_home   # can be overridden - not currently anticipated
		if render_list_file is None:	
			render_list_file = os.path.join(self.home, "PendingRenders")	
		
		print "Render list:", render_list_file
			
		self.render_list_file = render_list_file
		self.top = None		# force the first frame to open...
		self.init()
		
	def init(self):
		"""
		Continue the opening of the "initial" frame.  By separating
		this from the main init, we can call it from other methods
		to reopen the render frame in case someone has terminated it.
		"""
		# Have we created the render master window?   if not, do so...
		if isinstance(self.top, tk.Toplevel):
			return 
		
		self.top = tk.Toplevel()
		self.top.title("coLab Render Engine")
		self.top.geometry("+1000+60")
		self.top.lift(self.master)
		self.r_frame = tk.LabelFrame(self.top, text="coLab Render Engine", relief=tk.GROOVE)
		self.r_frame.grid(padx=25, pady=25, ipadx=10, ipady=10)
		active_frame = tk.LabelFrame(self.r_frame, text="Active render:")
		active_frame.grid(row=0, column=0, padx=5, pady=5, ipadx=10, ipady=10, stick=tk.E+tk.W)
		
		self.active_name = tk.StringVar()
		self.active_name.set("None")
		
		tk.Label(active_frame, textvariable=self.active_name, anchor=tk.NE, justify=tk.LEFT).grid()
		
		pending_frame = tk.LabelFrame(self.r_frame, text="Pending Renders:")
		pending_frame.grid(row=1, column=0, padx=5, pady=5, ipadx=10, ipady=10, sticky=tk.E+tk.W)
		
		self.pending_list = tk.StringVar()
		self.pending_list.set('')
		tk.Label(pending_frame, textvariable=self.pending_list, anchor=tk.NE, justify=tk.LEFT).grid()
		
		ttk.Button(self.r_frame, text="Terminate", command=self.terminate).grid(row=2, sticky=tk.SW)
		
		# initialize the pending list any existing file...
		try:
			f = open(self.render_list_file)
			self.pending_renders = f.read().split('\n')	# split on new lines - last one - remove
		except:
			print "Oops?"
			self.pending_renders = ['']
		
		
		print "Render file list:", self.pending_renders
		self.pending_renders.pop()
		self.refresh()

		# Make sure we stop by once in a while to see how things are going....
		self.master.after(2000,self.check)
	
	def check(self):	
		"""
		Called every now and then to see what we're up to...
		"""
		print "Entered check."
		try:
			next_render = self.pending_renders.pop(0)
		except:
			next_render = None
			self.active_name.set("(None)")
			return
		else:	
			self.active_name.set('--pending--')
			
			
		page = clclasses.Page()
		# If we got here "offline", i.e., an abandoned render found in the 
		# file, the let's set the rebuild/changed flags...
		try:
			page.needs_rebuild
		except:
			page.needs_rebuild = True
		try:
			page.changed
		except:
			page.changed = True
			
		try:
			page.load(next_render)
		except:
			print "Something went wrong with the loading of 'next_render'"
		
		# Build the new display text...
		active_text = page.desc_title + '\n'
		active_text += page.media_size + u"\u2190"
		self.active_name.set(active_text)
		page_thread=threading.Thread(target=self.render_all, args=(page,))
		page_thread.start()
		self.refresh()
		self.busy = True

		#self.master.after(2000,self.check)
		
	def refresh(self):
		"""
		Update the strings based on the current state of things....
		"""
		print "Greetings from refresh"
		# create a Page class - load it up to the title, 
		# build the titles from that...
		p = clclasses.Page('temp')
		renderlist = []		# titles of the pending renders...
		for path in self.pending_renders:
			#print "Path:", path
			#fullpath = os.path.join(self.home, path)
			p.load(path)
			renderlist.append(p.desc_title)
		#print "Renderlist is:", renderlist
		renderstring = '\n'.join(renderlist)
		self.pending_list.set('\n'.join(renderlist))
		
	
	def add_render(self, path):
		""" 
		Add the passed path to the render list
		"""
		print "Add_render: just called with:", path
		self.init()
		self.pending_renders.append(path)
		self.refresh()
		if not self.busy:
			self.master.after(5000,self.check)	# make sure we get called...
		
	def terminate(self):
		self.top.destroy()
		self.top = None
		
	def set_list(self, list):
		self.init()	# check?
		# tmp - just to see if I can set the list on the fly...
		print "Just received list:", list
		self.pending_list.set(list)
		
	def hello(self):
		print "Greetings from Page_builder"
		print "My render_list is:", self.render_list_file
	
	def render_all(self, page):
		"""
		Calls render_page for each of the media sizes 
		that relate to the page's specified size.
		"""
		# Save the size - we've already posted the size, and
		# we're going to generate the media by manipulating
		# page.media_size - but it's a good idea to set it
		# back when we're done...
		original_size = page.media_size
		size_c = config.Sizes()
		
		while True:
			print "Render-all, rendering:", page.media_size
			render_page(page)
			page.media_size = size_c.next_size(page.media_size)
			if page.media_size != config.SMALLEST:
				break
			
		page.media_size = original_size
		self.busy = False
		self.master.after(2000, self.check)
		local_url = "http://localhost/" + page.root
		browse_thread = threading.Thread(clSchedule.browse_url, args=(local_url))
		browse_thread.start()
		
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
	progressTop.title('coLab Page Rendering')
	title = "New Page Generation: " + page.desc_title + ' (' + media_size + ')'
	render_frame = tk.LabelFrame(master=progressTop, relief=tk.GROOVE, text=title, borderwidth=5)
	render_frame.lift(aboveThis=None)
	render_frame.grid(ipadx=10, ipady=40, padx=25, pady=15)
	#
	
	fps = imagemaker.calc_fps_val(page)
	frames = int(float(page.duration) * fps) 
	f0 = tk.Frame(render_frame)
	f0.grid(row=0, column=0, sticky=tk.W)
	
	snd_img_progbar = cltkutils.Progress_bar(f0, 'Sound Image Overview')
	snd_img_progbar.what = 'Line'
	snd_img_progbar.width = 500
	
	if page.needs_rebuild:
		f1 = tk.Frame(render_frame)
		f1.grid(row=1, column=0, sticky=tk.W)
		
		img_gen_progbar = cltkutils.Progress_bar(f1, 'Video Images', max=frames)
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
			imagemaker.make_sound_image(page, snd_img_progbar, sound_dest, img_dest, size, max_samples_per_pixel)
			#snd_img_progbar.stop()
			imagemaker.make_images(page, img_gen_progbar, media_size)
			#img_gen_progbar.progBar.stop()
			clAudio.make_movie(page, vid_gen_progbar)
			#vid_gen_progbar.stop()
	except:
		print "no page editor object - likely running free..."
		
	#ftp_progbar.progBar.start()
	try:
		rebuild(page.group_obj)		# currently the group name - change to the object...
	except:
		print"Need to find a solution to the group render problem!"
	#ftp_progbar.progBar.stop()
			
	progressTop.destroy()

	
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
	"""
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
	"""
	print "In main of rebuild..."
	master = tk.Tk()
	pb = Render_engine(master)
	#threading.Thread(target=test_thread, args=(pb,)).start()
	master.mainloop()
	
def test_thread(pb):
	print "Greetings from tt"
	pb.hello()
	"""
	for l in ("just-this", "A Test\nAnotherTest\nStormJustBecause", "Everybody happy\nNow You Happy Too"):
		time.sleep(5)
		print "Setting list to:", l
		pb.set_list(l)
	"""
	
if __name__ == '__main__':
	main()
