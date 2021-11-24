"""
Effects of cooling on spatial release from masking - Analysis By Ferret

Flattens data across vowel identity (defined by first formant: F1) and vowel location (left or right speaker)

Input
-----
Data comes from the analysis directory; i.e. some preprocessing has already been done to remove correction trials and any attenuations with small sample sizes.

We also define the variables that we want to:
    - Maintain (and thus plot) - e.g. noise condition (colocated/separated/clean), treatment (cooled/control) and in some cases, SNR
    - Collapse across (while ensuring we take equal sample sizes) - e.g. vowel identity, location, and in some cases, SNR

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
For each subject, the script saves csv files of performance on each bootstrap iteration, for each mask (clean / noisy) and treatment condition (cooled / control or light on/off)
Two files are generated: 
    - Results for every SNR tested
    - Results across SNR

The intention is then to plot the results separately (e.g. using 'bootstrap_plotting.py')

Version History
---------------
    - 2021-09-16: Created (Stephen Town)
    - 2021-11-02: Integrated with general bootstrap library from two-speaker experiments (Vowel Cooling)

"""

import os, sys

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from lib.bootstrap import ferret


def main():  

    rng_seed = 49252466450692985656297363781

    # Define subjects, including those that were not tested with cooling 
    ferrets = [
        ferret(1311,'Magnum', rng_seed),
        ferret(1509,'Robin', rng_seed),
        ferret(1201,'Florence', rng_seed),
        ferret(1203,'Virginia', rng_seed),
        ferret(1216,'Mini', rng_seed), 
        ferret(1217,'Clio', rng_seed)]

    for f in ferrets:

        # Load behavioral data
        f.load_data('Results/Vowels_Unmasking/data/analysis')

        # Run bootstrap by SNR
        f.bootstrap(plot_vars=['SpatialCondition', 'treatment','SNR'], flat_vars=['VowelLocation', 'F1'], nBoots=1000)
        f.write_results('Results/Vowels_Unmasking/data/bootstrap', 'BY_SNR')

        # Run bootstrap over SNR
        f.bootstrap(plot_vars=['SpatialCondition', 'treatment'], flat_vars=['SNR','VowelLocation', 'F1'], nBoots=1000)
        f.write_results('Results/Vowels_Unmasking/data/bootstrap', 'OVER_SNR')


if __name__ == '__main__':
    main()