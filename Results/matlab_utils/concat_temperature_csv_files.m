function concat_temperature_csv_files(file_path)
% Build cooling record

% Add temperature to each trial
% Add label (bilateral, right, left)

% Request source directory from user
if nargin == 0
    file_path = uigetdir();
end
     
% Load files
files = dir( fullfile( file_path, '*.csv'));
T = [];

% For each cooling file
for i = 1 : numel(files)
    
    % Load data
    t = readtable( fullfile(file_path, files(i).name));
    
    % Deal with temperature receiver faults - right was always cooler than
    % left but we couldn't record it on the computer. If we had decent
    % equipment then this wouldn't be a problem.
    if ~isempty( strfind(files(i).name, 'RACTL'))
        t.Loop_R    = t.data.Loop_L;
        t.ambient_R = t.data.ambient_L;
    end
    
    % Pad with warm temperatures before and after sessions as
    % interpolation later will screw up if we don't note that the
    % temperature returns to be warm
    zeroRow = t(1,:);
    lastRow = t(end,:);
    
    zeroRow.Sample = zeroRow.Sample -1; 
    zeroRow.datetime = zeroRow.datetime - seconds(1); 
    zeroRow.Loop_L = 37;
    zeroRow.Loop_R = 37;
    
    lastRow.Sample = lastRow.Sample +1; 
    lastRow.datetime = lastRow.datetime + seconds(1);
    lastRow.Loop_L = 37;
    lastRow.Loop_R = 37;
    
    % Assign to structure
    T = [T; zeroRow; t; lastRow];    
end

% Sort by date
T = sortrows(T,{'datetime'});

[save_name, save_path, ~] = uiputfile( fullfile( file_path, '*.csv'), 'Save summary');
writetable(T, fullfile( save_path, save_name))

% Remove error values (generated by temp sensors being disconnected)
% T.Loop_L = filterForErrors(T.datetime, T.Loop_L);
% T.Loop_R = filterForErrors(T.datetime, T.Loop_R);
% 
% T.ambient_L = filterForErrors(T.datetime, T.ambient_L);
% T.ambient_R = filterForErrors(T.datetime, T.ambient_R);



function y = filterForErrors(x, y)
% Replaces values that arise from typical errors produced by the
% temperature recording system when thermocouples are disconnected
%
% Parameters:
%   x : datetime vector
%   y : temperature vector
%
% Returns:
%   y : temperature vector with errors replaced with interpolated values

% Make sure x and y are sorted
[x, idx] = sort(x);
y = y(idx);

% Identify errors
errIdx(:,1) = y > 39 | y < 1;     
% errIdx(:,2) = [0; abs(diff(y))>5];     
errIdx = any(errIdx,2);

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




 