'''

Bring together data from multiple sessions with optogenetic testing 
of vowel discrimination in noise by F1706_Mimi

Tested in white elephant with sounds in restricted noise only, varying vowel in level and thus SNR.


'''

from datetime import datetime

import pandas as pd
from pathlib import Path

parent_dir = Path('Results/Vowels_Cooling/data/original/F1706_Mimi')


def filename_to_sessiondate(s):

    [f_date, _, f_time, _] = s.split()
    date_string = f_date + ' ' + f_time[0:5]
    session_dt = datetime.strptime(date_string, '%d_%m_%Y %H_%M')

    return session_dt


def main():

    all_data = []
    for file in parent_dir.glob('*.txt'):
        
        df = pd.read_csv( str(file), delimiter='\t', encoding='latin1', index_col='Trial')
        
        unnamed = [x for x in df.columns if 'Unnamed' in x]
        df.drop(unnamed, inplace=True, axis=1)

        df['Mask'] = 1
        df['sessionDate'] = filename_to_sessiondate(file.stem)

        df = df.rename(columns={'CorrectionTrial?': 'CorrectionTrial','CenterReward?': 'CenterReward'})

        all_data.append(df)

    all_data = pd.concat(all_data)
    all_data.to_csv('Results/Vowels_Cooling/data/summary/F1706_Behavior.csv')


if __name__ == '__main__':
    main()