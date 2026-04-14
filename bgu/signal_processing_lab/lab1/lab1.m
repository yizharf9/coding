addpath("./");

%% Lab Report Analysis using SD_LMS
clear; clc; close all;

% --- 1. Signal Setup ---
Ln = 200;                  % Number of iterations
k = 1:Ln;                  % Time index
x1 = cos(2*pi*k/16);       % Input 1
x2 = sin(2*pi*k/16);       % Input 2
InSig = [x1; x2];          % Formatted for MultiRef (2 rows)
RefSig = cos(2*pi*k/16 + pi/2); % Desired Response

% Theoretical optimal weights for comparison
w_opt = [0; -1];

%% --- Part B.1: Testing Step Size (Mu / U) ---
% We will test a small, optimal, and overly large U
U_small = 0.01;
U_opt   = 0.1;
U_large = 1.1; % May cause instability/oscillation depending on R eigenvalues

Win_default = [0; 0];

% Run the function for different U values
[~, WConv_s, Er_s] = SD_LMS(Win_default, InSig, RefSig, U_small);
[~, WConv_o, Er_o] = SD_LMS(Win_default, InSig, RefSig, U_opt);
[~, WConv_l, Er_l] = SD_LMS(Win_default, InSig, RefSig, U_large);


% Plotting Step Size Effects
figure('Name', 'Effect of Step Size (U)', 'Position', [100, 100, 900, 400]);

% Learning Curves (Error Squared)
subplot(1, 2, 1);
plot(k, Er_s.^2, 'b', k, Er_o.^2, 'g', k, Er_l.^2, 'r');
title('Learning Curves for Different U');
xlabel('Iterations (k)');
ylabel('Squared Error e^2(k)');
legend('Small U (0.01)', 'Optimal U (0.1)', 'Large U (1.1)');
grid on;

% Weight Trajectories (for Optimal U)
subplot(1, 2, 2);
plot(k, WConv_o(1,:), 'b', k, WConv_o(2,:), 'r');
hold on;
yline(w_opt(1), 'b--', 'w1 Optimal');
yline(w_opt(2), 'r--', 'w2 Optimal');
title('Weight Convergence (Optimal U)');
xlabel('Iterations (k)');
ylabel('Weight Value');
legend('w1 trajectory', 'w2 trajectory');
grid on;


%% --- Part B.2: Testing Initial Conditions ---
% We will use the optimal U but start from three different places

Win_1 = [0; 0];     % Origin
Win_2 = [2; 1];     % Far positive
Win_3 = [-2; -3];   % Far negative

[~, WConv_ic1, Er_ic1] = SD_LMS(Win_1, InSig, RefSig, U_opt);
[~, WConv_ic2, Er_ic2] = SD_LMS(Win_2, InSig, RefSig, U_opt);
[~, WConv_ic3, Er_ic3] = SD_LMS(Win_3, InSig, RefSig, U_opt);


% Plotting Initial Conditions Effects
figure('Name', 'Effect of Initial Conditions', 'Position', [150, 150, 900, 400]);

% Learning Curves
subplot(1, 2, 1);
plot(k, Er_ic1.^2, 'b', k, Er_ic2.^2, 'g', k, Er_ic3.^2, 'r');
title('Learning Curves (Different Initial Conditions)');
xlabel('Iterations (k)');
ylabel('Squared Error e^2(k)');
legend('Start [0,0]', 'Start [2,1]', 'Start [-2,-3]');
grid on;

% Weight 2 Trajectory Comparison
subplot(1, 2, 2);
plot(k, WConv_ic1(2,:), 'b', k, WConv_ic2(2,:), 'g', k, WConv_ic3(2,:), 'r');
hold on;
yline(w_opt(2), 'k--', 'w2 Optimal');
title('Trajectory of w2 from Different Starts');
xlabel('Iterations (k)');
ylabel('Weight 2 Value');
legend('Start [0,0]', 'Start [2,1]', 'Start [-2,-3]');
grid on;

Excess_MSE_exp = mean(Er_o(end-50:end).^2);

% Assuming you ran the simulation and have WConv_o (optimal weights over time)
% and your theoretical optimal weights are w_opt = [0; -1]

Ln = length(WConv_o);
w_opt = [0; -1];

% 1. Calculate the squared weight error for every iteration
Weight_Error_Sq = zeros(1, Ln);
for k = 1:Ln
    Weight_Error_Sq(k) = norm(WConv_o(:, k) - w_opt)^2;
end

% 2. Find initial value
Initial_Error = Weight_Error_Sq(1);

% 3. Calculate thresholds
Tau_Threshold = Initial_Error * exp(-1); % 1/e (~36.8%)
Settling_Threshold = Initial_Error * 0.02; % 2% for steady-state

