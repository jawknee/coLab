#!/usr/bin/env python
"""
	Raw html clumps that are used in various places...

"""

import config

class Html:
	"""
	An html object contains the headers, with substitutions marked with '!', (e.g.,
	!desc_title!).

	Methods are provided for emitting the various parts of most types of web pages.
	
	NOTE: __init__() method is a long string of string assignments - and is declared below.
	
	"""
	def emit_head(self, page, media=True):
		"""
		Emit a head element, with (default) or w/o a media insert

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

		return(head)


	def emit_body(self, group, page, media=True):
		"""
		Emit a body element, optionally  including the media segment.
		
		Requires both a group and a page (only requires group for paths, so
		duplicating the paths in the pages may not be a bad thing)
		"""
		# replace the strings...
		body = self.body.replace('!groupURL!', group.root)
		body = body.replace('!coLabRoot!', group.coLab_root)

		if media:
			body += '<center><img src="Title.png" class="fundesc" alt="' + page.fun_title + '">'
			
			# base the name of the media insert on the page type
			media_insert = eval('self.media_insert_' + page.page_type)
			# replace the name in the older, quicktime based pages, as 
			# well as the fallback "Small" version in the html5 version..
			media_insert = media_insert.replace("!name!", page.name) 
			body += media_insert.replace("!html5-source-lines!", self.gen_html5_source(page.name, page.media_size))
			body += '</center>'

		return(body)

	def emit_tail(self,page):
		"""
		Send out the last bit of the page...
		"""
		
		# Replace tags...
		tail = self.tail.replace('!name!', page.name)
		tail = tail.replace('!fun_title!', page.fun_title)
		tail = tail.replace('!desc_title!', page.desc_title)
		if page.obj_type == "Page":
			tail = tail.replace('!page_type!', page.page_type)	# "orig" or "html5"
		return(tail)	# ...and done.

	def gen_html5_source(self, name, size):
		"""
		This script generates a number of html5 video source lines, based on the
		size.  It works its way down the list of sizes, generating the codecs
		set up.
		
		<source src="!name!-media-!media_size!.webm" type='video/webm; codecs="vp8.0, vorbis"'>
		<source src="!name!-media-!media_size!.mp4" type='video/mp4'>
		"""
		print "gen_html5_source:", name, size
		sources = '\n'
		t3 = '\t' * 3	# 3 tabs - makes the html easier to read....
		size_c = config.Sizes()
		while size != config.SMALLEST:	# Stop when we get to the smallest size...
			# add webm...  (First because Chrome will pick up the mp4 if it finds it first,
			# and it does better with webm)
			sources += t3 +'<source src="' + name + '-media-' + size + '.webm" '	# first part
			sources += """type='video/webm; codecs="vp8.0, vorbis"'>\n"""		# type=  portion
			# add mp4...
			sources += t3 + '<source src="' + name + '-media-' + size + '.mp4" '	# first part
			sources += """type='video/mp4'>\n"""	# type= portion
			# We may want to consider:
			#sources += """type='video/mp4; codecs="avc1.42E01E, mp4a.40.2"'>"""
			# Now - move down to the next size...
			size = size_c.next_size(size)
			print "Next size:", size
		return(sources)

	def __init__(self):
		#
		# the html content for the head and body sections
	
		self.head = """<!DOCTYPE html>
		    <html>
			<head><title>!fun_title!</title>
			<link rel="stylesheet" type="text/css" href="/coLab/Resources/Style_Default.css">
			<link rel="shortcut icon" href="/coLab/Resources/CoLab_Logo2D.png">
			""" 

		self.head_insert_html5 = ''
		
		self.head_insert_orig="""<script src="http://www.apple.com/library/quicktime/scripts/ac_quicktime.js" language="JavaScript" type="text/javascript"></script>
		<script src="http://www.apple.com/library/quicktime/scripts/qtp_library.js" language="JavaScript" type="text/javascript"></script>
		<link href="http://www.apple.com/library/quicktime/stylesheets/qtp_library.css" rel="StyleSheet" type="text/css" />
		"""
	
		self.media_insert_html5="""
			<center>
			<video  poster="ScreenShot.png" width="640" height="530" controls>
			<!-- The following line is replaced the full complement of html5 video
			      codecs for this page... -->
			 !html5-source-lines!
			<!--  Older - replaced by the line above...
			  <source src="!name!-media-!media_size!.webm" type='video/webm; codecs="vp8.0, vorbis"'>
			  <source src="!name!-media-!media_size!.mp4" type='video/mp4'>
			 --> 
			  <!-- Fall back for non-html5 browsers, (WinXP/IE8, e.g.) simple mp4 embed tag -->
			  <br>
			  <embed src="!name!-media-Small.mp4" autostart="false" height="500" width="640" /><br>
			  <font size=-2>
			  <i>Your browser does not support html5 - using mp4 plug-in</i>
			  </font>
			  <p>
			</video>
			</center>
		"""
		self.media_insert_orig="""
			<script type="text/javascript"><!--
					QT_WritePoster_XHTML('Click to Play', '!name!-poster.jpg',
							'!name!.mov',
							'640', '496', '',
							'controller', 'true',
							'autoplay', 'true',
							'bgcolor', 'black',
							'scale', 'aspect');
			//-->
			</script>
			<noscript>
			<object width="640" height="496" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" codebase="http://www.apple.com/qtactivex/qtplugin.cab">
					<param name="src" value="!name!-poster.jpg" />
					<param name="href" value="!name!.mov" />
					<param name="target" value="myself" />
					<param name="controller" value="false" />
					<param name="autoplay" value="false" />
					<param name="scale" value="aspect" />
					<embed width="640" height="496" type="video/quicktime" pluginspage="http://www.apple.com/quicktime/download/"
							src="!name!-poster.jpg"
							href="!name!.mov"
							target="myself"
							controller="false"
							autoplay="false"
							scale="aspect">
					</embed>
			</object>
			</noscript>
		"""
	
		self.banner = """	
			<div class="banner" > <! start of banner>
			<!center>	 
					<table width=80% border=0 cellpadding=0 class="banner_txt">
					  <td align="center" ><a href="!groupURL!/index.shtml" title="Always a nice place to go...">Home</a></td>
	
					  <td align="center" ><a href="!groupURL!/Shared/WhatsNew/index.shtml" title="The place to be, if you want to be somewhere else.">What's&nbsp;New</a></td>
					  <td align="center" ><a href="!groupURL!/Shared/Nav/index.shtml" title="How to get to where you need go.">Nav</a></td>
					  <td align="center" ><a href="!groupURL!/Shared/Archive/index.shtml" title="What have we been up to...">Archive</a></td>
					  <td align="center" ><a href="!groupURL!/Shared/Help/index.shtml" tgitle="Hopefully, the help you need.">Help</a></td>
					</tr></table>
			<!/center>
			<br>
			</div>	<! end of banner>
		"""	
	
		# substitute !coLabRoot! with that...	
		self.body = """
			</head>
			<body>
			<!--   Menu Header -->
			<div id="container" style="height: 100%; width: 100%; overflow: hidden;">
			<div class="sidebar_l">
			<!--#include virtual="!groupURL!/Shared/mostrecent.html" -->
			<p><hr><P>
			<!--#include virtual="!groupURL!/Shared/projectlist.html" -->
			</div> <! End sidebar>
			<div class="sidebar_r">
			<!--#include virtual="!groupURL!/Shared/rightbar.html" -->
			</div> <! End right sidebar>
			<div id="Logo" class="logo"><img src="/coLab/Resources/CoLab_Logo3D.png" height=50 width=50></div> <! logo>
			""" + self.banner + """	
			<div id="Content" class="main" style="height: 97%; overflow: auto "> <! middle content >
			<p>
		"""

	
	
		self.tail = """
		<hr>
		Enter your comments here:<br>
		
		<form method=POST action="/coLab/bin/postcomments.cgi">
		Your name: <input type="text" name="Commenter" ><br>
		<center>
		<input type="hidden" name="page" value="!name!">
		<input type="hidden" name="desc_title" value="!desc_title!">
		<textarea name="Text" rows=7 cols=80></textarea>
		<br>
		</center>
		<input type="submit" value="Add your comment">
		</form>
		<p><hr><p>
		<h3>Comments:</h3>
		<!--#include virtual="Comments.log" -->
		<p>
		<br>
		<center>
		&copy; Catharsis Studios West 2013
		<p>
		</center>
		<!--#include virtual="links.html" -->
		<p>&nbsp;<p>
		</td></tr></table>
		<font size=1>
		Page type: !page_type!
		</font>
		</div>	<! middle content>
		</div>	<! container >

		</center>
		</body>
		</html>
		"""

def main():
	""" test gen_html5_sources"""
	h = Html()
	source = h.gen_html5_source("ZZZZZZ", "Super-HD-Letterbox")
	print "Got source:"
	print source
if __name__ == '__main__':
	main()