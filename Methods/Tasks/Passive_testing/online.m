function varargout = online(varargin)
% ONLINE MATLAB code for online.fig
%      ONLINE, by itself, creates a new ONLINE or raises gfe existing
%      singleton*.
%
%      H = ONLINE returns gfe handle to a new ONLINE or gfe handle to
%      gfe existing singleton*.
%
%      ONLINE('CALLBACK',hObject,eventData,handles,...) calls gfe local
%      function named CALLBACK in ONLINE.M wigf gfe given input arguments.
%
%      ONLINE('Property','Value',...) creates a new ONLINE or raises gfe
%      existing singleton*.  Starting from gfe left, property value pairs are
%      applied to gfe GUI before online_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to online_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit gfe above text to modify gfe response to help online

% Last Modified by GUIDE v2.5 02-Aug-2013 00:29:03

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @online_OpeningFcn, ...
                   'gui_OutputFcn',  @online_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before online is made visible.
function online_OpeningFcn(hObject, ~, handles, varargin)


global DA gf h rstr

handles.output = hObject;
guidata(hObject, handles);
h = handles;

% Establish connection with TDT 
DA = actxcontrol('TDevAcc.X');
DA.ConnectServer('Local');


% Ensure correct project is on RZ6
ProjectID = DA.GetTargetVal(sprintf('%s.ProjectID', gf.stimDevice));

if ProjectID ~= -55
    
    % Close connections and windows
    DA.CloseConnection;
    close(handles.figure1)
    
    % Restore default paths
    path(gf.defaultPaths)

    % Delete structures
    clear global DA gf h
    clear
    gf = [];

    % Warn user
    error('You have failed to select the correct project - further failure will not be tolerated')
end


% Choose whether to record or not
choice = questdlg('Do you want to record neural data to tank during task?', 'Neural Recordings');
              
