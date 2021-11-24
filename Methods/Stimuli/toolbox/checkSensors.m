function checkSensors(bits, vars)  
%
% This function checks the value of the bit inputs to the RM1, and also the
% parameter tags known as licks. Licks indicate when a sensor has been held
% for the minHoldTime. 
%

global DA gf h

for j = 1 : length(bits)
    
    bit      = bits(j);
    variable = vars{j};
    
    % Bit signal
    %
    % The bit signal is the input to the RM1, it will go high whenever
    % the sensor is covered. 
    %
    % It does not reflect a successful lick, as the sensor may not be
    % covered for long enough.
    %
    % Note also that the low sample frequency of Matlab means that the GUI
    % may not always show the bit signals that only occur over short
    % intervals.
    %
    
    handle = eval(sprintf('h.bit%d', bit));
    
    bitSignal = DA.GetTargetVal(sprintf('%s.sensor%d', gf.stimDevice, bit));
    set(handle,'val',bitSignal)
    

    
    % Lick signal
    %
    % The lick signal goes high when the animal holds it's head at the
    % spout for the minimum hold time. 
    %
    % It does not therefore represent the input to the RM1
    
    parTag = sprintf('%s.%sLick',gf.stimDevice,variable);
    handle = eval(sprintf('h.%sLick',variable));
    
    lickSignal  = invoke(DA,'GetTargetVal',parTag);
    
    set(handle,'val',lickSignal)
    

end
