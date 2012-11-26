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
import datetime

def main():

	# These will be passed in via opt parms or otherwise...
	name = "Beach-FlChEgEtc"
	desc_title="Beach, next phase"
	fun_title="Ham and Eggs on the Beach"

	hname = "../Sites/" + name + '/' + "index.shtml"

	try:
		os.system("rm -vf " + hname)
	except:
		print "rm exceptinon"


	description = """This little tool is getting close to useful.   Here is Beach with
	the piano doubled on a rhodes, and a few other rhythmical friends.  Also,
	all five flutes are on board,   Pretty much to show what we've got, 
	get a sense of what we can do, and...
	<p>
	a chance to see if this new tool can line up nicely with screen detail.
	<p>
	It appears that I've got comments working as well - have at it.   (The 
	backend is it still just debug, It will later route back to the page.)
	<p>
	Unseen is that large sections, like the left side bar and the back and forward links,
	are including files that are easily contructed as needed.  So, it's coming along.

	"""

	date = str(datetime.datetime.now())

	try:
		outfile = open(hname, 'wb')
	except:
		print "Failure opening ", hname
		exit(1)

	#
	# the html content for the head and body sections
	head_insert="""<script src="http://www.apple.com/library/quicktime/scripts/ac_quicktime.js" language="JavaScript" type="text/javascript"></script>
	<script src="http://www.apple.com/library/quicktime/scripts/qtp_library.js" language="JavaScript" type="text/javascript"></script>
	<link href="http://www.apple.com/library/quicktime/stylesheets/qtp_library.css" rel="StyleSheet" type="text/css" />
	"""

	media_insert="""
		<script type="text/javascript"><!--
		        QT_WritePoster_XHTML('Click to Play', '<name>-poster.jpg',
		                '<name>.mov',
		                '640', '496', '',
		                'controller', 'true',
		                'autoplay', 'true',
		                'bgcolor', 'black',
		                'scale', 'aspect');
		//-->
		</script>
		<noscript>
		<object width="640" height="496" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" codebase="http://www.apple.com/qtactivex/qtplugin.cab">
		        <param name="src" value="<name>-poster.jpg" />
		        <param name="href" value="<name>.mov" />
		        <param name="target" value="myself" />
		        <param name="controller" value="false" />
		        <param name="autoplay" value="false" />
		        <param name="scale" value="aspect" />
		        <embed width="640" height="496" type="video/quicktime" pluginspage="http://www.apple.com/quicktime/download/"
		                src="<name>-poster.jpg"
		                href="<name>.mov"
		                target="myself"
		                controller="false"
		                autoplay="false"
		                scale="aspect">
		        </embed>
		</object>
		</noscript>
	"""

	head = """<html>
		<head><title>""" + fun_title + """</title>
		<link rel="stylesheet" type="text/css" href="../../Resources/Style_Default.css">
		""" + head_insert + "</head>"

	body = """
		<body>
		<!--   Menu Header -->
		<div id="container">
		
		<div class="banner" > <! start of banner>
		<center>	 
		        <table width=80% height=30 border=0 cellpadding=10 class="banner_txt">
		          <td align="center"><a href="../../index.shtml">Home</a></td>
		          <td align="center"><a href="../../Common/new.shtml">What's&nbsp;New</a></td>
		          <td align="center"><a href="../../Common/nav.shtml">Nav</a></td>
		          <td align="center"><a href="../../Help/">Help</a></td>
		        </tr></table>
		</center>
		<br>
		</div>	<! end of banner>

		<!--#include virtual="../../Common/sidebar_l.html" -->
		<div id="Logo" class="logo"><img src="../../Resources/CoLab_Logo.png"></div>

		
		<div id="Content" class="main">
		<center>
		<h1 class=fundesc>
	""" + fun_title + "</h1>"

	content = """
	<table width=640 border=0><tr><td>

	<h2 class=fundesc>""" + desc_title + """</h2>
	<font color=a0b0c0>""" + description + "<p><i>" + date + """</i><p>
	<p>"""

	CommentLog="Comments.log" 

	tail = """
	<!--#include virtual="links.html" -->
	<br>
	Enter your comments here:<br>
	<center>
	<form method=POST action="../../bin/postcomments.cgi">
	<input type="hidden" name="site" value="<site>">
	<textarea name="Text" rows=15 cols=80 style="background-color: b0b0b8; font-family: Georgia; font-size: 14pt;"></textarea>
	<br>
	</center>
	<input type="submit">
	</form>
	<p><hr><p>
	<h3>Comments:</h3>
	<!--#include virtual="Comments.log" -->
	<p>
	<!--#include virtual="links.html" -->
	<br>
	<p><hr><p>
	<center>
	&copy; Catharsis Studios West 2012
	</center>
	</td></tr></table>

	</td></tr></table>
	</div>
	</div>
	
	</center
	</body>
	</html>
	"""

	"""
		Write out the various pieces...
	"""

	write = outfile.write

	write(head)
	write(head_insert)
	write(body)
	write(media_insert.replace("<name>", name))
	write(content)
	write(tail.replace("<site>", name))

	outfile.close()
	
	exit(0)


if __name__ == "__main__":
	main()


