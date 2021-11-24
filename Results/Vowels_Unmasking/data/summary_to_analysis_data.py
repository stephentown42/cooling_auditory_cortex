"""
Vowel unmasking data pre-processing to filter summary data into a form that 
is amenable for data analysis

Here we do some general housekeeping to get the columns into a common format, 
create columns to make the statistics in R more straightforward and bring 
together some columns containing redundant information.

We also filter the data for conditions such as correction trials, which we 
don't consider in this analysis but that are kept in the summary files in
case someone else is interested in behavior over consecutive trials etc,.


Version History
---------------
    - 2021-09-17: Created (Stephen Town)

"""



from dataclasses import dataclass
import os, sys

import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from lib import settings
from Results import cooling_analysis as ca
from Results import ferrets


@dataclass()
class ferret():

    num : int
    name : str
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

    def add_session_date(self) -> None:
        """ Extract date from session names for each trial"""
        self.data = (self.data.assign(day = lambda df_: pd.to_datetime( df_.originalFile.str.slice(0,10), format='%d_%m_%Y')))
        
        # if 'originalFile' in self.data.columns:            
            # self.data['sessionDate'] = self.data['originalFile'].apply(ca.filename_to_sessiondate)      
        
    def remove_correction_trials(self) -> None:
        """ Only take non-correction trials """
        self.data = self.data[self.data['CorrectionTrial'] == 0]                
        self.data.drop('CorrectionTrial', axis=1, inplace=True) 

    def remove_trials_without_response(self) -> None:
        """ Only take trials with responses (no response is very very rare) """
        self.data = self.data[self.data['Response'] >= 0]

    def format_sound_levels(self) -> None:
        """ Express vowel levels in absolute terms and relative to noise (SNR)"""

        self.data['vowel_level'] = (settings.default_level-3) - self.data['Atten']      # Drop default_level by 3 due to one rather than two speakers
        self.data['SNR'] = self.data['vowel_level'] - (settings.noise_level - 3)        # Drop default_level by 3 due to one rather than two speakers

    def format_stimulus_labels(self) -> None:
        """ Make codes for vowel location and mask condition human-readable """

        vowel_map = {
            0 : 'left', 1 : 'right', 2 : 'left', 3 : 'right', 4 : 'left', 5 : 'right'        
        }

        spatial_mask_map = {
            0 : 'colocated', 1 : 'colocated',
            2 : 'separated', 3 : 'separated',
            4 : 'single_speaker', 5 : 'single_speaker'
            }

        self.data['Mask'] = self.data['SpatialMask'].map(spatial_mask_map)
        self.data['VowelLocation'] = self.data['SpatialMask'].map(vowel_map)

    def match_attenuations(self) -> None:
        """ Ensure that we only use the same attenuations tested within a specific time window"""
        self.data = ca.match_for_atten(self.data, time_interval=self.attn_matching_window, condition_interval=self.attn_matching_variable)


# Subject specific issues
def magnum_level_correction(f):

    if f.name == 'Magnum':

        # Deal with calibration contamination 
        attn_correction = dict(F1 = 936, correction = 5.)
        
        for session, df in f.data.groupby('originalFile'):              # This has to be done by session, as we applied the fix to the acquistion system in the middle of testing (so some of the data is fine)
            if detect_contamination(df):
                idx = (df['F1'] == attn_correction['F1'])
                df.loc[idx, 'Atten'] += attn_correction['correction']

        # Consider attenuations in 3 dB intervals for Magnum (account for minor differences in parameters)
        f.data['Atten'] = ca.round_to_nearest(f.data['Atten'], 3)                 


def detect_contamination(df: pd.DataFrame) -> bool:

    # Get number of trials for each attenuation and vowel combination
    g = df.groupby(by=['F1', 'Atten']).count()['Trial']
    g = pd.DataFrame(g).reset_index(['F1','Atten'])

    # If there is no contaimination by calibration corrections, trials should exist in each (or nearly each combination)
    pt = pd.pivot_table(g, values='Trial', index='Atten', columns='F1')

    return pt.isnull().sum().sum() > 0


def robin_control_performance_management(f):
    
    if f.name == 'Robin':       
        f.data = ca.constrain_attenutations_by_control_performance(f.data, settings.control_limit)
               


def main():

    ferrets = [
        ferret(1311, 'Magnum', 'all', 'isCooled'), 
        ferret(1509, 'Robin',  'day', 'isCooled')       # note that in the cooling project, the condition interval is set to 'originalFile' (maybe worth checking how flexible that is)
        ]

    # For each ferrret
    for f in ferrets:

        f.load_data('Results/Vowels_Unmasking/data/summary')

        f.add_subject_metadata()
        f.add_session_date()        

        f.remove_correction_trials()
        f.remove_trials_without_response()

        f.data = ca.temperature_preprocessing(f.data, settings.warm_threshold, settings.cooled_threshold)
        
        magnum_level_correction(f)

        f.match_attenuations()        
        f.format_sound_levels()
        f.format_stimulus_labels()

        robin_control_performance_management(f)

        f.data = ca.drop_rare_attenuations(f.data, min_trials=settings.min_trials)
        f.data.rename({'isCooled':'treatment','Mask':'SpatialCondition'}, axis=1, inplace=True)                    # Tidy up column names        
        
        f.write_data('Results/Vowels_Unmasking/data/analysis')    


if __name__ == '__main__':
    main()