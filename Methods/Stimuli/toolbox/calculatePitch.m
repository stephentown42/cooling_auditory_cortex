function calculatePitch
%
% This function selects the hold time from a range of possible times
% 
% Required gf parameters:
%   pitchMin
%   pitchMax
%   pitchSteps
%   pInd
%
% Parameters generated:
%   pitch

global gf

if gf.pitchMin ~= gf.pitchMax,

    % Linerarly spaced array of times from min to max (dB)

    gf.pitchRange    = gf.pitchMin :(gf.pitchMax - gf.pitchMin)/ gf.pitchSteps : gf.pitchMax;


    % Initialize index variables
    if isfield(gf,'pInd') == 0,                                  
        gf.pInd = 1;
    end

    if isfield(gf,'pitchInd') == 0,                                  
        gf.pitchInd = randperm(length(gf.pitchRange));
    end

    % Calculate time in milliseconds for hold index array value
    % E.g. holdIndii = 1, i = 3, gf.hold = 1500

    i        = gf.pitchInd(gf.pInd);
    gf.pitch = gf.pitchRange(i); 


    % Move onto next index
    gf.pInd    = gf.pInd + 1;


    % When all times have been used once, randomize index array 
    % E.g. holdInd = [4 2 1 3]

    if gf.pInd == length(gf.pitchInd)
        gf.pitchInd = randperm(length(gf.pitchRange));
        gf.pInd     = 1;
    end
    
else 
    gf.pitch = gf.pitchMin;
end
    