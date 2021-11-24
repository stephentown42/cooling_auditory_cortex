function speech=newMakeVowel2009(dur,sampleRate, F0, f1,f2,f3,f4)
% y=jansMakeVowel(dur,sampleRate, F0, f1, f2, f3);
%   makes a very simple artificial vowel
%   adapted from Slattery's auditory toolbox makevowel.m
%   dur is duration in seconds
%   sample rate is in Hz
%   F0 is the fundamental (pitch)
%   f1-f3 are the formant frequencies (set to zero if fewer than 3 formants
%   are required
%   Example: say "oooeeeoooeeeooo" (o.k., it sounds like poor quality 70s daleks, but it
%   is a *simple* artificial vowel)
% fs=10000;
% uu=(jansMakeVowel(0.3, fs, 125, 300,870,2340));
% ee=(jansMakeVowel(0.3, fs, 125, 300,1900,2340));
% soundsc([uu ee uu ee uu], fs)
%
% Another example: morph oo to ee:
% oo2ee=[];
% for f2=870:200:2100, oo2ee=[oo2ee jansMakeVowel(0.3, fs, 125, 300,f2,2340)]; end;
% soundsc(oo2ee,fs)


%y=glottalPulseTrain(F0, sampleRate, dur,0.1);
y  = clicktrain(dur,F0,round(sampleRate));

F  =  [f1, f2, f3,f4]; % Formant frequencies (Hz)
BW = [80,  70,  160,300];  % Formant bandwidths (Hz)
fs = round(sampleRate);              % Sampling rate (Hz)

nsecs = length(F);
R     = exp(-pi*BW/fs);     % Pole radii
theta = 2*pi*F/fs;      % Pole angles
poles = R .* exp(j*theta); % Complex poles
B     = 1;  
A     = real(poly([poles,conj(poles)]));
%freqz(B,A); % View frequency response:

% Convert to parallel complex one-poles (PFE):
[r,p,f] = residuez(B,A);
As      = zeros(nsecs,3);
Bs      = zeros(nsecs,3);
% complex-conjugate pairs are adjacent in r and p:
for i=1:2:2*nsecs
    k       = 1+(i-1)/2;
    Bs(k,:) = [r(i)+r(i+1),  -(r(i)*p(i+1)+r(i+1)*p(i)), 0];
    As(k,:) = [1, -(p(i)+p(i+1)), p(i)*p(i+1)];
end

sos   = [Bs,As]; % standard second-order-section form
iperr = norm(imag(sos))/norm(sos); % make sure sos is ~real
sos   = real(sos); % and make it exactly real

%disp(sprintf('||imag(sos)||/||sos|| = %g',iperr)); % 1.6e-16

% Now filter the clicktrain (y):
sig     = y;
speech  = filter(1,A,sig);
%m=mean(speech);
%speech=speech-m;
speech=speech./sqrt(mean(speech.^2)); % normalise to unit RMS
%speech=speech/max(speech);
%soundsc([sig,speech]); % hear buzz, then 'ah'



