A1 = 1 ; f1 = 1;
A2 = 2 ; f2 = 2.5;
Ac = 2 ; fc = 25;

A = 3 ;

Kf = 1 ; 
fs = 3.34 * 1e3 
K1_dB = db(10) ; K2_dB = db(1/sqrt(10))

t = -3:1/fs:3
t1 = 4.8 *1e-3
t2 = 14.4 *1e-3

N = length(t)
f = -N/2 : N/2 -1 * (fs/N)

vm = @(t) A1 * sin(2*pi*f1*t) + A2 * sin(2*pi*f2*t) ;
vc = @(t) Ac * cos(2*pi*fc*t) ;

Vm = vm(t)
Vc = vc(t)

plot(t,Vm)
plot(t,Vc)

function vsc = DSB_SC_Mod(vm,vc)
    vsc = vm .* vc ;
end 

V_T1 = DSB_SC_Mod(Vm,Vc);

plot(t,V_T1)
title("DSB-SC in time. domain")
xlabel("time [sec]")
ylabel("Voltage [V]")

Vsc_w = fftshift(fft(V_T1,N))/( fs)
plot(f, abs(Vsc_w))

fs/N 

f_max = fc + max([f1,f2])
f_min = fc - max([f1,f2])

theta_max = f_max / fs * N
theta_min = f_min / fs * N

xline(theta_max,"--",Label="fc + fmax = " + theta_max)
xline(theta_min,"--",Label="fc - fmin = " + theta_min)

lim = 200;
xlim([-lim lim])
ylim([0 8])
title("DSB-SC in freq. domain")
xlabel("angular freq. [rad/sec]")
ylabel("Voltage [V]")

function vlc = DSB_LC_Mod(vm,vc,A)
    vlc = (A+vm).* vc ;
end 

V_T2 = DSB_LC_Mod(Vm,Vc,A);

plot(t,V_T2)
title("DSB-LC in time. domain")
xlabel("time [sec]")
ylabel("Voltage [V]")

Vsc_w = fftshift(fft(V_T2,N))/( fs);
plot(f, abs(Vsc_w))

f_max = fc + max([f1,f2]);
f_min = fc - max([f1,f2]);

theta_max = f_max / fs * N;
theta_c = fc / fs * N;
theta_min = f_min / fs * N;

xline(theta_max,"--",Label="fc + fmax = " + theta_max)
xline(theta_c,"--",Label="fc = " + theta_c)
xline(theta_min,"--",Label="fc - fmin = " + theta_min)

lim = 200;
xlim([-lim lim])
ylim([0 20])
title("DSB-LC in freq. domain")
xlabel("angular freq. [rad/sec]")
ylabel("Voltage [V]")


FM_Mod = @(t,signal) Ac * cos(2*pi*fc*t + 2*pi*Kf*cumtrapz(signal)) ;

Vc_fm= FM_Mod(t,Vm)
figure('Position', [100, 100, 1200, 1200]); % [left, bottom, width, height]
plot(t,Vc_fm)
xlim([0  0.2])
title("FM modulation in time domain")
xlabel("time [sec]")
ylabel("Voltage [V]")

K1 = 10^(K1_dB/20);
K2 = 10^(K2_dB/20);

P_ch = mean(V_T1.^2); 

B_bw = 5; 

SNRs_dB = [-10, 0, 10];

z = zeros(3, length(t)); 

for i = 1:3
    SNR_lin = 10^(SNRs_dB(i)/10);
    Ni = P_ch / (B_bw * SNR_lin);
    noise_var = Ni / 2;
    z(i, :) = sqrt(noise_var) * randn(1, length(t));
end

h_ch = zeros(1, length(t));

[~, idx_0] = min(abs(t)); 

idx_t1 = round(t1 * fs);
idx_t2 = round(t2 * fs);


if (idx_0 + idx_t1) <= length(t)
    h_ch(idx_0 + idx_t1) = K1 * fs; 
end
if (idx_0 + idx_t2) <= length(t)
    h_ch(idx_0 + idx_t2) = K2 * fs;
end

x_r1 = V_T1 + z(1, :);
x_r2 = V_T1 + z(2, :);
x_r3 = V_T1 + z(3, :);


v_distorted = conv(V_T1, h_ch, 'same') / fs;
x_r3_ch = v_distorted + z(3, :);

figure;
subplot(2,1,1);
plot(t, x_r3);
title('Received Signal (SNR=10dB, No Channel)');
xlabel('Time [s]'); ylabel('Amplitude');
xlim([0 0.5]); grid on;

subplot(2,1,2);
plot(t, x_r3_ch);
title('Received Signal (SNR=10dB, WITH Channel)');
xlabel('Time [s]'); ylabel('Amplitude');
xlim([0 0.5]); grid on;

% Plot Frequency Domain (Magnitude)
% Generate f axis
f = (-length(t)/2 : length(t)/2 - 1) * (fs/length(t));

