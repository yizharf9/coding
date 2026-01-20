Es = 1; 
N = 1e5;
p1 = 0.8;

SNR_s = -6 : 6;
SER = zeros(1,length(SNR_s));

for i = 1 : length(SNR_s)
    SNRb_DB = SNR_s(i);
    SNRb = 10^(SNRb_DB/10);
    [S,Y] = QAM4_Rec(SNRb, Es, N, p1);
    S_dec = QAM4_SymMAPDec(Y, SNRb, Es, p1);
    
    ser = CompSER(S,S_dec);
    SER(i) = ser;
end 

disp('SNR (dB):');
disp(SNR_s);
disp('SER:');
disp(SER);
figure
semilogy(SNR_s, SER, '-o');
grid on;
title('(1.2.8) 4-QAM SER vs SNR');
xlabel('SNR_b (dB)');
ylabel('Symbol Error Rate');

p1_s = 0.01: 0.01 : 0.99;
SER = zeros(1,length(p1_s));
SNRb_DB = -3;

for i = 1 : length(p1_s)
    p1 = p1_s(i);
    SNRb = 10^(SNRb_DB/10);
    [S,Y] = QAM4_Rec(SNRb, Es, N, p1);
    S_dec = QAM4_SymMAPDec(Y, SNRb, Es, p1);
    
    ser = CompSER(S,S_dec);
    SER(i) = ser;
end 

disp('p1:');
disp(p1_s);
disp('SER:');
disp(SER);
figure
plot(p1_s, SER, '-o');
grid on;
title('(1.2.9) 4-QAM SER vs p1');
xlabel('p1');
ylabel('Symbol Error Rate');

Es = 1; 
Nsym = 1e5;


SNR_dB = -25 : 1 : 0;
SER_Sim = zeros(1, length(SNR_dB));
SER_Theory = zeros(1, length(SNR_dB));

for i = 1 : length(SNR_dB)
    snr_db_val = SNR_dB(i);
    SNRb = 10^(snr_db_val/10);
    
    S = QAM8SymVec(Nsym, Es);
    Y = QAM8_Rec(S, SNRb, Es);
    S_dec = QAM8_SymMAPDec(Y, Es);
    
    SER_Sim(i) = CompSER(S, S_dec);
    SER_Theory(i) = 3 * 0.5 * erfc(sqrt(SNRb)/sqrt(2));
end 


disp('SNR (dB):'); disp(SNR_dB);
disp('SER Sim:'); disp(SER_Sim);

figure;
semilogy(SNR_dB, SER_Sim, 'bo-', 'LineWidth', 1.5);
hold on;
semilogy(SNR_dB, SER_Theory, 'r--', 'LineWidth', 1.5);
semilogy(SNR_dB, (SER_Theory - SER_Sim), 'black--', 'LineWidth', 1.5);
grid on;
title('(1.2.11) 8-QAM SER vs SNR_b');
xlabel('SNR_b [dB]');
ylabel('Symbol Error Rate');
legend('Simulation', 'Approximation','difference', 'Location', 'southwest');
axis([-25 0 1e-1 2.5]);


%% OFDM Performance Evaluation Script
% clear; close all; clc;

Nsc = 128;           
Ncp = 8;           
N_OFDM_Syms = 10000;
EbN0_dB = -10:2:20; 

constellations = {'BPSK', '4QAM', '8QAM'};
bits_per_symbol = [1, 2, 3]; % log2(M) for BPSK, 4QAM, 8QAM

BER_Ch1 = zeros(length(constellations), length(EbN0_dB));
BER_Ch2 = zeros(length(constellations), length(EbN0_dB)); 

%% --- 2. Simulation Loop ---
fprintf('Starting Simulation...\n');

