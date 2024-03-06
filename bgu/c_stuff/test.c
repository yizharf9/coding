// cls;gcc .\test.c;.\a.exe  <---use this command to run the program
#include <stdio.h>
#include <stdlib.h>

int main() {
    int var1 = 0b0010;
    int var2 = 0b10;
    int res = var1&var2;
    if (res){
        printf("returns true");
    }
    else{
        printf("returns false");
    }
    return 0;
}