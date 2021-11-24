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