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
import imp	# to input the data file
import shutil

import clutils
import cldate
from clclasses  import *

def htmlgen(group, page):
	"""
		Passed the name of the group and page, rebuilds
		the index.shtml 
	"""

	# these go a way...
	#domain_root = conf.coLab_home + "/Domains/Catharsis"
	#piece = domain_root + "/Pieces/" + name

	try:
		os.chdir(page.home)
	except OSError,info:
		print "Cannot cd to ", page.home
		print "fatal."
		sys.exit(1)


	now = cldate.now()

	index='index.shtml'
	# for now - shuffle the current one to a temp location...
	if os.path.exists(index):
		try:
			shutil.move(index, index + ".prev")
		except OSError, info:
			print "Error moving", index, index
			sys.exit(1)



	try:
		for file in ("Comments.log", "links.html" ):
			f=open(file,'w+')
			f.close()
	except IOError, info:
		print "Touch problem", file, info

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
	# Update the strings....
	media_insert.replace("<name>", page.name)

	head = """<html>
		<head><title>""" + page.fun_title + """</title>
		<link rel="stylesheet" type="text/css" href="/coLab/Resources/Style_Default.css">
		<link rel="shortcut icon" href="/coLab/Resources/CoLab_Logo.png">
		""" 

	# substitute !coLabRoot! with that...	
	body = """
		</head>
		<body>
		<!--   Menu Header -->
		<div id="container">
		
		<div class="banner" > <! start of banner>
		<!center>	 
		        <table width=80% border=0 cellpadding=0 class="banner_txt">
		          <td align="center" ><a href="!groupURL!/index.shtml" title="Always a nice place to go...">Home</a></td>

		          <td align="center" ><a href="!groupURL!/Shared/new.shtml" title="The place to be, if you want to be somewhere else.">What's&nbsp;New</a></td>
		          <td align="center" ><a href="!groupURL!/Shared/nav.shtml" title="How to get to where you need go.">Nav</a></td>
		          <td align="center" ><a href="!coLabRoot!/Help/" title="Hopefully, the help you need.">Help</a></td>
		        </tr></table>
		<!/center>
		<br>
		</div>	<! end of banner>

		<!--#include virtual="/coLab/Shared/mostrecent.html" -->
		<div id="Logo" class="logo"><img src="/coLab/Resources/CoLab_Logo.png" height=50 width=50></div>

		
		<div id="Content" class="main">
	"""

	body = body.replace('!groupURL!', group.root)
	body = body.replace('!coLabRoot!', group.coLab_root)

	content = """
		<center>
		<h1 class=fundesc>
		+ page.fun_title + "</h1>"
		</center>

	<!--#include virtual="links.html" -->
	<div class="maintext">
	<h2 class=fundesc>""" + page.desc_title + """</h2>
	<font color=a0b0c0>""" + page.description + "<p><i>" + cldate.utc2long(page.create) + """</i><p>
	<p>"""

	CommentLog="Comments.log" 

	tail = """
	<hr>
	Enter your comments here:<br>
	
	<form method=POST action="/coLab/bin/postcomments.cgi">
	Your name: <input type="text" name="Commenter" ><br>
	<center>
	<input type="hidden" name="page" value=""" + '"' + page.name + '"' + """>
	<input type="hidden" name="desc_title" value=""" + '"' + page.desc_title + '"' + """>
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
	write(media_insert.replace("<name>", page.name))
	write(content)
	write(tail)

	outfile.close()
	
	return()

def linkgen(group):
	# set up for the first and last links - cheat a bit - add a fake
	# page to the end of the list named "Archive" 
	#
	# A bit tricky...   append the list with a fake page: "Archive"
	p = Page()
	p.name = "Archive"
	p.home = os.path.join(group.coLab_root, 'Shared', 'Archive')
	group.pagelist.append(p)

	# "dummy" current entry for the home...
	currName = "Home"
	currTitle = "Home"
	currFun = group.name + " Home"
	currLink = group.root

	prevName = "not set yet"
	# step through the pages in order
	for p in group.pagelist:
		print ' '
		print 'lg:',p.name
		if p.name == 'Archive':
			nextName = 'Archive'
			nextTitle = "Archive"
			nextFun = "Archive - a place for everything"
			nextLink = p.home
		else:
			nextName = p.name
			nextTitle = p.desc_title
			nextFun = p.fun_title
			nextLink = "../" + p.name	 # yeah, I know, cheating

		print 'middle of loop lg:',p.name, 'prev', prevName, 'curr', currName, 'next', nextName
		if currName != 'Home':
			linkfile = os.path.join(currPath, 'links.html')
			print "Creating linkfile", linkfile
			try:
				l = open(linkfile, 'w+')
			except IOError, info:
				print "problem opening", linkfile, info
				raise IOError

			l.write( '<div class="links" style="float: left;">' + 
				'<a href="' + prevLink + '" title="' + prevFun +
					'">&larr; ' + prevTitle + '</a></div>' +
				'<div class="links" style="float: right;">' +
				'<a href="' + nextLink + '" title="' + nextFun +
					'">' + nextTitle + ' &rarr;</a></div>' +
				'<br>' )

				
			l.close()
			

		prevName = currName
		prevTitle = currTitle
		prevFun = currFun
		prevLink = currLink

		currPath = p.home
		currName = nextName
		currTitle = nextTitle
		currFun = nextFun
		currLink = nextLink
		print 'end of loop lg:',p.name, 'prev', prevName, 'curr', currName, 'next', nextName

	group.pagelist.pop()

				
if __name__ == "__main__":

	if len(sys.argv) < 2:
		print "Usage:", sys.argv[0], "page name"
		exit(1)

	name=sys.argv[1]

	htmlgen('Catharsis', name)


