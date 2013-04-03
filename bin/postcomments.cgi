#!/usr/bin/env bash
#
#	Copyright Johnny Klonaris 2012
#	
source ../.coLab.conf
#eval "$(./cgi-parse.py | tee -a ../logs/var.log | ./evalfix)"

log="$coLab_home/logs/var.log"

eval "$(tee -a $log | $coLab_home/bin/cgi-parse.py |  tee -a $log | $coLab_home/bin/evalfix.py )"

#
# For now - hardcoded addresses...
export cLmail_addresses="johnny@jawknee.com, jcdlansing@gmail.com, mccluredc@gmail.com"
#export cLmail_addresses="johnny@jawknee.com" 

source ../.coLab.conf	# don't like this...

cat <<EOF
Content-type: text/html

EOF

if [ -z "$Text" ]
then
	cat <<-EOF
	<html><body>
	<h1>No Content / No Play</h1>
	You <i>MUST</i> enter a name as well as comments.   Please go 
	back and make sure you've entered something into each field, 
	<p>
	Thanks.
	<p>
	<pre>
	(some possibly useful debug info):

	$(set)
	</pre>
	</body></html>
	EOF
	exit
fi
shopt -s extglob		# our old friend, extglob (pattern matching extension, next line)
dest=${HTTP_REFERER%index.?(s)html}	# removes index.html or index.shtml
shopt -u extglob

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
<head><title>coLab Comments: $desc_title</title>
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

if  echo $dirname | grep "/SBP/" >/dev/null
then
	echo No mail.
else
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
fi

datestring=$(./isodate.py)
cat <<-EOF >>$dirname/data
updatetime="$datestring"
EOF


cat <<-EOF
<p><hr>
<p style="font-size: smaller;">
Generated/processed by $0 on $(date)</p>
</td></tr>
<tr height=20><td> &nbsp; </td></tr>
</table>
</center>
</div>
</body>
</html>
EOF


