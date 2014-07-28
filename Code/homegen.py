#!/usr/bin/env python

""" Create Home page for a Domain

Passed in the Domain name and create the index.shtml in that dir.

Not currently used - replaced by htmlgen.homegen
"""

import os
import sys
import logging
import datetime	
import imp	# to input the data file
import shutil

import coLabUtils

def genHome(name):

	try:
		conf=coLabUtils.get_config()
	except ImportError:
		print "Cannot find config."
		sys.exit(1)

	domains=conf.coLab_home + "/Domains"

	try:
		os.chdir(domains)
	except OSError,info:
		print "Cannot cd to ", domains, info
		print "fatal."
		sys.exit(1)

	if not os.path.isdir(name):
		try:
			os.makedirs(name)
			os.chdir(name)
		except OSError, info:
			print "Domain dir problem with name:", name,  info
			sys.exit(1)

	os.chdir(name)

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
			os.remove(index)
		except OSError, info:
			print "Error removing", index, info
			sys.exit(1)
	#
	# It's finally time to start creating that home page...

	try:
		P = imp.load_source('','data')

	except ImportError, info: 
		print "Problem importing the data... ", info
		print "Cannot continue."

	shutil.rmtree('datac', ignore_errors=True)


	try:
		for file in ("Comments.log", "links.html" ):
			f=open(file,'w+')
			f.close()
	except IOError, info:
		print "Touch problem", file, info


	try:
		outfile = open(index, 'w+')
	except IOError, info:
		print "Failure opening ", hname, info
		sys.exit(1)

	resources = conf.coLab_root + "/Resources"
	style = resources + "/Style_Default.css" 
	logo = resources + "/CoLab_Logo.png"
	head = """<html>
		<head><title>""" + P.title + """</title>
		<link rel="stylesheet" type="text/css" href=""" + '"' + style + '"' + """>
		<link rel="shortcut icon" href="""  + '"'+ logo  + '"'+ """
		</head>
		""" 

	#
	# build the string with substitution:  !coLabRoot!  ->   conf.coLab_root
	body = """
		<body>
		<!--   Menu Header -->
		<div id="container">
		
		<div class="banner" > <! start of banner>
		<!center>	 
		        <table width=80%  border=0 cellpadding=0 class="banner_txt">
		          <td align="center"><a href="!coLabRoot!/index.shtml" title="Always a nice place to go...">Home</a></td>
		          <td align="center"><a href="!coLabRoot!/Shared/new.shtml" title="The place to be, if you want to be somewhere else.">What's&nbsp;New</a></td>
		          <td align="center"><a href="!coLabRoot!/Shared/nav.shtml" title="How to get to where you need go.">Nav</a></td>
		          <td align="center"><a href="!coLabRoot!/Help/" title="Hopefully, the help you need.">Help</a></td>
		        </tr></table>
		<!/center>
		<br>
		</div>	<! end of banner>

		<!--#include virtual="!coLabRoot!/Shared/sidebar_l.html" -->
		<div id="Logo" class="logo"><img src="!coLabRoot!/Resources/CoLab_Logo.png"></div>

		
		<div id="Content" class="main">
		<center>
		<h1 class=fundesc>
	""" + P.subtitle + "</h1>"
	body = body.replace('!coLabRoot!', conf.coLab_root)

	content = """
		</center>
	<div class="maintext">

	<h2 class=fundesc>""" + P.title + """</h2>""" + P.description + "<p><i>" + P.create + """</i><p> <p>"""

	CommentLog="Comments.log" 

	tail = """
	<!--#include virtual="links.html" -->
	<br>
	Enter your comments here:<br>
	<form method=POST action="!coLabRoot!/bin/postcomments.cgi">
	Your name: <input type="text" name="Commenter" ><br>
	<center>
	<input type="hidden" name="site" value=""" + '"' + name + '"' + """>
	<input type="hidden" name="desc_title" value=""" + '"' + P.title + '"' + """>
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
	&copy; Catharsis Studios West 2013
	</center>
	</div>

	</td></tr></table>
	</div>
	</div>
	
	</center
	</body>
	</html>
	"""
	tail = tail.replace('!coLabRoot!', conf.coLab_root)

	"""
		Write out the various pieces...
	"""

	write = outfile.write

	write(head)
	write(body)
	write(content)
	write(tail)

	outfile.close()
	
	exit(0)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Usage:", sys.argv[0], "<Domain>"
		exit(1)
	name=sys.argv[1]
	genHome(name)


