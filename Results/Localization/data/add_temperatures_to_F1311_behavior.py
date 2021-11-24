"""
This script adds manually recorded temperature values to single trial data from original data for F1311

There are two ways to achieve this:
- Start from scratch (i.e. go through all data)
- Label only those trials that were previously manually selected (i.e. where only cooled trials were included in the data, which assumes a fixed cooling threshold)

Start with previously selected data; we can work back to the original data in stages.

"""

import os, sys
from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import seaborn as sns

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


def replace_error_values(df: pd.DataFrame, column : str) -> None:
    """ Replace error values introduced during thermocouple disconnection"""

    df.loc[(df[column] > 39), column] = np.NaN          # Ferret cortex should never be 40 or more
    df.loc[(df[column] < 1), column] = np.NaN          # We never cooled this much

    df[column].ffill(axis = 0, inplace=True)


def postprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """ Format column names and variable codes to make user friendly (and consistent with previous analysis)"""


    # For F1311 Magnum, also included visual trials as an extra control experiment (but for F1509 we just used auditory stimuli)
    df['SoundOrLED'].replace({0:'Aud', 1:'Vis'}, inplace=True)

    # Correct for early column headers that included "?"
    df = df.rename(columns={'CorrectionTrial?': 'CorrectionTrial',
                            'CenterReward?': 'CenterReward',
                            'SoundOrLED': 'Modality',
                            'Loop_L':'LeftTemperature',
                            'Loop_R':'RightTemperature'})

    return df


def main():

    # Define parent directory for analysis
    paths = {'data': Path('Results/Localization/data')}
    
    # Import temperature summary
    paths['temperatures'] = paths['data'] / 'temperatures/F1311_Magnum/F1311_SummaryTemperatures.csv'
    
    temperature = pd.read_csv(paths['temperatures'])  
    temperature['datetime'] = pd.to_datetime(temperature['datetime'], format='%d-%b-%Y %H:%M:%S')  
    temperature.sort_values(by='datetime', inplace=True)

    replace_error_values(temperature, 'Loop_L') 
    replace_error_values(temperature, 'Loop_R') 
   
    # For each file for which temperature data is available
    paths['behavior'] = paths['data'] / 'original/F1311_Magnum'
    
    behavior = import_original_behavior(paths['behavior'])

    # Expand behavior so that the data is in the shape we eventually want
    behavior.reset_index(drop=True, inplace=True)
    behavior['datetime'] = behavior.SessionDate + pd.to_timedelta(behavior['StartTime'], unit='s')
    behavior['Loop_L'] = np.NaN
    behavior['Loop_R'] = np.NaN
    
    # Label data for later recovery
    behavior['recoveryIndex'] = behavior.index
    temperature['recoveryIndex'] = -1

    # Combine common data (with missing values for behavior)
    columns = ['datetime','Loop_R','Loop_L','recoveryIndex']
    xref = temperature[columns].copy().append(behavior[columns])
    
    # Sort by datetime and fill missing values (behavior) based on last observation (temperature)
    xref.sort_values(by='datetime', inplace=True)
    xref.fillna(method="ffill", inplace=True)

    # Recover behavioral data
    behavior.drop(['Loop_L', 'Loop_R'], axis=1, inplace=True)               # Remove missing data
        
    xref = xref[xref['recoveryIndex'] >= 0]
    xref.set_index( keys='recoveryIndex', inplace=True)

    behavior = behavior.join(xref[['Loop_L','Loop_R']])
    behavior.drop(['recoveryIndex','datetime'], axis=1, inplace=True)       # Remove columns used for cross-referencing

    # Tidy up dataframe
    behavior = postprocessing(behavior)

    # Save data
    paths['output'] = paths['data'] / 'summary/F1311_Magnum.csv'
    behavior.to_csv( paths['output'], index=False)

    



if __name__ == '__main__':
    main()