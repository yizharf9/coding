function [out]=quantize(in, R_bits, S_bits);
% Input:
% in : sampled vector.
% R_bits : Number of Bits in sampling card.
% output :
% S_bits : Number of bits in simulated sampling card.
% Checking new simulated card.
 if (R_bits<S_bits | S_bits<1),
 error(' Wrong simulated sampling card no. of bits')
 end
% Checking dynamic range. Max value is 2^(R_bits-1).
 M_val = max( abs(in) );
 if M_val>(2^(R_bits-1)) ,
 error('Error in sampled data range')
 end
% Changing data to new simulated sampling card.
 if (S_bits==R_bits)
 out=in;
 else 
 out = (floor( in*2^( S_bits - 1 )) + 0.5 )/( 2^( S_bits -1 ));
 end
end