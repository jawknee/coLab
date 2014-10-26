#!/usr/bin/env python
""" locTagger - at coLab <span> tags to text

	reads through the passed file name or stdin
	(or pass string to locTagger.loctagger() )
	and adds a LocMarker or TimeMarker class
	span tag to wrap the matching string.

	Tries to be smart about not retagging 
	text that may have already been tagged
	or other anomalies.

	Does not checking on the time beyond
	a natural limit of 9:59:59.999_ fromt
	the pattern matching or locators beyond
	#99 (both easily changed).  

	Range/validity checking is done by the
	javascript at page load time.

"""
import sys
import re
import logging

def loctagger(string):
	""" tag matching time and location strings.

	The bulk of this is the time matching regular expression. 
	It's built in pieces below to try to document it as
	we go.
	"""

	# build a regexp
	# Hours also matches minutes because in that case, 
	# both minute digits are required
	hrs = "([0-9]:[0-5][0-9])"	# optional hours string (plus mins)
	# minutes: one or two digits
	mins = "(([0-5])?[0-9])"	# optional minutes string
	secs = "(:([0-5][0-9]))"	# required seconds string
	frac = r"(\.[0-9]*)?" 		# optional fraction

	# one of either of the hours (+mins) or minutes string,
	# required seconds, and optional fraction
	time_regexp =  '(' +  hrs + '|' + mins + ')?' + secs + frac 
	loc_regexp = r'(\#[0-9][0-9]?)'		# locator just '#' and 1-2 digits
	regexp = r'(' + time_regexp + '|' + loc_regexp + ')'	# combined..

	index = 0
	while index < len(string):
		logging.info("searching: %s", string[index:])
		searchObj = re.search(regexp, string[index:])	# find the next match...
		if searchObj:
			s = searchObj.group()	
			logging.info("Found: %s <--------", s)
			index += string[index:].find(s) 	# move index to start of the match

			# some sanity checks...
			# are the prev or trailing characters something we don't want?
			# (tags ('<>'), digits, quote, colon...
			l = len(s)
			# reject some cases where there may already be a tag, or a partial match against a 
			# bad string (e.g., 11:22:33 - would match 11:22 - not right - 11 hours is too long)
			prevChar = string[index-1]
			if prevChar.isdigit() or '>:"'.find(prevChar) != -1:
				logging.info("skipping: %s", prevChar)
				index += l
				continue
			trailChar = string[index+l]
			if trailChar.isdigit() or '<:"'.find(trailChar) != -1:
				logging.info("skipping: %s", trailChar)
				index += l
				continue

			# we're happy - build the tag and insert it into the string
			if string[index] == '#':	# this is a LocMarker
				spanClass="LocMarker"
			else:
				spanClass="TimeMarker"
	
			spantag = '<span class="' + spanClass + '" value="' + s + '">' + s + '</span>'
			spanlen = len(spantag)

			string = string[:index] + spantag + string[index+l:]
			index += spanlen
			logging.info("New index: %s", index)
		else:
			logging.info("Nothing found")
			break
	# all done - we should have added all the tags at this point...
	return string.strip()


if  __name__ == '__main__':
	# open a passed file - if not, use stdin.	
	if len(sys.argv) > 1:
		try: 
			string = file(sys.argv[1]).read()
		except:
			string = sys.stdin.read()
	else:
		string = sys.stdin.read()

	print loctagger(string)
