# Spatial Release from Masking

Code for plotting the effects of spatial separation of noise and vowel on task performance, with and without cooling ([script](plot_unmasking_data.py) and [figures] (./images))


## Data
CSV files containing data from original experiments, through to analysis code.


## Simulations



## Matlab Utils (Obsolete)

Legacy code from initial analysis

- plotPerformance_SpatialMask_SNR
- plotPerformance_SpatialMask_SNR_bar
- plotPerformance_SpatialMask_SNR_cdf

Import data from .mat file for each subject in Results/Vowels_Unmasking/Cross-referenced Behavior

For each ferret, generate a 2 x 3 grid plot showing performance on cooled and control trials with:
* Vowel only
* Colocalized vowel + noise 
* Separated vowel + noise 

Also show are:
* Performance across SNR 
* Performance in control conditions
* Performance in cooling

In all cases, performance corresponds to % Correct, and an active figure is returned for the user to then save as they want




