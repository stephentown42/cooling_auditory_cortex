function h = drawPerformance_bar(X, ax, color)

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



