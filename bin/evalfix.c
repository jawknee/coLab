/*
 * A simple enough program to read from the stdin and write to the 
 * stdout, fixing charcters as it goes so that they'll work well 
 * in an HTML context.  This program is specific to evaluating 
 * values passed in from a form.  Thus while substitutions are 
 * done for many characters, the quote (") is not touched, less the
 * variable assignment not work any more.
 * 
 * Line feeds are tossed.
*/
#include <stdio.h>

main() {
	int c;

	while ( (c=getchar()) != EOF ) {
		switch (c) {
			case '<':
				printf("&#060;");	/* same as &lt; */
				break;
			case '>':
				printf("&#062;");	/* same as &gt; */
				break;
			/*	a bad idea, reconsidered...
			case ' ':	
				printf("&#32;");
				break;
			*/
			case '$':
				printf("&#36;");
				break;
			case '*':
				printf("&#42;");
				break;
			case '@':
				printf("&#64;");
				break;
			case '\\':
				printf("&#92;");
				break;
			case '`':
				printf("&#96;");
				break;
			case '\r':
				printf("<br>");
				break;
			default:
				putchar(c);
		}  /* switch */
	}  /* while */
} /* main */
