
#include "io430.h"

int main( void )
{
  // Stop watchdog timer to prevent time out reset
  WDTCTL = WDTPW + WDTHOLD;
  int a=2, b=2, c;
  c = a*b;
  while(1);
  return 0;
}
