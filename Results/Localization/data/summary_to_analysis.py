"""
Turns summary data into analysis-ready data

What does that mean?
Summary data is simply all trials from each session concatenated,
whereas analysis data contains has processed variables that are 
more useful for statistical assessment or plotting. 

Analysis data also contains extra columns for variables (e.g. error 
magnitude) that were not calculated during testing.

INPUT:
------
CSV files containing summary data


OUTPUT:
------
CSV files containing analysis data

Version history:
----------------
    2021-08-16: Separated from localization_cooling_analysis.py (ST)

"""

from datetime import datetime
import os, sys

import numpy as np
import pandas as pd
from pathlib import Path


bit_gen = np.random.PCG64(32106334791295636890)    # bit generator for subsampling


def preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get rid of trials that aren't interesting for this analysis, 
    and also add a couple of handy columns for later analysis

    Data is kept in summary as they might interest someone else

    Parameters:
    ----------
    df : Data from summary file

    Returns:
    --------
    df : Subset of rows from input data, with extra columns
    """

    df = df[df['Modality'] == 'Aud']
    df = df[df['CorrectionTrial'] == 0]                     # Remove correction trials
    
    df = df[df['Response'] >= 0]                            # Drop trials without response
    df = df[df['Response'] <= 8]                            # Very rare (n~=1) cases of dual response
    
    df['ResponseAngle'] = (df['Response'] - 5) * 30         # Angle in degrees
    df['ResponseAngle'] = df['ResponseAngle'] * -1          # Invert angular direction to make the same as Wood et al, 2017
    
    df['SpkrPos']  = df['SpkrPos'] * -1                     # Invert angular direction to make the same as Wood et al, 2017
    df['Spkr_Rad'] = df['SpkrPos'] / 180 * np.pi            # Degrees to radians

    angle_to_hemifield = {-90:'L',-60:'L',-30:'L',0:None, 90:'R',60:'R',30:'R'}     # Class as left / right
    df['spkr_hemifield'] = df['SpkrPos'].replace( angle_to_hemifield)
    df['resp_hemifield'] = df['ResponseAngle'].replace( angle_to_hemifield)

    df['LatCorrect'] = df['spkr_hemifield'] == df['resp_hemifield']                 # Lateralization performance
    df['LatCorrect'] = df['LatCorrect'].astype(int)

    df['Error'] = np.absolute(df['ResponseAngle'] - df['SpkrPos'])                  # Absolute error magnitude

    # Remove trials at midline if not tested during every cooling condition (F1509_Robin)
    n = df.groupby(by=['SpkrIdx','Condition'])['Trial'].count()
    n = n.reset_index(['Condition'])
    n = n.pivot(values='Trial', columns='Condition')

    good_speakers = n.dropna(axis=0)
    df = df[df['SpkrIdx'].isin(good_speakers.index.to_list())]

    # Sample equal numbers of sound durations for each speaker location
    if df['duration'].unique().shape[0] > 1:
        df = equate_durations_for_cooling_condition(df) 
        
    return df


def equate_durations_for_cooling_condition(df : pd.DataFrame) -> pd.DataFrame:
    """ Returns a subsampled dataframe with equal numbers of trials with each sound duration for each cooling condition"""

    # The following code assumes that the indices are unique
    assert df.index.is_unique           

    # For each cooling condition
    for condition, condition_data in df.groupby('Condition'):

        # Get the minimum number of trials available
        min_trials = min( condition_data['duration'].value_counts())
        
        # For each stimulus duration
        for duration, duration_data in condition_data.groupby('duration'):
    
            # Select a random sample to preserve and drop the rest
            indices_to_keep = duration_data.sample(n=min_trials, random_state=432).index            
            ind_to_drop = duration_data.index.difference(indices_to_keep)                           

            df.drop(ind_to_drop, inplace=True)

    return df




def flatten_sample_sizes(df, sample_size=50, nIterations=3) -> pd.DataFrame:
    """
    Adds columns indicating trial membership in subsampled dataset

    Parameters:
    ----------
    df : pandas dataframe
        Dataframe from which to randomly subsample trials from matched
        numbers of speaker locations and treatment conditions
    sample_size : int
        Number of trials to sample from each stimulus condition, or 
        combination of stimuli
    nIterations : int
        Number of bootstraps to run

    Notes:
    ------
    nIterations is kept low here as we will only want to check how repeatable
    the modelling results are on different samples.

    Returns:
    --------
    df : pandas dataframe
        Dataframe with added columns indicating trial membership in sample
    """

    strat_vars = ['SpkrIdx', 'Condition']

    df.reset_index(inplace=True)

    for iteration in range(0, nIterations):
              
        # Check sample size within bounds
        grouped = df.groupby(strat_vars)
        available_min = grouped['Trial'].count().min()

        if sample_size > available_min:
            sample_size = available_min
            print(f'Sample size exceeds max available - dropping to {available_min})')

        # Get indices of samples selected 
        idx = []
        for group, gdata in grouped:

            subsample = gdata.sample(n=sample_size, random_state=bit_gen)
            idx.extend( subsample.index)

        # Flag selected trials by adding a logical column for membership
        col_name = "Sample" + str(iteration)
        df[col_name] = 0
        df[col_name].iloc[idx] = 1

    return df.copy()



def main():

    root_dir = Path('Results/Localization/data/summary')    
    
    for csv_path in root_dir.glob('*.csv'):
                
        df = pd.read_csv(csv_path)       

        df['fNum'] = int(csv_path.stem[1:5])        # Ferret ID (for combining data from multiple files)

        df = preprocessing(df)               
        # df = flatten_sample_sizes(df, nIterations=3)       

        
        R_path = root_dir.parent / 'analysis' / (csv_path.stem[0:5] + '.csv')
        df.to_csv(R_path, index=False)                


   
if __name__ == '__main__':
    main()