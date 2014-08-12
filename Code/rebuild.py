#!/usr/bin/env python
""" Rebuild the links, side bar, and anything else needing routine maintenance.

	We're (currently) passed the name of a group and 
	rebuild the content found there.
"""
import os
import sys
import logging
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
import clColors
import imagemaker
import clSchedule
import htmlgen
# 
NOT_NEW = 14 * 86500		# how old is not new... in seconds (two weeks?)
# put these somewhere....
num_recent_entries = 7
num_project_entries = 20

class Render_engine():
	""" A class to allow us to render pages in the background.

	A file contains a list of page dirs that need to be
	rendered (relative to home / colab_home).  The rebuild_page method then calls render_page
	for each page - and each resolution needed.
	"""
	
	def __init__(self, master, render_list_file=None):
		""" Open the initial window if not already set.  

		Note this is a separate loop from the main edit
		as it can run offline.
		
		Process the waiting pages.
		"""
		self.master = master
		self.busy = False				# are we rendering now?
		self.group_rebuild_list = []		# which groups need a rebuild?
		
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
		""" Continue the opening of the "initial" frame.  
		
		By separating this from the main init, we can call it from other methods
		to reopen the render frame in case someone has terminated it.
		"""
		# Have we created the render master window?   if not, do so...
		if isinstance(self.top, tk.Toplevel):
			return 
		
		self.top = tk.Toplevel()
		self.top.title("coLab Render Engine")
		self.top.geometry("+1200+80")
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
			logging.info("No pending renders file.")
			self.pending_renders = []
		
		
		print "Render file list:", self.pending_renders
		if len(self.pending_renders) != 0:
			self.pending_renders.pop()	# the new line at the end of the last line creates a null entry - loose it.
		self.refresh()

		# Make sure we stop by once in a while to see how things are going....
		self.master.after(2000,self.check)
	
	def check(self):	
		""" Called every now and then to see what we're up to... """

		#print "Entered check."
		if self.busy:
			#print "still busy..."
			self.master.after(1000,self.check)	# every second should be sufficient...
			return
		
		print "Length of pending_renders is:", len(self.pending_renders)
		if len(self.pending_renders) == 0:
			next_render = None
			self.active_name.set("(None)")
			# What we want to do here is first, rebuild all the involved
			# groups, so the local pages are up to date, then for
			# each a mirror, a rebuild - to process any comments - then
			# another rebuild.   This does that - but for a bit of 
			# simplicity, it does one more rebuild than it needs to...
			#for mirroring in [ False, True, True ]:
			for mirroring in [ True ]:	# for now...
				for group in self.group_rebuild_list:
					print "rebuilding and uploading for group:", group, mirroring
					rebuild_and_upload(group, mirror=mirroring )
			return
		else:
			next_render = self.pending_renders.pop(0)


		page = clclasses.Page()
		"""
		If we got here "offline", i.e., an abandoned render found in the 
		file, the let's set the rebuild/changed flags...

		RBF - or at least check it...  if we ever actually carry along a 
		page object, and not just a path, then this might make sense...
		otherwise we'll always set it to true - which is basically OK at this point.
		"""
		page.needs_rebuild = True
		"""
		try:
			page.needs_rebuild
		except:
			page.needs_rebuild = True
			
		#"""

		try:
			page.load(next_render)
		except:
			print "Something went wrong with the loading of 'next_render'"
			return
		
		
		# Build the new display text...
		active_text = page.desc_title + '\n'
		page.base_size = page.media_size
		active_text += "--pending---"
		self.active_name.set(active_text)
		self.busy = True
		self.needs_rebuild = True
		page_thread=threading.Thread(target=self.render_all, args=(page,))
		page_thread.start()
		self.refresh()

		self.master.after(1000,self.check)	# just a sec...
		
	def refresh(self):
		""" Update the strings based on the current state of things.... """

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
		""" Add the passed path to the render list """

		print "Add_render: just called with:", path
		self.init()
		self.pending_renders.append(path)
		self.refresh()
		if not self.busy:
			self.master.after(1000,self.check)	# make sure we get called...
		
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
		""" Calls render_page for each of the media sizes 

		that relate to the page's specified size.
		"""

		# Save the size - we've already posted the size, and
		# we're going to generate the media by manipulating
		# page.media_size - but it's a good idea to set it
		# back when we're done...
		size_c = config.Sizes()
		try:
			os.chdir(page.home)
		except OSError, info:
			print "Problem changing to :", page.home
			print info
			sys.exit(1)

		# remove all media of the form <name>-media - plus the old stuff...
		print "Removing existing media files..."
		media_list = [ "-media-", "-desktop.m4v", "-iPhone-cell.3gp", "-iPhone.m4v", ".mov"  ]
		# create a new list with the name prefix..
		remove_list = []
		for med in media_list:
			remove_list.append(page.name + med)
		file_list = os.listdir(page.home)

		for file in file_list:
			for prefix in remove_list:
				if file.startswith(prefix):
					print "Removing media,", file, ", matching:", prefix
					os.system('rm -fv ' + file)

		#
		# Start at the current size and work our way down through the
		# sizes to generate all the media sizes we want.
		while True:
			# Build a new bit of text based on the size change, marking the one
			# we're doing now with an arrow...
			active_text = page.desc_title + '\n'
			size = page.base_size
			while True:
				active_text += "  " + size
				if size == page.media_size:
					active_text += u"\u2190"
				active_text += '\n'
				
				size = size_c.next_size(size)
				if size == config.SMALLEST:
					break
			self.active_name.set(active_text)	# post the name....

			# re-render this resolution...
			print "Render-all, rendering:", page.media_size
			top_bar = render_page(page)
			print "Back from the render_page"
			top_bar.destroy()		# seems to work better if we destroy the top bar here...

			page.media_size = size_c.next_size(page.media_size)		# next?
			if page.media_size == config.SMALLEST:
				break
		
		print "Done - scheduling check in 100 ms"
		page.media_size = page.base_size
		#self.master.after(100, self.check)
		# Need something here to keep things going...   
		#self.top.configure(takefocus=True)
		
		print "Scheduling browser..."
		local_url = "http://localhost/" + page.root
		clSchedule.browse_url(local_url)
		
		self.group_rebuild_list.append(page.group)
		print "Group rebuild list is:", self.group_rebuild_list
		self.busy = False
		#browse_thread = threading.Thread(clSchedule.browse_url, args=(local_url))
		#browse_thread.start()
		print "Scheduling browser..."			#  RBF!!   hardcoded URL
		remote_url = "http://jawknee.com/" + page.root
		clSchedule.browse_url(remote_url)
		print "Done."
		