% 4. Numerically find the time constants
% Find the FIRST iteration where the error drops below the threshold
tau_MSE_exp = find(Weight_Error_Sq <= Tau_Threshold, 1);

% Find the iteration where the error drops and STAYS below 2%
% (find the LAST time it was above the threshold, and add 1)
T_MSE_exp = find(Weight_Error_Sq > Settling_Threshold, 1, 'last') + 1;

% Display results
fprintf('--- Time Constants (Numerical vs Analytical for U=0.1) ---\n');
fprintf('Experimental tau_MSE: %d iterations\n', tau_MSE_exp);
fprintf('Analytical tau_MSE:   %d iterations\n', 1 / (2 * U_opt));
fprintf('Experimental T_MSE:   %d iterations\n', T_MSE_exp);
fprintf('Analytical T_MSE:     %d iterations\n', 2 / U_opt);

PART 1.d)
%% Section D: Newton-LMS Analysis
clear; clc; close all;

% 1. Signal Setup
Ln = 200;                  
k = 1:Ln;                  
x1 = cos(2*pi*k/16);       
x2 = sin(2*pi*k/16);       
InSig = [x1; x2];          
RefSig = cos(2*pi*k/16 + pi/2); 

% 2. Algorithm Parameters
Win = [0; 0];
U = 0.05;   % Convergence rate
dN = 16;    % Estimate R every 16 samples (1 full period)

% Analytical R matrix (calculated in part a)
R_analytical = [0.5, 0; 0, 0.5];

% 3. Run the algorithms
% Run 1: Newton LMS with Analytical R
[Wout_na, WConv_na, Er_na, Rout_na] = NEW_LMS(Win, InSig, RefSig, U, R_analytical, dN);

% Run 2: Newton LMS with Estimated R (pass empty R to trigger estimation)
[Wout_ne, WConv_ne, Er_ne, Rout_ne] = NEW_LMS(Win, InSig, RefSig, U, [], dN);

% Run 3: SD-LMS (for comparison)
% Note: To make a fair comparison, the effective step size in SD_LMS 
% should match the Newton step size. Newton uses 2*U*R^-1.
[~, WConv_sd, Er_sd] = SD_LMS(Win, InSig, RefSig, U);

% 4. Plotting the Comparison
figure('Name', 'Newton-LMS Comparisons', 'Position', [100, 100, 1000, 450]);

% --- Plot A: Learning Curves ---
subplot(1, 2, 1);
plot(k, Er_sd.^2, 'k', 'LineWidth', 1); hold on;
plot(k, Er_na.^2, 'b--', 'LineWidth', 1.5);
plot(k, Er_ne.^2, 'r-.', 'LineWidth', 1.5);
title('Learning Curve Comparison');
xlabel('Iterations (k)');
ylabel('Squared Error e^2(k)');
legend('SD-LMS', 'Newton (Analytical R)', 'Newton (Estimated R)');
grid on;

% --- Plot B: Weight Trajectories (w2) ---
subplot(1, 2, 2);
plot(k, WConv_sd(2,:), 'k', 'LineWidth', 1); hold on;
plot(k, WConv_na(2,:), 'b--', 'LineWidth', 1.5);
plot(k, WConv_ne(2,:), 'r-.', 'LineWidth', 1.5);
yline(-1, 'g:', 'Optimal w2 = -1', 'LineWidth', 2);
title('Weight 2 Trajectory Comparison');
xlabel('Iterations (k)');
ylabel('Weight Value (w2)');
legend('SD-LMS', 'Newton (Analytical R)', 'Newton (Estimated R)');
grid on;

Part 2 : ANC
%% Section 2: Narrowband Noise Cancellation
clear; clc; close all;

% 1. Load Speech Signal
% Make sure you have a .wav file in your directory
[s, Fs] = audioread('female_speech.wav'); 
s = s(:,1)'; % Ensure it is a row vector and mono
t = (0:length(s)-1) / Fs; % Time vector

% 2. Calculate Powers and Alpha for SNR = -30dB
P_speech = mean(s.^2);
P_noise_req = P_speech * 1000; % From the -30dB calculation
alpha = sqrt(2 * P_noise_req);

% 3. Generate the Noise Signal n(t)
omega = 250 * 2 * pi;
phi = pi/4; % Unknown arbitrary phase
% Generate the 10Hz triangle wave between -pi/2 and pi/2
% The '0.5' makes it a symmetric triangle wave
theta_t = (pi/2) * sawtooth(2 * pi * 10 * t, 0.5); 

n = alpha * sin(omega * t + theta_t + phi);

% The noisy input to the filter
x = s + n; 

% 4. Generate the Reference Signal r(t)
alpha_tilde = 1; % Chosen arbitrary amplitude
phi_tilde = 0;   % Chosen arbitrary phase
r = alpha_tilde * sin(omega * t + theta_t + phi_tilde);

