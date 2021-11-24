"""
function plot_unpaired_data_for_Magnum

INPUT:
- csv file containing behavioral data with cross-referenced temperature
values for each trial

OUTPUT:
- Figure with two axes showing:
    1. Bar plot of overall performance ( correct) for each noise
    condition in cooled and control testing, with individual session
    data shown in scatter plot
    2. Permutation testing results showing the difference between
    control and cooled performance in each noise condition, with null
    distributions for shuffled data underneath

Branched from plot_unpaired_data_for_Magnum.m
    Stephen Town - 24 Aug 2017

"""

import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import seaborn as sns

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from cooling import cooling_analysis as ca
from cooling import plot_tools as cplot
from cooling import settings

file_path = Path('Results/cooling/data/F1311_Behavior.csv') 


def main():

    # Load data and do housekeeping
    df = pd.read_csv( file_path)                                                        
    df = df[df['CorrectionTrial'] == 0]  
    df = df[df['Response'] >= 0]       
    df = df[df['Mask'] < 2]   

    df['vowel_level'] = settings['default_level'] - df['Atten']
    df['SNR'] = df['vowel_level'] - settings['noise_level']
    df['Mask'].replace({0:'Clean', 1:'Restricted', 2:'Continuous'}, inplace=True)       #   Make indices readable    
    
    df = ca.temperature_preprocessing(df, settings['warm_threshold'], settings['cooled_threshold'])

    df = ca.drop_rare_attenuations(df, min_trials=10)

    # Match attenuation range 
    df = ca.match_for_atten(df, time_interval='all', condition_interval='isCooled')

    # Get performance across trials
    bySession = ca.count_correct_trials(df, ['originalFile','Mask','isCooled'])

    overSessions = ca.count_correct_trials(df, ['Mask','isCooled'])
    
    by_SNR = ca.count_correct_trials(df, ['Mask','isCooled','SNR'])
    by_SNR = by_SNR[by_SNR['Mask'] == 'Restricted']

  
    # Run permuation tests
    perm_tests = []

    for mask, mdata in overSessions.groupby('Mask'):

        control = mdata[mdata['isCooled'] == False]
        cooled  = mdata[mdata['isCooled'] == True]

        pt = ca.permutation_test( 
            control['nTrials'].values[0], cooled['nTrials'].values[0], 
            control['nCorrect'].values[0], cooled['nCorrect'].values[0], nIterations=10000)

        pt['mask'] = mask
        perm_tests.append(pt)

        print(f"{mask}: p = {pt['p_below']}")
    
    perm_tests = pd.DataFrame(perm_tests)

    # Plotting
    fig, axs = plt.subplots(1,5, figsize=(15, 3))

    cplot.bars_across_sessions( overSessions, axs[1], splitVar='isCooled')

    cplot.permuation_violins( perm_tests, axs[2])

    cplot.pCorrect_vs_SNR( by_SNR, axs[3], mask='Restricted', treatment_var='isCooled')
    
    cplot.pCorrect_vs_SNR( by_SNR, axs[4], mask='Clean', treatment_var='isCooled')

    plt.show()