def render_page(page, media_size=None, max_samples_per_pixel=0):
	""" Interface to the routines to render a page.  
	
	By passing in size, it only renders that size - presumably for a preview.  
	Max samples/pixel can be set some number (100?) to speed up the generation of the 
	soundfile image - again, for previews. 
	
	This routine can be called from the interactive (clFunctions) section
	or the background task - so that multiple media types can be generated.
	"""
	
	if media_size is None:
		media_size = page.media_size
	else:
		page.media_size = media_size
		
	print "render_page - size is:", media_size
	sound_dest = page.localize_soundfile()
	img_dest = os.path.join(page.home, page.soundgraphic)
	#make_sound_image(page, sound_dest, img_dest, size, max_samples_per_pixel)
	
	progressTop = tk.Toplevel()
	progressTop.transient()
	progressTop.title('coLab Page Rendering')
	progressTop.geometry('+1500+100')
	title = "New Page Generation: " + page.desc_title + ' (' + media_size + ')'
	render_frame = tk.LabelFrame(master=progressTop, relief=tk.GROOVE, text=title, borderwidth=5)
	render_frame.lift(aboveThis=None)
	render_frame.grid(ipadx=10, ipady=10, padx=15, pady=15)
	
	size_c = config.Sizes()
	(width, height) = size_c.sizeof(media_size)
	
	if page.use_soundgraphic:
		adjust_factor = size_c.calc_adjust(height)
		page.xStart = int(config.SG_LEFT_BORDER * adjust_factor)
		page.xEnd = int(config.SG_RIGHT_BORDER * adjust_factor)
	#
	fps = imagemaker.calc_fps_val(page)
	frames = int(float(page.duration) * fps) 
	print "render_page fps, frames, page.duration", fps, frames,  page.duration
	if page.use_soundgraphic:
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
	page.desc_title + ' (' + media_size + ')'

	# create a label area with some helpful info...
	infotext =  '\nPage:\t' + page.desc_title +  '\n' 	
	infotext +=	'Size:\t' + media_size + ' (' + str(width) + ',' + str(height) + ')\n'
	infotext += 'Duration:\t' + '%.3f' % page.duration + ' seconds\n'
	infotext += 'fps:\t' + imagemaker.calc_fps_string(page) + '\n' 
	infotext += 'frames:\t' + str(frames) + '\n'
	infotext += 'Graphic:\t'
	if page.use_soundgraphic:
		infotext += "Sound Graphic"
	else:
		infotext += "Screenshot"
	infotext += '\n'

	info = tk.Label(render_frame, text=infotext, justify=tk.LEFT)
	info.grid(row=4, column=0)

	if page.use_soundgraphic:
		imagemaker.make_sound_image(page, sound_dest, img_dest, media_size, snd_img_progbar, max_samples_per_pixel)

	try:

		if page.needs_rebuild:	
		
			#snd_img_progbar.stop()
			#imagemaker.make_images(page, img_gen_progbar, media_size)
			imagemaker.make_images(page, img_gen_progbar)
			#img_gen_progbar.progBar.stop()
			clAudio.make_movie(page, vid_gen_progbar)
			print "Returned from clAudio.make_move"
			#vid_gen_progbar.stop()
	except Exception, info:
		logging.warning("TypeError: %s", info)
		
	#ftp_progbar.progBar.start()
	"""
	try:
		rebuild(page.group_obj)		# currently the group name - change to the object...
	except:
		print"Need to find a solution to the group render problem!"
	#"""
	#ftp_progbar.progBar.stop()
	print "returning the progTop var", progressTop
	#page.top.update_idletasks()
	#progressTop.destroy()
	progressTop.update_idletasks()
	return(progressTop)

