"""
This script adds manually recorded temperature values to single trial data from original data for F1509

There are two ways to achieve this:
- Start from scratch (i.e. go through all data)
- Label only those trials that were previously manually selected (i.e. where only cooled trials were included in the data, which assumes a fixed cooling threshold)

Start with previously selected data; we can work back to the original data in stages.

"""

import os, sys
from enum import Enum

import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from Results import cooling_analysis as ca


class Cooling(Enum):
    """ Experimental conditions in which cooling was performed"""

    LEFT = 'Left'
    RIGHT = 'Right'
    CONTROL = 'Control'
    BILATERAL = 'Bilateral'
    

def import_original_behavior(file_path: Path) -> pd.DataFrame:
    """ Gather behavioral data from directories split by condition"""

    all_data = []

    # For each type of cooling
    for condition in Cooling:    

        # Extend path
        condition_dir = file_path / condition.value

        # For each results file
        for text_file in condition_dir.glob('*.txt'):

            behav = pd.read_csv( text_file, sep='\t', encoding='latin1')
            
            # Add session metadata
            behav['Condition'] = condition.value    
            behav['SessionDate'] = ca.filename_to_sessiondate(text_file.name)
            behav['originalFile'] = text_file.stem

            # Add data to list of all data
            all_data.append(behav)

    all_data = pd.concat(all_data)

    # Remove unnamed columns (due to formatting of source data)    
    unnamed = [x for x in all_data.columns if 'Unnamed' in x]
    all_data.drop(columns=unnamed, inplace=True)

    return all_data


def expand_temperature_logs(temp_log: pd.DataFrame, nTrials : pd.DataFrame) -> pd.DataFrame:
    """ Turns temperature observations on specific trials into temperature estimates on each trial"""

    temperatures = []

    # For each session with temperature information
    for session, session_temps in temp_log.groupby('originalFile'):

        # Get max number of trials
        max_trial = nTrials[nTrials['originalFile'] == (session)]['Trial'].values
        assert len(max_trial) == 1

        # Get trials for which temperature estimates are required
        filled_data = pd.DataFrame(np.arange(start=1, stop=max_trial), columns=['Trial'])
        filled_data = filled_data.set_index('Trial').join(session_temps.set_index('Trial'), on='Trial')
        
        filled_data.interpolate(method='pad', inplace=True)
        filled_data.reset_index(level='Trial', inplace=True)
        
        temperatures.append(filled_data)

    # Concatenate and remove nans (occur for trials before first logged temperature)
    temperatures = pd.concat(temperatures)
    temperatures.dropna( axis=0, inplace=True)

    return temperatures


def postprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """ Format column names and variable codes to make user friendly (and consistent with previous analysis)"""

     # For F1311 Magnum, also included visual trials as an extra control experiment (but for F1509 we just used auditory stimuli)
    df['SoundOrLED'].replace({0:'Aud', 1:'Vis'}, inplace=True)

    # Correct for early column headers that included "?"
    df = df.rename(columns={'CorrectionTrial?': 'CorrectionTrial',
                            'CenterReward?': 'CenterReward',
                            'SoundOrLED': 'Modality',
                            'Left': 'LeftTemperature',
                            'Right': 'RightTemperature'})


    return df

def main():

    # Define parent directory for analysis
    paths = {'data': Path('Results/Localization/data')}
    
    # Import temperature records transcribed from log books
    paths['temperatures'] = paths['data'] / 'temperatures/F1509_Robin/F1509_TemperatureData.csv'

    temp_log = pd.read_csv(paths['temperatures'])
    temp_log.drop(temp_log[temp_log['originalFile'] == 'Unknown'].index, inplace=True)      # Drop session that we can't find (where did this go!?)

    # For each file for which temperature data is available
    paths['behavior'] = paths['data'] / 'original/F1509_Robin'
    
    behavior = import_original_behavior(paths['behavior'])

    # Expand temperature records to cover each trial
    nTrials = behavior[['Trial','originalFile']].groupby('originalFile').count()        # Max number of trials in each session
    nTrials.reset_index(level='originalFile', inplace=True)

    temperatures = expand_temperature_logs( temp_log, nTrials)

    paths['expanded_temps'] = paths['data'] / 'temperatures/F1509_Robin/F1509_ExpandedTemperatures.csv'
    temperatures.to_csv( paths['expanded_temps'], index=False)

    # Join expanded temperature records with behavioral data
    behavior.set_index(keys=['Condition','originalFile','Trial'], inplace=True)
    temperatures.set_index(keys=['originalFile','Trial'], inplace=True)
    temperatures.drop(columns=['Condition'], inplace=True)

    combined = behavior.join( temperatures[['Left','Right']], on=['originalFile','Trial'])

    # Tidy up dataframe
    combined = postprocessing(combined)

    # Save data
    paths['output'] = paths['data'] / 'summary/F1509_Robin.csv'
    combined.to_csv( paths['output'])

    



if __name__ == '__main__':
    main()