#!/usr/bin/env python
"""
	Raw html clumps that are used in various places...

"""
class Html:
	"""
	An html object contains the headers, with substitutions marked with '!', (e.g.,
	!desc_title!).

	Methods are provided for emitting the various parts of most types of web pages.
	"""
	def emit_head(self, page, media=True):
		"""
		Emit a head element, with (default) or w/o a media insert

		Does not close out the head (emit_body does)
		"""

		# Build the web page as we go...
		head = self.head.replace("!fun_title!", page.fun_title)
		head = head.replace("!desc_title!", page.desc_title)


		if media:
			head = head + self.head_insert

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
			body += self.media_insert.replace("!name!", page.name) + '</center>'

		return(body)

	def emit_tail(self,page):
		tail = self.tail.replace('!name!', page.name)
		tail = tail.replace('!fun_title!', page.fun_title)
		tail = tail.replace('!desc_title!', page.desc_title)
		return(tail)


	def __init__(self):
		#
		# the html content for the head and body sections
	
		self.head = """<html>
			<head><title>!fun_title!</title>
			<link rel="stylesheet" type="text/css" href="/coLab/Resources/Style_Default.css">
			<link rel="shortcut icon" href="/coLab/Resources/CoLab_Logo2D.png">
			""" 

		self.head_insert = ''
		
		self.old_head_insert="""<script src="http://www.apple.com/library/quicktime/scripts/ac_quicktime.js" language="JavaScript" type="text/javascript"></script>
		<script src="http://www.apple.com/library/quicktime/scripts/qtp_library.js" language="JavaScript" type="text/javascript"></script>
		<link href="http://www.apple.com/library/quicktime/stylesheets/qtp_library.css" rel="StyleSheet" type="text/css" />
		"""
	
		self.media_insert="""
			<center>
			<video  poster="ScreenShot.png" width="640" height="530" controls>
			  <source src="!name!-desktop.mp4
			  " type='video/mp4; codecs="avc1.42e01e, mp4a.40.2"'>
			  <!source src="!name!-desktop.oggtheora.ogg" type='video/ogg; codecs="theora, vorbis"'>
			  <p>
			  Oops something went wrong...
			  <br> Most likely your browser does not support html5
			  <p>
			</video>
			</center>
		"""
		self.old_media_insert="""
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
		</div>	<! middle content>
		</div>	<! container >

		</center>
		</body>
		</html>
		"""
	
