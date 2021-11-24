"""
Plot main sound localization figures

For each subject, show:
    - Bilateral cooling results as:
        - Bubble plots of response counts (normalized for total trial count) for each stimulus and response location, for control and bilateral cooling
        - Bar charts of performance (% correct) during control data and bilateral cooling
        - Line plots showing mean (± s.e.m.) absolute error of responses at each platform angle for control data and bilateral cooling
        - Bar charts of mean absolute error across platform angles during control data and bilateral cooling
    - Unilateral cooling results as:
        - Bubble plots of response counts (normalized for total trial count) for each stimulus and response location, for cooling left and right auditory cortex only
        - Bar charts of performance (% correct) during left and right cooling
        - Line plots showing mean (± s.e.m.) absolute error of responses at each platform angle for left and right cooling
        - Bar charts of mean absolute error across platform angles during left and right cooling

Notes on input data:
    Data comes from analysis directory within data folder - i.e. figures are plotting the same results that enter the statistical analysis.

Version History:
    2021-08-??: Created (ST)
"""


from datetime import datetime
import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Results import cooling_analysis as ca
from Results import plot_tools as cplot
from Results.plot_tools import metric_axes
from Results import fonts



fig_size = (5, 7)

colors = dict(
    Bilateral='#7e2e8d',
    Control='#808080',
    Left='#817eff',
    Right='#c04643'
)
     

def create_axes(fig_size, nrows=2, ncolumns=9):
    """
    Create a grid of subplots with specific sizes in centimeters

    Parameters:
    ----------
    fig_size : tuple
        Figure size in inches - should be big enough to contain all
        objects 
    nrows, ncols : int
        Number of rows and columns of axes
        Total number should be >= number listed in structure

    TO DO:
    Invert logic of process:
        Currently: Create axes, assign to struct
        Future: Define in struct, create in figure

    Returns:
    --------
    fig_struct : dict
        Nested dictionary containing plotting objects in a hierarchy 
        organized by plot type, subject and condition. 
        
        Note that all positions are in cm
    """

    fig, axs = plt.subplots(nrows=nrows, ncols=ncolumns, figsize=fig_size)

    fig_struct = dict(
        figure = fig, 
        axs = axs,
        confusion_matrics = dict(
            F1311_Bilateral = metric_axes(axs[0,0], [4, 14.1, 2.5, 2.5], 1311, dropSpines=False),
            F1509_Bilateral = metric_axes(axs[1,0], [4, 10.4, 2.5, 2.5], 1509, dropSpines=False),
            F1311_Left      = metric_axes(axs[0,1], [1.5, 5.4,  2.5, 2.5], 1311, dropSpines=False),
            F1509_Left      = metric_axes(axs[1,1], [1.5, 1.7,  2.5, 2.5], 1509, dropSpines=False),
            F1311_Right     = metric_axes(axs[0,2], [4.7, 5.4,  2.5, 2.5], 1311, dropSpines=False),
            F1509_Right     = metric_axes(axs[1,2], [4.7, 1.7,  2.5, 2.5], 1509, dropSpines=False)
        ),
        correct_over_angle = dict(
            F1311_bilateral  = metric_axes(axs[0,3], [8, 14.1, 1.5, 2.5], 1311),
            F1509_bilateral  = metric_axes(axs[1,3], [8, 10.4, 1.5, 2.5], 1509),
            F1311_unilateral = metric_axes(axs[0,4], [9,  5.4, 2.5, 2.5], 1311),
            F1509_unilateral = metric_axes(axs[1,4], [9,  1.7, 2.5, 2.5], 1509),            
        ),
    )

    # Apply some general settings to each column       
    for ax in fig_struct['confusion_matrics'].values():
        ax.format_by_speaker_location(withSymbol=True)

    fig_struct['confusion_matrics']['F1311_Bilateral'].title('Bilateral Cooling', colors['Bilateral'])
    fig_struct['confusion_matrics']['F1311_Left'].title('Cool Left', colors['Left'])
    fig_struct['confusion_matrics']['F1311_Right'].title('Cool Right', colors['Right'])

    fig_struct['confusion_matrics']['F1311_Bilateral'].ylabel('Response')
    fig_struct['confusion_matrics']['F1509_Bilateral'].ylabel('Response')
    fig_struct['confusion_matrics']['F1509_Bilateral'].xlabel('Sound')

    fig_struct['confusion_matrics']['F1311_Left'].ylabel('Response')
    fig_struct['confusion_matrics']['F1509_Left'].ylabel('Response')
    fig_struct['confusion_matrics']['F1509_Left'].xlabel('Stimulus')
    fig_struct['confusion_matrics']['F1509_Right'].xlabel('Stimulus')

    for ax in fig_struct['correct_over_angle'].values():
        ax.ylabel('% Correct')   
    
    return fig_struct


def get_ferret_info(stem):
    return stem, stem[0:5]


