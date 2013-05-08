#!/usr/bin/env sh
#
# rebuild the menu and link files...
# Temporary - need to move this to Python and/or PHP
#

home=~/dev/coLab

if ! cd $home
then
	echo "$0: cannot cd to $home"
	exit 1
fi

source ./.coLab.conf


#
# For now we just build the left menu
#
leftside="$home/Shared/sidebar_l.html"

if  ! touch $leftside 
then
	echo "$0: cannot access file: $leftside" >&2
	exit 1
fi

echo "$0: Updating $leftside"

cat <<-EOF >$leftside
<!--
	Shared left side bar, generated by $0 on $(date)
-->

<div class="sidebar_l">
<h4>Recent Updates</h4>
<ul>
EOF

domain_home="$home/Domains/Catharsis"
piecelist="$domain_home/Pieces/Piece.List"
if  [ ! -f  "$piecelist" ] 
then
	echo "$0: cannot access file: $piecelist" >&2
	exit 1
fi

domain_head="$coLab_root/Domains/Catharsis"
piece_dir="$domain_head/Pieces"
#
# return the 'n' most recent (non-comment) lines - last n lines
# in the file, in reverse order (or not)
n=10
recentlist=$(grep -v "^#" $piecelist | tail -n $n  ) 	# use -r to reverse to newest first..
for piece in $recentlist
do
	data="$domain_home/Pieces/$piece/data"
	if [ ! -f "$data" ]
	then
		echo "$0: Warning: no such file: $data"
		desc_title="$site"
	else
		source $data
	fi

	if [ -z "$fun_title" ]
	then
		fun_title="$desc_title"
	fi

	if [ -z "$create" ]
	then
		create="(unknown)"
	fi

	if [ -z "$update" ]
	then
		update="$create"
	fi
	#
	# Now we should be ready to emit a list item link...
	cat <<-EOF >>$leftside
	<li><a href="$piece_dir/$piece/" title="$fun_title">$desc_title</a><br><i>$update</i></li>
	EOF

done
cat <<-EOF >>$leftside
</li>

EOF

cat <<-EOF >>$leftside
(new)
</div>
EOF
#
# Now we rebuild each of the link files - this can be smarter in the future...
cd $home/Domains/Catharsis/Pieces
currName="Home"
currTitle="Home"
currFun="Home"
currLink="$coLab_root/Domains/Catharsis/index.shtml"


for site in $(grep -v "^#" Piece.List) Archive
do
	if [ "$site" = Archive ]
	then
		nextLink="$coLab_root/Shared/Archive.shtml"
		nextTitle="Archive"
		nextFun="Archive"
	else
		source $site/data
	
		nextName="$site"
		nextTitle="$desc_title"
		nextFun="$fun_title"
		nextLink="../$site/"
	fi
	
	if [ "$currName" != Home ]
	then	# generate the new html file
		link="$currName/links.html"
		echo Creating $link
		cat <<-EOF >$link
		<!p><!hr>
		<div class="links" style="float: left;">
		<a href="$prevLink" title="$prevFun">&larr; $prevTitle</a>
		</div>
		<div class="links" style="float: right;">
		<a href="$nextLink" title="$nextFun">$nextTitle &rarr;</a>
		</div>
		<br>
		<!hr><!p>
		EOF
	fi
	
	prevName="$currName"
	prevTitle="$currTitle"
	prevFun="$currFun"
	prevLink="$currLink"

	currName="$nextName"
	currTitle="$nextTitle"
	currFun="$nextFun"
	currLink="$nextLink"

done