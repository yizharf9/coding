#include "msp430xG46x.h"

        ORG 1100h

Arr     DW    2,4,6,8,10,12,14,16,18



        RSEG CODE ;
        
main    mov   #Arr,R5
        

        COMMON INTVEC
        ORG RESET_VECTOR ; POR, ext. Reset
        DW Main
        END