#!/usr/bin/env python

class item:
	def __init__(self):
		self.a='a string'
		self.b=23
		self.c=False
		self.d=43.2

def main():
	s = item()
	for thing in s:
		print "thing is:", thing


if __name__ == '__main__':
	main()
