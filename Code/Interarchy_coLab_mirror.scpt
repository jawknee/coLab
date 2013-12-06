#!/usr/bin/osascript
tell application "Interarchy"
	activate
	with timeout of 14400 seconds
		mirror «data fss 9CFF10EA1C0005636F4C616240010000BC40A8020483A80200566500000000000083A802530B000008A7FFBF57781D00CCA6FFBF000000005446725070A8FFBF50B3FFBF40B2» host "ftp.sonic.net" path "/home/j/jawknee/public_html/coLab" user "jawknee" protocol FTPProtocol without dryrun
	end timeout
end tell
