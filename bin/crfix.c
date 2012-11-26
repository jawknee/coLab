/*
 * This program reads the stdin.  If it finds a carriage return, it
 * outputs a line feed.  It also then checks the next character and if
 * it is a space or a line feed (should be) it's tossed.
*/
#include <stdio.h>

main() {
	int c;

	while ( (c=getchar()) != EOF ) {
		switch (c) {
			case '\x0d':	/* CR -> LF */
				c='\n';	/* fall through... */
				putchar(c);
				c=getchar();
				if ( (c != ' ') && (c != '\n') ) {
					putchar(c);
				}
			break;
			default:
				putchar(c);
		}  /* switch */
	}  /* while */
} /* main */

