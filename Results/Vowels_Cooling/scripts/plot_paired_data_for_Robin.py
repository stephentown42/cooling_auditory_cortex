"""
function plot_paired_data_for_Robin
 function plot_paired_data_for_Robin

 INPUT:
   - csv file containing behavioral data with cross-referenced temperature
   values for each trial

Notes:
Animals were tested twice daily (in AM and PM sessions).
Input data for Robin consists of paired sessions in which cooling was 
performed in one session and not in the session

TO DO:
Update adjustment for low performance in control conditions (will give more trials)

There is also an argument that preprocessing of data should be done before this 
analysis so we can focus on the details of the analytical tools; however I'm not sure
if that's the best idea


 OUTPUT:
   - Figure with three axes showing:
       1. Pairwise comparison of adjacent cooled and control sessions 
       2. Bar plot of overall performance ( correct) for each noise
       condition in cooled and control testing, with individual session
       data shown in scatter plot
       3. Permutation testing results showing the difference between
       control and cooled performance in each noise condition, with null
       distributions for shuffled data underneath

 Stephen Town - 24 Aug 2017




"""


import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from cooling import cooling_analysis as ca
from cooling import plot_tools as cplot
from cooling import settings


file_path = Path('Results/cooling/data/F1509_Behavior.csv')   
        
        
def main():

    # Load data and do housekeeping
    df = pd.read_csv( file_path)                                                        
    df = df[df['CorrectionTrial'] == 0]                                                 #   Remove correction trials
    df = df[df['Response'] >= 0]                                                        #   Remove trials without responses
    df = df[df['Mask'] < 2] 

    df['vowel_level'] = settings['default_level'] - df['Atten']
    df['SNR'] = df['vowel_level'] - settings['noise_level']
    df['Mask'].replace({0:'Clean', 1:'Restricted', 2:'Continuous'}, inplace=True)       #   Make indices readable 
       
    
    df = ca.temperature_preprocessing(df, settings['warm_threshold'], settings['cooled_threshold'])

    df = ca.match_for_atten(df, time_interval='day', condition_interval='originalFile')

    df = ca.constrain_attenutations_by_control_performance(df, settings['control_limit'])

    # df = ca.match_sample_sizes(df, levels=['Mask', 'isCooled'])

    df = ca.drop_rare_attenuations(df, min_trials=10)

    print(df.shape)

    # Get performance across trials
    bySession = ca.count_correct_trials(df, ['day','Mask','isCooled'])

    overSessions = ca.count_correct_trials(df, ['Mask','isCooled'])
    
    by_SNR = ca.count_correct_trials(df, ['Mask','isCooled','SNR'])
    

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

    cplot.scatter_by_session( bySession, axs[0], test_column='isCooled', groupby=['day','Mask'])

    cplot.bars_across_sessions( overSessions, axs[1], splitVar='isCooled')

    cplot.permuation_violins( perm_tests, axs[2])

    cplot.pCorrect_vs_SNR( by_SNR, axs[3], mask='Restricted', treatment_var='isCooled')
    
    cplot.pCorrect_vs_SNR( by_SNR, axs[4], mask='Clean', treatment_var='isCooled')

    plt.show()

    

if __name__ == '__main__':
    main()