function [COctrl, COcool, SPctrl, SPcool, SOctrl, SOcool] = import_data(dataDir, file_name)

% Open the data
T = load(fullfile(dataDir, file_name)); fprintf('%s\n', file_name)
B = T.behavior;

% Remove correction trials
B(B.CorrectionTrial==1,:) = [];
    
% Filter Data by noise type and mask
CO = filterData(B,[0 1]);   % Colocated
SP = filterData(B,[2 3]);   % Separated
SO = filterData(B,[4 5]);   % Signal only
    
% Run stats
%     getStats(SP, options);    
%     getStats(CO, options);    
%     getStats(SO, options);    
    
% Filter by temperature
[COctrl, COcool] = filterByTemperature(CO, options);    % Colocated
[SPctrl, SPcool] = filterByTemperature(SP, options);    % Separated
[SOctrl, SOcool] = filterByTemperature(SO, options);    % Signal only
    
% Match temperatures
[COctrl, COcool] = matchLevels(COctrl, COcool);
[SPctrl, SPcool] = matchLevels(SPctrl, SPcool);
[SOctrl, SOcool] = matchLevels(SOctrl, SOcool);

% Check sizes
if size(B,1) ~= size(CO,1)+size(SO,1)+size(SP,1)
    warning('Data lost - please investigate')
end


