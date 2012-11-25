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

	hname = "../Sites/" + name + '/' + name + ".html"

	try:
		os.system("rm -vf " + hname)
	except:
		print "rm exceptinon"


	description = """This is getting close to useful.   Here is Beach with
	the piano doubled on a rhodes, and a few other rhythmical friends.  Also,
	all five flutes are on board,   Pretty much to show what we've got, 
	get a sense of what we can do, and...
	<p>
	a chance to see if this new tool can line up nicely with screen detail.
	<p>
	I expect to have comments, and an improved user look/feel soon.
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
		""" + head_insert + "</head>"

	body = """
		<body background="../../Resources/P1Gray.png" text="black">
		<!--   Menu Header -->
		<div id="container">
		
		<div style="position: absolute; top: 4px; width: 1035; height: 50px;font-family:Georgia; background-color: #209090; background-image: ../../Resources/P1Gray.png; " >
		<center>
		<table width=80% height=40 background="../../Resources/P1CyanTex.png" cellpadding=0 border=0 ><tr><td>
		<font   size=-1>
		<center>
		        <table width=80% height=30 border=0 cellpadding=10 style="color: c0b000"><tr>
		          <td align="center">Home</td>
		          <td align="center">What's&nbsp;New</td>
		          <td align="center">Nav</td>
		          <td align="center">Help</td>
		        </tr></table>
		</center>
		</td></tr></table>
		</center>
		<br>
		</div>
		
		<div id="menu" style="width: 200px; position: absolute; top: 50; left: 20;  font-family: Helvetica;">
		<font size=-1>
		<h4>Unheard:</h4>
		<ul>
		<li>The Amazing Churango</li>
		<li>Cat Sound Symphony</li>
		</ul>
		<h4>Recently Active:</h4>
		<ul>
		<li>JDJ-V Asembly 233b</li>
		<li>The Pained Teddy Bear</li>
		<li>Where Are My Slippers?</li>
		</ul>
		<h4>Pieces You Are Following:</h4>
		<ul>
		<li>Billion Flute Parade</li>
		</ul>
		<hr>
		<h4>Projects:</h4>
		<ul>
		<li>JDJ</li>
		<li>Distant Conversation</li>
		<li>C-76 Fortieth Anniversary</li>
		</ul>
		<h4>Pieces:</h4>
		<ul>
		 <li>Must Have Been the Rain (V)
		 <li>JDJ-3
		 <li>50 Years (IV)
		 <li>Rosemary's in Bloom
		 <li>Water Moon
		 <li>JDJ-2
		 <li>JDJ-1
		</ul>
		
		<h4>Settings:</h4>
		<ul>
		 <li>Mail: On
		 <li>Remind: Off
		 <li>Follow this: No
		</ul>
		</div>
		
		<!--
		<div id="Content" style="width: 800px; float: left;">
		-->
		<div id="Content" style="position: absolute; top: 60; left: 240; backgound-image: ../../Resources/P1Black2.png;">
		<table border=0 style="color: e8e8d8 "><tr><td>
		</td></tr></table>
		
		<table background="../../Resources/P1Black2.png" width=800 cellpadding=30><tr><td>
		<font color=e8e8d8>
		<center>
		<h1 style="font-family: cursive">
	""" + fun_title + "</h1>"

	content = """
	</center>
	<p> <hr> <p>
	<font color="c0b0a0">
	<h2>""" + desc_title + """</h2>
	<font color=a0b0c0>""" + description + "<p><i>" + date + """</i><p>
	<b>Use this link to mail comments:</b> <a href="mailto:jawknee@sonic.net,mccluredc@gmail.com,jcdlansing@gmail.com?Subject=Second Turn w/DBeG">Comment Mail Link</a>
	<p>"""

	tail = """
	<p><hr>
	<div style="color: 905020; float: left; ">
	&larr;Your Groundhog's Got Gout
	</div>
	<div style="color: 905020; float: right; ">
	Why Not? &rarr;
	</div>
	<br>
	<hr><p>
	Enter your comments here:<br>
	<center>
	<form>
	<textarea rows=15 cols=80 style="background-color: b0b0b8; font-family: Georgia;">
	(doesn't work yet)
	</textarea>
	<br>
	<input type="submit">
	</form>
	</center>
	<p><hr><p>
	<h3>Comments:</h3>
	<i>Dan / 2012.11.18 4:32 AM PST</i><br>
	I like!  (tada-dada-dada)
	<p>
	<i>John / 2012.11.19 8:23 PM PST</i><br>
	I agree, well done!
	<p>
	<i>Johnny / 2012.11.19 9:44 PM PST</i><br>
	OK - I'll move forward then! Like I say, I hope to get the comments working first.   Tying all the
	other bits together - like what bits have you seen, which ones are you following (presumably to
	get mail if someone comments?) all has to be worked out.  I've recently gotten the OK to have
	shell access to my ISP...   hopefully I can do some CGI programming - and may be use SQL - I get
	to set up databases as part of my plan.  So - we'll see.  -jk
	<p><hr><p>
	</center>
	</font>
	</center>
	<div style="color: 905020; float: left; ">
	&larr;Your Groundhog's Got Gout
	</div>
	<div style="color: 905020; float: right; ">
	Why Not? &rarr;
	</div>
	<br>
	<p><hr><p>
	<center>
	&copy; Catharsis Studios West 2012
	</center>
	</td></tr></table>
	<p>
	<br>
	
	<p><hr><p>
	<center>
	&copy; Catharsis Studios West 2012
	</center>
	</td></tr></table>
	<p>
	<br>
	<hr><p>
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
	main()


