#!/usr/bin/env bash
#
# Schedule Photoshop Elements against the passed file...
file=$1
if [ ! -f "$file" ]
then
	echo "$0: Cannot find passed file: $file" >&2
	exit 1
fi
#
# Now cat the rest of this into applescript...
/usr/bin/osascript <<-EOF
tell application "Adobe Photoshop Elements"
	activate
	open  file "$file"
end tell
EOF