X_r1_w = fftshift(fft(x_r1)) / fs;
X_r2_w = fftshift(fft(x_r2)) / fs;
X_r3_w = fftshift(fft(x_r3)) / fs;
X_r3_ch_w = fftshift(fft(x_r3_ch)) / fs;

figure;
plot(f, abs(X_r1_w), 'g', 'DisplayName', 'SNR -10dB'); hold on;
plot(f, abs(X_r3_w), 'b', 'DisplayName', 'SNR +10dB'); 
plot(f, abs(X_r3_ch_w), 'r', 'DisplayName', 'SNR +10dB w/ Channel');
hold off;
legend;
title('Magnitude Spectrum of Received Signals');
xlabel('Frequency [Hz]'); ylabel('|X(f)|');
xlim([-50 50]); grid on;

wp = 1.2 * 2 * pi * B_bw;

h_lpf = sin(wp * t) ./ (pi * t);
h_lpf(t == 0) = wp / pi;

h_bpf = 2 * h_lpf .* cos(2 * pi * fc * t);

H_BPF = fftshift(fft(h_bpf));
f_axis = linspace(-fs/2, fs/2, length(t));

figure;
plot(f_axis, abs(H_BPF));
title('Frequency Response of the Generated Bandpass Filter');
xlabel('Frequency (Hz)');
ylabel('Magnitude');
xlim([-50 50]);
grid on;

Ts = 1/fs
x_L1_SC = conv(x_r1, h_bpf, 'same') * Ts;
x_L2_SC = conv(x_r2, h_bpf, 'same') * Ts;
x_L3_SC = conv(x_r3, h_bpf, 'same') * Ts;

figure;
subplot(3,1,1); plot(t, x_L1_SC); title('Filtered DSB-SC Signal 1'); grid on;
subplot(3,1,2); plot(t, x_L2_SC); title('Filtered DSB-SC Signal 2'); grid on;
subplot(3,1,3); plot(t, x_L3_SC); title('Filtered DSB-SC Signal 3'); grid on;
xlabel('Time (s)');

x_L2_LC = conv(V_T2, h_bpf, 'same') * Ts;
x_L2_FM = conv(Vc_fm, h_bpf, 'same') * Ts;

figure;
subplot(2,1,1); plot(t, x_L2_LC); title('Filtered DSB-LC Signal'); grid on;
subplot(2,1,2); plot(t, x_L2_FM); title('Filtered FM Signal'); grid on;
xlabel('Time (s)');

% DSB-SC Demodulation (Coherent Detection)
x_mix1 = x_L1_SC .* (2 * cos(2 * pi * fc * t));
x_d1_SC = conv(x_mix1, h_lpf, 'same') * Ts;

x_mix2 = x_L2_SC .* (2 * cos(2 * pi * fc * t));
x_d2_SC = conv(x_mix2, h_lpf, 'same') * Ts;

x_mix3 = x_L3_SC .* (2 * cos(2 * pi * fc * t));
x_d3_SC = conv(x_mix3, h_lpf, 'same') * Ts;

% DSB-LC Demodulation (Envelope Detector)
x_hat = imag(hilbert(x_L2_LC));
envelope = sqrt(x_L2_LC.^2 + x_hat.^2);
x_d2_LC = (envelope - A * Ac) / Ac;

% FM Demodulation
freq_dev = 50; % Assuming standard deviation, adjust if given in previous section
x_d2_FM = fmdemod(x_L2_FM, fc, fs, freq_dev);

% Ensure all signals match the length of t
L = length(t);

% Trim signals if they are longer than t
x_d1_SC = x_d1_SC(1:L);
x_d2_SC = x_d2_SC(1:L);
x_d3_SC = x_d3_SC(1:L);
x_d2_LC = x_d2_LC(1:L);
x_d2_FM = x_d2_FM(1:L);
vm      = vm(1:L); % Just in case vm is different

figure('Name', 'Demodulated Signals vs Original Message');

% --- Plot 1: DSB-SC Channel 1 ---
subplot(5,1,1);
plot(t, Vm, 'g', 'LineWidth', 1.5); hold on;
plot(t, x_d1_SC, 'b--');
title('DSB-SC (Channel 1) Demodulated Output');
legend('Original v_m(t)', 'Demodulated');
grid on; hold off;

% --- Plot 2: DSB-SC Channel 2 ---
subplot(5,1,2);
plot(t, Vm, 'g', 'LineWidth', 1.5); hold on;
plot(t, x_d2_SC, 'b--');
title('DSB-SC (Channel 2) Demodulated Output');
grid on; hold off;

% --- Plot 3: DSB-SC Channel 3 ---
subplot(5,1,3);
plot(t, Vm, 'g', 'LineWidth', 1.5); hold on;
plot(t, x_d3_SC, 'b--');
title('DSB-SC (Channel 3) Demodulated Output');
grid on; hold off;

% --- Plot 4: DSB-LC Channel 2 ---
subplot(5,1,4);
plot(t, Vm, 'g', 'LineWidth', 1.5); hold on;
plot(t, x_d2_LC, 'b--');
title('DSB-LC (Channel 2) Demodulated Output');
grid on; hold off;

