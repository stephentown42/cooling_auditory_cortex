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
