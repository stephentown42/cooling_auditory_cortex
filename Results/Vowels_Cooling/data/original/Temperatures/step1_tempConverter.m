function step1_tempConverter(rootDir)
%
% Convert weird temp files from TC Central into table with same file name
% (but different extension)

try


% Define paths
if nargin == 0
    rootDir = Cloudstation('Vowels\Noise\Cooling\Data');
%     rootDir = Cloudstation('Vowels\Spatial_Unmasking\Cooling\Data');
end
% 
% sourceDir = fullfile(rootDir, 'Temperature Records - Original');
% destDir   = fullfile(rootDir, 'Temperature Records - Converted');

% 24 Aug 2017
sourceDir = fullfile(rootDir, 'Temperature Records - Editted');
destDir   = fullfile(rootDir, 'Temperature Records - Editted');

% Get list of ferrets
ferrets = dir( fullfile(sourceDir,'F*'));

% Preassign
headers = {'Sample','Month','Day','Year','Hour','Minute','Second',...
                'Loop_L','ambient_L','Loop_R','ambient_R'};

% For each ferret 
for i = 1 : size(ferrets,1)
            
    ferrDir = fullfile( sourceDir, ferrets(i).name);   % List files
    saveDir = fullfile( destDir,   ferrets(i).name);
    files   = dir( fullfile( ferrDir, '*.txt'));
    
    % For each file
    for j = 1 : numel(files)
                              
        data = [];  % Preassign 

        % Open record
        fid = fopen( fullfile(ferrDir, files(j).name));
        
        % Skip text filler at the start
        for bb = 1 : 15
            b = fgets(fid); 
        end
        
        % Read data rows
        while ~feof(fid)
            
            rowData = fscanf(fid,'%f %f /%f /%f %f :%f :%f %f %f %f %f',[11,1])';                        
            data    = [data; rowData];
        end
        
        % Close record
        fclose(fid);
              
        % Convert to table
        data = array2table(data,'variableNames',headers); 
        
        % Define save name
        saveName = fullfile( saveDir, strrep(files(j).name,'txt','mat'));
        
        % Check overwrite
        if exist(saveName,'file')
            warning('%s already exists - not saved',saveName)
        else
            save(saveName,'data')
        end
    end
end

 catch err
     err
     keyboard
end
