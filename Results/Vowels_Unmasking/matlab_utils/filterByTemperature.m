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
