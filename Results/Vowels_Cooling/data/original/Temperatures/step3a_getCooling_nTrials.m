function step3a_getCooling_nTrials

if nargin ==0
    pathname = Cloudstation('Vowels\Perceptual_Constancy');
end

pathname = fullfile( pathname, 'Cooling\Data\Cross-referenced Behavior');

% Get files
files = dir( fullfile(pathname, '*.mat'));

% For each file
for i = 1 : numel(files)
    
    % Load data
    load( fullfile(pathname, files(i).name),'behavior','temperatures');
    
    % Filter for bilateral data
    bIdx = behavior.LeftTemperature <= 11 & behavior.RightTemperature <= 11;
    B    = behavior(bIdx,:);
    
    % Remove correction trials
    B = B(B.CorrectionTrial==0,:);
    
    % Draw by F0 and F1
    stimList = [B.Pitch B.F1];
    stims = unique(stimList,'rows');
    nStim = size(stims,1);
    nTrials = nan(nStim,1);
    
    for j = 1 : nStim
        jIdx = ismember(stimList, stims(j,:),'rows');
        nTrials(j) = sum(jIdx);
    end
    
    
    keyboard
    
end