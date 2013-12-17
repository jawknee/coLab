#!/usr/bin/env bash
#
# Just a simple interface to 
# run the ftp client in the background...
# 
minutes=5

if [ "$1" = "-m" ]
then
	minutes=$2
	echo "$0: Setting minutes to: $minutes"
else
	echo "$0: Defaulting minutes to: $minutes"
fi

delay=$(expr $minutes \* 60)	# sleep delay is in seconds...

while sleep $delay
do
	start=$(date +%s)
	echo Starting at: $(date)
	/usr/bin/osascript Interarchy_coLab_mirror.scpt
	echo Ending at $(date)
	end=$(date +%s)
	etime=$(expr $end - $start)
	#echo etime is $etime
	echo Elapsed Time: $(~/bin/nicetime.py $etime)
done
