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

% %y = bit value * height + offset
center = DA.GetTargetVal( sprintf( '%s.sensor1', gf.stimDevice))*0.25 + 1.5;
left   = DA.GetTargetVal( sprintf( '%s.sensor3', gf.stimDevice))*0.25 + 0.5;
right  = DA.GetTargetVal( sprintf( '%s.sensor5', gf.stimDevice))*0.25 + 2.5;


% y = zeros(10,1);
% 
% for i = 1 : 10,
%    
%     y(i) = DA.GetTargetVal( sprintf( '%s.sensor%d', gf.stimDevice, i));
% end


if get(0,'CurrentFigure') ~= h.timelineF,
    figure(h.timelineF)
end

if get(gcf,'CurrentAxes') ~= h.timelineA,    
    axes(h.timelineA)
end

p = gf.period / 2;

hold on
plot([x - p x + p],[left left],'color',[0.85 0.2 0.85])     % left   (bit0)
plot([x - p x + p],[center center],'c')     % center (bit2)
plot([x - p x + p],[right right],'r')     % right  (bit1)
hold off

%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Lick plot %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


center = DA.GetTargetVal( sprintf( '%s.lick1', gf.stimDevice));
left   = DA.GetTargetVal( sprintf( '%s.lick8', gf.stimDevice));
right  = DA.GetTargetVal( sprintf( '%s.lick2', gf.stimDevice));


if get(0,'CurrentFigure') ~= h.timelineF,
    figure(h.timelineF)
end

if get(gcf,'CurrentAxes') ~= h.timelineA,
    axes(h.timelineA)
end

if center,
    hold on
    plot(x, center * 0.25 + 1.8, '*','markerEdgeColor', 'c', 'markerFaceColor', 'c', 'MarkerSize', 5)
end

if left,
    hold on
    plot(x, left*1/4 + 0.8, '*','markerEdgeColor', [0.85 0.2 0.85], 'markerFaceColor', [0.85 0.2 0.85], 'MarkerSize', 5)
end

if right,
    hold on
    plot(x, right*1/4 + 2.8, '*','markerEdgeColor', 'r', 'markerFaceColor', 'r', 'MarkerSize', 5)
end

% var    = {'left'    'right' 'center'};
% color  = {'y'       'r'     'c'     };
% offset = [0         2       1       ] - 0.3;  % This is added to the y value (i.e. 1 + offset)
% 
% 
% for i = 4 : 6,
%    
%     y = DA.GetTargetVal( sprintf( '%s.lick%d', gf.stimDevice, i));
%     
%     if y > 0,
%        
%         y = y + offset(i-3);
%                 
%         if get(0,'CurrentFigure') ~= h.timelineF,
%             figure(h.timelineF)
%         end
%         
%         if get(gcf,'CurrentAxes') ~= h.timelineA,    
%             axes(h.timelineA)
%         end
%         
%         hold on
%         plot(x, y,...
%             'marker',           '*',...
%             'markerEdgeColor',  color{i-3},...        
%             'markerFaceColor',  color{i-3},...
%             'MarkerSize',        5)        
%         
%         hold off
%     end   
% end


%%%%%%%%%%%%%%%%%%%%%%%% Solenoid plot (bits 4-6) %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%         left  right   center
valve  = [3     5       1       ];
color  = {'m'   'r'     'c'     };
offset = [0     2       1       ] + 0.2;          % This is added to the y value (i.e. 1 + offset)

for i = 1 : 3,
   
    y = DA.GetTargetVal( sprintf( '%s.valve%dout',gf.stimDevice,valve(i)));
    
    if y > 0,
       
         y = y + offset(i);
        
        
        if get(0,'CurrentFigure') ~= h.timelineF,
            figure(h.timelineF)
        end
        
        if get(gcf,'CurrentAxes') ~= h.timelineA,    
            axes(h.timelineA)
        end
        
        hold on
        plot(x, y,...
            'marker',           'v',...
            'markerEdgeColor',  color{i},...        
            'markerFaceColor',  color{i},...
            'MarkerSize',        5)        
        
        hold off
    end   
end



