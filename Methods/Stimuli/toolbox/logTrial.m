function logTrial(centerReward, response)                                                %#ok<*INUSL>

% Reports stimulus and response parameters 

global gf

if ischar(response), % Enter string as arguement to get header
    
    headings = {'Trial','CorrectionTrial?','StartTime','CenterReward?','F1','F2','F3','F4','HoldTime','Atten',...
                'Pitch','Side','Response','RespTime','Correct'};

        for i = 1 : length(headings),
            fprintf(gf.fid, '%s\t', headings{i});
        end

    fprintf(gf.fid,'\n');
    
    % Initiate trial number
    gf.TrialNumber  = 1;
else    
    
    if ~isfield(gf,'side'),
        gf.side = -99;
    end
    
    if ~isfield(gf,'holdTime'),
        gf.holdTime = -99;
    end

    if ~isfield(gf,'atten'),
        gf.atten = -99;
    end
    
    if ~isfield(gf,'pitch'),
        gf.pitch = -99;
    end
    
    % For levels with one sound
    if ~isfield(gf,'formants')
        gf.formants = [-99 -99 -99 -99];                           % Sessions involving only one sound                    
    end
    
%     %For levels with multiple sounds
%     for i = 1 : 10,
%         fieldName = sprintf('sound%d',gf.side);
%         
%         if isfield(gf, fieldName)
%             f = eval(sprintf('gf.sound%d',gf.side));       % Sessions involving multiple sounds  
%         end
%     end
    
    if isfield(gf,'side'),
        if gf.side >= 0,
            correct = response == gf.side;
        else
            correct = -1;
        end
    else
        correct = -1;
    end

    %           variable                 format            
    output = {'gf.TrialNumber'          ,'%d'   ;
              'gf.correctionTrial'      ,'%d'   ;
              'gf.startTrialTime'       ,'%.3f' ;
              'centerReward'            ,'%d'   ;
              'gf.formants(1)'          ,'%d'   ;
              'gf.formants(2)'          ,'%d'   ;
              'gf.formants(3)'          ,'%d'   ;
              'gf.formants(4)'          ,'%d'   ;
              'gf.holdTime'             ,'%d'   ;
              'gf.atten'                ,'%.1f' ;
              'gf.pitch'                ,'%d'   ;
              'gf.side'                 ,'%d'   ;
              'response'                ,'%d'   ;
              'gf.responseTime'         ,'%.3f' ;
              'correct'                 ,'%d'   };


        for i = 1 : length(output),
        
            variable = eval(output{i,1});
            format   = output{i,2};
        
            fprintf(gf.fid, format, variable);          % Print value
            fprintf(gf.fid,'\t');                       % Print delimiter (tab so that excel can open it easily)
        end

        fprintf(gf.fid,'\n');                           % Next line
        
        % Move to next trial
        gf.TrialNumber  = gf.TrialNumber + 1;
end
 
 
 