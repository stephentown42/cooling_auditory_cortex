function plotSpectrogram

global DA gf

axes(handles.axes2)
cla % clear all current objects

L = invoke(DA,'GetTargetVal',sprintf('%s.stimNPoints',gf.stimDevice));
y = invoke(DA,'ReadTargetVEX',sprintf('%s.Sound_data%d',gf.stimDevice,gf.side),0,L,'F32','F32');

NFFT = 2^nextpow2(L);
Y    = fft(y,NFFT) / L;
f    = (gf.fstim / 2) * linspace(0,1,NFFT/2+1);

plot(f,2*abs(Y(1:NFFT/2+1)),'k') 
title('Single-Sided Amplitude Spectrum of y(t)')
xlabel('Frequency (Hz)')
ylabel('|Y(f)|')

ymax = max(2*abs(Y));
updateAxis(0,7000,0,ymax)