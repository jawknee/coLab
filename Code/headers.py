#!/usr/bin/env python
""" Raw html clumps that are used in various places... """

import logging
import config

class Html:
	""" An object contains the various html headers  
	
	Most a place to hold bits of html with substitutions marked with '!', (e.g.,
	!desc_title!).

	Methods are provided for emitting the various parts of most types of web pages.
	
	NOTE: __init__() method is a long collection of string assignments - and is declared below
	for readability.
	"""

	def emit_head(self, page, media=True):
		""" Emit a head element, with (default) or w/o a media insert

		Does not close out the head (emit_body does)
		"""

		# Build the web page as we go...

		# Replace specific tags in the html...		
		
		head = self.head.replace("!fun_title!", page.fun_title)
		head = head.replace("!desc_title!", page.desc_title)

		# send the media content, if needed, also send the
		# page_type specific content
		if media:
			# slightly tricky - append the page_type to 
			head_insert = eval('self.head_insert_' + page.page_type)
				
			head += head_insert
			#head = head + self.head_insert
		head += '\n'	# always nice to have one at the end
		return(head)


	def emit_body(self, group, page, media=True):
		""" Emit a body element, optionally including the media segment.
		
		Requires both a group and a page (only requires group for paths, so
		duplicating the paths in the pages may not be a bad thing)
		"""
		# replace the strings...
		body = self.body.replace('!groupURL!', group.root)
		body = body.replace('!coLabRoot!', group.coLab_root)
		if page.obj_type == 'Page':
			body = body.replace('!soundinfo!', page.soundinfo)

		if media:
			body += '\t<img src="Title.png" class="fundesc" alt="' + page.fun_title + '">'
			
			# base the name of the media insert on the page type
			media_insert = eval('self.media_insert_' + page.page_type)
			# replace the name in the older, quicktime based pages, as 
			# well as the fallback "Small" version in the html5 version..
			media_insert = media_insert.replace("!name!", page.name) 
			body += media_insert.replace("!html5-source-lines!", self.gen_html5_source(page.name, page.media_size))
			# do we include the video controls?
			body += self.video_controls
			body += self.media_tail
			body += self.gen_locbutton_tags(page)
			body += self.gen_geometry_tags(page)
		return(body)

	def emit_tail(self,page):
		""" Send out the last bit of the page... """
		
		# Replace tags...
		tail = self.tail.replace('!name!', page.name)
		tail = tail.replace('!fun_title!', page.fun_title)
		tail = tail.replace('!desc_title!', page.desc_title)
		if page.obj_type == "Page":
			tail = tail.replace('!page_type!', page.page_type)	# "orig" or "html5"
		return(tail)	# ...and done.

	def gen_html5_source(self, name, size):
		""" Generate the html5 video source
		
		This function generates a number of html5 video source lines, based on the
		size.  It works its way down the list of sizes, generating the codecs
		that are being used.
		
		<source src="!name!-media-!media_size!.webm" type='video/webm; codecs="vp8.0, vorbis"'>
		<source src="!name!-media-!media_size!.mp4" type='video/mp4'>
		"""
		logging.info("gen_html5_source: %s size %s", name, size)
		
		# a list of source type / info pairs...
		# order matters: if specified: mp4, ogg, webm   then:
		# 		chrome picks up mp4  (doesn't break up like webm)
		#		firefox picks up ogg (doesn't break up like webm)
		#		opera picks up webm (doesn't seem to actually play the video in ogg)
		# Safari and IE will pick up mp4 an in any case - oddly, firefox on windows seems
		# to also pickup mp4 - who knew?
		# media type, codec info
		sourceinfo = [ 
			( 'mp4', 'avc1.42E01E, mp4a.40.2'), 
			( 'webm', 'vp8.0, vorbis'),
			( 'ogg', 'theora, vorbis') 
			]
		sources = '\n'
		t3 = '\t' * 3	# 3 tabs - makes the html easier to read....
		size_c = config.Sizes()
		while True:
			for media_info in sourceinfo:
				(type, codecs) = media_info
				sources += t3 + '<source src="' + name + '-media-' + size + '.' + type + '"'	# first part
				sources += "type='video/" + type + '; codecs="' + codecs + '''"'/>\n'''	
			
			# Now - move down to the next size...
			size = size_c.next_size(size)
			if size is None:
				break
			if size == config.SMALLEST:	# Stop when we get to the smallest size...
				break
		return(sources)

	def gen_locbutton_tags(self, page):
		""" Generate "hidden" tags to pass button info to javascript
		
		Location (float seconds) and description (string) 
		to describe the locator buttons.
		"""
		loc_html = """
			<!-- Locator button info -->
				<input type="hidden" id="numbut" value="%d">\n""" % config.NUM_BUTS
		for i in range(1, config.NUM_BUTS+1):
			varname = "Loc_%d" % i
			value = eval('page.' + varname)
			loc_html += """
				<input type="hidden" id="%s" class="locId" value="%f">""" % (varname, value)
			value = eval('page.' + varname + '_desc')
			loc_html += """
				<input type="hidden" id="%s_desc" value="%s">""" % (varname, value)


		loc_html += """
			<!-- End loccator button info -->
			"""
		return loc_html

	def gen_geometry_tags(self, page):
		""" Generate "hidden" tags to pass info to javascript

		Generates a series of hidden input tags to specify
		the geometry and other items so the javascript can calculate 
		what to with the positioning clicks.
		"""
		sizes = config.Sizes()	
		# what is the width of the page display?
		(pgview_width, pgview_height) = sizes.sizeof(config.BASE_SIZE)
		(media_width, media_height) = sizes.sizeof(page.media_size)
		# for page - x-axis scale is all we need...
		# calculate offset - center media in the <div>
		xOffset = config.MAIN_LEFT_EDGE 
		
		geo_html = '<!-- info about X-coordinates -->\n'
		geo_html += '  <!-- page view info -->\n'
		if page.use_soundgraphic:
			# there is no screen shot - use the media size...
			pgview_scale = float(media_width) / pgview_width
			screenshot_width = "None"
			# open loop alert: calculating the image borders as per imagemaker...
			adjust_factor = sizes.calc_adjust(media_height) 
			xStart = int(config.SG_LEFT_BORDER * adjust_factor) 
			xEnd = int(media_width - ( config.SG_RIGHT_BORDER * adjust_factor) )
		else:
			pgview_scale = float(page.screenshot_width) / pgview_width
			screenshot_width = page.screenshot_width
			xStart = int( page.xStart )
			xEnd = int( page.xEnd )

		geo_html += '    <input type="hidden" id="xOffset" value="' + str(xOffset) + '">\n'
		geo_html += '    <input type="hidden" id="xStart" value="' + str(xStart) + '">\n'
		geo_html += '    <input type="hidden" id="xEnd" value="' + str(xEnd) + '">\n'
		geo_html += '    <input type="hidden" id="pageScale" value="' + str(pgview_scale) + '">\n'
		geo_html += '    <input type="hidden" id="screenshotWidth" value="' + str(screenshot_width) + '">\n'
		geo_html += '  <!-- media info (fullscreen) -->\n'
		geo_html += '    <input type="hidden" id="duration" value="' + str(page.duration) + '">\n'
		geo_html += '    <input type="hidden" id="media_width" value="' + str(media_width) + '">\n'
		geo_html += '    <input type="hidden" id="media_height" value="' + str(media_height) + '">\n'
		geo_html += '    <input type="hidden" id="media_start" value="' + str(page.xStart) + '">\n'
		geo_html += '    <input type="hidden" id="media_end" value="' + str(page.xEnd) + '">\n'

		return geo_html

	def __init__(self):
		#
		# the html content for the head and body sections
	
		self.head = """<!DOCTYPE html>
		    <html>
			<head><title>!fun_title!</title>
			<meta http-equiv="content-type" content="text/html; charset=UTF-8">
			<link rel="stylesheet" type="text/css" href="/coLab/Resources/Style_VidAuto.css">
			<!link rel="stylesheet" type="text/css" href="/coLab/Resources/bootstrap/css/bootstrap.css">
			<!link rel="stylesheet" type="text/css" href="/coLab/Resources/context.bootstrap.css">
			<link rel="stylesheet" type="text/css" href="/coLab/Resources/context.standalone.css">
			<link rel="shortcut icon" href="/coLab/Resources/CoLab_Logo2D.png">
			""" 

		self.head_insert_orig = ''
		self.head_insert_html5 = ''
	
		self.banner = """	
			<div class="banner" > <! start of banner>
					<table width=80% border=0 cellpadding=0 class="banner_txt">
					  <td align="center" ><a href="!groupURL!/index.shtml" title="Always a nice place to go...">Home</a></td>
	
					  <td align="center" ><a href="!groupURL!/Shared/WhatsNew/index.shtml" title="The place to be, if you want to be somewhere else.">What's&nbsp;New</a></td>
					  <td align="center" ><a href="!groupURL!/Shared/Nav/index.shtml" title="How to get to where you need go.">Nav</a></td>
					  <td align="center" ><a href="!groupURL!/Shared/Archive/index.shtml" title="What have we been up to...">Archive</a></td>
					  <td align="center" ><a href="!groupURL!/Shared/Help/index.shtml" title="Hopefully, the help you need.">Help</a></td>
					</tr></table>
			<br>
			</div>	<! end of banner>
		"""	
	
		# substitute !coLabRoot! with that...	
		self.body = """
			</head>
			<body>

			<! Good old jQuery >
			<script type="text/javascript" src="/coLab/Resources/jquery-1.11.1.min.js"></script>
			<! Our main javascript to drive the video - and most everything else >
			<script type= "text/javascript" src="/coLab/Resources/video_engine.js"></script>
			<! the ContextJS package for working context menus >
			<script type="text/javascript" src="/coLab/Resources/context.js"></script>

			<!--   Menu Header -->
			<div id="container" style="height: 100%; width: 100%; overflow: hidden;">
			<div class="sidebar_l">
			<!--#include virtual="!groupURL!/Shared/mostrecent.html" -->
			<p><hr><P>
			<!--#include virtual="!groupURL!/Shared/projectlist.html" -->
			</div> <! End sidebar>
			<div class="sidebar_r">
			<!--#include virtual="/coLab/Resources/News.html" -->
			<!--#include virtual="!groupURL!/Shared/News.html" -->
			<!--#include virtual="!groupURL!/Shared/rightbar.html" -->
			<p id="locators"></p>
			<p>
			<button type="button" id="sound-info-btn" title="Sound Info">Sound Info</button>
			<input type="hidden" id="sound-info" value="!soundinfo!">
			<hr><br>
			<p id="info"></p>	<! A paragraph for displaying...  info from javascript.>
			</div> <! End right sidebar>
			<div id="Logo" class="logo"><img src="/coLab/Resources/CoLab_Logo3D.png" height=50 width=50></div> 
			<! end logo>
			""" + self.banner + """	
			<div id="Content" class="main" style="height: 97%; overflow: auto ">
		"""
	
		self.media_insert_orig=''	# just in case we ever need to render an "orig" page...
		
		self.media_insert_html5="""
			<div id="video-container">		
			<!div id="clickdiv">
			<video  id="video" poster="Poster_Start.png" width="640" height="530">
			<!-- The following line is replaced with the full complement of html5 video codecs for this page... -->
			 !html5-source-lines!
			  <!-- Fall back for non-html5 browsers, (WinXP/IE8, e.g.) simple mp4 embed tag -->
			  <br>
			  <embed src="!name!-media-Small.mp4" autostart="false" height="500" width="640" /><br>
			  <font size=-2>
			  <i>Your browser does not support html5 - using mp4 plug-in</i>
			  </font>
			</video>
		<!/div><! end clickdiv>
		"""
		self.media_tail="""</div> <! video-container>\n"""
		
		# optional controls
		self.video_controls="""
		<!-- Video Controls -->
		  <div id="video-controls">
		    <span title="Play/Pause">
				<button type="button" style="vidbarbutton" id="play-pause">P</button>
			</span>
			""" + self.emit_loc_buttons() + """
			<input type="range" id="volume-bar" min="0" max="1" step="0.1" value="1">
		    <span title="FullScreen">
				<button type="button" id="full-screen">FS</button>
			</span>
		 </div> <! video-controls>
		"""
	
		self.tail = """
		<hr>
		Enter your comments here:<br>
		
		<form method=POST action="/coLab/bin/postcomments.cgi">
		Your name: <input type="text" name="Commenter" ><br>
		<input type="hidden" name="page" value="!name!">
		<input type="hidden" name="desc_title" value="!desc_title!">
		<textarea name="Text" rows=7 cols=80 id="CommentBox"></textarea>
		<br>

		<input type="submit" value="Add your comment">
		</form>
		<p><hr><p>
		<h3>Comments:</h3>
		<!--#include virtual="Comments.log" -->
		<p>
		<br>
		<div class=copyright>
		&copy; Catharsis Studios West 2014
		</div><! end of copyright>
		<!--#include virtual="links.html" -->
		<p>&nbsp;<p>
		</td></tr></table>
		<font size=1>
		Page type: !page_type!
		</font>
		</div>	<! middle content>
		</div>	<! container >

		</body>
		</html>
		"""
	def emit_loc_buttons(self,numbuttons=config.NUM_BUTS):
		""" Generate some buttons

		Simple for now - these will likely be modified by the javascript
		"""
		loc_string="""
			<span>"""
		for button in range(1, numbuttons+1):
			loc_string += """
				<button type="button" id="LocBtn%d">%d</button>""" % ( button, button)
		loc_string += """
			</span>"""
		return loc_string	
			
		


def main():
	""" test gen_html5_sources"""
	h = Html()
	source = h.gen_html5_source("ZZZZZZ", "Super-HD-Letterbox")
	print ("Got source:")
	print (source)
if __name__ == '__main__':
	main()