for c_idx = 1:length(constellations)
    current_const = constellations{c_idx};
    M = 2^bits_per_symbol(c_idx); % Constellation order
    k = bits_per_symbol(c_idx);   % Bits per subcarrier
    
    Nbits_total = N_OFDM_Syms * Nsc * k;
    fprintf('Testing %s (%d bits)... ', current_const, Nbits_total);
    
    bit_stream = rand(1, Nbits_total) > 0.5; 
    xofdm = OFDM_Mod(bit_stream, Nsc, Ncp, current_const);
    sig_power = mean(abs(xofdm).^2); 
    
    for snr_idx = 1:length(EbN0_dB)
        ebn0_lin = 10^(EbN0_dB(snr_idx)/10);
        N0 = sig_power / (ebn0_lin * k);

        [r1ofdm, r2ofdm] = Wireless_Channel(xofdm, N0);

        rx_bits_1 = OFDM_Demod(r1ofdm, Nsc, Ncp, current_const, 1);
        
        rx_bits_1 = rx_bits_1(1:Nbits_total);
        
        num_err_1 = sum(abs(bit_stream - rx_bits_1));
        BER_Ch1(c_idx, snr_idx) = num_err_1 / Nbits_total;
        
        if strcmp(current_const, 'BPSK') || strcmp(current_const, '4QAM')

            rx_bits_2 = OFDM_Demod(r2ofdm, Nsc, Ncp, current_const, 2);
            rx_bits_2 = rx_bits_2(1:Nbits_total); % Truncate
            
            num_err_2 = sum(abs(bit_stream - rx_bits_2));
            BER_Ch2(c_idx, snr_idx) = num_err_2 / Nbits_total;
        end
    end
    fprintf('Done.\n');
end

figure('Name', 'BER vs Eb/N0 - Channel 1');
semilogy(EbN0_dB, BER_Ch1(1, :), 'b-o', 'LineWidth', 1.5, 'DisplayName', 'BPSK');
hold on;
semilogy(EbN0_dB, BER_Ch1(2, :), 'r-s', 'LineWidth', 1.5, 'DisplayName', '4QAM');
semilogy(EbN0_dB, BER_Ch1(3, :), 'g-^', 'LineWidth', 1.5, 'DisplayName', '8QAM');
grid on;
xlabel('E_b/N_0 [dB]');
ylabel('Bit Error Rate (BER)');
title('(2.2.8) BER Performance on Channel 1 (AWGN-like)');
legend('Location', 'southwest');


% -- Plot 2: Channel 1 vs Channel 2 (Sec 2.2.8) --
figure('Name', 'Channel 1 vs Channel 2 Performance');
% Channel 1 Curves (Dashed)
semilogy(EbN0_dB, BER_Ch1(1, :), 'b--', 'LineWidth', 1.5, 'DisplayName', 'Ch1 BPSK');
hold on;
semilogy(EbN0_dB, BER_Ch1(2, :), 'r--', 'LineWidth', 1.5, 'DisplayName', 'Ch1 4QAM');

% Channel 2 Curves (Solid)
semilogy(EbN0_dB, BER_Ch2(1, :), 'b-o', 'LineWidth', 1.5, 'DisplayName', 'Ch2 BPSK');
semilogy(EbN0_dB, BER_Ch2(2, :), 'r-s', 'LineWidth', 1.5, 'DisplayName', 'Ch2 4QAM');

grid on;
xlabel('E_b/N_0 [dB]');
ylabel('Bit Error Rate (BER)');
title('(2.2.8) BER Comparison: Channel 1 vs Channel 2');
legend('Location', 'southwest');
ylim([1e-5 1]); % Set limit to see floor clearly if present
hold off


function bit_vec = BitVec(Nbit,pbit)
    bit_vec = rand(1,Nbit) < pbit ;
end

function sym_vec = QAM4SymVec(bit_vec,Es)
    L = length(bit_vec);
    sym_vec = zeros(1,L/2) ;
    for i = 1 : L/2
        a = bit_vec(2*i-1);
        b = bit_vec(2*i);
        s = (-1)^a + (-1)^b * 1i ;
        sym_vec(i) = s / abs(s) * sqrt(Es); 
    end 
end


