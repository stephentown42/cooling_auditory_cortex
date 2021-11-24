"""
Localization - Analysis By Ferret

Flattens data across vowel identity

Input
-----
Data comes from the analysis directory; i.e. some preprocessing has already been done to remove correction trials and equate sound durations (F1311)

We also define the variables that we want to:
    - Maintain (and thus plot) - e.g. treatment
    - Collapse across (while ensuring we take equal sample sizes) - e.g. sound location and attenuation

Algorithm
---------
1. Determine the number of samples to take from each condition (during initialization of summary table)
Here, each condition refers to the combination of all variables in the analysis (e.g. /a/ in clean conditions during cooling at -10 dB). There are two methods we've looked at
    - Minimum number of trials across conditions (probably the right thing to do)
    - Median number of trials across conditions (gives larger sample sizes)

2. Decide if you're actually going to bootstrap
If not, simply count the number of correct trials for each combination of plotted variables and return.
If yes, resample.

3. Resample
On each bootstrap iteration, flatten the data by taking a fixed number of trials from each condition with replacement. Summarize the flattened data, by counting the number of correct trials for each combination of plotted variables. Append the iteration as an index to the count and then add to list of dataframe results. At the end, concatenate the list to give the performance for each plot condition on each iteration.


Output
------
For each subject, the script saves csv files of performance on each bootstrap iteration, for each treatment condition (cooled / control)


The intention is then to plot the results separately (e.g. using 'bootstrap_plotting.py')

Version History
----------------
    2021-08-??: Created (ST) and continuous updated until 2021-09
    2021-10-18: Branched from vin_cooling_by_ferret.py
    2021-11-01: Moved classes into separate module
    2021-11-17: Branched from vowels in noise -> localization
"""

import os, sys
sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))

from lib.bootstrap import ferret


def main():

    rng_seed = 49252466450692985656297363781
       
    ferrets = [ferret(1311, 'Magnum', rng_seed), ferret(1509, 'Robin', rng_seed)]   
    
    for f in ferrets:
        
        # Load data and filter for control and bilateral
        f.load_data('Results/Localization/data/analysis')

        # Split data according to cooling analysis
        f.unilateral_data = f.data[f.data['Condition'].isin(['Right','Left'])].copy()
        f.data = f.data[f.data['Condition'].isin(['Control','Bilateral'])] 

        # # Run bootstrap across speaker location for bilateral cooling
        # f.bootstrap(plot_vars=['Condition'], flat_vars=['SpkrPos','Atten'], nBoots=1000)
        # f.write_results('Results/Localization/data/bootstrap', 'Control_vs_bilateral')
        
        # Run bootstrap by speaker hemifield
        f.data = f.unilateral_data

        f.bootstrap(plot_vars=['Condition','spkr_hemifield'], flat_vars=['SpkrPos','Atten'], nBoots=1000)
        f.write_results('Results/Localization/data/bootstrap', 'Left_vs_Right')
        
     
if __name__ == '__main__':
    main()