% --- Plot 5: FM Channel 2 ---
subplot(5,1,5);
plot(t, Vm, 'g', 'LineWidth', 1.5); hold on;
plot(t, x_d2_FM, 'b--');
title('FM (Channel 2) Demodulated Output');
xlabel('Time [s]');
grid on; hold off;


function s_t = sym_gen(p_s1, p_s2, N)
    % Define symbols
    symbols = [-1, 0, 1]; % corresponding to s1, s2, s3
    
    % Calculate cumulative probabilities
    p_s3 = 1 - p_s1 - p_s2;
    edges = [0, p_s1, p_s1 + p_s2, 1];
    
    % Generate random numbers
    rand_vals = rand(1, N);
    
    % Map to symbols
    s_t = zeros(1, N);
    
    % Assign s1 (-1)
    s_t(rand_vals <= edges(2)) = symbols(1);
    
    % Assign s2 (0)
    s_t(rand_vals > edges(2) & rand_vals <= edges(3)) = symbols(2);
    
    % Assign s3 (1)
    s_t(rand_vals > edges(3)) = symbols(3);
end

function received_t = rec_gen(s_t, tran_prob)
    % tran_prob is the 3x4 matrix defined in the analysis
    % s_t contains values -1, 0, 1
    
    N = length(s_t);
    received_t = zeros(1, N);
    
    % Map symbols to indices 1, 2, 3 for matrix indexing
    % -1 -> 1, 0 -> 2, 1 -> 3
    s_indices = zeros(1, N);
    s_indices(s_t == -1) = 1;
    s_indices(s_t == 0) = 2;
    s_indices(s_t == 1) = 3;
    
    % Generate random numbers for channel transition
    rand_vals = rand(1, N);
    
    for i = 1:N
        row_idx = s_indices(i);
        probs = tran_prob(row_idx, :);
        
        % Create cumulative distribution for this row
        cdf = cumsum(probs);
        
        % Determine output r1(1), r2(2), r3(3), or r4(4)
        if rand_vals(i) <= cdf(1)
            received_t(i) = 1;
        elseif rand_vals(i) <= cdf(2)
            received_t(i) = 2;
        elseif rand_vals(i) <= cdf(3)
            received_t(i) = 3;
        else
            received_t(i) = 4;
        end
    end
end

function dec_s = test_dec(received_t, type)
    N = length(received_t);
    dec_s = zeros(1, N);
    
    % Decisions derived from Analysis
    % s1 = -1, s2 = 0, s3 = 1
    
    if strcmp(type, 'ML')
        % ML Rules:
        % r1 -> s1 (-1)
        % r2 -> s3 (1)
        % r3 -> s2 (0)
        % r4 -> s3 (1)
        
        for i = 1:N
            r = received_t(i);
            if r == 1
                dec_s(i) = -1;
            elseif r == 2
                dec_s(i) = 1;
            elseif r == 3
                dec_s(i) = 0;
            elseif r == 4
                dec_s(i) = 1;
            end
        end
        
    elseif strcmp(type, 'MAP')
        % MAP Rules:
        % r1 -> s1 (-1)
        % r2 -> s1 (-1)
        % r3 -> s2 (0)
        % r4 -> s3 (1)
        
        for i = 1:N
            r = received_t(i);
            if r == 1
                dec_s(i) = -1;
            elseif r == 2
                dec_s(i) = -1;
            elseif r == 3
                dec_s(i) = 0;
            elseif r == 4
                dec_s(i) = 1;
            end
        end
    else
        error('Invalid type. Choose ML or MAP.');
    end
end

clc; clear; close all;

% --- Setup ---
N = 10000;
p1 = 0.5;
p2 = 0.25;

% Define Transition Matrix (Rows=s1,s2,s3; Cols=r1,r2,r3,r4)
% Values taken from the visual diagram analysis
tran_prob = [0.6, 0.2, 0.2, 0.0; ...
             0.3, 0.1, 0.5, 0.1; ...
             0.0, 0.25, 0.4, 0.35];

% --- 1. Generate Symbols ---
s_t = sym_gen(p1, p2, N);

% --- 2. Generate Received Signals ---
received_t = rec_gen(s_t, tran_prob);

% --- 3. ML Decoding and Error ---
dec_s_ML = test_dec(received_t, 'ML');
errors_ML = sum(s_t ~= dec_s_ML);
Pe_ML_sim = errors_ML / N;

% --- 4. MAP Decoding and Error ---
dec_s_MAP = test_dec(received_t, 'MAP');
errors_MAP = sum(s_t ~= dec_s_MAP);
Pe_MAP_sim = errors_MAP / N;

% --- 5. Display Results ---
fprintf('--- Simulation Results (N=%d) ---\n', N);
fprintf('Theoretical ML Error: 0.4250\n');
fprintf('Simulated ML Error:   %.4f\n\n', Pe_ML_sim);

fprintf('Theoretical MAP Error: 0.3875\n');
fprintf('Simulated MAP Error:   %.4f\n', Pe_MAP_sim);