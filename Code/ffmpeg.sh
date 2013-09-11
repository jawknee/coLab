#!/usr/bin/env bash
#
# A simple shell interface to the ffmpeg program
# We validate the values found in the info file,
# passed on the command line, then build and 
# execute a command line to import and export
# in once step.
# 

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

overlay_dir=$pagedir/coLab_local/Overlays

#
# Build the runstring...
# 
# command:
ffmpeg=/usr/local/bin/ffmpeg
#
# input of image sequence...
input_opts="-y -r $fps -i $overlay_dir/Frame-%05d.png -i $pagedir/$soundfile"

# output streams...
#
# Ogg / theora
ogg_opts="-r $fps  -codec:v libtheora -s 640x480 -qscale:v 5 -codec:a libvorbis -qscale:a 5 $pagedir/$name-media.ogg"
# Webm
webm_opts="-r $fps -codec:v libvpx  -b:v 500k -codec:a libvorbis -qscale:a 5  $pagedir/$name-media.webm"
webm_opts="-r $fps -codec:v libvpx -crf 10 -b:v 500k -codec:a libvorbis -qscale:a 5  $pagedir/$name-media.webm"
# mp4
mp4_opts="-r $fps -codec:v libx264 -profile:v baseline -pix_fmt yuv420p -threads 2 -codec:a aac -strict -2  $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline -preset slow -crf 22 -pix_fmt yuv420p -threads 2 -codec:a aac -strict -2 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -vcodec h264 -acodec aac -strict -2 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -b:v 1500k -preset slow -profile:v baseline -vcodec libx264 -g 30 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -b 1500k -vcodec libx264 -vpre slow -vpre baseline -g 30 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -i %1 -b 1500k -vcodec libx264 -vpre slow -vpre baseline g 30 -s 640x480 $pagedir/$name-media.mp4"	
#mp4_opts="-r $fps -codec:v libx264 -b:v 1500k -vpre slow -vpre baseline -g 30 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline -preset slow -movflags faststart -pix_fmt yuv420p -threads 2 -codec:a aac -strict -2 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline  -movflags faststart -pix_fmt yuv420p -threads 2 -codec:a aac -strict -2 $pagedir/$name-media.mp4"

# redirect the stderr to stdout - changing carriage returns to new lines so we can read it...
$ffmpeg $input_opts $ogg_opts $webm_opts $mp4_opts 2>&1 | tr -u '\r' '\n'

# earlier attempts
#mp4_opts="-r $fps -codec:v mpeg4  -strict -2  -b:a 320k $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v mpeg4 -preset slow -crf 22 -strict -2  -b:a 320k $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline -preset slow -crf 22 -codec:a aac -strict -2 $pagedir/$name-media.mp4"
#ogg_opts="-r $fps -flags:v qscale -global_quality:v "10*QP2LAMBDA" -codec:v libtheora -s 640x480 -acodec libvorbis -b:a 320k $pagedir/$name-media.ogg"
#webm_opts="-r $fps -acodec libvorbis -b:a 320k $pagedir/$name-media.webm"
