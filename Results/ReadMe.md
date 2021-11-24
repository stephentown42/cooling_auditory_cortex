# Results

## Results by Task:
* [Vowel discrimination in noise](./Vowel_Behavior)
* [Effects of cooling / optogenetics on vowel discrimination in noise](./Vowel_Cooling)
* [Effects of cooling on sound localization](./Localization)
* [Effects of cooling on spatial release from masking](./Vowel_Unmasking)

Code used to visualize results across tasks, such as temperature distributions is held in [Supplementary](./Supplementary)

Matlab utilities holds [legacy code](./matlab_utils) previously used to cross-reference behavioral data with temperatures


## Figure references:

Figures presented in the manuscript and supplementary information

| Figure | Title       | Code        | Image     |
| ------| ----------- | ------      | --------- |
| 2     | Effect of cooling / optogenetics on vowel discrimination in noise | [.py](./Vowels_Cooling/bootstrap_plotting.py ) | [F1311](./Vowels_Cooling/images/F1311.png), [F1509](./Vowels_Cooling/images/F1509.png), [F1706](./Vowels_Cooling/images/F1706.png) |
| 3B-E  | Effect of cooling on spatial release from masking | [.py](./Vowels_Unmasking/plot_unmasking_data.py/)  | [/dir](./Vowels_Unmasking/images)|
| 4B-C  | Effects of cooling on sound localization          | [.py](./Localization/localization_analysis.py)     | [.png](./Localization/images/localization.png)|
| S1    | Temperature distributions                         | [.py](./Supplementary/plot_cortical_temperature_dist.py)  | [.png](./Supplementary/images/Temperature_Distributions.png)|
| S2    | Spatial release from masking in additional animals | [.py](./Localization/lateralization_supplementary.py)     | [.png](https://github.com/stephentown42/cooling_auditory_cortex/blob/main/Results/Vowels_Unmasking/images/F1201_control.png)|
| S3    | Effect of cooling on sound lateralization         | [.py](./Localization/lateralization_supplementary.py)     | [.png](./Localization/images/lateralization.png)|
| S4    | Performance vs trial         | [.py](./Supplementary/learning_during_cooling.py)     | [F1311](./Supplementary/images/Performance_vs_trial_F1311.png), [F1509](./Supplementary/images/Performance_vs_trial_F1509.png)|
