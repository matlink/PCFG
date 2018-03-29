#define PWD_T  20
#define BASE_T 20
#define TERM_T 20
typedef struct {
	char base[BASE_T];
	char terms[TERM_T][PWD_T];
	int  nbterms;
} gramm;

gramm parse(char* word);
