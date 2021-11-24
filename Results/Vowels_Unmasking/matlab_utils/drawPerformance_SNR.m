function h = drawPerformance_SNR(X, ax, color)

if isempty(X)
    h = nan; return
end

% Get signal levels
attns = unique(X.Atten);
nAttn = numel(attns);

% Preassign
N = zeros(1, nAttn);
Y = zeros(1, nAttn);

% Get performance
for j = 1 : nAttn
    
    rows = X.Atten == attns(j);
    
    N(j) = sum(rows);
    Y(j) = mean(X.Correct(rows)) * 100;
end

% Filter by sample size
Nt = 6;
attns(N < Nt) = [];
Y(N < Nt) = [];
N(N<Nt) = [];

% h = plot3(attns,Y,N,'-','Marker','.','LineWidth',1,'MarkerSize',18,'parent',ax);
h = plot3(attns,Y,N,'Marker','.','MarkerSize',18,'parent',ax,'lineStyle','none','color',color);
mdl = fitglm(X.Atten, X.Correct,'distribution','binomial');

xnew = linspace(min(attns), max(attns), 50);
ynew = predict(mdl, xnew') .* 100;
znew = ones( size(ynew));
plot3(xnew,ynew,znew,'-','linewidth',1,'color',color,'parent',ax)

set(h,'LineWidth',1.5)
