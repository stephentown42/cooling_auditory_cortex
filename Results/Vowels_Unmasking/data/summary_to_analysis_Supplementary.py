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
    - 2021-10-10: Branched from summary_to_analysis_data.py
"""

from dataclasses import dataclass
import itertools
import os, sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from Results import cooling_analysis as ca
from Results import settings


@dataclass
class ferret():
    """ Data associated with a specific subject """    

    num : int

    def load_data(self, file_path: str) -> None:
        """ Imports summary csv file """
        
        self.data = pd.read_csv( Path(file_path) / f"F{self.num}.csv")

        self.data['fNum'] = self.num        # Label subject


    def add_dummy_treatement_variable(self) -> None:
        """ For consistency with cooled data """        # not really dummy as is technically true
        self.data['treatment'] = False

    
    def add_session_datetime(self) -> None:
        """ Get session date from file name"""
        
        self.data = (self.data.assign(day = lambda df_: pd.to_datetime( df_.originalFile.str.slice(0,10), format='%d_%m_%Y')))


    def deal_with_attenuations(self) -> None:
        """ Round attenuations and drop rare values """

        self.data['Atten'] = ca.round_to_nearest(self.data['Atten'], 1)                         

        self.data['vowel_level'] = (settings['default_level'] - 3) - self.data['Atten']              # Drop default_level by 3 due to one rather than two speakers
        self.data['SNR'] = self.data['vowel_level'] - (settings['noise_level'] - 3)                 # Drop noise_level by 3 due to one rather than two speakers

        self.data = ca.drop_rare_attenuations(self.data, min_trials=settings['min_trials'])


    def make_codes_readable(self) -> None:
        """ Convert codes to human readable labels """      # see level_23.m in methods for original encoding

        self.data['Mask'] = self.data['SpatialMask'].map({
            0 : 'colocated', 
            1 : 'colocated',
            2 : 'separated', 
            3 : 'separated',
            4 : 'single_speaker', 
            5 : 'single_speaker',
        })        
        
        self.data['VowelLocation'] = self.data['SpatialMask'].map({
            0 : 'left',
            1 : 'right',
            2 : 'left',
            3 : 'right',
            4 : 'left', 
            5 : 'right'        
        })


    def remove_correction_trials(self) -> None:
        """ Remove non-correction trials and drop column """
        
        self.data = self.data[self.data['CorrectionTrial'] == 0]
        self.data.drop('CorrectionTrial', axis=1, inplace=True)  


    def check_SNRs_are_balanced(self) -> None:
        """ Flag if SNRs are not tested under all conditions"""

        columns = ['SpatialCondition', 'treatment','SNR','VowelLocation', 'F1']
        isOk, n_trials = self.check_all_permutations_tested(self.data, columns)

        if not isOk:
            print('Permutation warning')
            self.data = self.fix_unbalanced_stimuli(self.data, columns)
    

    @staticmethod                                                                   # Brought directly from bootstrap
    def check_all_permutations_tested(df: pd.DataFrame, columns: list) -> bool:
        """ Does data exist for all possible combinations of values within columns """

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


    def write_data(self, file_path : str) -> None:
        """ Save as csv format """

        summary_file = Path(file_path) / f"F{self.num}.csv"

        self.data.to_csv(summary_file, index=False)



def main():

    # Define subjects that were not tested with cooling (control behavior only)
    ferrets = [ ferret(1201), ferret(1203), ferret(1216), ferret(1217)]

    # For each ferret
    for f in ferrets:

        f.load_data('Results/Vowels_Unmasking/data/summary')
       
        f.remove_correction_trials()                                          # Data preprocessing
        f.deal_with_attenuations()        
        f.add_session_datetime()

        f.add_dummy_treatement_variable()        
        f.make_codes_readable()        
        f.data.rename({'Mask':'SpatialCondition'}, axis=1, inplace=True)      # Tidy up column names        

        f.check_SNRs_are_balanced()
        f.write_data('Results/Vowels_Unmasking/data/analysis')
        

if __name__ == '__main__':
    main()