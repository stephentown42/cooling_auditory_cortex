function steady_state_spectra
%
% Shows the challenge presented to the brain across sound spectra for two
% vowels being discriminated at each signal to noise ratio.
%
% Stephen Town - 14 March 2021



% Base data
fs = 50000;
F = [460        1105        2857        4205;   % Formants
     730        2058        2857        4205;
     936        1551        2975        4263;
     437        2761        2975        4263];
 
tags = {'/u/','/\epsilon/','/a/','/i/'};    

noise_attn = 10;
vowel_attn = -10 : 10 : 10;   % Attenuation provided to vowels (0 = dB SPL)
n = numel(vowel_attn);

% Create noise (70 dB SPL)
r_samps = round( 0.25 * fs);
r_noise = rand(1, r_samps);
r_noise = r_noise .* 10^(-(noise_attn/20));   % Attenuations
r_noise = envelope(r_noise, ceil(0.005 .* fs));

% Create graphics objects
figure
ax = zeros(n, 2);

for i = 1 : n % For each sound level
       
    ax(i,1) = subplot(n, 2, (i-1)*2 + 1);
    ax(i,2) = subplot(n, 2, (i-1)*2 + 2);
    set(ax(i,:),'nextplot','add')
                
    for j = 1 : 2   % For each vowel
                
        vowel = newMakeVowel2009( 0.25, fs, 200, F(j,1), F(j,2), F(j,3), F(j,4));
        vowel = vowel .* 10^(-(vowel_attn(i)/20));
        vowel = envelope(vowel, 250);

        vowel_in_noise = r_noise + vowel;
            
        plot_spectrum(ax(i,j), fs, vowel, [0 0 0 0.75]);
        plot_spectrum(ax(i,j), fs, vowel_in_noise, [0.6 0 0 0.65]);        
    end
    
    % Add SNR label
    snr = (60 - vowel_attn(i)) - 70;
    text(4.55,80,sprintf('SNR: %d dB', snr),...
        'parent', ax(i,2),...
        'FontWeight','bold',...
        'FontSize',9)
end

set(ax, 'xlim', [0 6],...
        'xgrid', 'on',...
        'xtick', 0 : 2 : 6,...
        'ygrid', 'on',...
        'yticklabel', [],...
        'fontsize', 8,...
        'color', [0 0 0] + 0.84,...
        'GridColor','w',...
        'GridAlpha', 1,...
        'units', 'centimeters')
    
set(ax(1:n-1,:),'xticklabel','')    

xlabel(ax(i,1), 'Frequency (kHz)')
ylabel(ax(2,1), 'Power (dB)')    
title(ax(1,1),'/u/')
title(ax(1,2),'/\epsilon/')

linkaxes(ax(:))
resize_axis(ax, 2, 2.5)
set_axis_xpos(ax(:,1), 5.6)
set_axis_ypos(ax(1,:), 5.45)
set_axis_ypos(ax(2,:), 3.34)


function resize_axis(ax, h, w)

for i = 1 : numel(ax)    
    pos = get(ax(i),'position');
    set(ax(i),'position',[pos(1:2) w h])
end


function set_axis_xpos(ax, x)

for i = 1 : numel(ax)  
    pos = get(ax(i),'position');
    set(ax(i),'position',[x pos(2:4)])
end


function set_axis_ypos(ax, y)

for i = 1 : numel(ax)  
    pos = get(ax(i),'position');
    set(ax(i),'position',[pos(1) y pos(3:4)])
end


function h = plot_spectrum(ax, fs, vowel, color)

NFFT  = length(vowel);
Y     = fft(vowel,NFFT);
f     = fs/2 * linspace(0,1,NFFT/2);    
Yf    = 2 * abs(Y(1:NFFT/2));
yf    = 20 * log10(Yf);

h = plot(f./1000, yf,...
    'color', color,...
    'lineWidth', 1,...
    'parent', ax);