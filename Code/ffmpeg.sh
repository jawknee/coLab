#!/usr/bin/env bash
#
# A simple shell interface to the ffmpeg program
# We validate the values found in the info file,
# passed on the command line, then build and 
# execute a command line to import and export
# in once step.
# 

set -x
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

#name=$(basename $pagedir)
cd "$pagedir"
source data

if [ -z "$soundfile" -o ! -f "$soundfile" ]
then
	echo "$0: no sound file: $soundfile"
	exit 1
fi

# and just to be safe...
# let's source the info file again.. (media_size - at least - conflicts with data)
source $infofile
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
input_opts="-y -r $fps -i $overlay_dir/Frame-%05d.png -i"

# threads - kludge this for now
if [ $generateMP3 = yes ]
then
	threads=3
else
	threads=4
fi
threads=7

# output streams...
# Webm
webm_opts="-codec:v libvpx  -crf 20 -b:v 500k  -auto-alt-ref 1 -lag-in-frames 1 -codec:a libvorbis -threads 8 -qscale:a 5 -r $fps -threads $threads $pagedir/$name-media-$media_size.webm"
mp4_opts="-codec:v libx264 -preset faster -crf 30 -movflags faststart -pix_fmt yuv420p  -threads 8 -codec:a aac -strict -2 -b:a 192k -r $fps -threads $threads $pagedir/$name-media-$media_size.mp4"

ogg_opts="-r $fps -flags:v qscale -qscale:v 1 -codec:v libtheora -codec:a libvorbis -qscale:a 6 -threads $threads $pagedir/$name-media-$media_size.ogg"

# for audio...
#mp3_opts="-codec:a libmp3lame -qscale:a 1 -metadata title=\"$desc_title\" -metadata artist=\"$group\" $name.mp3"
mp3_opts="-codec:a libmp3lame -qscale:a 1 -threads 1"

# use these to turn off one or more gnerators
#unset ogg_opts webm_opts
#unset ogg_opts 
#unset webm_opts
#unset mp4_opts
# redirect the stderr to stdout - changing carriage returns to new lines so we can read it...
cat <<-EOF
Runstring: $ffmpeg
input:	$input_opts "$soundfile"
ogg:	$ogg_opts
webm:	$webm_opts
mp4:	$mp4_opts
mp3:	$mp3_opts
EOF

if [ $generateMP3 = no ]
then
	$ffmpeg $input_opts "$soundfile"   $mp4_opts $webm_opts $mp3_opts 2>&1 | tr -u '\r' '\n'
else
	rm -f $name.mp3 >/dev/null 2>&1
	$ffmpeg $input_opts "$soundfile" $mp4_opts $webm_opts $mp3_opts \
		-id3v2_version 3  \
		-metadata title="$title" -metadata artist="$artist" \
		-metadata TIT3="$TIT3" -metadata date="$date" -metadata TDAT="$TDAT" \
		-metadata encoded_by="$encoded_by" -metadata copyright="$copyright" \
		"$name.mp3" 2>&1 | tr -u '\r' '\n'
fi

rc=$?
echo "$ffmpeg has completed with return code: $rc"
exit $rc
