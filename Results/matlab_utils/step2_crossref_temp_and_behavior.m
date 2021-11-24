function step2_crossref_temp_and_behavior(rootDir)


% Add temperature to each trial
% Add label (bilateral, right, left)

% Define paths
if nargin == 0
%    rootDir = Cloudstation('Vowels\Noise\Cooling\Data'); 
    rootDir = Cloudstation('Vowels\Spatial_Unmasking\Cooling\Data');
end

behavDir = fullfile(rootDir,'GoFerret Performance');
tempDir  = fullfile(rootDir,'Temperature Records - Converted');
saveDir  = fullfile(rootDir,'Cross-referenced Behavior');

% Get ferrets
ferrets = dir( fullfile(tempDir, 'F*'));

% For each ferret
for i = 1 : numel(ferrets)
        
    % Build cooling record
    temperatures = buildCoolingRecord(tempDir, ferrets(i).name);

    % Build behavioral record
    behavior = buildBehavioralRecord(behavDir, ferrets(i).name);    
    
    % Cross reference
    behavior = crossref(temperatures, behavior);
    
    % Draw it out
    fig = drawData(ferrets(i).name, temperatures, behavior);
                
    % Save output
    saveas(fig, fullfile(saveDir, sprintf('%s_time_vs_temperature.fig',ferrets(i).name)))
    save( fullfile(saveDir, sprintf('%s.mat',ferrets(i).name)),'behavior','temperatures')
end


function T = buildCoolingRecord(pathname, ferret)

% Load files
pathname = fullfile(pathname, ferret);
files = dir( fullfile(pathname, '*.mat'));
T     = [];

% For each cooling file
for i = 1 : numel(files)
    
    % Load data
    t = load( fullfile(pathname, files(i).name));
    
    % Deal with temperature receiver faults - right was always cooler than
    % left but we couldn't record it on the computer. If we had decent
    % equipment then this wouldn't be a problem.
    if ~isempty( strfind(files(i).name, 'RACTL'))
        t.data.Loop_R    = t.data.Loop_L;
        t.data.ambient_R = t.data.ambient_L;
    end
    
    % Append borders - warm temperatures before and after sessions as
    % interpolation later will screw up if we don't note that the
    % temperature returns to be warm
    zeroRow = t.data(1,:);
    lastRow = t.data(end,:);
    
    zeroRow.Sample = zeroRow.Sample -1; 
    zeroRow.Second = zeroRow.Second -1; 
    zeroRow.Loop_L = 37;
    zeroRow.Loop_R = 37;
    lastRow.Sample = lastRow.Sample +1; 
    lastRow.Second = lastRow.Second +1;
    lastRow.Loop_L = 37;
    lastRow.Loop_R = 37;
    
    t.data = [zeroRow; t.data; lastRow];
    
    % Assign to structure
    T = [T; t.data];    
end

% Calculate data numbers
T.Datenum = datenum(T.Year, T.Month, T.Day, T.Hour, T.Minute, T.Second);

% Sort by date
T = sortrows(T,{'Datenum'});

% Remove error values (generated by temp sensors being disconnected)
T.Loop_L = filterForErrors(T.Datenum, T.Loop_L);
T.Loop_R = filterForErrors(T.Datenum, T.Loop_R);
T.ambient_L = filterForErrors(T.Datenum, T.ambient_L);
T.ambient_R = filterForErrors(T.Datenum, T.ambient_R);



function y = filterForErrors(x,y)


% Make sure x and y are sorted
[x, idx] = sort(x);
y = y(idx);

% Identify errors
errIdx(:,1) = y > 39 | y < 1;     
% errIdx(:,2) = [0; abs(diff(y))>5];     
errIdx      = any(errIdx,2);

% Split data into good and bad, and then interpolate the bad
y2 = y(~errIdx);
x2 = x(~errIdx);
xe = x(errIdx);
ye = interp1(x2,y2,xe);

% Reconstruct
y = [y2; ye];
x = [x2; xe];

% Resort
[~,idx] = sort(x);
y = y(idx);


function B = buildBehavioralRecord(pathname, ferret)

try
    
% Get files
files   = dir( fullfile(pathname, ferret, '*.txt'));
nFiles  = numel(files);

% Table setup
B = [];
remQ = @(x) strrep(x,'?','');

% For each file
for i = 1 : nFiles
    
   % Get date from filename 
   nPoints = numel(strfind(files(i).name,'.'));
   
   if nPoints == 2
       offset = getFileDate(files(i).name, 'new');
   else
       offset = getFileDate(files(i).name, 'old');
   end
   
   % Import data
   K = importdata( fullfile(pathname, ferret, files(i).name));   
   
   % Format headers to make table compatible
   headers = cellfun(remQ, K.colheaders,'un',0);
   
   % Convert to table 
   Ti = array2table(K.data,'variableNames',headers);
   
   % Add continuous mask 
   if ~isempty( strfind(files(i).name,'continuous'))
       Ti.Mask = repmat(2,size(Ti.Correct));
   end
   
   % Add universal time and file name to distinguish data from other files
   Ti.UniversalStartTime = offset + (Ti.StartTime/(60*60*24));   
   Ti.originalFile       = repmat({files(i).name}, size(Ti,1),1);
   
   % Append to larger data set
   B = [B; Ti];
end

catch err
    err
    keyboard
end


function x = getFileDate(str, method)

sid    = strfind(str,' log');
day    = str2double(str(1:2));
month  = str2double(str(4:5));
year   = str2double(str(7:10));

switch method
    case 'old'
        hour   = str2double(str(sid-5:sid-4));
        minute = str2double(str(sid-2:sid-1));
        second = 0;
    case 'new'        
        hour   = str2double(str(sid-12:sid-11));
        minute = str2double(str(sid-9:sid-8));
        second = str2double(str(sid-6:sid-1));
end

x = datenum(year, month, day, hour, minute, second);


function B = crossref(T,B)

B.LeftTemperature  = interp1(T.Datenum, T.Loop_L, B.UniversalStartTime);
B.RightTemperature = interp1(T.Datenum, T.Loop_R, B.UniversalStartTime);

B.LeftTemperature( isnan(B.LeftTemperature)) = 37;
B.RightTemperature( isnan(B.RightTemperature)) = 37;



function f = drawData(ferret,T,B)

% Fig/Ax
f = figure('name',sprintf('Temperature record: %s', ferret));
hold on

% Cooling Data
plot(T.Datenum,T.ambient_R,'--or')
plot(T.Datenum,T.ambient_L,'--ob')
plot(T.Datenum,T.Loop_R,'r')
plot(T.Datenum,T.Loop_L,'b')

% Behavior
plot(B.UniversalStartTime, B.LeftTemperature,'xb');
plot(B.UniversalStartTime, B.RightTemperature,'xr');

% Axes
dateaxis('x',0)
xlabel('Date')
ylabel(sprintf('Temperature (%cC)', char(176)))




 