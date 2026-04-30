clear all;

n = 6;
num_of_samples = 8192 ; 
fs = 24e3;

fc1 = 4e3;
fc2 = 8e3;

Rp = 1;
Wp = [fc1/fs,fc2/fs];
ftype = 'bandpass';

[b,a] = cheby1(n,Rp,Wp,ftype);

[h,f] = freqz(b,a,num_of_samples );


figure;
% semilogx(f/pi,mag2db(abs(h*fs )))
grid
legend('TF Design','ZPK Design')
xlabel('Normalized Frequency (\times\pi rad/sample)')
ylabel('Magnitude (dB)')


figure;
hold on ;
sys = tf(b,a);

Ps = pole(sys);

Zs = zero(sys);
% pzp = zplane([],Ps);


theta_sampling = 1e3;
theta = linspace(0,2*pi,theta_sampling);
% plot(cos(theta),sin(theta),"--k","LineWidth",2)


grid on;
hold off ; 

% first row is the poly with poles closest to unit circle
[sos,g] = tf2sos(b,a,"down"); 
disp('Initial sos Coefficient matrix (float32/64):');
disp(sos)


% ---------------------------------------------------------------------------------------------------
% 3.1 : no, the coeff are not in the range [-1,1-e-15] ... 

% 3.2 : the problem with a gain that is too high is possible overflow
% exceeding the precision capability of the q15 fixed-point format.
% ---------------------------------------------------------------------------------------------------


% Separate the b and a coefficients
b_coeffs = sos(:, 1:3);
a_coeffs = sos(:, 4:6);

% --- Step 1: Scale ONLY the b coefficients ---
[b_scaled, g_scaled] = scale_b_coeffs(b_coeffs, g);

% --- Step 2: Quantize BOTH to Q15 ---
% Quantize the scaled 'b' coefficients
[b_q15_binary, b_q15_math] = quantize_to_q15(b_scaled);

% Quantize the unscaled 'a' coefficients
[a_q15_binary, a_q15_math] = quantize_to_q15(a_coeffs);


disp('Scaled B Coefficients (Q15 Binary):');
disp(b_q15_binary);
disp(b_q15_math);

disp('Unscaled A Coefficients (Q15 Binary):');
disp(a_q15_binary);
disp(a_q15_math);



















function [b_scaled, g_scaled] = scale_b_coeffs(b, g)
    % SCALE_B_COEFFS Scales biquad numerator coefficients to prevent Q15 overflow
    % Inputs:
    %   b - The Nx3 matrix of numerator coefficients
    %   g - The global system gain
    % Outputs:
    %   b_scaled - The scaled Nx3 matrix
    %   g_scaled - The compensated global gain
    
    q15_max = 1 - 2^-15;
    
    % Find max absolute value per row
    scale_factors = max(abs(b), [], 2);
    
    % Avoid division by zero if a row is completely empty
    scale_factors(scale_factors == 0) = 1; 
    
    % Calculate exact scale factors to hit q15_max
    scale_factors = scale_factors / q15_max;
    
    % Apply scaling and compensate gain
    b_scaled = b ./ scale_factors;
    g_scaled = g * prod(scale_factors);
end

function [bin_display, quantized_math_vals] = quantize_to_q15(coeffs)
    % QUANTIZE_TO_Q15 Converts floating-point matrices to Q15 binary strings AND numerical values
    % Inputs:
    %   coeffs - Any matrix of floating-point numbers
    % Outputs:
    %   bin_display         - Cell array of 16-bit binary strings (for display)
    %   quantized_math_vals - Floating point numbers with Q15 precision loss applied (for math)
    
    % 1. Shift fractional parts to integer domain
    coeffs_int = round(coeffs * 2^15);
    
    % 2. Cast to 16-bit signed integer (this applies Q15 saturation boundaries)
    coeffs_int16 = int16(coeffs_int);
    
    % ==========================================
    % FOR DSP CALCULATIONS:
    % Convert the saturated integers back to floating point range [-1, 1)
    % Use this output for your filter() or freqz() commands
    % ==========================================
    quantized_math_vals = double(coeffs_int16) / 2^15;
    
    % ==========================================
    % FOR DISPLAY ONLY:
    % Trick dec2bin by typecasting the raw Two's complement data to unsigned
    % ==========================================
    coeffs_uint16 = typecast(coeffs_int16(:), 'uint16');
    bin_strings = dec2bin(coeffs_uint16, 16);
    bin_display = reshape(cellstr(bin_strings), size(coeffs));
end