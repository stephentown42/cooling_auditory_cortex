"""
Permutation tests on individual ferret data to determine the effect of cooling
on performance discriminating vowels for each noise condition (clean / noise)

Version History
----------------
    2021-11-01: Branched from vin_cooling_by_ferret.py

"""

import os, sys

from pathlib import Path
import pandas as pd

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Results import cooling_analysis as ca
from Results import ferrets

from lib.settings import default_level, noise_level


def main():

    data_dir = Path('Results/Vowels_Cooling/data/analysis')

    # For each ferret
    for ferret in ferrets:
        
        if ferret['method'] is None:        # Allow skip for Mini (no cooling)
            continue

        # Load data and do general housekeeping
        file_path = data_dir / f"F{ferret['fNum']}.csv"
        print(file_path.stem)

        df = pd.read_csv( file_path)                                                        
         
        if ferret['name'] == 'Magnum':       
            df['Atten'] = ca.round_to_nearest(df['Atten'], ferret['attn_round'])                 # Consider attenuations in 3 dB intervals for Magnum (account for minor differences in parameters)

        df['rnded_level'] = default_level - df['Atten']
        df['rnded_SNR'] = df['rnded_level'] - noise_level

        ###################################################################################################
        # Run permuation tests for each mask

        # Observed performance
        overSessions = ca.count_correct_trials(df, ['Mask', 'treatment'])
        
        for mask, mdata in overSessions.groupby('Mask'):

            control = mdata[mdata['treatment'] == False]
            test = mdata[mdata['treatment'] == True]

            pt = ca.permutation_test( 
                control['nTrials'].values[0], test['nTrials'].values[0], 
                control['nCorrect'].values[0], test['nCorrect'].values[0], nIterations=10000)

            print(f"{mask}: p = {pt['p_below']:.3f}, obs_delta: {pt['observed_delta']:.3f}")

            
        
        


if __name__ == '__main__':
    main()