#ifndef _bsp_H_
#define _bsp_H_

#include  <msp430.h>          // MSP430x2xx
// #include  <msp430xG46x.h>  // MSP430x4xx

#define  DataSegStart      0x200
#define  CodeSegStart      0xC000
#define  StackTosStart     0x0400

#define   debounceVal      250
#define   delay62_5ms      0xFFFF

// LEDs abstraction
#define LEDsArrPort        &P1OUT
#define LEDsArrPortDir     &P1DIR
#define LEDsArrPortSel     &P1SEL

// Switches abstraction
#define SWsArrPort         &P2IN
#define SWsArrPortDir      &P2DIR
#define SWsArrPortSel      &P2SEL
#define SWmask             0x0F

// PushButtons abstraction
#define PBsArrPort	   &P2IN 
#define PBsArrIntPend	   &P2IFG 
#define PBsArrIntEn	   &P2IE
#define PBsArrIntEdgeSel   &P2IES
#define PBsArrPortSel      &P2SEL 
#define PBsArrPortDir      &P2DIR 
#define PB0                0x10
#define PB1                0x20
#define PB2                0x40
#define PB3                0x80

#endif



