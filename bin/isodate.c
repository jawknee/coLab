#include <stdio.h>
#include <time.h>

time_t now_t;
struct tm now;
time(&now_t);
now = *localtime(&now_t);
printf("%4d-%02d-%02d",
	now.tm_year+1900, now.tm_mon+1,
	now.tm_mday);

