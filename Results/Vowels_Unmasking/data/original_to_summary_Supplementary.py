"""
Makes summary data tables for supplementary ferrets not tested with cooling

Created on 2021-10-10 by Stephen Town
"""

from dataclasses import dataclass
import os, sys
from pathlib import Path

import pandas as pd


sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from Results import cooling_analysis as ca


# Calibration corrections applied to get the same level (this information has contaminated the Atten values in the original data)
correction_values = dict(
    F1201 = dict(F1 = 730, correction = 2.),
    F1203 = dict(F1 = 730, correction = 2.),
    F1216 = dict(F1 = 936, correction = 5.),
    F1217 = dict(F1 = 730, correction = 2.),
    F1311_Magnum = dict(F1 = 936, correction = 5.)
)


@dataclass
class ferret():
    """ Data associated with a specific subject """
    
    num : int
    name : str

    def __post_init__(self):
        self.fstr = f"F{self.num}"
        self.attn_correction = correction_values[self.fstr]

    def import_original_data(self, file_path : str) -> pd.DataFrame:
        """ Bring together source data files, saved as text format during experiments"""


        # Extend path to specific subject
        file_path = Path(file_path) / f"F{self.num}_{self.name}"
        all_data = []

        # For each text file 
        for file in file_path.glob('*.txt'):

            df = pd.read_csv(file, sep='\t', encoding='latin1')
                    
            # Pick calibration contamination up as we load in each source file
            if detect_contamination(df):
                idx = (df['F1'] == self.attn_correction['F1'])
                df.loc[idx, 'Atten'] += self.attn_correction['correction']

            df['originalFile'] = file.name
            all_data.append(df)

        self.data = pd.concat(all_data)


    def add_dummy_temperatures(self, dummy_val=37) -> None:
        """ Add dummy values to give the same structure as cooled summary data """

        self.data['LeftTemperature'] = 37
        self.data['RightTemperature'] = 37


    def drop_unnamed_columns(self) -> None:
        """ Remove columns arising from fomatting issue in original data (creates unnamed col at end of table)"""

        unnamed_columns = [x for x in self.data.columns if 'Unnamed' in x]
        self.data.drop(columns=unnamed_columns, inplace=True)


    def format_column_names(self) -> None:
        """ Correct for early column headers that included "?" """

        self.data.rename(columns={'CorrectionTrial?': 'CorrectionTrial', 'CenterReward?': 'CenterReward'}, inplace=True)

      
    def write_data(self, file_path : Path) -> None:
        """ Save as csv format """

        summary_file = Path(file_path) / f"F{self.num}.csv"

        self.data.to_csv(summary_file, index=False)


def detect_contamination(df: pd.DataFrame) -> bool:

    # Get number of trials for each attenuation and vowel combination
    g = df.groupby(by=['F1', 'Atten']).count()['Trial']
    g = pd.DataFrame(g).reset_index(['F1','Atten'])

    # If there is no contaimination by calibration corrections, trials should exist in each (or nearly each combination)
    pt = pd.pivot_table(g, values='Trial', index='Atten', columns='F1')

    return pt.isnull().sum().sum() > 0


def main():
    
    # Define subjects that were not tested with cooling (control behavior only)
    ferrets = [ ferret(1201, 'Florence'), ferret(1203, 'Virginia'), ferret(1216, 'Mini'), ferret(1217, 'Clio')]

    
    for f in ferrets:
        
        f.import_original_data('Results/Vowels_Unmasking/data/original')

        f.add_dummy_temperatures()

        f.drop_unnamed_columns()

        f.format_column_names()
        
        f.write_data('Results/Vowels_Unmasking/data/summary')




if __name__ == '__main__':
    main()