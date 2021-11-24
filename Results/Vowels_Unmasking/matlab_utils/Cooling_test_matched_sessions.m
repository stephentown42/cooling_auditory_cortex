function Cooling_test_matched_sessions

% Start be defining the limits above and below which you consider cooled
% and control data (thresholds equal to or below/greater than)
options = struct('coolThreshold',   11,...
                 'warmThreshold',   35);
             
% Define colors
c = struct('ctrl',[0 0 0],'coloc',[1 0 0],'sep',[0 0.5 0]);
d = struct('ctrl',[0.5 0.5 0.5],'coloc',[1 0.4 0.4],'sep',[0.1 0.9 0.1]);

% List ferrets
dataDir = Cloudstation('Vowels\Spatial_Unmasking\Cooling\Vowels\Cross-referenced Behavior');
ferrets = dir( fullfile(dataDir,'*.mat'));

% For each ferret
for i = 1 : numel(ferrets)
        
    % Update user 
    fprintf('%s\n', ferrets(i).name)
    
    % Open the data
    load(fullfile(dataDir, ferrets(i).name),'behavior');  
        
    % Remove correction trials
    behavior(behavior.CorrectionTrial==1,:) = [];
    
    % Create variable 'Day' to reflect the rounded down datenum
    behavior.day = floor(behavior.UniversalStartTime);
        
    % Split data by cooling
    [ctrl_data, test_data] = filterByTemperature(behavior, options);
    
    % Filter for cooling days
    test_days = unique(test_data.day);   
    match_idx = bsxfun(@eq, ctrl_data.day, transpose(test_days));
    ctrl_data = ctrl_data( any(match_idx, 2), :);
    
    % Filter Data by noise type and mask
    COctrl = filterData(ctrl_data, [0 1]);   % Colocated
    SPctrl = filterData(ctrl_data, [2 3]);   % Separated
    SOctrl = filterData(ctrl_data, [4 5]);   % Signal only
        
    COcool = filterData(test_data, [0 1]);   % Colocated
    SPcool = filterData(test_data, [2 3]);   % Separated
    SOcool = filterData(test_data, [4 5]);   % Signal only
       
    % Run stats
%     getStats(SP, options);    
%     getStats(CO, options);    
%     getStats(SO, options);    
        
        
%     % Match temperatures
%     [COctrl, COcool] = matchLevels(COctrl, COcool);
%     [SPctrl, SPcool] = matchLevels(SPctrl, SPcool);
%     [SOctrl, SOcool] = matchLevels(SOctrl, SOcool);
    
    % Check sizes
%     if size(behavior,1) ~= size(CO,1)+size(SO,1)+size(SP,1)
%         warning('Data lost - please investigate')
%     end
        
    % New figure
    figure('name',ferrets(i).name)
    sp(1) = subplot(2,3,1); title('Signal Only')
    sp(2) = subplot(2,3,2); title('Colocalized')
    sp(3) = subplot(2,3,3); title('Separated')
    sp(4) = subplot(2,3,4); title('Across Attn')
    sp(5) = subplot(2,3,5); title('Control')
    sp(6) = subplot(2,3,6); title('Cooled')
    
    set(sp,'nextPlot','add','ylim',[40 100],'FontSize',9);   % Hold on 
    
    
    for j = 1 : numel(sp)
        ylabel(sp(j),'% Correct')
        xlabel(sp(j),'Attenuation (dB)')
    end
    
    % Line plot
    drawPerformance(SOctrl, sp(1), c.ctrl); % Signal only - control
    drawPerformance(SOcool, sp(1), d.ctrl); % Signal only - cooled
    
    drawPerformance(COctrl, sp(2), c.coloc); % Colocalized - control
    drawPerformance(COcool, sp(2), d.coloc); % Colocalized - cooled
    
    drawPerformance(SPctrl, sp(3), c.sep); % Separated - control
    drawPerformance(SPcool, sp(3), d.sep); % Separated - cooled
    
    drawPerformance(SOctrl, sp(5), c.ctrl); % Signal only
    drawPerformance(SPctrl, sp(5), c.sep); % Separated
    drawPerformance(COctrl, sp(5), c.coloc); % Colocalized
    
    drawPerformance(SOcool, sp(6), d.ctrl); % Signal only
    drawPerformance(SPcool, sp(6), d.sep); % Separated
    drawPerformance(COcool, sp(6), d.coloc); % Colocalized
    
    
    
    % Bar plot
    myBar = @(x) mean(x).*100;
    axes(sp(4))
    
    b(1) = bar(1, myBar(SOctrl.Correct),'FaceColor','k');
    b(2) = bar(2, myBar(SOcool.Correct),'FaceColor',[0.5 0.5 0.5]);
    b(3) = bar(4, myBar(SPctrl.Correct),'FaceColor',[0 0.5 0]);
    b(4) = bar(5, myBar(SPcool.Correct),'FaceColor',[0.1 0.9 0.1]);
    b(5) = bar(7, myBar(COctrl.Correct),'FaceColor','r');
    b(6) = bar(8, myBar(COcool.Correct),'FaceColor',[1.0 0.4 0.4]);
    
    set(sp(4),'xtick',2:3:8,'xticklabel',{'Signal only','Separated','Colocalized'})
    
    
    % Change color
    c = struct('ctrl',[0 0 0],'coloc',[1 0 0],'sep',[0 0.5 0]);
    d = struct('ctrl',[0 0 0]+0.5,'coloc',[1 0.4 0.4],'sep',[0.1 0.9 0.1]);