def rebuild_and_upload(group, mirror=True, opt="nope"):
	""" Simple interface to do the uploading.   
	
	We want the pages rebuilt first, but we also need to rebuild after a mirror, 
	in case any comments were added since we last did this.  So: the plan is: 
	rebuild, upload, rebuild, upload
	"""
	#
	# Just do it twice...
	print "Full rebuild and upload...   ", time, "time."
	# For now...
	# Used to pass a group name - still do from the "Refresh" button.
	# A bit kludgy, but if the passed item does not have a coLab_home, 
	# let's assume we have a group "name" and try to load it.
	try:
		group.coLab_home
	except:
		gname=group
		print "WARNING: obsolescent call: group passed as a name:", gname
		group = clclasses.Group(gname)
		group.load()
		
	rebuild(group)
	#return
	
	if mirror:
		do_mirror(group.coLab_home)

def do_mirror(coLab_home=None):
	""" call interarchy to do the ftp / upload / mirror """

	# Now that we have the paths, let's call the interarchy applescript
	# to update the mirror
	if coLab_home is None:
		# I'll configure this when I get a chance....
		sys.exit(1)	 # What were you thinking???

	#return		# skip the auto-ftp for now...		

	scriptpath = os.path.join(coLab_home, 'Code', 'Interarchy_coLab_mirror.scpt')
	osascript = "/usr/bin/osascript"
	print "Mirror:", osascript, scriptpath
	try:
		pid = subprocess.Popen([osascript, scriptpath]).pid
		print "do_mirror - mirror pid is:", pid
	except:
		print "Mirror error: cannot continue."
		sys.exit(1)

