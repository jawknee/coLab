#!/usr/bin/env bash
#
#	Copyright Johnny Klonaris 2012
#	
source ../.coLab.conf
#eval "$(./cgi-parse.py | tee -a ../logs/var.log | ./evalfix)"

ulog="$coLab_home/logs/uri.log"		# what is passed in...
vlog="$coLab_home/logs/var.log"		# what is processed...
elog="$coLab_home/logs/eval.log"		# what is processed...

eval "$(tee $ulog | $coLab_home/bin/cgi-parse.py |  tee -a $vlog | $coLab_home/bin/evalfix.py | tee $elog )"


source ../.coLab.conf	# don't like this...

cat <<EOF
Content-type: text/html

EOF

if [ -z "$Text" ]
then
	cat <<-EOF
	<html><body>
	<h1>No Content / No Play</h1>
	You <i>MUST</i> at least enter comments (didn't get anything here). 
	<p>
	(Variable: "Text")
	<p>
	This is an uncharacterized bug at this point and intermittent.
	If you think of anything unusual about you entered the comments,
	please let me know.
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
#   Convert any html &#xxx; characters...
text_title=$(echo $desc_title | $coLab_home/bin/html_decode.py)
export cLmail_subject="New: $text_title Comment"
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

# oh - this is a bit ugly....
group=$(basename $(dirname $(dirname $dirname)))

#
# For now - hardcoded addresses...
case $group in
Catharsis)
	export cLmail_addresses="johnny@jawknee.com, jcdlansing@gmail.com, mccluredc@gmail.com"
	#export cLmail_addresses="johnny@jawknee.com" 
	;;
SBP)
	export cLmail_addresses="johnny@jawknee.com"
	;;
Johnny)
	export cLmail_addresses="johnny@jawknee.com"
	;;
*)
	cLmail_bodytext="$cLmail_bodytext NOTE: group is $group and dirname is $dirname"
	export cLmail_addresses="johnny@jawknee.com"
	
esac

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


