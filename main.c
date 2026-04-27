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

Int16 left_input;
Int16 right_input;
Int16 left_output;
Int16 right_output;
Int16 mono_input;


#define SAMPLES_PER_SECOND 48000
#define NUM_STAGES 6

unsigned long int i = 0;


/* ------------------------------------------------------------------------ *
 *                                                                          *
 *  main( )                                                                 *
 *                                                                          *
 * ------------------------------------------------------------------------ */
void main( void ) 
{
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



//     left_output =  left_input;            // Very simple processing. Replace with your own code!
//     right_output = right_input;           // Directly connect inputs to outputs.


     process_audio_sample(left_in, right_in, &left_out, &right_out)


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
































// Define the number of SOS stages.
// Note: Your MATLAB output generated 6 stages (a 12th order filter).
// If your lab required a strict overall 6th order filter, you will need 3 stages.

// The scaled B coefficients (Q15 format)
const int16_t b_coeffs_q15[NUM_STAGES][3] = {
    { 16404, -32768,  16364 },
    { 16404,  32767,  16364 },
    { 16364,  32767,  16404 },
    { 16364, -32768,  16404 },
    { 16384,  32767,  16384 },
    { 16384, -32768,  16384 }
};

// The unscaled A coefficients (Q15 format)
const int16_t a_coeffs_q15[NUM_STAGES][3] = {
    { 32767, -31759,  31044 },
    { 32767,  31759,  31044 },
    { 32767,  23501,  27732 },
    { 32767, -23501,  27732 },
    { 32767,   8880,  25185 },
    { 32767,  -8880,  25185 }
};

// State buffers for the delay lines. Initialized to 0.
// We need history for both inputs (x) and outputs (y) for EVERY stage.
int16_t x_history[NUM_STAGES][2] = {0};
int16_t y_history[NUM_STAGES][2] = {0};

/*
 * This function should be called for every incoming audio frame.
 * It takes the raw hardware inputs and assigns the computed outputs.
 */
void process_audio_sample(int16_t left_in, int16_t right_in, int16_t *left_out, int16_t *right_out) {

    // We are instructed to filter the left channel only
    int16_t current_val = left_in;

    // Cascade the signal through all Second-Order Sections
    for (int stage = 0; stage < NUM_STAGES; stage++) {

        // Use a 32-bit accumulator to prevent overflow during addition
        int32_t accumulator = 0;
        int16_t stage_input = current_val;

        // 1. Feedforward terms (Numerator / B coefficients)
        accumulator += (int32_t)b_coeffs_q15[stage][0] * stage_input;
        accumulator += (int32_t)b_coeffs_q15[stage][1] * x_history[stage][0]; // x[n-1]
        accumulator += (int32_t)b_coeffs_q15[stage][2] * x_history[stage][1]; // x[n-2]

        // 2. Feedback terms (Denominator / A coefficients)
        // Notice the SUBTRACTION here because we are moving terms to the right side of the difference equation
        accumulator -= (int32_t)a_coeffs_q15[stage][1] * y_history[stage][0]; // y[n-1]
        accumulator -= (int32_t)a_coeffs_q15[stage][2] * y_history[stage][1]; // y[n-2]

        // 3. Bit-shift to convert the Q30 accumulator back to a Q15 16-bit integer
        int16_t stage_output = (int16_t)(accumulator >> 15);

        // 4. Update the delay lines for the NEXT sample loop
        x_history[stage][1] = x_history[stage][0]; // x[n-2] = x[n-1]
        x_history[stage][0] = stage_input;         // x[n-1] = x[n]

        y_history[stage][1] = y_history[stage][0]; // y[n-2] = y[n-1]
        y_history[stage][0] = stage_output;        // y[n-1] = y[n]

        // The output of this stage becomes the input for the next stage
        current_val = stage_output;
    }

    // Optional: Because you scaled all B coefficients by 0.1 earlier,
    // the total gain has dropped significantly. You may need to multiply
    // 'current_val' by a scaling factor here to restore the original volume.
    // current_val = current_val * restore_factor;

    // Send the final filtered result to both the left and right output channels
    *left_out  = current_val;
    *right_out = current_val;
}
