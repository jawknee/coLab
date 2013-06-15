#!/usr/bin/env bash

infofile="$1"

if [ ! -r "$infofile" ]
then
	echo "$0: No info file: $infofile"
	exit 1
fi

source $infofile
if [ ! -d "$pagedir" ]
then
	echo "$0: pagedir is not a directory: $pagedir"
	exit 1
fi
name=$(basename $pagedir)

if [ -z "$soundfile" -o ! -f "$pagedir/$soundfile" ]
then
	echo "$0: no sound file: $pagedir/$soundfile"
	exit 1
fi

#
if [ -z "$fps" ]
then
	echo "$0: fps is not set."
	exit 1
fi

/usr/bin/osascript <<-EOF
tell application "QuickTime Player 7"
       activate
       close every window
       #set frontWindow to window 1
       open "$pagedir/$soundfile"
       select all
       copy movie (name of window 1)
       close movie (name of window 1)
       delay .5

       open image sequence "$pagedir/coLab_local/Overlays/Frame-00001.png" frames per second $fps

       add movie (name of window 1)
       rewind movie (name of window 1)

       set myfile to "$pagedir/$name-desktop.m4v"
       set mysettings to "/User/Johnny/coLab/Code/QTmovie-mp4.settings"

       display dialog myfile 

       #set filepath to POSIX path of myfile

       export movie (name of window 1) to myfile as QuickTime movie using settings mysettings replacing true

end tell
EOF
