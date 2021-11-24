function checkOutputs(bits)  
%This function is expandable to any number of sensors
global DA gf h

for j = 1 : length(bits)
    
    signal = invoke(DA,'GetTargetVal',sprintf('%s.bit%d',gf.stimDevice,bits(j)));
  
    %update gui
    handle = eval(sprintf('h.bit%d',bits(j)));
    set(handle,'val',signal)

end