switch choice
    
    case 'Yes'       
         gf.subjectDir = gf.saveDir(max(strfind( gf.saveDir,'\')):end);
        gf.tankDir = ('T:\Data');
        gf.tankDir = fullfile(gf.tankDir, gf.subjectDir);
        
        if ~isdir(gf.tankDir),
            warning('Tank \n %s \n does not exist - please create in open Ex')          %#ok<*WNTAG>
        end
        
        DA.SetTankName(gf.tankDir)
        DA.SetSysMode(3);
        
        pause(3)
        
        % Get block name
        TT = actxcontrol('TTank.X');
        TT.ConnectServer('Local','Me');
        TT.OpenTank(gf.tankDir,'R'); 
        gf.recBlock = TT.GetHotBlock;
        TT.CloseTank; 
        TT.ReleaseServer; 
        clear TT
        
        if isempty(gf.recBlock), 
            gf.recBlock = 'UnknownBlock';
        end
        
    case 'No'        
        DA.SetSysMode(2);
        gf.recBlock = 'log';
    
    case 'Cancel'
        return
end
              

% Find out sample rates
gf.fStim = DA.GetDeviceSF(gf.stimDevice);       %was Srate in jenny's code but changed to accomodate multiple devices
gf.fRec  = DA.GetDeviceSF(gf.recDevice);


if gf.fStim < 1, 
    gf.fStim = 48828.125; 
    warning('RZ6 returned erroneous sample rate - please make a note in the log book')
end

if gf.fRec < 1, 
    gf.fRec = 24414.0625; 
end

% Reset all parameter tags in GUI
tags = {'bit0C','bit1C','bit2C','bit4C','bit5C','bit6C','bit7C',...
        'leftLick','centerLick','rightLick',...
        'leftValve','centerValve','rightValve'};

for i = 1 : length(tags)

    tag = sprintf('%s.%s',gf.stimDevice, tags{i});
    DA.SetTargetVal(tag,0);   
end


%Set date in GUI
t        = fix(clock);    
temp{1}  = sprintf('%02d-%02d-%02d',t(3),t(2),t(1)); 
temp{2}  = sprintf('%02d:%02d:%02d',t(4),t(5),t(6));
set(handles.dateH,'string',sprintf('%s\n%s\n',temp{1},temp{2}))

    
% Make a new tab delimited file 
    paramFile = gf.paramFile(1:length(gf.paramFile)-4);                  % Remove extension from file name
    logName   = sprintf('%02d_%02d_%02d %s %02d_%02d %s.txt', t(3), t(2), t(1), paramFile, t(4), t(5), gf.recBlock);      % Time Filename log.txt   
    
    gf.fid    = fopen( fullfile(gf.saveDir, logName), 'wt+');    

    logTrial(0,'header')  % Writes header in log
    
    set(h.saveTo, 'string', strcat('Save to: ',gf.saveDir,'\', logName))
    
    %Set devices
    set(handles.devices,'string',sprintf(' %s \n %.3f',gf.stimDevice, gf.fStim))
    
    % Initialize GUI control parameters    
   
    if isfield(gf,'holdMin') && isfield(gf,'holdSteps') && isfield(gf,'holdMax'),
        set(handles.editHoldMin,    'string', num2str(gf.holdMin))  
        set(handles.editHoldSteps,  'string', num2str(gf.holdSteps)) 
        set(handles.editHoldMax,    'string', num2str(gf.holdMax))    
    end
    
    if isfield(gf,'attenMin') && isfield(gf,'attenSteps') && isfield(gf,'attenMax'),
        set(handles.editAttenMin,   'string', num2str(gf.attenMin))
        set(handles.editAttenSteps, 'string', num2str(gf.attenSteps))
        set(handles.editAttenMax,   'string', num2str(gf.attenMax))   
    end
    
    if isfield(gf,'pitchRange'),
        set(handles.editPitchMin,   'string', num2str(min(gf.pitchRange)))
        set(handles.editPitchSteps, 'string', num2str(length(gf.pitchRange)))
        set(handles.editPitchMax,   'string', num2str(max(gf.pitchRange)))       
    end
    
    if isfield(gf,'pitchMin') && isfield(gf,'pitchSteps') && isfield(gf,'pitchMax'),
        set(handles.editPitchMin,   'string', num2str(gf.pitchMin))
        set(handles.editPitchSteps, 'string', num2str(gf.pitchSteps))
        set(handles.editPitchMax,   'string', num2str(gf.pitchMax))
    end
        
    set(handles.editLeftValveTime,  'string',num2str(gf.leftValveTime))
    set(handles.editCenterValveTime,'string',num2str(gf.centerValveTime))
    set(handles.editRightValveTime, 'string',num2str(gf.rightValveTime))
    
    set(handles.slideCenterRewardP, 'value', gf.centerRewardP)
    set(handles.editCenterRewardP, 'string', num2str(gf.centerRewardP))
    
    
% Position Online GUI
    set(h.figure1, 'units',         'centimeters',...
                   'position',      [ -28.0510    7.6935   22.5518   16.2331],...
                   'KeyPressFcn',   @KeyPress)

% Performance               
    % Create figure
    h.performanceF = figure('NumberTitle',    'off',...
                             'name',           'Performance (no trials yet completed)',...
                             'color',          'k',...%                             'units',          'centimeters',...                             'position',       [-10.6282  -10.6810    8.9890    8.5131],...
                             'MenuBar',        'none',...
                             'KeyPressFcn',    @KeyPress);    
    % Create axes                  
    h.performanceA = axes( 'position',      [0.1 0.1 0.6 0.85],...
                            'FontSize',     8,...
                            'FontName',     'arial',...
                            'color',        'none',...
                            'xcolor',       'w',...
                            'xdir',         'reverse',...
                            'xlim',         [0 10],...
                            'ycolor',       'w',...
                            'ylim',         [0 6],...
                            'ytick',        1:5,...
                            'yaxislocation','right',...
                            'yticklabel',   {'Right - Incorrect','Right - Correct','Aborted','Left - Correct','Left - Incorrect'});
     xlabel('Trials (n)')
     
     % Create bars
     colors = [255 160 122;   % Right-incorrect: lightsalmon1 
               255 0   0  ;   % Right-correct: 	 red
               150 150 150;   % Aborted:         grey
               255 255 0  ;   % Left-correct:    yellow
               255 246 143];  % Left-incorrect:  kahki 1
     
     for i = 1 : 5,
        hold on 
            barh(i, 0, 'FaceColor', colors(i,:)/255, 'edgecolor','none','barWidth', 0.1)
        hold off
     end
                   
% Timeline               
    % Create figure
    h.timelineF = figure('NumberTitle',    'off',...
                          'name',           'Timeline',...
                          'color',          'w',...%                           'units',          'centimeters',...%                           'position',       [-27.8923   -1.2426   26.0152    7.8786],...
                          'MenuBar',        'none',...
                          'KeyPressFcn',    @KeyPress);    
                      
    h.timelineA = axes('position',   [0.1 0.1 0.85 0.85],...
                        'FontSize',   8,...
                        'FontName',   'arial',...
                        'color',      'none',...
                        'ylim',       [0 3.5],...
                        'ytick',      [0.8 1.8 2.8],...
                        'yticklabel', {'Left','Center','Right'});
                    

    xlabel('Time (seconds)')
    ylabel('Events')
    
    
    if str2num(gf.filename(6:7))>=20 && str2num(gf.filename(6:7))<=30 % JB's passive
        type = str2num(gf.filename(6:7));
        LoadPassiveTrialStructure(type)
   
        gf.Index = 1;
    elseif str2num(gf.filename(6:7))==81 % AV stim for Ana's project
        type = (gf.filename(9:10));
        
        % Load inverse filters for sound calibration
        gf.fltL = load( fullfile(gf.calibDir, 'fltL.mat'), 'flt');
        gf.fltR = load( fullfile(gf.calibDir, 'fltR.mat'), 'flt');
        
        if strcmp(type,'OA')
            load('C:\Users\Ferret\Documents\MATLAB\Applications\GoFerret\MRC_speech_test\AVstimJKB_OA_180219.mat');
            gf.stim = stim;            
            gf.stimArray = stimuliID;
            gf.metadata = metadata;

        elseif strcmp(type,'TC')
            load('C:\Users\Ferret\Documents\MATLAB\Applications\GoFerret\MRC_speech_test\AVstimJKB_TC_210319.mat');
            gf.stim = stim;
            gf.stimArray = stimuliID;
            gf.metadata = metadata;
        end
    else
        % Load stimuli
        disp('WARNING: these are probably not what you want!!')
        load('C:\Users\Ferret\Documents\MATLAB\Applications\GoFerret\MRC_speech_test\AVstimJKB150219.mat')
        %       load('C:\Users\ferret2\Documents\MATLAB\Applications\GoFerret\MRC_speech_test\adaptTest_eu_30Nov17.mat')
%         load('C:\Users\ferret\Documents\MATLAB\Applications\GoFerret\MRC_speech_test\stim_Vowels_eu_14Aug14.mat')
%         load('C:\Users\ferret\Documents\MATLAB\Applications\GoFerret\MRC_speech_test\stim_Vowels_ai_14Aug14.mat')
        gf.stim = stim;
        gf.metadata = metadata;        
        if exist('mask','var'), gf.mask = mask; end

        % Level 84 replicate stimuli across masks 
        if strcmp(gf.filename,'level84')
        
            % Preassign
            nStim = numel(gf.metadata);
            unmasked_metadata = cell(1,nStim);
            
            % For each stimulus, duplicate metadata and add mask value
            for i = 1 : nStim                                
               unmasked_metadata{i} = [gf.metadata{i} 0];
               gf.metadata{i} = [gf.metadata{i} 1];
            end
            
            % Combine / replicate data sets
            gf.stim = [gf.stim gf.stim];
            gf.metadata = [gf.metadata unmasked_metadata];            
        end
    end

% Setup timer
h.tasktimer = timer( 'TimerFcn',         sprintf('%s',gf.filename),...
                    'BusyMode',         'drop',...
                    'ExecutionMode',    'fixedRate',...
                    'Period',           gf.period);                    

% Initialize variables
gf.pInd      = 0;
gf.startTime = now;    
gf.status    = 'PrepareStim';   


if isvalid(h.tasktimer) == 1,
    start(h.tasktimer);
end


function varargout = online_OutputFcn(~, ~, ~)  %#ok<STOUT>
%varargout{1} = handles.output;


%%%%%%%%%%%%%%%%%%%%%%% CONTROLABLE PARAMETERS %%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% gf.variable = str2num( get(handles.variable,'value'))
% 

% Hold time controls
function setHoldMin_Callback(~, ~, handles)

global gf
gf.holdMin = str2num( get(handles.editHoldMin,'string')); %#ok<*ST2NM>

function setHoldSteps_Callback(~, ~, handles)

global gf
gf.holdSteps = str2num( get(handles.editHoldSteps,'string'));

function setHoldMax_Callback(~, ~, handles)

global gf
gf.holdMax = str2num( get(handles.editHoldMax,'string'));


% Attenuation controls
function setAttenMin_Callback(~, ~, handles)

global gf
gf.attenMin = str2num( get(handles.editAttenMin,'string'));

function setAttenSteps_Callback(~, ~, handles)

global gf
gf.attenSteps = str2num( get(handles.editAttenSteps,'string'));

function setAttenMax_Callback(~, ~, handles)

global gf
gf.attenMax = str2num( get(handles.editAttenMax,'string'));


% Pitch controls
function setPitchMin_Callback(~, ~, handles)

global gf
gf.pitchMin = str2num( get(handles.editPitchMin,'string'));

function setPitchSteps_Callback(~, ~, handles)

global gf
gf.pitchSteps = str2num( get(handles.editPitchSteps,'string'));

function setPitchMax_Callback(~, ~, handles)

global gf
gf.pitchMax = str2num( get(handles.editPitchMax,'string'));

% Valve time controls

function setLeftValveTime_Callback(~, ~, handles)

global gf
gf.leftValveTime = str2num( get(handles.editLeftValveTime,'string')); 

function setCenterValveTime_Callback(~, ~, handles)

global gf
gf.centerValveTime = str2num( get(handles.editCenterValveTime,'string')); 

function setRightValveTime_Callback(~, ~, handles)

global gf
gf.rightValveTime = str2num( get(handles.editRightValveTime,'string')); 




%%%%%%%%%%%%%%%%%%%%%%%%%%%% Key Press %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%   Monitors key pressed when online GUI is current figure
%
%	Key:        name of the key that was pressed, in lower case
%	Character:  character interpretation of the key(s) that was pressed
%	Modifier:   name(s) of the modifier key(s) (i.e., control, shift) pressed
%
function KeyPress(~,event)

global gf

switch event.Character
    case '+'        
        valve(6, gf.centerValveTime, 1, 'center'); %valve(bit, pulse time, pulse number, %sValve)
        
    case '{'
        valve(4, gf.leftValveTime, 1, 'left'); 
        
    case '}'        
        valve(5, gf.rightValveTime, 1, 'right'); 
end


%%%%%%%%%%%%%%%%%%%%%%%%%%% Unit Graphics %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function addUnit_Callback(~,~,~)

global h

list = get(h.unitList,'string');
str  = input('Channel to add: ');

list{end+1} = str;

set(h.unitList,'string',list)


function removeUnit_Callback(~,~,~)

global h

str = get(h.unitList,'string');
val = get(h.unitList,'value');

str(val) = [];
set(h.unitList,'string',str)

%%%%%%%%%%%%%%%%%%%%%%%%%%% Valve Controls %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Left Valve Control
function leftValveC_Callback(~, ~, handles)

global gf

if get(handles.leftValveC,'value') == 1 && get(handles.enableControl,'value') == 1,
    valve(4, gf.leftValveTime, 1, 'left');                                                 %valve(bit, pulse time, pulse number, %sValve)
end

%Center Valve Control
function centerValveC_Callback(~, ~, handles)

global gf

if get(handles.centerValveC,'value') == 1 && get(handles.enableControl,'value') == 1,
    valve(6, gf.centerValveTime, 1, 'center'); 
end

%Right Valve Control
function rightValveC_Callback(~, ~, handles)

global gf

if get(handles.rightValveC,'value') == 1 && get(handles.enableControl,'value') == 1,
    valve(5, gf.rightValveTime, 1, 'right'); 
end

function slideCenterRewardP_Callback(~, ~, handles)

global gf

val = get(handles.slideCenterRewardP,'value');

set(handles.editCenterRewardP, 'string', sprintf('%.2f',val));
gf.centerRewardP = val;


function editCenterRewardP_Callback(~, ~, handles)

global gf

str              = get(handles.editCenterRewardP,'string');  
gf.centerRewardP = str2num(str); %#ok<ST2NM>



%%%%%%%%%%%%%%%%%%%%%%%%%%%%% GRAPHICS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%PLOT SOUND WAVEFORM
function plotWaveform_Callback(~, ~, ~)

plotWaveform   %see toolbox


%PLOT SPECTROGRAM OF STIMULUS
function plotSpectrogram_Callback(~, ~, ~)

plotSpectrogram % see toolbox


%%%%%%%%%%%%%%%%%%%%%%%%% EXIT BUTTON %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function Exit_Callback(~, ~, handles)                                 %#ok<*DEFNU>

global DA gf h      


    % Turn valves off
    invoke(DA,'SetTargetVal',sprintf('%s.pulseThi',gf.stimDevice),0.1);
    tags2= {'leftValve','rightValve','centerValve'};
    for i = 1 : 3,       
        invoke(DA,'SetTargetVal',sprintf('%s.%s',gf.stimDevice, tags2{i}),1);
        invoke(DA,'SetTargetVal',sprintf('%s.%s',gf.stimDevice, tags2{i}),0);
    end


    % Check valves are closed
    tags = {'bit4','bit5','bit6'};    
    val  = NaN(3,1);
    
    for i = 1 : length(tags)

        tag    = sprintf('%s.%s',gf.stimDevice, tags{i});
        val(i) = DA.GetTargetVal(tag);   
    end

%     if any(val)    
%         msgbox('Warning: Valves open. Please close manually or wait until closed\n Program will not close until valves do')
%         val
%     else

    % Close log file
    fclose(gf.fid);
    
    % Report data to command window
    l_incorrect  = get( findobj(h.performanceA,'XData',5), 'YData'); % Left  incorrect
    l_correct    = get( findobj(h.performanceA,'XData',4), 'YData'); % Left  correct
    abort        = get( findobj(h.performanceA,'XData',3), 'YData'); % abort trials
    r_correct    = get( findobj(h.performanceA,'XData',2), 'YData'); % Right correct
    r_incorrect  = get( findobj(h.performanceA,'XData',1), 'YData'); % Right incorrect
    
    total    = l_incorrect+l_correct+abort+r_correct+r_incorrect;
    nCorrect = l_correct + r_correct;
    
    fprintf('Trials: %d, Correct: %.0f percent (%d / %d)\n',...
                gf.TrialNumber - 1,...
                nCorrect/total * 100,...
                nCorrect,...
                total)

    % Stop task timer
    stop(h.tasktimer);  

    % Reset all parameter tags

    tags = {'bit0C','bit1C','bit2C','bit4C','bit5C','bit6C','bit7C',...
            'leftLick','centerLick','rightLick',...
            'leftValve','centerValve','rightValve'};

    for i = 1 : length(tags)

        tag = sprintf('%s.%s',gf.stimDevice, tags{i});
        DA.SetTargetVal(tag,0);   
    end

    % Set device to idle 
    % (This avoids sounds/lights being produced when you no longer have GUI control)
    DA.SetSysMode(0);

    % Close connections and windows
    DA.CloseConnection;

    close(handles.figure1)
    close(h.timelineF)
    close(h.performanceF)
    


    % Restore default paths
    path(gf.defaultPaths)

    % Delete structures
    clear global DA gf h
    clear

    gf = [];

    disp('session ended')
    disp('All structures removed and default paths restored')
% end



function leftLick_Callback(~,~,~)
function rightLick_Callback(~,~,~)
function centerLick_Callback(~,~,~)
function bit0_Callback(~,~,~)
function bit1_Callback(~,~,~)
function bit2_Callback(~,~,~)
function bit4_Callback(~,~,~)
function bit5_Callback(~,~,~)
function bit6_Callback(~,~,~)
function bit7_Callback(~,~,~)
function leftValve_Callback(~,~,~)
function rightValve_Callback(~,~,~)
function centerValve_Callback(~,~,~)
function led_Callback(~,~,~)

function editHoldMax_Callback(~, ~, ~)
function editHoldMax_CreateFcn(~, ~, ~)
function editHoldSteps_Callback(~, ~, ~)
function editHoldSteps_CreateFcn(~, ~, ~)
function editHoldMin_Callback(~, ~, ~)
function editHoldMin_CreateFcn(~, ~, ~)

function editAttenMax_Callback(~, ~, ~)
function editAttenMax_CreateFcn(~, ~, ~)
function editAttenSteps_Callback(~, ~, ~)
function editAttenSteps_CreateFcn(~, ~, ~)
function editAttenMin_Callback(~, ~, ~)
function editAttenMin_CreateFcn(~, ~, ~)

function editPitchMax_Callback(~, ~, ~)
function editPitchMax_CreateFcn(~, ~, ~)
function editPitchSteps_Callback(~, ~, ~)
function editPitchSteps_CreateFcn(~, ~, ~)
function editPitchMin_Callback(~, ~, ~)
function editPitchMin_CreateFcn(~, ~, ~)

function editLeftValveTime_Callback(~, ~, ~)
function editLeftValveTime_CreateFcn(~, ~, ~)
function editRightValveTime_Callback(~, ~, ~)
function editRightValveTime_CreateFcn(~, ~, ~)
function editCenterValveTime_Callback(~, ~, ~)
function editCenterValveTime_CreateFcn(~, ~, ~)

function slideCenterRewardP_CreateFcn(~, ~, ~)
function editCenterRewardP_CreateFcn(~, ~, ~)


function unitList_Callback(~,~,~)
function unitList_CreateFcn(~,~,~)
function drawStore_Callback(~,~,~)
function drawStore_CreateFcn(~,~,~)
function drawChan_Callback(~,~,~)
function drawChan_CreateFcn(~,~,~)
function drawWaveforms_Callback(~,~,~)

function rasterChan_Callback(~,~,~)
function rasterChan_CreateFcn(~,~,~)
function psthChan_Callback(~,~,~)
function psthChan_CreateFcn(~,~,~)
    
