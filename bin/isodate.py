#!/usr/bin/env python
"""
	A quick one-off to supply the current UTC in ISO-8601
"""
import datetime

def main():
	print datetime.datetime.utcnow().strftime('%Y-%M-%dT%H:%m:%S')

if __name__ == '__main__':
	main()
