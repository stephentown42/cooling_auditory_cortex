function updatePerformance(x)
% Used to update horizontal bar chart of task performance
% Requires input based on the type of response given

%   1. Incorrect response to right
%   2. Correct response to right
%   3. Abort trial - no peripheral response within response window
%   4. Correct response to left
%   5. Incorrect response to left

% Note that left/right refers to the spout the animal goes to (i.e. the
% response), not the spout that would be rewarded

% E.g. Left incorrect means a trial on which the animal went left. This was
% incorrect as the sound was rewarded by visiting the right spout.

global gf h

if gf.side >= 0,
%% Change selected bar
%
% Finds horizontal bar at height x (Matlab barH function puts x on the vertical)
% and adds 1 to the horizontal bar. 
% 
% Function should be used to mark each trial
%

obj = findobj(h.performanceA,'Type','hggroup'); %hggroup = bars

if ~isempty(obj)  && gf.correctionTrial(1) ~= 1,   % Only search if its not a correction trial
    
    for i = 1 : length(obj),

        obj_x = get(obj(i),'XData'); 
        obj_y = get(obj(i),'YData'); 

        if x == obj_x,  
            axes(h.performanceA)
            hold on        
            set(obj(i), 'YData', obj_y + 1)        
            hold off
        end
    end
end

%% Update percentage correct

% Read values from bar chart
l_incorrect  = get( findobj(h.performanceA,'XData',5), 'YData'); % Left  correct
l_correct    = get( findobj(h.performanceA,'XData',4), 'YData'); % Left  correct
abort        = get( findobj(h.performanceA,'XData',3), 'YData'); % Left  correct
r_correct    = get( findobj(h.performanceA,'XData',2), 'YData'); % Left  correct
r_incorrect  = get( findobj(h.performanceA,'XData',1), 'YData'); % Right correct

% If values were measured
if ~isempty(l_correct) && ~isempty(r_correct),

    % Calculate percentage
    n_Correct   = l_correct + r_correct; 
    totalTrials = l_correct + r_correct + l_incorrect + r_incorrect + abort; 
    p_Correct   = (n_Correct / totalTrials) * 100;

    % Generate String 
    title = strcat( sprintf('%.0f', p_Correct), '% correct',...
                    sprintf(' (%d/%d non-correction trials)', n_Correct, totalTrials));

    % Update graph title
    set(h.performanceF, 'name', title)
end


%% Adjust x axis

if gf.TrialNumber > 10,
    set(h.performanceA,'xlim', [0 gf.TrialNumber])
end

end