"""
 Summarize data across sessions

 Plot
figureST('F1311_Magnum');
sp = dealSubplots(2,1);


title(sp(1),sprintf('Temperature limit = d�C', cooled_threshold))

colors = {'k','r','b'};
shades = [grey; 1 .4 .4; 0 .5 1];

bar_offset = 0.2;

 For each mask
for mask = 0 : 2
    
     For each cooling condition
    for j = 0 : 1
        
         Filter data
        idx = behavior.Mask == mask & behavior.isCooled == j;
        test_data = behavior(idx,:);
        
        
         Get individual session data
        sessions = unique(test_data.originalFile);
        nSessions = numel(sessions);        
        [session_correct, session_nTrials] = deal(nan(nSessions, 1));
        
        for i = 1 : nSessions  For each individual session
               
             Calculate percentage correct
            session_idx = strcmp(test_data.originalFile, sessions{i});
            session_correct(i) = mean( test_data.Correct(session_idx)) * 100;
            session_nTrials(i) = sum(session_idx);           
        end
        
         Draw individual session data
        session_x = mask + (randn(nSessions,1) ./ 30);               
        session_h = scatter( session_x, session_correct,...
                             'parent',sp(1),...
                             'SizeData', session_nTrials./2,...
                             'Marker','o',...
                             'MarkerEdgeColor',colors{mask+1});
                        
        if j ==  1  If cooled
            set(session_h,'MarkerFaceColor','none',...
                'xdata', session_h.XData + bar_offset);
        else
            set(session_h,'MarkerFaceColor',colors{mask+1},...
                'xdata', session_h.XData - bar_offset);
        end                           
    end

                            
                            
    Run binomial test on cooled and control data separately
   bp_ctrl = myBinomTest( nCorrect(1, mask+1), nTrials(1, mask+1), 1/2); 
   bp_cool = myBinomTest( nCorrect(2, mask+1), nTrials(2, mask+1), 1/2);
                            
    Calculate performance across trials
   pCorrect_ctrl = nCorrect(1, mask+1) / nTrials(1, mask+1) * 100;
   pCorrect_cool = nCorrect(2, mask+1) / nTrials(2, mask+1) * 100;
   control_minus_cooled = pCorrect_ctrl - pCorrect_cool;

    Add bar plot
   b(1) = bar( mask - bar_offset, pCorrect_ctrl,'parent',sp(1));
   b(2) = bar( mask + bar_offset, pCorrect_cool,'parent',sp(1));

   set(b,'EdgeColor',colors{mask+1},'BarWidth', bar_offset*2)
   set(b(1),'FaceColor',shades(mask+1,:))
   set(b(2),'FaceColor','w')
   uistack(b,'bottom')
      
    Add permutation test
   jitter = randn(size(permTest.perm_val)) / 10;
   scatter( jitter + mask, permTest.perm_val .* 100, 'parent', sp(2),...
            'marker','.','MarkerEdgeColor',shades(mask+1,:),'MarkerEdgeAlpha',0.05)
        
        
   plot( mask, control_minus_cooled,'o','MarkerEdgeColor',colors{mask+1},...
       'MarkerFaceColor', colors{mask+1},'parent', sp(2))
   
   text(mask, 20, sprintf('p = .3f', permTest.p_below),...
       'HorizontalAlignment','center','Color',colors{mask+1}) 

    Report sample sizes in command window
   fprintf('Mask = d\n', mask)   
   fprintf('\tControl: d / d trials (p = .3f)\n', nCorrect(1, mask+1),...
                                                     nTrials(1, mask+1), bp_ctrl)
   fprintf('\tCooled: d / d trials  (p = .3f)\n', nCorrect(2, mask+1),...
                                                     nTrials(2, mask+1), bp_cool)
   fprintf('\tPerm test: p = 0.3f\n', permTest.p_below)
end

ylabel(sp(1), ' Correct')
ylabel(sp(2), 'Control - Cooled ()')

set(sp(1),'ylim',[50 100],'xcolor','none')
set(sp(2),'ylim',[-25 25],'xtick',0:2,'xticklabel',{'No noise','Restricted','Continuous'},...
        'xticklabelrotation',45)

set(sp,'xlim',[-1 3])
    
 Reference line (no effect)    
drop(plotXLine(0, sp(2)))
    
 Compare continuous and restricted noise

fprintf('\nComparison of continuous and restricted noise\n')

 During cooling
RN_cool_perm = cooling_perm_test(nTrials(2, 2), nTrials(2, 3),...
                            nCorrect(2, 2), nCorrect(2, 3));  

fprintf('Cooling: p = .3f\n',RN_cool_perm.p_below)                        
                        
                        
 In control data                        
RN_ctrl_perm = cooling_perm_test(nTrials(1, 2), nTrials(1, 3),...  Restricted
                            nCorrect(1, 2), nCorrect(1, 3));   Continuous

fprintf('Control: p = .3f\n',RN_ctrl_perm.p_below)                        

                        
                        

 Stats
 
  Main effect of cooling via logistic regression
 for mask = 0 : 2
     
      Filter for mask only
     mask_data = new_table(new_table.Mask == mask, :);
     
      Define predictors (including attenuation and vowel may reduce error
      of model)
     X = [mask_data.averageTemp mask_data.Atten, mask_data.F1];
     
      Fit the logistic regression model
     mdl = fitglm(X, mask_data.Correct,'interactions', 'distribution','binomial');
    
     
      Run binomial task on each condition
     for j = 0 : 1
        
         j_data = mask_data( mask_data.isCooled == j,:);
         
          Report performance (sanity check)
         fprintf('Mask = d, isCooled = d, ', mask, j)
         fprintf('pCorrect = .3f, ', mean(j_data.Correct))
         
          Run binomica test
         nCorrect = sum(j_data.Correct);
         nTrials = numel(j_data.Correct);
         binomial_p = myBinomTest( nCorrect, nTrials, 1/2); 
         
         fprintf('binomial p = .3f\n', binomial_p)
     end
     
    
     
 end

 Compare noise vs. unmasked using GLM
 test_data = new_table(new_table.Mask ~= 2, :);
 X = [test_data.isCooled, test_data.Mask, test_data.Atten, test_data.F1];
 mdl = fitglm(X, test_data.Correct,'interactions', 'distribution','binomial');
   
"""


if __name__ == '__main__':
    main()