% 5. Adaptive Filtering using SD_LMS
% Format variables for the function
InSig = r;       % The reference signal goes into the filter
RefSig = x;      % The noisy signal is what we try to match

U = 0.01;        % Step size
num_weights = 20; 
Win = zeros(num_weights, 1); % Initial weights

% Run the algorithm
[Wout, WConv, Er] = SD_LMS(Win, InSig, RefSig, U);

% THE MAGIC: The error signal 'Er' IS the cleaned speech!
s_hat = Er; 


% 6. Playing noisy audio
sound(x, Fs); 

% Playing denoised audio
sound(s_hat, Fs); 
% The sound track says : "dont ask me to carry an oiley rag like that"

2.c)
%% Section C: Power Spectral Density (PSD) Analysis
% Make sure s, x, s_hat, and Fs are in your workspace from the previous part

figure('Name', 'Power Spectral Density Comparison', 'Position', [100, 100, 800, 700]);

% --- 1. PSD of Clean Original Speech ---
subplot(3, 1, 1);
% Using default pwelch windows/overlap, but explicitly passing Fs for Hz axis
[pxx_s, f_s] = pwelch(s, [], [], [], Fs); 
plot(f_s, 10*log10(pxx_s), 'b', 'LineWidth', 1);
title('PSD of Clean Speech Signal (s)');
ylabel('PSD (dB/Hz)');
% The prompt asks to zoom into the relevant range. 
% Speech is mostly 0-4000Hz, and the noise is at 250Hz.
xlim([0 1000]); 
grid on;

% --- 2. PSD of Noisy Signal (SNR = -30dB) ---
subplot(3, 1, 2);
[pxx_x, f_x] = pwelch(x, [], [], [], Fs);
plot(f_x, 10*log10(pxx_x), 'r', 'LineWidth', 1);
title('PSD of Noisy Signal (x = s + n) [SNR = -30dB]');
ylabel('PSD (dB/Hz)');
xlim([0 1000]); % Keep axes consistent for comparison
grid on;

% --- 3. PSD of Filtered Signal ---
subplot(3, 1, 3);
[pxx_shat, f_shat] = pwelch(s_hat, [], [], [], Fs);
plot(f_shat, 10*log10(pxx_shat), 'g', 'LineWidth', 1);
title('PSD of Filtered Signal (LMS Output \approx Clean Speech)');
xlabel('Frequency (Hz)');
ylabel('PSD (dB/Hz)');
xlim([0 1000]); % Keep axes consistent for comparison
grid on;

%% Section D: Parameter Sweep (Weights and Step Size)
% Assuming 's' (clean speech), 'x' (noisy speech), and 'r' (reference) are loaded

% --- Experiment 1: Effect of Number of Weights ---
U_fixed = 0.01;
weights_to_test = [5, 20, 100];
figure('Name', 'Effect of Filter Length and Step Size', 'Position', [100, 100, 900, 500]);

subplot(2, 1, 1 );
hold on;
colors = {'r', 'b', 'k'};
for i = 1:length(weights_to_test)
    L = weights_to_test(i);
    Win = zeros(L, 1);
    [~, ~, s_hat] = SD_LMS(Win, r, x, U_fixed);
    
    % Calculate true error between clean speech and filter output
    true_error = (s - s_hat).^2;
    % Use a moving average to smooth the curve for visualization
    smoothed_error = movmean(true_error, 500); 
    
    plot(smoothed_error, colors{i}, 'LineWidth', 1.5);
end
title('Effect of Number of Weights (U = 0.01)');
xlabel('Iterations (Samples)');
ylabel('Smoothed True MSE (s - s_{hat})^2');
legend('L = 5', 'L = 20', 'L = 100');
ylim([0 0.005 ])
grid on;

% --- Experiment 2: Effect of Step Size ---
L_fixed = 20;
Win_fixed = zeros(L_fixed, 1);
U_to_test = [0.005, 0.01, 0.1];

subplot(2, 1, 2);
hold on;
for i = 1:length(U_to_test)
    U = U_to_test(i);
    [~, ~, s_hat] = SD_LMS(Win_fixed, r, x, U);
    
    true_error = (s - s_hat).^2;
    smoothed_error = movmean(true_error, 500); 
    
    plot(smoothed_error, colors{i}, 'LineWidth', 1.5);
end
title('Effect of Step Size (L = 20)');
xlabel('Iterations (Samples)');
ylabel('Smoothed True MSE (s - s_{hat})^2');
legend('U = 0.001', 'U = 0.01', 'U = 0.1');

grid on;



part 3.a)
addpath("./")
%% Part 3: System Identification
% Section A: Synthesizing the AR system output
clear; clc; close all;

% Define the number of samples 
% (10,000 is a good starting point to give the LMS time to learn later)
N = 10000; 