function [sym_vec_tx,yvec] = QAM4_Rec(SNRb, Es, Nbit, pbit)
    Eb = Es / 2;
    N0 = Eb / SNRb;
    
    B = BitVec(Nbit,pbit);
    sym_vec_tx = QAM4SymVec(B,Es);
    Ns = length(sym_vec_tx);

    CSCN = randn(1,Ns) + randn(1,Ns) * 1i;
    yvec = sym_vec_tx + CSCN * sqrt(N0/2);
end 


function svecdec=QAM4_SymMAPDec(yvec, SNRb, Es, pbit)
    svecdec = zeros(1,length(yvec));
    P = [ (1-pbit)^2 , (1-pbit)*pbit , (pbit)^2 , (1-pbit)*pbit ];
    
    Eb = Es / 2;
    N0 = Eb / SNRb; 
    
    % FIX: Swapped P(2)/P(3) to P(3)/P(2) to align 'Left/Right' ratio 
    % with 'Bottom/Top' logic used in bias_Im
    bias_Re = N0/2 * log(P(3)/P(2)); 
    bias_Im = N0/2 * log(P(2)/P(1));

    for i = 1 : length(yvec)
        y = yvec(i);
        a = real(y);
        b = imag(y);
        
        s_raw = (-1)^((a >= bias_Re)+1) + (-1)^((b >= bias_Im)+1) * 1i;
        
        svecdec(i) = s_raw / abs(s_raw) * sqrt(Es);
    end
end


function ser=CompSER(sym_vec_tx,svecdec)
    ser = 1 - sum(abs(sym_vec_tx - svecdec) < 1e-5) / length(sym_vec_tx);
end

function sym_vec = QAM8SymVec(Nsym, Es)
    sqEs = sqrt(Es);
    
    S0 =  sqEs + 1i*(sqEs/2);
    S1 =  sqEs - 1i*(sqEs/2);
    S2 =  (sqEs/2) + 1i*0;
    S3 =  0 + 1i*(sqEs/2);
    S4 =  0 - 1i*(sqEs/2);
    S5 = -(sqEs/2) + 1i*0;
    S6 = -sqEs + 1i*(sqEs/2);
    S7 = -sqEs - 1i*(sqEs/2);
    
    Constellation = [S0, S1, S2, S3, S4, S5, S6, S7];
    
    indices = randi([1, 8], 1, Nsym);
    sym_vec = Constellation(indices);
end

function yvec = QAM8_Rec(sym_vec8, SNRb, Es)
    E_avg = 0.75 * Es;
    Eb = E_avg / 3;
    N0 = Eb / SNRb;
    
    Ns = length(sym_vec8);
    noise = (randn(1, Ns) + 1i*randn(1, Ns)) * sqrt(N0/2);
    yvec = sym_vec8 + noise;
end 

function svecdec = QAM8_SymMAPDec(yvec, Es)
    sqEs = sqrt(Es);
    Constellation = [ ...
         (sqEs + 1i*sqEs/2), ...
         (sqEs - 1i*sqEs/2), ...
         (sqEs/2 + 1i*0), ...
         (0 + 1i*sqEs/2), ...
         (0 - 1i*sqEs/2), ...
         (-sqEs/2 + 1i*0), ...
         (-sqEs + 1i*sqEs/2), ...
         (-sqEs - 1i*sqEs/2) ];
         
    svecdec = zeros(1, length(yvec));
    
    for i = 1 : length(yvec)
        y = yvec(i);
        [~, idx] = min(abs(y - Constellation).^2);
        svecdec(i) = Constellation(idx);
    end
end

function s = QAM4_Mapper(bits)
    b = bits(1)*2 + bits(2);
    scale = 1/sqrt(2);
    switch b
        case 0 % 00
            s = (1 + 1i) * scale;
        case 1 % 01
            s = (1 - 1i) * scale;
        case 3 % 11
            s = (-1 - 1i) * scale;
        case 2 % 10
            s = (-1 + 1i) * scale;
    end
