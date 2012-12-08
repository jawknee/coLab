#!/usr/bin/env python
"""
	various routines for converting, importing and displaying dates

"""
from datetime import datetime, timedelta
from dateutil import tz

HERE = tz.tzlocal()
UTC = tz.gettz('UTC')
IFMT="%Y-%m-%dT%H:%M:%S"
SHORT_FMT="%b, %d, %I:%M %p %Z"
LONG_FMT="%Y-%m-%d %I:%M:%S %p %Z"


def format(time, format, frzone, tozone):

	"""
	convewt naive time from/to the passed time zones,
	and return as a formatted string
	"""
	orig_time=time.replace(tzinfo=frzone)
	new_time=orig_time.astimezone(tozone)
	return(new_time.strftime(format))


def utc2short(time):
	return (format (time, SHORT_FMT, UTC, HERE))

def utc2long(time):
	return (format (time, LONG_FMT, UTC, HERE))

def string2utc(datestring):
	return(datetime.strptime(datestring,IFMT))

def utc2string(time):
	return(time.strftime(IFMT))

def epochtime(time):
	"""
	Total seconds since the epoch - for sorting
	"""
	epoch = datetime.utcfromtimestamp(0)
	delta = time - epoch
	return delta.days*86400+delta.seconds

def main():
	
	now=datetime.utcnow()	 # naive utc time
	print "utc2short:", utc2short(now)
	print "utc2long: ", utc2long(now)
	print "epoch:    ", epochtime(now)
	s = utc2string(now)
	print "utc string", s
	then = string2utc(s)
	print "then utc  ", then
	


if __name__ == '__main__':
	main()
