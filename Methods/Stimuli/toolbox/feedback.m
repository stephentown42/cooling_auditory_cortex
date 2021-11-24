function feedback(correct, side)

global DA gf

gf.TrialNumber = gf.TrialNumber + 1;

if correct == 1, 
    if side == 0,        
        valve(4,200,1,5,'left') %(bit, pulse_time, pulse_N, index and name for recording time)
        
    elseif side == 1,        
        valve(5,200,1,7,'right') %(bit, pulse_time, pulse_N, index and name for recording time)
        
    end
        
    gf.status      = 'PrepareStim';
    gf.currentStat = sprintf('Correct response to side %d',gf.side);
    gf.sumCorrect  = gf.sumCorrect + 1;
    
    pause(0.5);
    
else
    
    gf.currentStat           = sprintf('Incorrect response - time out for %d seconds',gf.TimeOutDuration);
    gf.performance(2,side+1) = gf.performance(2,side+1) + 1;    
    gf.status                = 'TimeOut';
    gf.TOtime                = invoke(DA,'GetTargetVal',sprintf('%s.zTime',gf.stimDevice)) / gf.fStim;
    
    softwareTrigger('timeout')  
end

%save and change status
%gf.FeedbackTime     = invoke(DA,'GetTargetVal',sprintf('%s.zTime',gf.stimDevice)) / gf.fStim;

%fprintf(gf.datafile,...
%        '%d, %d, %d, %d, %d, %f, %f \r\n',...
%        gf.TrialNumber,...
%        gf.side,...
%        gf.atten,...
%        invoke(DA,'GetTargetVal',sprintf('%s.MinHoldTime',gf.stimDevice)),...
%        gf.response,...
%        gf.ResponseLickTime,...
%        gf.FeedbackTime);