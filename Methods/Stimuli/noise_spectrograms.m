function noise_spectrograms
% function noise_spectrograms
%
% Draws example spectrograms to illustrate the three noise conditions (clean, temporally restricted and continuous)
%
% Stephen Town - 2018

% Options
fS = 48848.125;
t_max = 1.25; % seconds
offset = 0.25;
noise_attn = 10;
vowel_attn = 10;

window_s = 256;   % Spectrogram properties
n_overlap = 250;


% Calculate some numbers 
n_samps = round(t_max * fS);
t_vec = (1 : n_samps) ./ fS;
t_vec = t_vec - offset;
offset = round(offset * fS);

baseline = rand(1, n_samps);    % Baseline clean conditions are very low noise
baseline = baseline .* 10^(-(70/20));

%% Generate signals

% Clean signal
v_duration = 0.25;
vowel = newMakeVowel2009(v_duration, fS, 200, 460, 1105, 2857, 4205);
vowel = vowel .* 10^(-(vowel_attn/20));
vowel = envelope(vowel, 250);


v_signal = baseline;

v_samps = round( v_duration * fS) - 1;
v_signal(offset : offset+v_samps) = vowel;

offset_2 = offset + round(0.5*fS);
v_signal(offset_2 : offset_2+v_samps) = vowel;
% 
% v_signal(isnan(v_signal)) = 0;

% Restricted noise
r_samps = round( 0.75 * fS);
r_noise = rand(1, r_samps);
r_noise = r_noise .* 10^(-(noise_attn/20));   % Attenuations
r_noise = r_noise - median(r_noise);

r_signal = baseline;
r_signal(offset : offset + r_samps -1) = r_noise;

r_signal(offset : offset+v_samps) = vowel + r_signal(offset : offset+v_samps) ;
r_signal(offset_2 : offset_2+v_samps) = vowel + r_signal(offset_2 : offset_2+v_samps) ;

r_signal(isnan(r_signal)) = 0;

% Continuous noise
c_noise = rand(1, n_samps);
c_noise = c_noise .* 10^(-(noise_attn/20));   % Attenuations
c_noise = c_noise - median(c_noise);

c_signal = c_noise;
c_signal(offset : offset+v_samps) = vowel + c_signal(offset : offset+v_samps) ;
c_signal(offset_2 : offset_2+v_samps) = vowel + c_signal(offset_2 : offset_2+v_samps) ;


%% Plot data

figure

subplot(231)
title('Clean')
plot(t_vec, v_signal)
xlabel('Time (s)')
ylabel('V')

subplot(232)
title('Restricted')
plot(t_vec, r_signal)
xlabel('Time (s)')
ylabel('V')

subplot(233)
title('Continuous')
plot(t_vec, c_signal)
xlabel('Time (s)')
ylabel('V')

subplot(234)
pspectrum(v_signal,fS,'spectrogram','Leakage',0.2,'OverlapPercent',80,'MinThreshold',-50)
% spectrogram(v_signal, window_s, n_overlap, [], fS, 'yaxis')
ylim([0 5])

subplot(235)
pspectrum(r_signal(t_vec < 20.2),fS,'spectrogram','Leakage',0.2,'OverlapPercent',80,'MinThreshold',-50)
% spectrogram(r_signal, window_s, n_overlap, [], fS, 'yaxis')
drawnow
ylim([0 5])

subplot(236)
pspectrum(c_signal(t_vec < 20.2),fS,'spectrogram','Leakage',0.2,'OverlapPercent',80,'MinThreshold',-50)
ylim([0 5])
