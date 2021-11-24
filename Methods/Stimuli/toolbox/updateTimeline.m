function updateTimeline_WE(width)
%
% Function used to continuously shift the timeline slightly ahead of the
% current time every two seconds. 
%
% width - time window in seconds in which show of events
%

global DA gf h

fig = h.timelineF;
ax  = h.timelineA;

% X axis
xMax(2)  = ceil(gf.sessionTime);     % session time 

if isOdd(xMax(2)) == 1,              % Make maximum value even
    xMax(2) = xMax(2) + 1;
end

if xMax(2) > xMax(1)                 %If 2 seconds has elapsed, update graph

    xMax(1) = xMax(2);

    if xMax(2) > width, 
        xMin = xMax(2) - width;
    else
        xMin = 0;
    end

    xRange = xMin : width/10 : xMax(2);

    set(h.timelineA,...
        'xlim',      [xMin xMax(2)],...
        'xtick',      xRange);
end

%%%%%%%%%%%%%%%% Get rid of objects outside view (saves memory) %%%%%%%%%%%%

% Find line objects
obj = findobj(h.timelineA,'type','line');

% if there are any such objects
if ~isempty(obj), 
    for i = 1 : length(obj),

        x = get(obj(i),'XData'); % Either a vector or a single value, depending on object type

        if max(x) < xMin,
            delete(obj(i))        
        end
    end
end

%%%%%%%%%%%%%%%%%%%%%%%% Sensor plot (bits 0-2) %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

x = gf.sessionTime;

%y = bit value * height + offset
y0 = DA.GetTargetVal('RM1.bit0') * 0.1 + 0.5;    % left
y2 = DA.GetTargetVal('RM1.bit2') * 0.1 + 1.5;     % center
y1 = DA.GetTargetVal('RM1.bit1') * 0.1 + 2.5;     % right


if get(0,'CurrentFigure') ~= h.timelineF,
    figure(h.timelineF)
end

if get(gcf,'CurrentAxes') ~= h.timelineA,    
    axes(h.timelineA)
end

p = gf.period / 2;

hold on
plot([x - p x + p],[y0 y0],'y')     % left   (bit0)
plot([x - p x + p],[y2 y2],'c')     % center (bit2)
plot([x - p x + p],[y1 y1],'r')     % right  (bit1)
hold off

%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Lick plot %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

var    = {'left'    'right' 'center'};
color  = {'y'       'r'     'c'     };
offset = [0         2       1       ] - 0.3;  % This is added to the y value (i.e. 1 + offset)

for i = 4 : 6,
   
    tag = sprintf('%s.%sLick', gf.stimDevice, var{i-3});
    y = DA.GetTargetVal(tag);%get( eval(sprintf('h.bit%d',i)),'value');
    
    if y > 0,
       
        y = y + offset(i-3);
                
        if get(0,'CurrentFigure') ~= h.timelineF,
            figure(h.timelineF)
        end
        
        if get(gcf,'CurrentAxes') ~= h.timelineA,    
            axes(h.timelineA)
        end
        
        hold on
        plot(x, y,...
            'marker',           '*',...
            'markerEdgeColor',  color{i-3},...        
            'markerFaceColor',  color{i-3},...
            'MarkerSize',        5)        
        
        hold off
    end   
end


%%%%%%%%%%%%%%%%%%%%%%%% Solenoid plot (bits 4-6) %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%         left  right   center
%bit   = [4     5       6       ];
color  = {'y'   'r'     'c'     };
offset = [0     2       1       ] + 0.1;          % This is added to the y value (i.e. 1 + offset)

for i = 4 : 6,
   
    tag = sprintf('%s.bit%d',gf.stimDevice,i);
    y = DA.GetTargetVal(tag);%get( eval(sprintf('h.bit%d',i)),'value');
    
    if y > 0,
       
        y = y + offset(i-3);
        
        
        if get(0,'CurrentFigure') ~= h.timelineF,
            figure(h.timelineF)
        end
        
        if get(gcf,'CurrentAxes') ~= h.timelineA,    
            axes(h.timelineA)
        end
        
        hold on
        plot(x, y,...
            'marker',           'v',...
            'markerEdgeColor',  color{i-3},...        
            'markerFaceColor',  color{i-3},...
            'MarkerSize',        5)        
        
        hold off
    end   
end



