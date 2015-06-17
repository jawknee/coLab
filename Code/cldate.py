#!/usr/bin/env python
""" various routines for converting, importing and displaying dates """

from datetime import datetime, timedelta
from dateutil import tz

import logging

HERE = tz.tzlocal()
UTC = tz.gettz('UTC')
IFMT="%Y-%m-%dT%H:%M:%S"
# Note both of  these SHORT formats use %-d which may not work on all formats
# (Also there is  "%-I )
SHORT_FMT="%a, %b %-d, %-I:%M %p"
SHORT_OLD_FMT="%a, %b %-d, %Y"
LONG_FMT="%Y-%m-%d %I:%M:%S %p %Z"


def format(time, format, frzone=UTC, tozone=HERE):
	""" called by next routines, returns a data string """
	orig_time=time.replace(tzinfo=frzone)
	new_time=orig_time.astimezone(tozone)
	return(new_time.strftime(format))


def utc2short(time):
	""" let's get a little tricky - if 
		older than a certain amount, don't put the
		time of day, but the year...
	"""
	CUTOFF = 86400 * 180	# Approx. six months 
	now = epochtime(utcnow())
	then = epochtime(time)
	howlong = now - then
	if howlong > CUTOFF:
		time_fmt = SHORT_OLD_FMT
	else:
		time_fmt = SHORT_FMT
	return (format (time, time_fmt, UTC, HERE))

def utc2long(time):
	return (format (time, LONG_FMT, UTC, HERE))

def string2utc(datestring):
	return(datetime.strptime(datestring,IFMT))

def utc2string(time):
	return(time.strftime(IFMT))

def epochtime(time):
	""" Total seconds since the epoch - for sorting """
	epoch = datetime.utcfromtimestamp(0)
	try:
		delta = time - epoch
	except:
		if isinstance(time, basestring):
			# we've been sent a string - not correct...
			logging.warning("String sent for a datetime's job: %s", time, exc_info=True)
			time = string2utc(time)
			delta = time - epoch
		else:
			logging.error("Passed something for time that was not a string.", exc_info=True)

	return delta.days*86400+delta.seconds

def now():
	""" Quick, easy way to get a time string """
	return (datetime.now().isoformat())

def utcnow():
	""" UTC as a datetime object """
	return (datetime.utcnow())

def main():
	""" some tests for the above... """
	
	now=datetime.utcnow()	 # naive utc time
	print "utc2short:", utc2short(now)
	print "utc2long: ", utc2long(now)
	print "epoch:    ", epochtime(now)
	s = utc2string(now)
	print "utc string", s + ' ' +  s
	then = string2utc(s)
	print "then utc  ", then
	


if __name__ == '__main__':
	main()
