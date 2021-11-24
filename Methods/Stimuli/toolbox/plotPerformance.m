function plotPerformance

global gf

if sum([gf.abortTrials, gf.performance(1,:), gf.performance(2,:)]) > 0,

    axes(handles.axes2)
    cla % clear all current objects
    
    n = 100./gf.TrialNumber;                     %Percentage conversion up here to save repetition
    
    hold on
        bar(1,gf.abortTrials*n,'FaceColor','k')
        bar(3,gf.performance(1,1)*n,'FaceColor','y') %Left, correct
        bar(4,gf.performance(2,1)*n,'FaceColor','y') %Left, incorrect
        bar(5,gf.performance(1,2)*n,'FaceColor','r') %Right, correct
        bar(6,gf.performance(2,2)*n,'FaceColor','r') %Right, incorrect
    hold off
    box off
    
    ymax = max([gf.abortTrials*n, gf.performance(1,:).*n, gf.performance(2,:).*n]);
    updateAxis(0,7,0,ymax);

    set(gca,'xtick',        [1 3 4 5 6],...
            'xticklabel',   {'Abort','LC','LI','RC','RI'},...
            'ytick',        [0 ymax/2 ymax])

    ylabel('% of Trials')    
end