"""
Create figures for spatial unmasking portion of cooling paper

TO DO:
Flatten sample sizes across SNR

I've tried to make this as well coded as possible, but it's impossible to 
make everything tidy when there are so many small formatting differences
between panels

There are almost certainly improvements that can be made to reflect better
design principles, but this is what we've got for the moment


Version History
---------------
    - 2021-09-16: Created (Stephen Town)

"""

from dataclasses import dataclass
import os, sys


import matplotlib.pyplot as plt
import numpy as np
from numpy.random import PCG64
import pandas as pd
from pathlib import Path
import seaborn as sns

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Results import cooling_analysis as ca
from Results import plot_tools as cplot
from Results.plot_tools import metric_axes
from Results import settings, ferrets

@dataclass
class ferret():
    """ Data associated with a specific subject """
    
    num : int
    name : str

    def __post_init__(self):
        self.fstr = f"F{self.num}"


    def load_data(self, parent_dir) -> None:
        """Import behavioral data from csv file and do some minor formatting"""

        df = pd.read_csv( parent_dir / f"{self.fstr}.csv")

        df.rename({'Mask':'SpatialCondition'}, axis=1, inplace=True)
        
        self.data = df


    def summarize_data(self) -> None:
        """Get proportion of trials correct in each spatial condition, with and without cooling"""
       
        count_by_attn = ca.count_correct_trials(self.data, ['SpatialCondition', 'treatment','Atten'])
        count_by_attn['Treatment'] = count_by_attn['treatment'].replace({True:'Test', False:'Control'})                              # Labels that are consistent with other areas of the project (could be cleaner)
        
        self.summary_by_attn = count_by_attn
        self.summary_over_attn = ca.count_correct_trials(self.data, ['SpatialCondition', 'treatment'])


    def get_release_from_masking(self) -> None:
        """Get performance change (raw and normalized) resulting from separation of speakers"""

        self.release_from_masking = get_release_from_masking(self.summary_over_attn.copy())




@dataclass
class perm_test():

    subject : ferret            # Original results
    shuffle_var : str
    nIterations : int
    experimental_var : str
    layered_var : str

    def __post_init__(self):    
        self.data = self.subject.data.copy()        
        self.rng = PCG64(224947)

        self.values_to_shuffle = self.data[self.shuffle_var].copy().reset_index()


    def shuffle_data(self) -> None:
        """ Shuffle values within one column """
                 
        shuffled_values = self.values_to_shuffle.sample(frac=1, random_state=self.rng)
        shuffled_values.reset_index(inplace=True, drop=True)     
       
        self.data.drop(self.shuffle_var, axis=1, inplace=True)        # Drop any residual record
        self.data[self.shuffle_var] = shuffled_values[self.shuffle_var]

    
    def get_results(self, i: int) -> pd.DataFrame:
        """ Get performance in each spatial condition, with and without cooling"""
                
        result = ca.count_correct_trials(self.data, ['SpatialCondition', 'treatment'])
        result['iteration'] = i

        return result


    def generate_shuffled_data(self) -> None:
        """ Run the test by repeated shuffling and remeasuring results """

        results = []

        for i in range(0, self.nIterations):

            self.shuffle_data()

            results.append( self.get_results(i))
        
        self.results = pd.concat(results)
        

    def get_null_distribution(self) -> None:
        """ Organize shuffled results prior to evaluation of observed values """

        results = pd.pivot_table(self.results, values='pCorrect', columns=self.experimental_var, index=['iteration', self.layered_var])

        results = self.get_performance_delta(results, self.experimental_var)

        self.null_dist = results.reset_index(level=[self.layered_var])


    def get_experimental_effect(self) -> None:
        """ Give experimental results same format as null distributions for easy evaluation """

        results = pd.pivot_table(self.subject.summary_over_attn, values='pCorrect', columns=self.experimental_var, index=[self.layered_var])

        results = self.get_performance_delta(results, self.experimental_var)        

        self.experimental_obs = results.reset_index(level=[self.layered_var])


    @staticmethod
    def get_performance_delta(results, experimental_var) -> pd.DataFrame:
        """ Caluculate difference between conditions of interest """

        if experimental_var == 'treatment':                                     # This could be tidier
            results['delta'] = results[True] - results[False]
        elif experimental_var == 'SpatialCondition':
            results['delta'] = results['separated'] - results['colocated']
        else:
            pass

        return results


    def evaluate_observations(self) -> None:

        print(self.subject.fstr)
                
        for layer, layer_data in self.experimental_obs.groupby(by=self.layered_var):
            
            null_data = self.null_dist[ self.null_dist[ self.layered_var]== layer]

            observation = layer_data['delta'].to_numpy()
            null_vector = null_data['delta'].to_numpy()

            p_above = sum(null_vector > observation) / len(null_vector)
            p_below = sum(null_vector < observation) / len(null_vector)

            print(f"{self.layered_var} = {layer}: observed = {observation}, null = {np.mean(null_vector)} ± {np.std(null_vector)}")
            print(f"p < obs = {p_below}, p > obs = {p_above}")



