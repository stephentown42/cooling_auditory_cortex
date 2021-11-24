function S = cooling_perm_test(nX, nY, correctX, correctY)
%
% This test calculates the difference in proportion correct between
% conditions X (e.g. control) and Y (e.g. cooled)
%
% nX, nY = number of trials overall
% correctX, correctY = number of trials correct

% Options
nIterations = 1e4;
draw = false; % Allows visualization of permuted distribution

% Make repeatable
rng(1)

%% Generate arrays of data
x_response = zeros(nX,1);
y_response = zeros(nY,1);

x_response(1:correctX) = 1;
y_response(1:correctY) = 1;

x_predictor = zeros(nX,1);
y_predictor = ones(nY,1);

% Bring together arrays
predictor = [x_predictor; y_predictor]; % is cooled or not
response  = [x_response; y_response]; % is correct or not

nTotal = nX + nY;


%% Run permuation test

% Calculate probabilities for x and y from true data
p0_true = mean( response(predictor == 0));
p1_true = mean( response(predictor == 1));

test_val = p1_true - p0_true;


% Preassign arrays for shuffled results
[p0, p1] = deal( nan(nIterations, 1));

% For each iteration
for i = 1 : nIterations 
    
    % Shuffle predictor
    shuffled_predictor = predictor(randperm(nTotal));
   
    % Recompute probabilities
    p0(i) = mean( response(shuffled_predictor == 0));
    p1(i) = mean( response(shuffled_predictor == 1));
end

% Calculate permuted value
S.perm_val = p1 - p0;

% Calculate permuted value being lower than
S.p_below = sum(S.perm_val < test_val) / nIterations;
S.p_above = sum(S.perm_val > test_val) / nIterations;

%% Draw 
if draw
    edges = -1 : 0.001 : 1;
    n = histc(S.perm_val, edges);

    figure
    hold on

    bar(edges, n, 'histc')
    plotYLine(test_val)
end

