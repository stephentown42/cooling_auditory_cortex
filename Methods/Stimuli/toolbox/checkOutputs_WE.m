function checkOutputs_WE(nSensors)  
%This function is expandable to any number of sensors
global DA gf 

for j = 1 : length(nSensors)
    
    signal = DA.GetTargetVal(sprintf('%s.sensor%d',gf.stimDevice,j));
  
    %update gui
%     handle = eval(sprintf('h.bit%d',nSensors(j)));
%     set(handle,'val',signal)

end
