#!/usr/bin/env python
"""
	convert existing PST dates into UTC
"""

import imp
from datetime import datetime, timedelta
from dateutil import tz

IFMT="%Y-%m-%dT%H:%M:%S"

do not run any more - one time only.

for ref.


def convertTime(name, time, fromzone, tozone):
	"""
	output the time in an ISO 8601 style - to the second
	"""

	local = time.replace(tzinfo=fromzone)	# set to local tme...
	gmt = local.astimezone(tozone)		# convert to UTC/GMT

	string = name + '="' + gmt.strftime(IFMT) + '"\n'

	print string,

	f=open('data','a')
	f.write(string)
	f.close




def main():


	try:
		d = imp.load_source('','data')
	except:
		print "failed import"
		sys.exit(1)

	print "create date is", d.create
	IN_FORMAT="%Y-%m-%d %H:%M:%S"


	HERE = tz.tzlocal()
	UTC = tz.gettz('UTC')


	createtime=datetime.strptime(d.create, IN_FORMAT)
	print "Createtime is", createtime
	convertTime('create', createtime, HERE, UTC)

	updatetime=datetime.strptime(d.update, IN_FORMAT)
	print "updatetime is", updatetime
	convertTime('update', updatetime, HERE, UTC)





if __name__ == "__main__":
	main()
