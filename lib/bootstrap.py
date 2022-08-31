"""
Classes for managing, resampling and summarizing data using pandas dataframes

"""
from dataclasses import dataclass
import itertools
from pathlib import Path
from typing import Optional

import numpy as np
from numpy.random import PCG64
import pandas as pd


@dataclass
class ferret():
    """ Data associated with a specific subject """
    
    num : int
    name : str
    seed : Optional[int]

    def __post_init__(self):
        self.fstr = f"F{self.num}"

        if hasattr(self, 'seed'):
            self.rng = PCG64(self.seed)


    def load_data(self, file_path: str) -> None:
        """Import behavioral data from csv file"""

        self.data = pd.read_csv( Path(file_path) / f"{self.fstr}.csv")        
        print(f"{self.fstr}.csv")


    def count_correct_trials(self, plot_columns : list) -> None:                            # Remove if bootstrap works
        """This is the old way """
                
        self.by_SNR = count_correct_trials(self.data, plot_columns + ['rnded_SNR'])
        self.by_level = count_correct_trials(self.data, plot_columns + ['rnded_level'])
        self.overSessions = count_correct_trials(self.data, plot_columns)
                   

    def bootstrap(self, plot_vars: list, flat_vars: list, nBoots: int = 0) -> None:
        """Get proportion of trials correct in each clean and noise conditions, with and without cooling"""

        summary = summary_table(self.data, plot_vars, flat_vars, self.rng, nBoots)
        summary.count_correct_trials()
        summary.post_processing()

        self.results = summary.bootstrap_data
        self.sample_data = summary.flattened_sample


    def write_results(self, file_path: str, file_suffix: str) -> None:
        """ Write csv files containing bootstrap results and seample data"""

        self.results.to_csv(Path(file_path) / f"{self.fstr}_{file_suffix}.csv", index=False)
        self.sample_data.to_csv(Path(file_path) / f"{self.fstr}_{file_suffix}_SAMPLE.csv", index=False)




@dataclass()
class summary_table():
    """ Data management for bootstrap resampling """

    data : pd.DataFrame
    plot_columns : list
    flat_columns : list
    rng : PCG64
    nBootstrap : int = 0

    def __post_init__(self):
        """ Get lowest number of trials that a given attenuation has for all combinations of conditions """
                
        isOk, n_trials = self.check_all_permutations_tested(self.data, self.plot_columns + self.flat_columns)

        if not isOk:
            print('Permutation warning')
            
        self.median_trials = n_trials.median()
        self.median_trials = int(np.floor(self.median_trials))


    @staticmethod
    def check_all_permutations_tested(df: pd.DataFrame, columns: list) -> bool:
        # Does data exist for all possible combinations of values within columns

        n_conditions = [len(df[c].unique()) for c in columns]
        n_permutations = np.prod(n_conditions)

        n_trials = df.groupby(by=columns).size()
        
        return n_trials.shape[0] == n_permutations, n_trials


    def flatten(self) -> pd.DataFrame:
        """ Subsample equal numbers of trials (flatten) for all combinations of columns of interest """

        flat_data = []
        for conditions, uneven_data in self.data.groupby(by=self.plot_columns+self.flat_columns):           

            flat_data.append( uneven_data.sample(n = self.median_trials, random_state=self.rng, replace=True))

        return pd.concat(flat_data)

    
    def bootstrap_resample(self) -> pd.DataFrame:
        """ Count correct trials for many instances of flattened data """
        bootstrap_results = []

        for i in range(0, self.nBootstrap):

            flat_data = self.flatten()        # Resample data each iteration

            flat_results_i = count_correct_trials(flat_data, self.plot_columns)
            flat_results_i['iteration'] = i

            bootstrap_results.append( flat_results_i)
            
            if i % 100 == 0:                    # Report progress
                print(f"\t\tIteration {i} of {self.nBootstrap}")

        return pd.concat(bootstrap_results), flat_data


    def summarize_bootstrap(self, bootstrap_results: pd.DataFrame) -> pd.DataFrame:
        """ Get mean performance across bootstrap resamples"""
        
        # Group by all the variables we care about
        g = bootstrap_results.drop(columns=['nTrials','nCorrect','iteration']).groupby(by=self.plot_columns)

        # Give each metric it's name        
        pCorrect_mean = g.mean().rename({'pCorrect':'mean'}, axis=1)
        pCorrect_std = g.std().rename({'pCorrect':'std'}, axis=1)

        # Join and send the variable information back into the dataframe 
        table = pCorrect_mean.join(pCorrect_std)
        table.reset_index(self.plot_columns, inplace=True)

        return table


    def count_correct_trials(self) -> None:

        if self.nBootstrap == 0:
            self.table = count_correct_trials(self.data, self.plot_columns)

        else:
            print('Running bootstrap - this might take a while')
            self.bootstrap_data, self.flattened_sample = self.bootstrap_resample()
            self.table = self.summarize_bootstrap( self.bootstrap_data)


    def post_processing(self) -> None:
        """ Add extra information for plotting - this isn't the cleanest code, sorry!"""

        if any(self.table.columns == 'Treatment'):
            self.table['Treatment'] = self.table['treatment'].replace({True:'Test', False:'Control'})                              # Labels that are consistent with other areas of the project (could be cleaner)        



# ANALYSIS:
def count_correct_trials(df, groupvars) -> pd.DataFrame:
    """
    Gets the number of trials correct and in total for each combination of variables
    to preserve
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing columns for trials and whether the animal was correct
        on those trials, as well as some other columns that may be used for grouping
    groupvars : list of str
        Column names to obtain separate trial counts 

    >>> count_correct_trials( pd.DataFrame(np.array([[1, 6, 0], [2, 5, 1], [3, 6, 1]]), columns=['Trial', 'Condition', 'Correct']), ['Condition'])        
        Condition  nTrials  nCorrect    pCorrect
    0          5        1         1        100.0
    1          6        2         1         50.0

    Returns:
    --------
    results : pandas dataframe
        Dataframe containing number of trials and number of trials correct for each 
        combination of groupvars
    """

    grouped_data = df.groupby(groupvars)
    nTrials  = grouped_data['Trial'].count()
    nCorrect = grouped_data['Correct'].sum()

    results = pd.concat([nTrials, nCorrect], axis=1)    
    results.reset_index(level=groupvars, inplace=True)
    results.rename({'Trial':'nTrials', 'Correct':'nCorrect'}, axis=1, inplace=True)

    results['pCorrect'] = results['nCorrect'] / results['nTrials'] * 100

    return results
