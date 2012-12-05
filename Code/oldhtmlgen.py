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
import datetime
import imp	# to input the data file

def htmlgen(name):

	# These will be passed in via opt parms or otherwise...

	sitedir = "../Sites/" + name
	hname = "index.shtml"


	try:
		os.chdir(sitedir)
	except OSError, info:
		print "Could not cd to $sitedir", info
		exit(1)

	try:
		os.system("rm -vf " + hname)
	except:
		print "rm exception"

	try:
		f = open("data")
	except:
		print "Could not open data file: data - ", sys.exc_info()[0]
		exit(1)

	try:
		P = imp.load_source('','data')

	except: 
		print "Problem importing the data... ", sys.exc_info()[0]
		print "Cannot continue."
		os.system("/bin/pwd")
		os.system("cat data")
		exit(1)

	f.close

	os.system("rm -f c")	# consequece of the import...


	try:
		os.system("touch Comments.log")
		os.system("touch links.html")
		os.system("rm -vf " + hname)
	except:
		print "touch/rm Problem - continuing."

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
		<head><title>""" + P.fun_title + """</title>
		<link rel="stylesheet" type="text/css" href="../../Resources/Style_Default.css">
		<link rel="shortcut icon" href="../../Resources/CoLab_Logo.png">
		""" + head_insert + "</head>"

	body = """
		<body>
		<!--   Menu Header -->
		<div id="container">
		
		<div class="banner" > <! start of banner>
		<center>	 
		        <table width=80% height=30 border=0 cellpadding=10 class="banner_txt">
		          <td align="center"><a href="../../index.shtml" title="Always a nice place to go...">Home</a></td>
		          <td align="center"><a href="../../Shared/new.shtml" title="The place to be, if you want to be somewhere else.">What's&nbsp;New</a></td>
		          <td align="center"><a href="../../Shared/nav.shtml" title="How to get to where you need go.">Nav</a></td>
		          <td align="center"><a href="../../Help/" title="Hopefully, the help you need.">Help</a></td>
		        </tr></table>
		</center>
		<br>
		</div>	<! end of banner>

		<!--#include virtual="../../Shared/oldsidebar_l.html" -->
		<div id="Logo" class="logo"><img src="../../Resources/CoLab_Logo.png"></div>

		
		<div id="Content" class="main">
		<center>
		<h1 class=fundesc>
	""" + P.fun_title + "</h1>"

	content = """
		</center>
	<div class="maintext">

	<h2 class=fundesc>""" + P.desc_title + """</h2>
	<font color=a0b0c0>""" + P.description + "<p><i>" + P.create + """</i><p>
	<p>"""

	CommentLog="Comments.log" 

	tail = """
	<!--#include virtual="links.html" -->
	<br>
	Enter your comments here:<br>
	<form method=POST action="../../bin/oldpostcomments.cgi">
	Your name: <input type="text" name="Commenter" ><br>
	<center>
	<input type="hidden" name="site" value=""" + '"' + name + '"' + """>
	<input type="hidden" name="desc_title" value=""" + '"' + P.desc_title + '"' + """>
	<textarea name="Text" rows=15 cols=80></textarea>
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
	<center>
	&copy; Catharsis Studios West 2012
	</center>
	</div>

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
	write(tail)

	outfile.close()
	
	exit(0)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage:", sys.argv[0], "<Sitename>"
		exit(1)
	name=sys.argv[1]
	htmlgen(name)