def get_count_over_attn(data):
    """ Count the number of correct trials for each spatial condition and cooling condition"""

    count_over_attn = ca.count_correct_trials(data, ['SpatialCondition', 'treatment'])
    

    return count_over_attn


def get_release_from_masking(summary_over_attn):
    """Get performance change (raw and normalized) resulting from separation of speakers"""

    # Get performance across and by sound level
    count_over_attn = summary_over_attn.set_index('SpatialCondition')

    # Split by cooling
    cooled = count_over_attn[count_over_attn['treatment'] == True]['pCorrect'].to_dict()
    control = count_over_attn[count_over_attn['treatment'] == False]['pCorrect'].to_dict()

    # Calculate release (I know there's faster ways of doing this, but I don't have time to streamline every bit of code)
    cool_release = cooled['separated'] - cooled['colocated']
    ctrl_release = control['separated'] - control['colocated']

    cool_norm_release = cool_release / (cooled['single_speaker'] - cooled['colocated']) * 100
    ctrl_norm_release = ctrl_release / (control['single_speaker'] - control['colocated']) * 100

    # Assign to object as nested dictionary
    return dict(
        raw_control = ctrl_release,
        raw_cooled = cool_release,
        norm_control = ctrl_norm_release,
        norm_cooled = cool_norm_release
    )




def main():  

    # Filter imported ferrets for those that had cooling
    cooled_ferrets = [ferret(x['fNum'], x['name']) for x in ferrets if x['method'] == 'cool']

    # Load behavioral data
    root_dir = Path('Results/Vowels_Unmasking/')
    input_path = root_dir / 'data' / 'analysis'

    [x.load_data(input_path) for x in cooled_ferrets]

    # Get performance summary for each animal
    [x.summarize_data() for x in cooled_ferrets]

    # Get release from masking values for each animal
    [x.get_release_from_masking() for x in cooled_ferrets]

    # Set up and run permutation tests
    # perm_tests = [perm_test(x, 'Correct', nIterations=1000, experimental_var='treatment', layered_var='SpatialCondition') for x in cooled_ferrets]

    # [x.generate_shuffled_data() for x in perm_tests]

    # # Organize results to measure effect of cooling
    # [x.get_null_distribution() for x in perm_tests]

    # [x.get_experimental_effect() for x in perm_tests]

    # [x.evaluate_observations() for x in perm_tests]
    
    # Set up and run permutation tests
    effect_of_condition = [perm_test(x, 'Correct', nIterations=1000, experimental_var='SpatialCondition', layered_var='treatment') for x in cooled_ferrets]

    for x in effect_of_condition:

        x.generate_shuffled_data()
        
        x.get_null_distribution()

        x.get_experimental_effect() 

        x.evaluate_observations()




if __name__ == '__main__':
    main()