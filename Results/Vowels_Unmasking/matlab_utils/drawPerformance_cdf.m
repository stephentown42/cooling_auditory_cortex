function h = drawPerformance_CDF(X, ax, color)

if isempty(X)
    h = nan; return
end

% Get signal levels
attns = unique(X.Atten);
nAttn = numel(attns);

% Preassign
N = zeros(1, nAttn);
Y = zeros(1, nAttn);
C = zeros(1, nAttn);

% Get performance
for j = 1 : nAttn
    
    rows = X.Atten == attns(j);
    
    N(j) = sum(rows);
    Y(j) = mean(X.Correct(rows)) * 100;
    C(j) = sum(X.Correct(rows));
end

% Filter by sample size
Nt = 6;
attns(N < Nt) = [];
Y(N < Nt) = [];
C(N<Nt) = [];
N(N<Nt) = [];

% Get cumulative proportion
cN = cumsum(C) ./ sum(C);
sigLevel = 60 - attns;
h = bar(sigLevel, cN, 'EdgeColor','none','FaceColor',color,'parent',ax);

set(h,'LineWidth',1.5)