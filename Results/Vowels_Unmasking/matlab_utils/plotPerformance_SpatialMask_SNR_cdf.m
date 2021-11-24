function plotPerformance_SpatialMask_SNR_cdf

[dataDir, options, c, d] = import_settings()

% For each ferret
files = dir( fullfile(dataDir,'*.mat'));

for i = 1 : numel(files)
        
    [COctrl, COcool, SPctrl, SPcool, SOctrl, SOcool] = import_data(dataDir, files(i).name);
        
    sp = create_figure( files(i).name);
    
    % Line plot
    drawPerformance_CDF(SOctrl, sp(1), c.ctrl); % Signal only - control
    drawPerformance_CDF(SOcool, sp(1), d.ctrl); % Signal only - cooled

    drawPerformance_CDF(COctrl, sp(2), c.coloc); % Colocalized - control
    drawPerformance_CDF(COcool, sp(2), d.coloc); % Colocalized - cooled

    drawPerformance_CDF(SPctrl, sp(3), c.sep); % Separated - control
    drawPerformance_CDF(SPcool, sp(3), d.sep); % Separated - cooled
  
    drawPerformance_CDF(SOctrl, sp(5), c.ctrl); % Signal only
    drawPerformance_CDF(SPctrl, sp(5), c.sep); % Separated
    drawPerformance_CDF(COctrl, sp(5), c.coloc); % Colocalized
    
    drawPerformance_CDF(SOcool, sp(6), d.ctrl); % Signal only
    drawPerformance_CDF(SPcool, sp(6), d.sep); % Separated
    drawPerformance_CDF(COcool, sp(6), d.coloc); % Colocalized

    linkaxes(sp([1 2 3 5 6]),'x')    

    add_bar_plot(sp, COctrl, COcool, SPctrl, SPcool, SOctrl, SOcool)
end