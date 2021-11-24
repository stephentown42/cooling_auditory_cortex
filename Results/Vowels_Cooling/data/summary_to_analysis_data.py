"""
Vowel Cooling: Format data for analysis / plotting

Here we do some general housekeeping to get the columns into a common format, 
create columns to make the statistics in R more straightforward and bring 
together some columns containing redundant information.

We also filter the data for conditions such as correction trials, which we 
don't consider in this analysis but that are kept in the summary files in
case someone else is interested in behavior over consecutive trials

Version History
---------------
    2021-09-??: Created (Stephen Town)

"""

from dataclasses import dataclass
import itertools
import os, sys

import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from lib import settings
from Results import cooling_analysis as ca


@dataclass()
class ferret():

    num : int
    name : str
    method : str
    attn_matching_window : str
    attn_matching_variable : str

    def load_data(self, file_path: str) -> None:
        """ Load data from csv file """

        file_path = Path(file_path) / f"F{self.num}_{self.name}.csv"
        self.data = pd.read_csv( file_path)    
        print(file_path.stem)

    def write_data(self, file_path: str) -> None:
        """ Save to csv for further analysis """
        file_path = Path(file_path) / f"F{self.num}.csv"                          
        self.data.to_csv(file_path, index=False)

    def add_subject_metadata(self) -> None:
        """ Add ferret number and method to dataframe """
        self.data['fNum'] = self.num
        self.data['method'] = self.method

    def add_session_date(self) -> None:
        """ Extract date from session names for each trial"""
        if 'originalFile' in self.data.columns:
            self.data['sessionDate'] = self.data['originalFile'].apply(ca.filename_to_sessiondate)      
        
    def remove_correction_trials(self) -> None:
        """ Only take non-correction trials """
        self.data = self.data[self.data['CorrectionTrial'] == 0]                

    def remove_trials_without_response(self) -> None:
        """ Only take trials with responses (no response is very very rare) """
        self.data = self.data[self.data['Response'] >= 0]

    def add_reaction_times(self, decimal_places: int) -> None:
        """ Turn start and response time marks into floating reaction time"""
        
        self.data['rxnTime'] = self.data['RespTime'] - self.data['StartTime']                                
        self.data['rxnTime'] = self.data['rxnTime'].round(decimal_places)

    def remove_continuous_noise_and_format_mask(self) -> None:
        """ Drop data from other projects and make codes for noise masks human-readable"""
        self.data = self.data[self.data['Mask'] < 2]                        
        self.data['Mask'].replace({0:'Clean', 1:'Restricted'}, inplace=True)

    def format_vowel_labels(self) -> None:
        """ Make codes for vowel identity human-readable """

        self.data['vowel'] = self.data['F1'] + self.data['F2'] + self.data['F3'] + self.data['F4'] # This line could probably be shortend
        self.data['vowel'].replace({8627:'u',9725:'a', 9850:'e', 10436:'i'}, inplace=True)  

    def format_sound_levels(self) -> None:
        """ Express vowel levels in absolute terms and relative to noise (SNR)"""

        self.data['vowel_level'] = settings.default_level - self.data['Atten']
        self.data['SNR'] = self.data['vowel_level'] - settings.noise_level

    def format_treatment(self):
        """ Identify inactivation trials using a method-dependent strategy """

        if self.method == 'opto':                                                  
            self.data['opto'].replace({0:False, 1:True}, inplace=True)
            self.treatment_var = 'opto'

        elif self.method == 'cool':
            self.data = ca.temperature_preprocessing(self.data, settings.warm_threshold, settings.cooled_threshold)
            self.treatment_var = 'isCooled'

    def match_attenuations(self) -> None:
        """ Ensure that we only use the same attenuations tested within a specific time window"""
        self.data = ca.match_for_atten(self.data, time_interval=self.attn_matching_window, condition_interval=self.attn_matching_variable)

    def tidy_up_column_names(self) -> None:
        
        self.data.rename({self.treatment_var:'treatment'}, axis=1, inplace=True)                    

        columns = ['F1','F2','F3','F4','Side','RespTime','StartTime','UniversalStartTime','originalFile','day','CorrectionTrial','noiseAtten','laserOnset','laserOffset']  # Drop these columns
        [self.data.drop(c, axis=1, inplace=True) for c in columns if c in self.data.columns.to_list() ]

    def check_SNRs_are_balanced(self) -> None:

        columns = ['Mask','treatment','SNR', 'vowel']
        isOk, n_trials = self.check_all_permutations_tested(self.data, columns)

        if not isOk:
            print('Permutation warning')
            self.data = self.fix_unbalanced_stimuli(self.data, columns)
    

    @staticmethod                                                                   # Brought directly from bootstrap
    def check_all_permutations_tested(df: pd.DataFrame, columns: list) -> bool:
        # Does data exist for all possible combinations of values within columns

        n_conditions = [len(df[c].unique()) for c in columns]
        n_permutations = np.prod(n_conditions)

        n_trials = df.groupby(by=columns).size()
        
        return n_trials.shape[0] == n_permutations, n_trials

    @staticmethod
    def fix_unbalanced_stimuli(df: pd.DataFrame, columns: list):                # Brought directly from bootstrap

        # Create a dataframe with all the required experimental conditions
        conditions = [df[c].unique() for c in columns]
        required = pd.DataFrame( list(itertools.product(*conditions)), columns=columns)         

        # Identify those required conditions that aren't in the test data
        tested = df.groupby(columns).size().reset_index(columns)
        missing = required.merge(tested, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='left_only']        
        print(missing[columns])

        # Resolve based on SNR - this is specific for the vowel/noise project and might not generalize (need to think more on that if it arises)
        for SNR_to_drop in missing['SNR'].unique():
            df.drop(df[df['SNR'] == SNR_to_drop].index, inplace=True)

        if df.shape[0] == 0:
            raise NameError('Correction for imbalanced stimuli removed all the data! (Better have a look)')

        return df


# Subject specific issues
def magnum_level_correction(f):

    if f.name == 'Magnum':  
        f.data.loc[f.data['F1'] == 936, 'Atten'] += 5                          # Fix for error when calibration correction included in logging (this shouldn't happen, and was corrected for the later animals)     
        f.data['Atten'] = ca.round_to_nearest(f.data['Atten'], 3)                 # Consider attenuations in 3 dB intervals (account for minor [1 dB] differences in parameters)

def robin_control_performance_management(f):
    
    if f.name == 'Robin':       
        f.data = ca.constrain_attenutations_by_control_performance(f.data, settings.control_limit)
               


def main():
        

    ferrets = [
        ferret(1311, 'Magnum', 'cool', 'all', 'isCooled'), 
        ferret(1509, 'Robin', 'cool', 'day', 'originalFile'), 
        ferret(1706, 'Mimi', 'opto', 'sessionDate', 'opto')
        ]
    
    for f in ferrets:          

        f.load_data('Results/Vowels_Cooling/data/summary')
       
        f.remove_correction_trials()
        f.remove_trials_without_response()
        f.remove_continuous_noise_and_format_mask()

        f.add_subject_metadata()
        f.add_session_date()
        f.add_reaction_times(decimal_places=4)
        
        magnum_level_correction(f)

        f.format_vowel_labels()
        f.format_sound_levels()
        f.format_treatment()

        f.match_attenuations()
        
        robin_control_performance_management(f)
        
        f.data = ca.drop_rare_attenuations(f.data, min_trials=settings.min_trials)
            
        f.tidy_up_column_names()
        f.check_SNRs_are_balanced()
        f.write_data('Results/Vowels_Cooling/data/analysis')



if __name__ == '__main__':
    main()