%     
%     set([h(1,1) h2(1,1)],'color','k')
%     set([h(2,1) h2(2,1)],'color','r')
%     set([h(3,1) h2(3,1)],'color',[0 0.5 0])
%     
%     set([h(1,2) h2(1,2)],'color',[0.5 0.5 0.5])    
%     set([h(2,2) h2(2,2)],'color',[1.0 0.4 0.4])
%     set([h(3,2) h2(3,2)],'color',[0.1 0.9 0.1])
        
    % Link axes
    linkaxes(sp([1 2 3 5 6]),'x')    
end



function C = filterData(B, masks)

if isempty(B)
    C = []; return
end

% Filter by noise type
isOk = B.SpatialMask == masks(1) | B.SpatialMask == masks(2);
C    = B(isOk,:);  % Apply filter


function [x,y] = matchLevels(x,y)

% Get levels
xLevels = unique(x.Atten);
yLevels = unique(y.Atten);

% Identify shared levels
sharedLevels = intersect(xLevels, yLevels);

% Filter
xTrials = ismember(x.Atten, sharedLevels);
yTrials = ismember(y.Atten, sharedLevels);

x = x(xTrials,:);
y = y(yTrials,:);




function getStats(S, options)

% Get number of masks
masks  = unique(S.Mask);
nMask = numel(masks);

% For each mask
for i = 1 : nMask

    % Filter for mask
    rows = S.Mask == masks(i);    
    T    = S(rows,:);
    
    % Calculate average temperature
    T.Temperature = mean([T.LeftTemperature T.RightTemperature],2);
    
    % Get cold attenuation levels
    cooledTrials = T.Temperature <= options.coolThreshold;
    cooledAttn   = unique(T.Atten(cooledTrials));
    
    % Get the number of each cooled level
    trialOk = bsxfun(@eq, T.Atten, cooledAttn');
    nTrials = sum(trialOk);
    
    % Require threshold number of trials
    attnOk     = nTrials > 1;
    cooledAttn = cooledAttn(attnOk);
    %nTrials    = nTrials(attnOk);
    
    % Filter data for cooled attenuations with enough trials
    trialOk = bsxfun(@eq, T.Atten, cooledAttn');
    T       = T(any(trialOk,2),:);
        
    % Filter for trials within cool and warm windows
    cooledTrials = T.Temperature <= options.coolThreshold;
    warmTrials   = T.Temperature >= options.warmThreshold;    
    T.trialType  = nan(size(T,1),1);
    
    T.trialType(cooledTrials) = -1;
    T.trialType(warmTrials)   = 1;

    T = T(~isnan(T.trialType),:);
    T.trialType = categorical(T.trialType);
    
    % Report mask to user
    fprintf('Mask = %d\n',masks(i))
    
    % Create analysis table
    M = table(T.Atten,T.trialType,T.Correct,'VariableNames',{'Atten','TrialType','Correct'});
    
    % Fit logistic regression model
    mdl = fitglm(M,'interactions','Distribution','Binomial')
    
    % Check confidence intervals
    confint = coefCI(mdl)
                    
end

function [control, cooled] = filterByTemperature(X, options)

if isempty(X)
    [control, cooled] = deal([]); return
end

% Split by temperature
coolThreshold = options.coolThreshold;
warmThreshold = options.warmThreshold;

controlRows = X.LeftTemperature >= warmThreshold & X.RightTemperature >= warmThreshold;
cooledRows  = X.LeftTemperature <= coolThreshold & X.RightTemperature <= coolThreshold;

cooled  = X(cooledRows,:);
control = X(controlRows,:);





function h = drawPerformance(X, ax, color)

if isempty(X)
    h = nan; return
end

% Specify required number of stimuli
Nt = 6;

% Get signal levels
attns = unique(X.Atten);
nAttn = numel(attns);

% Preassign
N = zeros(1, nAttn);
Y = zeros(1, nAttn);
h = nan(1,nAttn);

% Get performance
for j = 1 : nAttn
    
    rows = X.Atten == attns(j);
    
    N(j) = sum(rows);
    Y(j) = mean(X.Correct(rows)) * 100;
    
    % Filter by sample size
    if N(j) > Nt
        h(j) = bar( attns(j), Y(j),'parent',ax);
    end
end

h = exciseRows(h);
set(h,'FaceColor',color,'EdgeColor','none')



