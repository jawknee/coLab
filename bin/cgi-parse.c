/*
        cgi-parse.c

	To be used in a cgi-bin script - reads stdin and output shell assignments.

                eval $(cgi-parse)

	Various special characters are converted to html equivalents.
	All are numeric codes, e.g.:  " (quote) becomes &#034;

*/
#include <stdio.h>

int gethex(void);

main()
{
   char c;
   int quoted=0;

   while ( ( c=getchar()) != EOF ) {
     switch (c)  {

       case ('%'):      /* next two chars are hex code */
         c=(char) ( gethex()*16 + gethex() );
         switch (c)     {       /* further handling... */
           case '\'':
             printf("&#039;");  /* apostrophe */
             break;
           case '\\':
             printf("&#092;");  /* backslash */
             break;
           case '"':
             printf("&#034;");  /* quote */
             break;
           case '\x0a':         /* I'm not sure what this does */
             if (quoted)
               putchar(c);
             break;
           default:

             putchar(c);
         }
         break;
       case ('+'):      /* 'space' */
         putchar(' ');
         break;
       case ('='):      /* add a " to handle spaces and such */
         putchar('=');
         putchar('"');
         quoted=1;
         break;
       case ('\x0c'):
         break;
       case ('&'):      /* end of line... */
         if (quoted) {
           putchar('"');        /* close the quote */
           quoted=0;
         }
         putchar('\n');
         break;

       default:
         putchar(c);
     }
   }
   if (quoted)          /* just in case... */
     putchar('"');
   putchar('\n');
}
int gethex(void)
{
  char c;
  int i;

  c=getchar();  /* get a character and return the hex equivalent */
  if ( ( c >= '0' ) && ( c <= '9' ) ) {
    i = (int) (c - '0');
  }
  else
  if ( ( c >= 'a' ) && ( c <= 'f' ) ) {
    i = (int) (c - 'a' + 10);
  }
  else
  if ( ( c >= 'A' ) && ( c <= 'F' ) ) {
    i = (int) (c - 'A' + 10);
                                
  }
  else
  if ( ( c >= 'A' ) && ( c <= 'F' ) ) {
    i = (int) (c - 'A' + 10);
  }
  return i;
}          