def draw_confusion_matrix( df, condition, ax, scaleFactor=1000):
    """
    Plot the number of trials for each combination of sound and
    response location
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe formatted so that columns are speaker positions, and
        rows are response locations
    control : str
        Type of cooling (e.g. 'Control','Bilateral','Left','Right')        
    ax : Matplotlib axes
        Axes to plot on
    scaleFactor : int
        Scaling to put marker sizes in visible range 
        (given proportion of trials, by itself, is too small)
    
    Returns:
    --------
    None
    """
    
    g = df.groupby(by=['spkr_hemifield', 'resp_hemifield'])
    n = g['Trial'].count()    
    n = n.reset_index(['spkr_hemifield', 'resp_hemifield'])
    
    n['spkr_hemifield'].replace({'L': -90, 'R':90}, inplace=True)
    n['resp_hemifield'].replace({'L': -90, 'R':90}, inplace=True)

    n['Trial'] = n['Trial'] / n['Trial'].sum() 

    if condition == 'Control':
        ax.scatter(x=n['spkr_hemifield'], y=n['resp_hemifield'], s=n['Trial']* scaleFactor, facecolors='none', edgecolors='k', linewidth=0.5)
    else:
        ax.scatter(x=n['spkr_hemifield'], y=n['resp_hemifield'], s=n['Trial']* scaleFactor, c=colors[condition], alpha=0.5, linewidths=0.5)
        
    ax.set_xlim((-150, 150))
    ax.set_ylim((-150, 150))
    
    ax.set_xticks([-90, 90])
    ax.set_yticks([-90, 90])

    ax.set_xticklabels(['L','R'])
    ax.set_yticklabels(['L','R'])

    return None


            


def main():

    root_dir = Path('Results/Localization/data/analysis')
    
    sfig = create_axes(fig_size, nrows=2, ncolumns=5)

    for csv_path in root_dir.glob('*.csv'):
        
        # Load data
        ferret, fNum = get_ferret_info(csv_path.stem)                

        df = pd.read_csv(csv_path)       

        df.drop( df[df['SpkrPos'] == 0].index, inplace=True)
        df.drop( df[df['ResponseAngle'] == 0].index, inplace=True)


        # Run permutation test
        nTrials = df.groupby('Condition')['LatCorrect'].count()
        nCorrect = df.groupby('Condition')['LatCorrect'].sum()

        pt = ca.permutation_test( 
            nTrials['Control'], nTrials['Bilateral'], 
            nCorrect['Control'], nCorrect['Bilateral'], nIterations=10000)

        print(f"{fNum}, bilateral vs control:  p = {pt['p_below']}")


        # For each condition
        for condition, xf in df.groupby(by='Condition'):
            
            color_c = colors[condition]
            f_condition = f"{fNum}_{condition}"
            print(f"{fNum}_{condition}: {xf.shape[0]} trials")

            print(f"{fNum}_{condition}: {xf['LatCorrect'].mean()* 100} % correct (lateraliz)")

            # Plotting
            if condition in ('Left', 'Right'):                  
                f_grp_condition = f"{fNum}_unilateral"
            else:
                f_grp_condition = f"{fNum}_bilateral"
            
            if condition == 'Control':
                draw_confusion_matrix( xf, condition, sfig['confusion_matrics'][f"{fNum}_Bilateral"].ax)
                draw_confusion_matrix( xf, condition, sfig['confusion_matrics'][f"{fNum}_Left"].ax)
                draw_confusion_matrix( xf, condition, sfig['confusion_matrics'][f"{fNum}_Right"].ax)
            else:                                                    
                draw_confusion_matrix( xf, condition, sfig['confusion_matrics'][f_condition].ax)
                        
            
                    
            if condition in ['Bilateral','Control']:        # Show performance across left and right speakers

                condition = condition.replace('Bilateral', 'Cooled')

                sfig['correct_over_angle'][f_grp_condition].add_bar( None, xf['LatCorrect']*100, color_c, condition)  
            
            else:                            

                x_struct = dict(Left = dict(L = 1, R = 4), Right = dict(L = 2, R = 5))
                
                for hemifield, hdata in xf.groupby(by='spkr_hemifield'):        # Show performance by left and right speakers

                    if hemifield is None:       # Skip midline speaker
                        continue

                    hemifield_condition = f"S{hemifield}, C{condition[0]}"
                    bar_x = x_struct[condition][hemifield]                    

                    sfig['correct_over_angle'][f_grp_condition].add_bar( bar_x, hdata['LatCorrect']*100, color_c, hemifield_condition)      
                
    
    # Axes formatting
    sfig['correct_over_angle']['F1311_bilateral'].xticks(None)
    sfig['correct_over_angle']['F1509_bilateral'].bars_to_ticks()   
    sfig['correct_over_angle']['F1311_bilateral'].ax.set_xlim(-0.75, 1.75)
    sfig['correct_over_angle']['F1509_bilateral'].ax.set_xlim(-0.75, 1.75)

    sfig['correct_over_angle']['F1311_unilateral'].ax.set_xticks([1.5, 4.5])
    sfig['correct_over_angle']['F1311_unilateral'].ax.set_xticklabels(['Left', 'Right'])
    
    sfig['correct_over_angle']['F1509_unilateral'].ax.set_xticks([1.5, 4.5])
    sfig['correct_over_angle']['F1509_unilateral'].ax.set_xticklabels(['Left', 'Right'])
    sfig['correct_over_angle']['F1509_unilateral'].xlabel('Speaker Hemifield')

    sfig['correct_over_angle']['F1311_bilateral'].add_chance_line(100/2)
    sfig['correct_over_angle']['F1509_bilateral'].add_chance_line(100/2)
    sfig['correct_over_angle']['F1311_unilateral'].add_chance_line(100/2)
    sfig['correct_over_angle']['F1509_unilateral'].add_chance_line(100/2)

    for obj in sfig['correct_over_angle'].values():                
        obj.ax.set_ylim((0, 100))
        obj.ax.set_yticks(np.linspace(0, 100, 3))
        obj.ax.set_yticklabels(['0','50','100'])        


    # plt.show()
    save_path = 'Results/Localization/images/lateralization.png'
    plt.savefig(save_path, dpi=300)

   
if __name__ == '__main__':
    main()