% 1. Generate Gaussian White Noise input x[n]
% 'randn' generates normally distributed (Gaussian) random numbers 
% with a mean of 0 and variance of 1.
x = randn(N, 1)'; 

% 2. Define the AR filter coefficients
% Denominator coefficients 'a' as given in the prompt
a = [1, -0.25, 0.5]; 
% Since it is a purely autoregressive (AR) model, the numerator 'b' is simply 1
b = 1; 

% 3. Synthesize the output signal y[n] 
y = filter(b, a, x);

% Optional: Plot a small snippet to verify it worked
figure('Name', 'System Identification - Signals');
subplot(2,1,1);
plot(x(1:100), 'b'); 
title('Input White Gaussian Noise (x[n])');
grid on;

subplot(2,1,2);
plot(y(1:100), 'r'); 
title('Output of AR Filter (y[n])');
xlabel('Samples (n)');
grid on;

3.b)
%% Part 3B: System Identification (Full Sweep and Extraction)
clear; clc; close all;

% 1. Setup the Unknown AR System
N = 10000; % Number of iterations to test
x = randn(N, 1); % Input white noise
a_true = [1, -0.25, 0.5]; % Original AR coefficients
y = filter(1, a_true, x); % Reference signal (Unknown system output)

%% --- Sweep 1: Effect of Number of Weights (L) ---
mu_fixed = 0.01;
L_test = [5, 20, 100];
figure('Name', 'System ID Parameter Sweeps', 'Position', [100, 100, 1000, 400]);

subplot(1, 2, 1); hold on; title('Effect of Number of Weights (mu = 0.01)');
colors = {'r', 'b', 'k'};
for i = 1:length(L_test)
    L = L_test(i);
    w_init = zeros(L, 1);
    [~, e, ~] = SD_LMS(w_init, x', y, mu_fixed);
    plot(movmean(e.^2, 200), colors{i}, 'LineWidth', 1.5);
end
xlabel('Iterations'); ylabel('Smoothed MSE'); set(gca, 'YScale', 'log');
legend('L = 5', 'L = 20', 'L = 100'); grid on;

%% --- Sweep 2: Effect of Step Size (mu) ---
L_fixed = 50; 
mu_test = [0.001, 0.01, 0.1];

subplot(1, 2, 2); hold on; title('Effect of Step Size (L = 50)');
for i = 1:length(mu_test)
    mu = mu_test(i);
    w_init = zeros(L_fixed, 1);
    [~, e, ~] = SD_LMS(w_init, x, y, mu);
    plot(movmean(e.^2, 200), colors{i}, 'LineWidth', 1.5);
end
xlabel('Iterations'); ylabel('Smoothed MSE'); set(gca, 'YScale', 'log');
legend('\mu = 0.001', '\mu = 0.01', '\mu = 0.1 (Unstable/Noisy)'); grid on;

%% --- Extracting AR Coefficients ---
% Run a robust model to extract weights
L_extract = 50;
mu_extract = 0.01;
w_init = zeros(L_extract, 1);
[W_final, ~, ~] = SD_LMS(w_init, x, y, mu_extract);

% The final weights are in the last column of W_final
w_converged = W_final(:, end); 

% Calculate a1 and a2 using the relationship formulas
w0 = w_converged(1);
w1 = w_converged(2);
w2 = w_converged(3);

a1_est = -w1 / w0;
a2_est = -(w2 + a1_est * w1) / w0;

fprintf('--- Coefficient Estimation ---\n');
fprintf('Original a1: %f | Estimated a1: %f\n', a_true(2), a1_est);
fprintf('Original a2: %f | Estimated a2: %f\n', a_true(3), a2_est);

%% --- Testing Initial Conditions ---
w_init_zero = zeros(L_extract, 1);
w_init_random = randn(L_extract, 1) * 2; % Start with terrible random weights

[W_zero, e_zero, ~] = SD_LMS(w_init_zero, x, y, mu_extract);
[W_rand, e_rand, ~] = SD_LMS(w_init_random, x, y, mu_extract);

figure('Name', 'Effect of Initial Conditions');
plot(movmean(e_zero.^2, 100), 'b', 'LineWidth', 1.5); hold on;
plot(movmean(e_rand.^2, 100), 'r', 'LineWidth', 1.5);
title('Effect of Initial Conditions on Learning Curve');
xlabel('Iterations'); ylabel('Smoothed MSE'); set(gca, 'YScale', 'log');
legend('W_{init} = 0', 'W_{init} = Random'); grid on;

% Compare final weights to prove they converge to the same place
weight_diff = norm(W_zero(:, end) - W_rand(:, end));
fprintf('\n--- Initial Conditions Test ---\n');
fprintf('Difference between final weights (Zero vs Random start): %e\n', weight_diff);