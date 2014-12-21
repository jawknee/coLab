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

#name=$(basename $pagedir)
cd "$pagedir"
source data

if [ -z "$soundfile" -o ! -f "$soundfile" ]
then
	echo "$0: no sound file: $soundfile"
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
input_opts="-y -r $fps -i $overlay_dir/Frame-%05d.png -i"

# output streams...
threads=auto	
# Webm
webm_opts="-codec:v libvpx  -crf 20 -b:v 500k  -auto-alt-ref 1 -lag-in-frames 1 -codec:a libvorbis -threads 8 -qscale:a 5 -r $fps $pagedir/$name-media-$media_size.webm"
mp4_opts="-codec:v libx264 -preset faster -crf 30 -movflags faststart -pix_fmt yuv420p  -threads 8 -codec:a aac -strict -2 -b:a 192k -r $fps  $pagedir/$name-media-$media_size.mp4"

ogg_opts="-r $fps -flags:v qscale -qscale:v 1 -codec:v libtheora -codec:a libvorbis -qscale:a 6 -threads $threads $pagedir/$name-media-$media_size.ogg"

# for audio...
#mp3_opts="-codec:a libmp3lame -qscale:a 1 -metadata title=\"$desc_title\" -metadata artist=\"$group\" $name.mp3"
mp3_opts="-codec:a libmp3lame -qscale:a 1"

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
		-metadata title="$title" -metadata artist="$artist" \
		-metadata TIT3="$TIT3" -metadata date="$date" \
		-metadata encoded_by="$encoded_by" -metadata copyright="$copyright" \
		"$name.mp3" 2>&1 | tr -u '\r' '\n'
fi

rc=$?
echo "$ffmpeg has completed with return code: $rc"
exit $rc



# earlier attempts
#ogg_opts="-r $fps -flags:v qscale -global_quality:v "10*QP2LAMBDA" -codec:v libtheora -s 640x480 -acodec libvorbis -b:a 320k -threads 2 $pagedir/$name-media-$media_size.ogg"
#mp4_opts="-codec:v libx264 -preset faster -tune stillimage -crf 30 -movflags faststart -pix_fmt yuv420p -threads 2 -codec:a aac -strict -2 -b:a 192k -r $fps $pagedir/$name-media-$media_size.mp4"
#mp4_opts="-codec:v libx264 -profile:v baseline -movflags faststart -pix_fmt yuv420p -threads 3 -codec:a aac -strict -2 -r $fps $pagedir/$name-media-$media_size.mp4"
#webm_opts="-codec:v libvpx  -crf 30 -b:v 500k -codec:a libvorbis -qscale:a 5 -threads 3 -r $fps $pagedir/$name-media-$media_size.webm"
#webm_opts="-codec:v libvpx  -crf 30 -b:v 900k -auto-alt-ref 1 -lag-in-frames 4 -codec:a libvorbis -qscale:a 5 -threads 3 -r $fps $pagedir/$name-media-$media_size.webm"
#webm_opts="-codec:v libvpx  -b:v 500k -codec:a libvorbis -qscale:a 5 -threads 3 -r $fps $pagedir/$name-media-$media_size.webm"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline -preset slow -movflags faststart -pix_fmt yuv420p -threads 3 -codec:a aac -strict -2 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline -level 3 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -s 640x480 -codec:v libx264 -profile:v baseline -level 3 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v h264 -codec:a aac -strict -2 -pix_fmt yuv420p $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline -preset slow -crf 22 -pix_fmt yuv420p -threads 2 -codec:a aac -strict -2 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -vcodec h264 -acodec aac -strict -2 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -b:v 1500k -preset slow -profile:v baseline -vcodec libx264 -g 30 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -b 1500k -vcodec libx264 -vpre slow -vpre baseline -g 30 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -i %1 -b 1500k -vcodec libx264 -vpre slow -vpre baseline g 30 -s 640x480 $pagedir/$name-media.mp4"	
#mp4_opts="-r $fps -codec:v libx264 -b:v 1500k -vpre slow -vpre baseline -g 30 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline  -movflags faststart -pix_fmt yuv420p -threads 2 -codec:a aac -strict -2 $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v mpeg4  -strict -2  -b:a 320k $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v mpeg4 -preset slow -crf 22 -strict -2  -b:a 320k $pagedir/$name-media.mp4"
#mp4_opts="-r $fps -codec:v libx264 -profile:v baseline -preset slow -crf 22 -codec:a aac -strict -2 $pagedir/$name-media.mp4"
#ogg_opts="-r $fps -flags:v qscale -global_quality:v "10*QP2LAMBDA" -codec:v libtheora -s 640x480 -acodec libvorbis -b:a 320k $pagedir/$name-media.ogg"
#webm_opts="-codec:v libvpx  -b:v 500k -codec:a libvorbis -qscale:a 5 -threads 3 $pagedir/$name-media.webm"
#webm_opts="-strict -2 $pagedir/$name-media.webm"
#webm_opts="-r 1 -codec:v libvpx  -b:v 500k -codec:a libvorbis -qscale:a 5  $pagedir/$name-media.webm"
# mp4
#webm_opts="-r $fps -acodec libvorbis -b:a 320k $pagedir/$name-media.webm"
#
# Ogg / theora
#ogg_opts="-codec:v libtheora -qscale:v 3 -codec:a libvorbis -qscale:a 5 $pagedir/$name-media.ogg"
#ogg_opts="-r 1  -codec:v libtheora -s 640x480 -qscale:v 5 -codec:a libvorbis -qscale:a 5 $pagedir/$name-media.ogg"
