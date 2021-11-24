function valve(bit, time_on, pulseN, var)
%
% This script allows you to control the solenoids for any length of time
% and number of pulses. It's designed with the ACME 2000 in mind, but may
% be suitable for expansion in the future.
%
% bit            - bit number for required solenoid (e.g. left = 4; right = i; center = 6)
%
%varargin
% time_on*  - (integer) time for valve to be on (in ms)
% pulseN*   - (integer) number of pulses 
% i*        - (integer) index for timelineI field, involved in generating the timeline in the online gui
% var*      - (string)  variable name for recording the time of valve opening (e.g. center, left or right)
%
% * These variables are optional, but the are not interchangeable. 
%   I.e. you can't put 'var' before 'i'.
%
% Troubleshooting: 
% The function assumes you are working with GoFerret (gf) and so have
% defined the device. If you aren't, it will default to the RM1. If you're
% working with another device, you should redefine gf.stimDevice
a
global DA gf h

%Check connection and create if it doesn't exist
if iscom(DA) == 0,
    DA = actxcontrol('TDevAcc.X');
    DA.ConnectServer('Local');
    invoke(DA,'SetSysMode',1); 
end

%Check device name and fall back on 'RM1' with a sample rate of 24414 Hz
if isfield(gf,'stimDevice') == 0,
    gf.stimDevice = 'RM1';
    disp(sprintf('Device undefined, assuming use of the %s',gf.stimDevice))
end

if isfield(gf,'fStim') == 0,
    gf.fStim = 24414.625;
    disp(sprintf('Device undefined, assuming sample rate of %f Hz',gf.stimDevice))
end


%Set pulse time
if time_on > 0,
    if invoke(DA,'SetTargetVal',sprintf('%s.pulseThi',gf.stimDevice),time_on) ~= 1,
        disp('Failed to set pulse time')
    end
end

%Set pulse number
if pulseN > 0        
    if invoke(DA,'SetTargetVal',sprintf('%s.pulseN',gf.stimDevice),pulseN) ~= 1,
        disp('Failed to set pulse number')
    end
end

%Trigger valve
val = sprintf('%s.%sValve',gf.stimDevice, var);

if invoke(DA,'SetTargetVal',val,1) ~= 1 ||...
    invoke(DA,'SetTargetVal',val,0) ~= 1, 

    disp('Failed to trigger bit')
end


%Mark timeline
x = gf.sessionTime;

if get(0,'CurrentFigure') ~= h.timelineF,
    figure(h.timelineF)
end

if get(gcf,'CurrentAxes') ~= h.timelineA,    
    axes(h.timelineA)
end

hold on
switch var
   
    case 'left'
        plot(x, 0.9, '^y')
        
    case 'center'
        plot(x, 1.9, '^c')
        
    case 'right'     
        plot(x, 2.9, '^r')   
    
end
hold off


