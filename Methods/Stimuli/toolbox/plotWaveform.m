function plotWaveform

global DA gf

axes(handles.axes2)
cla % clear all current objects

xmin = str2double(get(handles.xMinEdit,'string'));
xmax = str2double(get(handles.xMaxEdit,'string'));
ymin = str2double(get(handles.yMinEdit,'string'));
ymax = str2double(get(handles.yMaxEdit,'string'));

updateAxis(xmin,xmax,ymin,ymax);

xlabel('time (ms)')
ylabel('V')

n = invoke(DA,'GetTargetVal',sprintf('%s.stimNPoints',gf.stimDevice));
x = gf.duration/n : gf.duration/n : gf.duration; 
y = invoke(DA,'ReadTargetVEX',sprintf('%s.Sound_data%d',gf.stimDevice,gf.side),0,n,'F32','F32');
   
plot(x,y,'k')