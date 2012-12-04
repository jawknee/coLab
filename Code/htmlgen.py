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
import shutil
import coLabUtils

def htmlgen(name):



	try:
		conf=coLabUtils.get_config()
	except ImportError:
		print "Cannot find config."
		sys.exit(1)

	domain_root = conf.coLab_home + "/Domains/Catharsis"
	piece = domain_root + "/Pieces/" + name

	try:
		os.chdir(piece)
	except OSError,info:
		print "Cannot cd to ", piece, info
		print "fatal."
		sys.exit(1)


	date = str(datetime.datetime.now())

	if os.path.exists('data'):
		print "Found data file"
	else:
		src=conf.coLab_home + "/Resources/domain_home_data.template"
		try:
			shutil.copy(src, 'data')
			f=open('data','a')
			dates="""\ncreate=\"""" + date + """\"\nupdate=\"""" + date + """\"\n"""
			f.write(dates)
			f.close
		except OSError, info:
			print "Failed to create data file", info
			sys.exit(1)
		print "Created new data file"

	index='index.shtml'
	if os.path.exists(index):
		try:
			shutil.move(index, index + ".prev")
		except OSError, info:
			print "Error moving", index, index
			sys.exit(1)


	try:
		P = imp.load_source('','data')

	except: 
		print "Problem importing the data... ", sys.exc_info()[0]
		print "Cannot continue."
		os.system("/bin/pwd")
		os.system("cat data")
		exit(1)


	os.system("rm -f datac c")	# consequece of the import...

	try:
		for file in ("Comments.log", "links.html" ):
			f=open(file,'w+')
			f.close()
	except IOError, info:
		print "Touch problem", file, info



	date = str(datetime.datetime.now())

	try:
		outfile = open(index, 'w+')
	except IOError, info:
		print "Failure opening ", index, info
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
		<link rel="stylesheet" type="text/css" href="/coLab/Resources/Style_Default.css">
		<link rel="shortcut icon" href="/coLab/Resources/CoLab_Logo.png">
		""" + head_insert + "</head>"

	# substitute !coLabRoot! with that...	
	body = """
		<body>
		<!--   Menu Header -->
		<div id="container">
		
		<div class="banner" > <! start of banner>
		<!center>	 
		        <table width=80% border=0 cellpadding=0 class="banner_txt">
		          <td align="center" ><a href="!coLabRoot!/index.shtml" title="Always a nice place to go...">Home</a></td>
		          <td align="center" ><a href="!coLabRoot!/Shared/new.shtml" title="The place to be, if you want to be somewhere else.">What's&nbsp;New</a></td>
		          <td align="center" ><a href="!coLabRoot!/Shared/nav.shtml" title="How to get to where you need go.">Nav</a></td>
		          <td align="center" ><a href="!coLabRoot!/Help/" title="Hopefully, the help you need.">Help</a></td>
		        </tr></table>
		<!/center>
		<br>
		</div>	<! end of banner>

		<!--#include virtual="/coLab/Shared/oldsidebar_l.html" -->
		<div id="Logo" class="logo"><img src="/coLab/Resources/CoLab_Logo.png" height=50 width=50></div>

		
		<div id="Content" class="main">
		<center>
		<h1 class=fundesc>
	""" + P.fun_title + "</h1>"

	body = body.replace('!coLabRoot!', conf.coLab_root)

	content = """
		</center>

	<!--#include virtual="links.html" -->
	<div class="maintext">
	<h2 class=fundesc>""" + P.desc_title + """</h2>
	<font color=a0b0c0>""" + P.description + "<p><i>" + P.create + """</i><p>
	<p>"""

	CommentLog="Comments.log" 

	tail = """
	<hr>
	Enter your comments here:<br>
	
	<form method=POST action="/coLab/bin/postcomments.cgi">
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
	<br>
	<center>
	&copy; Catharsis Studios West 2012
	<p>
	</center>
	</div>
	<!--#include virtual="links.html" -->
	<p>&nbsp;<p>
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