end
function dec_bits = QAM4_Decode(sym_est_vec)
    L = length(sym_est_vec);
    dec_bits = zeros(1, 2*L);
    for i = 1:L
        re = real(sym_est_vec(i));
        im = imag(sym_est_vec(i));
        if re >= 0 && im >= 0
            b = [0 0];
        elseif re >= 0 && im < 0
            b = [0 1];
        elseif re < 0 && im >= 0
            b = [1 0];
        else
            b = [1 1];
        end
        dec_bits(2*i-1 : 2*i) = b;
    end
end


function s = QAM8_Mapper(bits)
    Es = 1;
    sqEs = sqrt(Es);
    
    dec = bits(1)*4 + bits(2)*2 + bits(3);
    
    switch dec
        case 0 % 000 -> S3
            s = 0 + 1i*(sqEs/2);
        case 1 % 001 -> S0
            s = sqEs + 1i*(sqEs/2);
        case 3 % 011 -> S1
            s = sqEs - 1i*(sqEs/2);
        case 2 % 010 -> S4
            s = 0 - 1i*(sqEs/2);
        case 6 % 110 -> S7
            s = -sqEs - 1i*(sqEs/2);
        case 7 % 111 -> S6
            s = -sqEs + 1i*(sqEs/2);
        case 5 % 101 -> S5
            s = -(sqEs/2) + 1i*0;
        case 4 % 100 -> S2
            s = (sqEs/2) + 1i*0;
    end
end

function dec_bits = QAM8_Decode(sym_est_vec)
    Es = 1; sqEs = sqrt(Es);
    S = [ (0+1i*sqEs/2), (sqEs+1i*sqEs/2), (sqEs-1i*sqEs/2), (0-1i*sqEs/2), ...
          (-sqEs-1i*sqEs/2), (-sqEs+1i*sqEs/2), (-sqEs/2), (sqEs/2) ];
    % 1:000, 2:001, 3:011, 4:010, 5:110, 6:111, 7:101, 8:100
    BitsMap = [0 0 0; 0 0 1; 0 1 1; 0 1 0; 1 1 0; 1 1 1; 1 0 1; 1 0 0];
    
    L = length(sym_est_vec);
    dec_bits = zeros(1, 3*L);
    
    for i = 1:L
        val = sym_est_vec(i);
        [~, idx] = min(abs(val - S).^2); 
        dec_bits(3*i-2 : 3*i) = BitsMap(idx, :);
    end
end

% --- 1. OFDM Modulator (Item 2.2.1) ---
function xofdm = OFDM_Mod(bit_stream, Nsc, Ncp, constellation)
    if strcmp(constellation, 'BPSK')
        M_bits = 1;
        Es = 1; 
        map_func = @(b) (2*b - 1) * sqrt(Es); 
        
    elseif strcmp(constellation, '4QAM')
        M_bits = 2;
        Es = 1;
        map_func = @QAM4_Mapper;
        
    elseif strcmp(constellation, '8QAM')
        M_bits = 3;
        Es = 1;
        map_func = @QAM8_Mapper;
    else
        error('Unknown constellation');
    end
    bits_per_ofdm = Nsc * M_bits;
    L = length(bit_stream);
    remainder = mod(L, bits_per_ofdm);

    if remainder ~= 0
        padding = randi([0 1], 1, bits_per_ofdm - remainder);
        bit_stream = [bit_stream, padding];
    end
    
    num_bits = length(bit_stream);
    num_syms = num_bits / M_bits;     % Number of constellation symbols
    num_ofdm = num_syms / Nsc;        % Number of OFDM symbols (m)
    
    const_symbols = zeros(1, num_syms);
    for i = 1:num_syms
        b_idx = (i-1)*M_bits + 1;
        bits = bit_stream(b_idx : b_idx+M_bits-1);
        const_symbols(i) = map_func(bits);
    end

    sym_matrix = reshape(const_symbols, Nsc, num_ofdm).'; 
    
    sym_matrix_T = sym_matrix.'; % Size Nsc x m
    time_matrix_T = ifft(sym_matrix_T) * sqrt(Nsc) ;% Nsc x m
    
    cp_part = time_matrix_T(end-Ncp+1:end, :);
    ofdm_syms_T = [cp_part; time_matrix_T]; % Size (Nsc+Ncp) x m
    
    xofdm = ofdm_syms_T(:).'; 
