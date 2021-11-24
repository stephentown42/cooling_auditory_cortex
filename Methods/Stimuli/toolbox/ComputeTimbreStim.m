function [vSound] = ComputeTimbreStim(formants)
% 
% Creates vowel or click train 
%
% Includes attenuation and envelope of sounds


global gf

if sum(formants)>0
    
    vowel = newMakeVowel2009(   gf.duration/1000,...
                                gf.fStim, ...
                                gf.pitch,...
                                formants(1),...
                                formants(2),...
                                formants(3),...
                                formants(4));
    % attempt to make difference more salient
  
    % envelope to prevent clicking transients
    vowel   = envelope(vowel,250);
    atten   = gf.atten;
    vSound  = vowel.*10^(-(atten/20));

else
    y       = clicktrain(gf.duration/1000, gf.pitch, gf.fStim);
    vowel   = y./sqrt(mean(y.^2));                              % normalise to unit RMS
    vowel   = envelope(vowel,250);                              % envelope to prevent clicking transients
    atten   = gf.atten - 5;                                     % compensate as clicks seem to be quieter
    vSound  = vowel.*10^(-(atten/20));
end
