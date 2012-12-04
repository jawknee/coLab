#!/usr/bin/env bash
#
#	Copyright Johnny Klonaris 2012
#	
#eval "$(./cgi-parse.py | tee -a ../logs/var.log | ./evalfix)"
eval "$(tee -a ~/dev/coLab/logs/var.log | ./cgi-parse |  tee -a ~/dev/coLab/logs/logs/var.log | ./evalfix.py )"

#
# For now - hardcoded addresses...
export cLmail_addresses="johnny@jawknee.com, jcdlansing@gmail.com, mccluredc@gmail.com"
export cLmail_addresses="johnny@jawknee.com" 

source ../.coLab.conf	# don't like this...



cat <<EOF
Content-type: text/html

EOF

if [ -z "$Text" ]
then
	cat <<-EOF
	<html><body>
	<h1>No Content / No Play</h1>
	</body></html>
	EOF
	exit
fi

dest=${HTTP_REFERER%index.html}
dirname=$coLab_home/${dest#$coLab_url_head}
logfile="$dirname/Comments.log"

if [ -z "$Commenter" ]
then
	Commenter="Some Anonymous Entity"
fi

cat <<-EOF >>$logfile
<hr width=25% align=left>
<i>$(date) - $Commenter</i><br>
$Text
EOF

cat <<EOF
<html>
<head><title>form process</title>
<!meta HTTP-EQUIV="REFRESH" content="5;URL="$HTTP_REFERER/index.shtml">
<link rel="stylesheet" type="text/css" href="../Resources/Style_Default.css">
</head>
<body>
<div class="main">
<center>
<table width=640 border=0>
<tr height=20><td> &nbsp; </td></tr>
<tr><td>
EOF
#
# At this point the web page is ready for the content.  We also want to mail that content
# so we put it all into vars, post the content to the and mail it to list.
export cLmail_subject="New: $desc_title Comment"
# hardcoded for now - header should move to .coLab.conf

export cLmail_bodytext=$(cat <<-EOF
	<h2>New Comment on $desc_title</h2>
	At $(date),<br>
	$Commenter commented on 
	<a href="$HTTP_REFERER">$desc_title</a>:<P>

	$Text
	<p><hr><p>
	<h3>The full set of comments:</h3>
	$(cat $logfile)
	<p><hr><p>
	<a href="$HTTP_REFERER">&larr; Back to the $desc_title page.</a>
	<p>
	EOF
	)

cat <<-EOF 
$cLmail_bodytext
<pre>

EOF
#
# the necessary vars should be set/exported - let's just call the mailer...
$coLab_home/bin/coLabMailer 2>&1
rc=$?
if [ $rc = 0 ]
then
	echo "Mail sent."
else
	echo "Problem sending mail."
fi

cat <<-EOF 
<!--
<pre>
$(set)
</pre>
-->
<p><hr>
<p style="font-size: smaller;">
Generated/processed by $0 on $(date)
</td></tr>
<tr height=20><td> &nbsp; </td></tr>
</table>
</center>
</div>
</body>
</html>
EOF
