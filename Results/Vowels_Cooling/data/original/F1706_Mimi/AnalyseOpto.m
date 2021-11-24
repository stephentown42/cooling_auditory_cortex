%
%
% Created:
%   2021-06-??: Jennifer Bizley
% Modified:
%   2021-06-14: Stephen Town
%       - Added column headers and documentation
%       - Implemented correction for logging error in BlockWE-127 in data
%       - Added consistent column headers to source data
%       - Saved concatenated data as csv file




cd('C:\Users\steph\Desktop\F1706_Mimi')
d = dir('*.txt');
all_data=[];PC=[];
for dd = 1:length(d)
    
    d_info = split(erase(d(dd).name, '.txt'), ' ');
    block = str2double(erase(d_info{end}, 'BlockWE-'));
    
    t = readtable(d(dd).name, 'delimiter', '\t');    
    t.Block = repmat(block, size(t, 1), 1);
    
    all_data = [all_data; t];       
end

% Save concatenated data
writetable(all_data, 'F1706_Mimi_Opto.csv', 'delimiter',',')

% Drop correction trials
data = all_data( all_data.CorrectionTrial_ ==0, :);


% Split data into control and opto
cData = data(data.opto==0,:);
oData = data(data.opto==1,:);
totals=[];

for oo = 1:2
    if oo == 1
        data = cData;
    else
        data = oData;
    end
    u = sort(unique(round(data(:,10))));
    u = u(u>-11);% remove the 2 trials at -13
    u = u(u~=-6);% remove the 3 trials at -6 dB
    for uu = 1:length(u)
        f = find(round(data(:,10))==u(uu));
        totals(uu,1,oo) = u(uu);
        totals(uu,2,oo) = sum(data(f,15));
        totals(uu,3,oo) = length(f);
    end
end

xVal = [-10:1:15];
Bc = glmfit(totals(:,1,1),[totals(:,2,1),totals(:,3,1)],'binomial');
Yc = glmval(Bc,xVal,'logit');

Bo = glmfit(totals(:,1,2),[totals(:,2,2),totals(:,3,2)],'binomial');
Yo = glmval(Bo,xVal,'logit');

figure; 
clf;SetFigure(10,10,'opto');
plot(-1*xVal,Yo,'b','linewidth',2)
hold on;
plot(-1*xVal,Yc,'k','linewidth',2)
plot(-1*totals(:,1,2),totals(:,2,2)./totals(:,3,2),'b*')
plot(-1*totals(:,1,1),totals(:,2,1)./totals(:,3,1),'kd','markerfacecolor','k')
ylim([0.5 .9])
xlim([-10 10])
set(gca,'fontsize',14)

set(gca,'xtick',[-10 :5:10],'ytick',[0.5:0.1:0.9],'yticklabel',[50:10:90])
box off
xlabel('SNR (dB SPL)')
legend('laser ON','laser OFF')
ylabel('% Correct')


pred = [totals(:,1,1);totals(:,1,2)];
pred(:,2) = [ones(7,1);zeros(7,1)];
y = [totals(:,2:3,1);totals(:,2:3,2)];
glm = fitglm(y,x,'interactions','distribution','binomial')


% glm = 
% 
% 
% Generalized linear regression model:
%     logit(y) ~ 1 + x1 + x2
%     Distribution = Binomial
% 
% Estimated Coefficients:
%                    Estimate       SE        tStat       pValue  
%                    ________    ________    _______    __________
% 
%     (Intercept)     0.65794     0.15125     4.3501    1.3606e-05
%     x1             -0.05176    0.017604    -2.9403     0.0032789
%     x2              0.62567     0.23628     2.6479     0.0080982
% 

