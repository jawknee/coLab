#!/usr/bin/env python
"""
	To start, some time fragment that I'll need.
"""

from datetime import datetime, timedelta
from dateutil import tz

def utils():
	coLab_tz='US/Pacific'

	d=datetime.utcnow()


	print "utc: ", d.isoformat(), str(d)

	iss = d.isoformat()

	# time format -
	# ifmt is for reading/write naive (UTC) time
	# ofmt is for short output (sidebar), lfmt is long (comments)
	ifmt="%Y-%m-%dT%H:%M:%S.%f%Z"	# long - not fully supported
	ifmt="%Y-%m-%dT%H:%M:%S"
	sfmt="%b, %d, %I:%M %p %Z"
	lfmt="%Y-%m-%d %I:%M:%S %p %Z"
	print "d in", ifmt, "is", d.strftime(ifmt)
	inTime=d.strftime(ifmt)


	if iss == inTime:
		print "same"
	else:
		print "different"

	print iss, "iso"
	print inTime, "ifmt", ifmt

	nd = datetime.strptime(inTime, ifmt)

	print "Read nd as: ", nd, nd.isoformat()

	HERE = tz.tzlocal()
	UTC = tz.gettz('UTC')

	gmt = nd.replace(tzinfo=UTC)
	lt=gmt.astimezone(HERE)

	print "lt is", lt, lt.isoformat(), lt.strftime(ifmt)
	print "lt is", lt.strftime(sfmt)
	print "lt is", lt.strftime(lfmt)
	


if __name__ == "__main__":
	utils()
