"""
function plot_paired_data_for_Mimi
 function plot_paired_data_for_Mimi

 INPUT:
   - csv file containing behavioral data with cross-referenced temperature
   values for each trial

 Notes:
   - Testing here was done in the white elephant, so left and right
   responses are coded as 8 and 2 respectively.

TO DO:
    Discard data from sessions where only restricted noise was test, 
    do this using code rather than dropping trials from the input data
    for transparency

OUTPUT:
- Figure with two axes showing:
    1. Bar plot of overall performance ( correct) for each noise
    condition in cooled and control testing, with individual session
    data shown in scatter plot
    2. Permutation testing results showing the difference between
    control and cooled performance in each noise condition, with null
    distributions for shuffled data underneath

Stephen Town - 21 July 2021

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


file_path = Path('Results/cooling/data/F1706_Behavior.csv')   


def main():

    # Load data  and do housekeeping
    df = pd.read_csv( file_path)                                                        
    df = df[df['CorrectionTrial'] == 0]             #   Remove correction trials
    df = df[df['Response'] >= 0]                    #   Remove trials without responses (does nothing for Mimi)
    
    df['vowel_level'] = settings['default_level'] - df['Atten']
    df['SNR'] = df['vowel_level'] - settings['noise_level']

    df['Mask'].replace({0:'Clean', 1:'Restricted'}, inplace=True)       #   Make indices readable    
    # df['opto'].replace({0:'Control', 1:'+ 463 nm'}, inplace=True)

    
    df = ca.match_for_atten(df, time_interval='Block', condition_interval='opto')

    df = ca.drop_rare_attenuations(df, min_trials=10)

    # Get performance across different levels of the dataset    
    bySession = ca.count_correct_trials(df, ['Block','Mask','opto'])

    overSessions = ca.count_correct_trials(df, ['Mask','opto'])

    by_SNR = ca.count_correct_trials(df, ['Mask','opto','SNR'])

    # Assess the effect of light delivery on performance across sessions
    control = overSessions[overSessions['opto'] == 0]
    laserON = overSessions[overSessions['opto'] == 1]
    
    pt = ca.permutation_test( 
        control['nTrials'].values[0], laserON['nTrials'].values[0], 
        control['nCorrect'].values[0], laserON['nCorrect'].values[0], nIterations=10000)

    print(f"Restricted Noise: observed effect = {pt['observed_delta']*100:.3f}%, p = {pt['p_below']}")

    pt['mask'] = 'Restricted'
    pt = pd.DataFrame([pt])             # Make compatible with plotting function
    

    # Plotting
    fig, axs = plt.subplots(1,4, figsize=(12, 3))

    cplot.scatter_by_session( bySession, axs[0], test_column='opto', groupby=['Block','Mask'])

    cplot.bars_across_sessions( overSessions, axs[1], splitVar="opto")

    cplot.permuation_violins( pt, axs[2])

    cplot.pCorrect_vs_SNR( by_SNR, axs[3])

    plt.show()

if __name__ == '__main__':
    main()