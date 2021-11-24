# Results

The directory contains the modules used across the repository for standard processing ([cooling_analysis.py](cooling_analysis.py)) and plotting ([plot_tools.py](plot_tools.py)) of data.

## Results by Task:
* [Vowel discrimination in noise](./Vowel_Behavior)
* [Effects of cooling / optogenetics on vowel discrimination in noise](./Vowel_Cooling)
* [Effects of cooling on sound localization](./Localization)
* [Effects of cooling on spatial release from masking](./Vowel_Unmasking)

Code used to visualize results across tasks, such as temperature distributions is held in [Supplementary](./Supplementary)

Matlab utilities holds [legacy code](./matlab_utils) previously used to cross-reference behavioral data with temperatures


## Figure references:

Figures presented in the manu.py and supplementary information

| Figure | Title       | Code        | Image     |
| ------| ----------- | ------      | --------- |
| 1B    | Effect of noise on vowel discrimination           | [.py](./Vowels_Behavior/reaction_time_analysis.py) | [.png](./Vowels_Behavior/images/Fig_1bc.png) |
| 2B-C  | Effect of cooling / optogenetics on vowel discrimination in noise | [.py](./Vowels_Cooling/vin_cooling_by_ferret.py) | [.png](./Vowels_Cooling/images/Vowels_in_Noise_Cooling.png)|
| 3B-C  | Effects of cooling on sound localization          | [.py](./Localization/localization_analysis.py)     | [.png](./Localization/.pngs/localization.png)|
| 4B-D  | Effect of cooling on spatial release from masking | [.py](./Vowels_Unmasking/plot_unmasking_data.py/)  | [/dir](./Vowels_Unmasking/images)|
| S1    | Temperature distributions                         | [.py](./Supplementary/plot_cortical_temperature_dist.py)  | [.png](./Supplementary/images/Temperature_Distributions.png)|
| S2    | Effect of cooling on sound lateralization         | [.py](./Localization/lateralization_supplementary.py)     | [.png](./Localization/images/lateralization.png)|