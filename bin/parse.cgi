#!/usr/bin/env bash
#
#	Copyright Johnny Klonaris 2012
#	
eval "$(./cgi-parse | tee ../logs/var.log | ./evalfix)"

cat <<EOF
Content-type: text/html

EOF

logfile="../Sites/Test/Commentlog"
cat <<-EOF >>$logfile
<hr width=50%>
$(date)<br>
$Text
EOF

cat <<EOF
<html>
<head><title>form process</title></head>
<body bgcolor=405060 text=a0b0c0>

<h2>Log Posting...</h3>

Here's the result of your text entry (at the <a href="#bottom">bottom</a>.
<pre style="background-color: 304050; font-family: Georgia;">
$(cat $logfile)
</pre>
<a name=bottom>
<p><hr><p>
Looks like it's working...
<pre>
Env:

$(set)
</pre>
EOF
date