end



% --- 2. Wireless Channel (Item 2.2.2) ---
function [r1ofdm, r2ofdm] = Wireless_Channel(xofdm, N0)
    % Constants
    omega0 = 2 * pi * sqrt(2);
    
    % Channel 1 Def
    a1_vals = [8.1, 2.3, 5, 2.3, 1.9, 0.5];
    a1 = (1/10.2424) * a1_vals;
    L1 = length(a1);
    h1 = zeros(1, L1);
    for n = 0:L1-1
        h1(n+1) = a1(n+1) * exp(1i * omega0 * n);
    end
    
    % Channel 2 Def
    a2_vals = [8.1, 2.3, 5, 2.3, 1.9, 0.5, 3, 1.1, 0.9, 0.35, 1.5, 2, 3];
    a2 = (1/11.4648) * a2_vals;
    L2 = length(a2);
    h2 = zeros(1, L2);
    for n = 0:L2-1
        h2(n+1) = a2(n+1) * exp(1i * omega0 * n);
    end
    
    % Apply Convolutions
    r1_conv = conv(xofdm, h1);
    r2_conv = conv(xofdm, h2);
    
    % Truncate to length of input
    Lx = length(xofdm);
    r1_trunc = r1_conv(1:Lx);
    r2_trunc = r2_conv(1:Lx);
    
    % Generate Noise
    % CN(0, N0) -> Real/Imag parts have var N0/2
    noise = (randn(1, Lx) + 1i*randn(1, Lx)) * sqrt(N0/2);
    
    % Add Noise
    r1ofdm = r1_trunc + noise;
    r2ofdm = r2_trunc + noise;
end

% --- 3. OFDM Demodulator (Item 2.2.3) ---
function dec_bits = OFDM_Demod(rvec, Nsc, Ncp, constellation, Channel)
    omega0 = 2 * pi * sqrt(2);
    if Channel == 1
        a_vals = [8.1, 2.3, 5, 2.3, 1.9, 0.5];
        norm_fac = 1/10.2424;
    else
        a_vals = [8.1, 2.3, 5, 2.3, 1.9, 0.5, 3, 1.1, 0.9, 0.35, 1.5, 2, 3];
        norm_fac = 1/11.4648;
    end

    a = norm_fac * a_vals;
    L = length(a);
    h = zeros(1, L);

    for n = 0:L-1
        h(n+1) = a(n+1) * exp(1i * omega0 * n);
    end
    H_k = fft(h, Nsc);
    
    Nsym = Nsc + Ncp;
    num_samples = length(rvec);
    m = floor(num_samples / Nsym);
    r_matrix = reshape(rvec(1:m*Nsym), Nsym, m);
    r_no_cp = r_matrix(Ncp+1:end, :); % Size Nsc x m
    y_freq = fft(r_no_cp) / sqrt(Nsc); % Size Nsc x m
    H_k_mat = repmat(H_k.', 1, m); % Ensure H_k is column
    sym_est_mat = y_freq ./ H_k_mat;
    
    % Serialize to vector of symbols
    % sym_est_vec = sym_est_mat.'; % Transpose to get row-by-row
    % sym_est_vec = sym_est_vec(:).';
    sym_est_vec = sym_est_mat(:).';
    
    % 6. Demap / Decode Bits
    dec_bits = [];
    if strcmp(constellation, 'BPSK')
        dec_bits = real(sym_est_vec) > 0;
    elseif strcmp(constellation, '4QAM')
        dec_bits = QAM4_Decode(sym_est_vec);
    elseif strcmp(constellation, '8QAM')
        dec_bits = QAM8_Decode(sym_est_vec);
    end
end
