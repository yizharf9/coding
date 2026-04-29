/*****************************************************************************/
/*                                                                           */
/* FILENAME                                                                  */
/* 	 main.c                                                                  */
/*                                                                           */
/* DESCRIPTION                                                               */
/*   TMS320C5505 USB Stick. Application 1. Getting started.                  */
/*   Take microphone input and send to headphones.                           */
/*                                                                           */
/* REVISION                                                                  */
/*   Revision: 1.00	                                                         */
/*   Author  : Richard Sikora                                                */
/*---------------------------------------------------------------------------*/
/*                                                                           */
/* HISTORY                                                                   */
/*   Revision: 1.00                                                          */
/*   5th March 2010. Created by Richard Sikora from TMS320C5510 DSK code.    */
/*                                                                           */
/*****************************************************************************/
/*
 * Copyright (C) 2010 Texas Instruments Incorporated - http://www.ti.com/ 
 * 
 * 
 *  Redistribution and use in source and binary forms, with or without 
 *  modification, are permitted provided that the following conditions 
 *  are met:
 *
 *    Redistributions of source code must retain the above copyright 
 *    notice, this list of conditions and the following disclaimer.
 *
 *    Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the 
 *    documentation and/or other materials provided with the   
 *    distribution.
 *
 *    Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 *  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
 *  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
 *  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
 *  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 *  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
 *  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
*/

#include "stdio.h"
#include "usbstk5505.h"
#include "aic3204.h"
#include "PLL.h"
#include "stereo.h"
#include <stdint.h>
#include <stdbool.h>

Int16 left_input;
Int16 right_input;
Int16 left_output;
Int16 right_output;
Int16 mono_input;


#define SAMPLES_PER_SECOND 48000
#define NUM_STAGES 3 // Match your coefficient array size
unsigned long int i = 0;



/* ------------------------------------------------------------------------ *
 *                                                                          *
 *  main( )                                                                 *
 *                                                                          *
 * ------------------------------------------------------------------------ */
void main( void ) 
{

    bool processing = true ;
    /* Initialize BSL */
    USBSTK5505_init( );
	
	/* Initialize PLL */
	pll_frequency_setup(100);

    /* Initialise hardware interface and I2C for code */
    aic3204_hardware_init();
    
    /* Initialise the AIC3204 codec */
	aic3204_init(); 

    printf("\n\nRunning Getting Started Project\n");
    printf( "<-> Audio Loopback from Stereo IN --> to HP/Lineout\n" );
	
	/* Setup sampling frequency and 30dB gain for microphone */
    set_sampling_frequency_and_gain(SAMPLES_PER_SECOND, 0);
  
     asm(" bclr XF");
   
 	for ( i = 0  ; i < SAMPLES_PER_SECOND * 600  ;i++  )
 	{

     aic3204_codec_read(&left_input, &right_input); // Configured for one interrupt per two channels.
   
     /*  *****************************************************************************************  */


     if (processing) {
         void process_audio_sample(short left_in, short right_in, short *left_out, short *right_out);

         process_audio_sample(left_input, right_input, &left_output, &right_output);
     }
     else{

         left_output =  left_input;            // Very simple processing. Replace with your own code!
         right_output = right_input;           // Directly connect inputs to outputs.
     }



     /*  *****************************************************************************************  */

     aic3204_codec_write(left_output, right_output);
 	}

   /* Disable I2S and put codec into reset */ 
    aic3204_disable();

    printf( "\n***Program has Terminated***\n" );
    SW_BREAKPOINT;
}

/* ------------------------------------------------------------------------ *
 *                                                                          *
 *  End of main.c                                                           *
 *                                                                          *
 * ------------------------------------------------------------------------ */
































// The scaled B coefficients (Q15 format with gain distributed)
const short b_coeffs_q15[NUM_STAGES][3] = {
    { 11698,  23397,  11698 }, // Stage 1
    { 11698, -23397,  11698 }, // Stage 2
    { 11698,      0, -11699 }  // Stage 3
};

// The unscaled A coefficients (Q15 format)
// Note: 32768 capped to 32767 to prevent signed integer overflow
const short a_coeffs_q15[NUM_STAGES][3] = {
    { 32767,  28971,  26358 }, // Stage 1
    { 32767, -28971,  26358 }, // Stage 2
    { 32767,      0,  18220 }  // Stage 3
};

// State buffers for the delay lines. Initialized to 0.
short x_history[NUM_STAGES][2] = {0};
short y_history[NUM_STAGES][2] = {0};


/*
 * This function should be called for every incoming audio frame.
 * It takes the raw hardware inputs and assigns the computed outputs.
 */
void process_audio_sample(short left_in, short right_in, short *left_out, short *right_out) {

    // 1. Pre-scale input to prevent 32-bit overflow during the 5-term summation
    int32_t current_val_32 = (int32_t)left_in >> 2; // Divide by 4

    int stage;
    // CORRECTED: Loop now iterates through all 3 stages
    for (stage = 0; stage < NUM_STAGES; stage++) {
        int32_t acc = 0;
        short s_in = (short)current_val_32;

        // B terms
        acc += (int32_t)b_coeffs_q15[stage][0] * s_in;
        acc += (int32_t)b_coeffs_q15[stage][1] * x_history[stage][0];
        acc += (int32_t)b_coeffs_q15[stage][2] * x_history[stage][1];

        // A terms
        acc -= (int32_t)a_coeffs_q15[stage][1] * y_history[stage][0];
        acc -= (int32_t)a_coeffs_q15[stage][2] * y_history[stage][1];

        // Shift back to Q15 and apply basic saturation
        int32_t result = acc >> 15;
        if (result > 32767) result = 32767;
        else if (result < -32768) result = -32768;

        short s_out = (short)result;

        // Update buffers
        x_history[stage][1] = x_history[stage][0];
        x_history[stage][0] = s_in;
        y_history[stage][1] = y_history[stage][0];
        y_history[stage][0] = s_out;

        current_val_32 = result;
    }

    // 2. Post-scale to restore headroom gain
    int32_t final_out = current_val_32 << 2;
    if (final_out > 32767) final_out = 32767;
    else if (final_out < -32768) final_out = -32768;

    *left_out  = (short)final_out;
    *right_out = (short)final_out;
}