def rebuild(g, mirror=False, opt="nope"):
	""" rebuilt a group page

	Takes a passed group object (or, for somewhat questionable
	reasons - a group name) which is then loaded,
	
	mirror specifies if the ftp (or other method) file mirror should 
	be done, and the 'opt' var can be set to 'All' to force all
	entities to be rebuilt (comes back from clutils.needs_update).
	"""
	# As above, this is hopefully a temporary catch for older calls,
	# that still call rebuild directly
	try:
		g.coLab_home
	except:
		gname=g 
		print "WARNING: obsolecent call: group passed as a name:", gname
		g = clclasses.Group(gname)
		g.load()
		
	print "Rebuilding group object:", g.title
	
	"""
	At this point, we should have a populated group object, which includes
	the group specific items as well as a list of pages, a
	list of songs, (and eventually, probably projects)
	"""
	# debug - print them out...	
	for s in g.pagelist:
		print "group->page", s.name

	print "----------"
	#  sort pages by creation date - old to new...
	g.pagelist.sort(key=clclasses.createkey)

	pagedir = os.path.join(g.coLab_home, 'Page')

	song_dict = {}	# a dictionary of songs we've created:  song name -> song object

	"""
	step through the pages in creation order, rebuilding link files and, 
	as needed, index.shtml (data file change)
	"""
	for pg in g.pagelist:
		print "Next page - name, song is:", pg.name, pg.song
		thissong = g.songdict[pg.song]	# Song obj. for this page
		# 
		# and rebuild the html in that case...
		if clutils.needs_update(pg.home, file='index.shtml', opt=opt):    #  possibly:  or pg.needs_rebuild:
			# Update this page
			htmlgen.pagegen(g, pg)
			# this should be replaced - or at least enhanced by 
			# checking existing song objects for the "needs_rebuild" option
			songdatafile=os.path.join(thissong.home, 'data')	# path to the song's data file
			clutils.touch(songdatafile)		# touch the data file so we rebuild this song
		
		"""
		Create a dictionary for each song - each part points to a list of Pages,
		this is how we build the Song pages - indexed by part, showing the related
		pages.
		"""
		# Do we know this part yet?
		try:
			thispart = thissong.part_dict[pg.part]
		except KeyError:
			print "new part:", pg.part
			thissong.part_dict[pg.part] = []

		thissong.part_dict[pg.part].append(pg)
		
		#RBF:   This whole section above needs a good look pretty soon.

	"""  old debug code...
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
		f_recent = open(recent, 'w')
	except IOError, info:
		print "Error opening file:", recent, info

	# a quick header...
	f_recent.write("""<!-- Shared "most-recent" list generated by """ + sys.argv[0] + 
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

		# If the page is new or has been updated recently,
		# then make a "mark"
		age = cldate.epochtime(cldate.utcnow()) - cldate.epochtime(pg.updatetime)
		print "Age is:", age

		flag = ''		# any tag on the end of name...
		if age < NOT_NEW:
			flag = '<span style="font-size: smaller;'	# first part
			if pg.updatetime == pg.createtime:
				# is it really new?
				flag = flag + ' color: red;"> New!'
			else:
				brgreen = clColors.htmlcolor(clColors.GREEN)	# use our brighter green
				flag = flag + ' color: ' + brgreen + ';"> (u)'
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
		if len(sg.partname_dict) > 1:	# also list the parts
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
	htmlgen.linkgen(g)	# build the included links for the each page
	for song in g.songlist:
		print "precheck:", g.name, song.name

	htmlgen.songgen(g)	# build the song pages

	htmlgen.homegen(g)	# The pages associated with the banner links...
	htmlgen.newgen(g)
	htmlgen.navgen(g)
	htmlgen.archivegen(g)
	htmlgen.helpgen(g)
	print "Rebuild done."


def main():
	"""  older debug code...
	
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
	
	master.mainloop()

if __name__ == '__main__':
	main()
