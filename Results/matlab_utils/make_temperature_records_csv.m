function make_temperature_records_csv(file_path)
%
% Convert weird temp files from TC Central into table with same file name
% (but different extension)
%
% Parameters
% --------------
% file_path : str
%   Directory containing text files with temperature records in the format
%   saved by the Omega system
%
% Returns
% --------------
% Subdirectory within input directory, contains csv files for each original
% file

try

    % Request source directory from user
    if nargin == 0
        file_path = uigetdir();
    end

    % Preassign
    headers = {'Sample','Month','Day','Year','Hour','Minute','Second',...
                    'Loop_L','ambient_L','Loop_R','ambient_R'};

    % List files
    files = dir( fullfile( file_path, '*.txt'));

    if numel(files) == 0
        error('Could not find any text files in requested directory')
    end

    % Create folder to hold results
    save_path = fullfile( file_path, 'csv_export');
    if ~isfolder( save_path), mkdir(save_path); end

    % For each file
    for j = 1 : numel(files)

        data = [];  % Preassign 

        % Open record
        fid = fopen( fullfile(file_path, files(j).name));

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
        data.datetime = datetime(data.Year, data.Month, data.Day, data.Hour, data.Minute, data.Second);
        data = removevars(data,{'Year','Month','Day','Hour','Minute','Second'});

        % Define save name
        save_file = fullfile( save_path, strrep(files(j).name,'.txt','.csv'));

        % Check overwrite
        if exist(save_file,'file')
            warning('%s already exists - not saved', save_file)
        else
            writetable( data, save_file)
        end
    end

catch err
     err
     keyboard
end
