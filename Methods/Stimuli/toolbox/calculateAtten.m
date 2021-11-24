function calculateAtten
%
% This function selects the hold time from a range of possible times
% 
% Required gf parameters:
%   attenMin
%   attenMax
%   attenSteps
%   aInd
%
% Parameters generated:
%   atten

global gf

% Linerarly spaced array of times from min to max (dB)

gf.attenRange    = gf.attenMin :(gf.attenMax - gf.attenMin)/ gf.attenSteps : gf.attenMax;


% Initialize index variables
if isfield(gf,'aInd') == 0,                                  
    gf.aInd = 1;
end

if isfield(gf,'attenInd') == 0,                                  
    gf.attenInd = randperm(length(gf.attenRange));
end

% Calculate time in milliseconds for hold index array value
% E.g. holdIndii = 1, i = 3, gf.hold = 1500

i        = gf.attenInd(gf.aInd);
gf.atten = gf.attenRange(i); 


% Move onto next index
gf.aInd    = gf.aInd + 1;


% When all times have been used once, randomize index array 
% E.g. holdInd = [4 2 1 3]

if gf.aInd == length(gf.attenInd)
    gf.attenInd = randperm(length(gf.attenRange));
    gf.aInd     = 1;
end