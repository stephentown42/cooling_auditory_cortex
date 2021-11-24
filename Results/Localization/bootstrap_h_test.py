"""
Report results of bootstrap hypothesis testing that cooling impairs vowel discrimiantion


Motivation:
------------
Bootstrap data contains the number of correct trials for each stimulus condition (noise|clean) and treatment condition (e.g. cooled|control).

We want to know if cooling signficantly impairs performance. In essence, what that means is, how certain are we that any observed difference between performance in cooled and control conditions (for a specific stimulus condition) is different from zero.

To address this, we can calculate the effect of cooling on each bootstrap resample and measure the confidence interval for that value.
"""

from pathlib import Path

import pandas as pd

data_dir = Path('Results/Localization/data/bootstrap')

for file_ in data_dir.glob('*bilateral.csv'):

    df = pd.read_csv(file_)



    # Pivot to get the data we need
    pt = pd.pivot_table(df, values='pCorrect', columns=['Condition'], index='iteration')

    # Get difference: cooled - control or light on - off
    pt['delta'] = pt['Bilateral'] - pt['Control']
    pt['above_zero'] = pt['delta'] >= 0 

    conf_int = [(pt['delta'].std() * x) + pt['delta'].mean() for x in [-1.96, 1.96]]
    p = pt['above_zero'].astype(int).sum() / pt.shape[0]

    print(f"{file_.stem[0:5]}: mean delta = {pt['delta'].mean():.3f}, CI: {conf_int[0]:.3f} to {conf_int[1]:.3f}, p = {p:.3f}")