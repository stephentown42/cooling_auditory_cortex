function calculateHoldTimes
%
% This function selects the hold time from a range of possible times
% 
% Required gf parameters:
%   holdMin
%   holdMax
%   holdSteps
%   holdIndii
%
% Parameters generated:
%   holdRange
%   holdInd
%   holdTime
%   holdSamples

global gf

% Linerarly spaced array of times from min to max (in milliseconds)
% E.g. holdRange = [500 1000 1500 2000]
gf.holdRange    = gf.holdMin :(gf.holdMax - gf.holdMin)/ gf.holdSteps : gf.holdMax;


% Initialize index variables
if isfield(gf,'holdInd') == 0,                                  
    gf.holdInd = randperm(length(gf.holdRange));
end

if isfield(gf,'holdIndii') == 0,                                  
    gf.holdIndii = 1;
end

% Calculate time in milliseconds for hold index array value
% E.g. holdIndii = 1, i = 3, gf.hold = 1500

i           = gf.holdInd(gf.holdIndii);
gf.holdTime = gf.holdRange(i); 


% Convert value to number of samples (in order to control LED)

gf.holdSamples = ceil((gf.holdTime / 1000) * gf.fStim);


% Move onto next index

gf.holdIndii    = gf.holdIndii + 1;


% When all times have been used once, randomize index array 
% E.g. holdInd = [4 2 1 3]

if gf.holdIndii == length(gf.holdInd)
    gf.holdInd   = randperm(length(gf.holdRange));
    gf.holdIndii = 1;
end