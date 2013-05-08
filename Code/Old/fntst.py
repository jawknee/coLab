#!/usr/bin/env python
"""
	test the make_test_graphic routine
"""

from imagemaker import make_text_graphic

def main():
	output_file = '/Users/Johnny/tmp/Title.png'
	fontpath = '/Users/Johnny/dev/coLab/Resources/Fonts/WorstveldSling/WorstveldSling.ttf'


	tan = (196, 176, 160, 255)
	make_text_graphic("Four Flutes to Choose From", output_file, fontpath, fontsize=45, border=2, fill=tan )



if __name__ == '__main__':
	main()
