"""
Plot main sound localization figures

For each subject, show:
    - Bilateral cooling results as:
        - Bubble plots of response counts (normalized for total trial count) for each stimulus and response location, for control and bilateral cooling
        - Bootstrap scatter plots (markers with mean ± s.d.) charts of performance (% correct) during control data and bilateral cooling
        - Line plots showing mean (± s.e.m.) absolute error of responses at each platform angle for control data and bilateral cooling
        - Bar charts of mean absolute error across platform angles during control data and bilateral cooling
    - Unilateral cooling results as:
        - Bubble plots of response counts (normalized for total trial count) for each stimulus and response location, for cooling left and right auditory cortex only
        - Bootstrap scatter plots (markers with mean ± s.d.) of performance (% correct) during left and right cooling
        - Line plots showing mean (± s.e.m.) absolute error of responses at each platform angle for left and right cooling
        - Bar charts of mean absolute error across platform angles during left and right cooling

Notes on input data:
    Data comes from analysis directory within data folder - i.e. figures are plotting the same results that enter the statistical analysis.

Version History:
    2021-08-??: Created (ST)
    2021-11-19: Updated for bootstrap plotting
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import sem

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from lib import plot_utils as cplot
from Results.Localization.plotting import metric_axes


colors = dict(
    Bilateral='#7e2e8d',
    Control='#808080',
    Left='#817eff',
    Right='#c04643'
)


@dataclass()
class ferret_to_plot():
   
    num : int
    name : str
    n_speakers : int

    def __post_init__(self):
        ''' Define chance performance as a function of number of speaker locations '''
        self.chance_p = 100.0 / float(self.n_speakers)

    def load_bootstrap_results(self, file_path : str) -> None:
        """ Load results from bootstrapping """
        file_path = Path(file_path)
        self.bilateral_bootstrap = pd.read_csv( file_path / f"F{self.num}_Control_vs_bilateral.csv")
        self.unilateral_bootstrap = pd.read_csv( file_path / f"F{self.num}_Left_vs_Right.csv")


    def load_analysis_data(self, file_path : str) -> None:
        """ Load results from bootstrapping """
        file_path = Path(file_path)
        self.analysis_data = pd.read_csv( file_path / f"F{self.num}.csv")


    def get_effect_of_cooling(self) -> None:
        """Get performance change (raw and normalized) resulting from separation of speakers"""

        # Filter for cooling and then pivot to make the calculation easy to read        
        df = self.bootstrap_data.pivot_table(index=['iteration'], columns=['Condition'], values='pCorrect')

        # Calculate the absolute difference between separated and colocated speakers, and then express relative to the max difference (i.e. that observed between clean and colocated noise)
        df['effect'] = df['Bilateral'] - df['Control']        
        
        # Assign to object as dataframe with release from masking on each iteration (for scatter plotting)
        self.bootstrap_effect_of_cooling = df.reset_index(level=['iteration'])


    def report_performance_by_cooling_condition(self) -> None:
        ''' Text report to console for adding to manuscript'''
        
        for condition, xf in self.analysis_data.groupby(by='Condition'):
                    
            print(f"F{self.num}, {condition}: {xf.shape[0]} trials")
            print(f"{condition}: Mean % correct = {xf['Correct'].mean()*100})")
            print(f"{condition}: Mean error = {xf['Error'].mean()}°)")


@dataclass()
class localization_figure():
    """ Output figure  """

    fig_size: tuple
    nrows: int
    ncols: int

    def __post_init__(self):
        ''' Create graphics objects '''

        self.fig, self.axs = plt.subplots(nrows=self.nrows, ncols=self.ncols, figsize=self.fig_size)

        self.struct = self.organize_layout(self.axs)

    @staticmethod
    def organize_layout(axs) -> dict:    
        """  Create a grid of subplots with specific sizes in centimeters """

        fig_struct = dict(
            confusion_matrics = dict(
                F1311 = dict(
                    Bilateral = metric_axes(axs[0,0], [6.1, 14.1, 2.5, 2.5], 1311, dropSpines=False),
                    Left      = metric_axes(axs[0,1], [1.5, 5.4,  2.5, 2.5], 1311, dropSpines=False),
                    Right     = metric_axes(axs[0,2], [4.2, 5.4,  2.5, 2.5], 1311, dropSpines=False),
                ),
                F1509 = dict(
                    Bilateral = metric_axes(axs[1,0], [6.1, 10.4, 2.5, 2.5], 1509, dropSpines=False),
                    Left      = metric_axes(axs[1,1], [1.5, 1.7,    2.5, 2.5], 1509, dropSpines=False),                
                    Right     = metric_axes(axs[1,2], [4.2, 1.7,    2.5, 2.5], 1509, dropSpines=False)
                )
            ),
            correct_over_angle = dict(
                F1311 = dict(
                    bilateral  = metric_axes(axs[0,3], [10, 14.1, 1.5, 2.5], 1311),
                    unilateral = metric_axes(axs[0,4], [8,  5.4,  2.5, 2.5], 1311)
                ),
                F1509 = dict(
                    bilateral  = metric_axes(axs[1,3], [10, 10.4, 1.5, 2.5], 1509),
                    unilateral = metric_axes(axs[1,4], [8,  1.7,    2.5, 2.5], 1509)
                )
            ),
            error_vs_angle = dict(
                F1311 = dict(
                    bilateral  = metric_axes(axs[0,5], [13.1, 14.1, 2.5, 2.5], 1311),                            
                    unilateral = metric_axes(axs[0,6], [12,   5.4, 2.5, 2.5], 1311)
                ),
                F1509 = dict(
                    bilateral  = metric_axes(axs[1,5], [13.1, 10.4, 2.5, 2.5], 1509),
                    unilateral = metric_axes(axs[1,6], [12,   1.7,   2.5, 2.5], 1509)
                )
            ),
            error_over_angle = dict(
                F1311 = dict(
                    bilateral  = metric_axes(axs[0,7], [16, 14.1, 1.5, 2.5], 1311),
                    unilateral = metric_axes(axs[0,8], [15, 5.4,  2.5, 2.5], 1311)
                ),
                F1509 = dict(
                    bilateral  = metric_axes(axs[1,7], [16, 10.4, 1.5, 2.5], 1509),
                    unilateral = metric_axes(axs[1,8], [15, 1.7,  2.5, 2.5], 1509)
                )
            ),        
        )
        
        return fig_struct


    def format_axes_for_saving(self) -> None:
        ''' Axes formatting - gotta suffer to be beautiful '''

        cplot.match_axes_limits([
            self.struct['error_vs_angle']['F1509']['bilateral'].ax,
            self.struct['error_vs_angle']['F1509']['unilateral'].ax,
            self.struct['error_over_angle']['F1509']['bilateral'].ax,            
            self.struct['error_over_angle']['F1509']['unilateral'].ax
        ], 'y', min_to_zero=True)


    def save(self, file_path: str, file_name: str) -> None:
        ''' Save figure as png '''
        
        save_path = Path(file_path) / file_name
        plt.savefig(save_path, dpi=300)


# Could have a class here for confusion matrix
def add_confusion_matrices(sfig: localization_figure, f: ferret_to_plot) -> None:
    ''' Show proportion of trials at each target/response combination as bubble plot '''

    ax_dict = sfig.struct['confusion_matrics'][f"F{f.num}"]

    # Confusion matrices shown for analysis data
    for condition, xf in f.analysis_data.groupby(by='Condition'):

        # Plot control data on all axes (as background)
        if condition == 'Control':
            draw_confusion_matrix( xf, condition, ax_dict["Bilateral"].ax)
            draw_confusion_matrix( xf, condition, ax_dict["Left"].ax)
            draw_confusion_matrix( xf, condition, ax_dict["Right"].ax)
        
        # Plot cooled data on just one axes (as overlay)
        else:                                                    
            draw_confusion_matrix( xf, condition, ax_dict[condition].ax)

    # Axes formatting
    for ax in ax_dict.values():
        ax.format_by_speaker_location(withSymbol=True)

    # Add titles to top row
    if f.num == 1311:
        ax_dict['Bilateral'].title('Bilateral Cooling', colors['Bilateral'])
        ax_dict['Left'].title('Cool Left', colors['Left'])
        ax_dict['Right'].title('Cool Right', colors['Right'])
    
    # Add xlabels to bottom row
    if f.num == 1509:
        [ax.xlabel('Stimulus') for ax in ax_dict.values()]        

    # Add y label to relevant axes, or get rid of labels if not showing 
    ax_dict['Bilateral'].ylabel('Response')    
    ax_dict['Left'].ylabel('Response')
    ax_dict['Right'].ax.set_yticklabels('')
    

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
    
    g = df.groupby(by=['SpkrPos', 'ResponseAngle'])
    n = g['Trial'].count()    
    n = n.reset_index(['SpkrPos', 'ResponseAngle'])

    n['Trial'] = n['Trial'] / n['Trial'].sum() 

    if condition == 'Control':
        ax.scatter(x=n['SpkrPos'], y=n['ResponseAngle'], s=n['Trial']* scaleFactor, facecolors='none', edgecolors='k', linewidth=0.5)
    else:
        ax.scatter(x=n['SpkrPos'], y=n['ResponseAngle'], s=n['Trial']* scaleFactor, c=colors[condition], alpha=0.5, linewidths=0.5)
        
    return None


# Percentage Correct
def plot_pCorrect_by_condition(sfig: localization_figure, f: ferret_to_plot) -> None:

    # Get axes for this subject
    ax_dict = sfig.struct['correct_over_angle'][f"F{f.num}"]
    
    # Convert proportion to percentage
    c_data = f.unilateral_bootstrap[['Condition','pCorrect','spkr_hemifield']].copy()    
    
    # Plot mean and standard deviation for bilateral vs. control data
    df = f.bilateral_bootstrap[f.bilateral_bootstrap['Condition'] == 'Bilateral']
    ax_dict['bilateral'].plot_bootstrap_scatter( 0, df['pCorrect'], colors['Bilateral'], 'Cooled')

    df = f.bilateral_bootstrap[f.bilateral_bootstrap['Condition'] == 'Control']
    ax_dict['bilateral'].plot_bootstrap_scatter( 1, df['pCorrect'], colors['Control'], 'Control')

    # Plot mean and standard deviation for unilateral cooling (left vs. right cortex / left vs. right speaker hemifield)
    df = c_data[(c_data['Condition'] == 'Left') &  (c_data['spkr_hemifield'] == 'L')]
    ax_dict['unilateral'].plot_bootstrap_scatter( 1, df['pCorrect'], colors['Left'])            

    df = c_data[(c_data['Condition'] == 'Left') &  (c_data['spkr_hemifield'] == 'R')]
    ax_dict['unilateral'].plot_bootstrap_scatter( 4, df['pCorrect'], colors['Left'])            

    df = c_data[(c_data['Condition'] == 'Right') &  (c_data['spkr_hemifield'] == 'L')]
    ax_dict['unilateral'].plot_bootstrap_scatter( 2, df['pCorrect'], colors['Right'])            

    df = c_data[(c_data['Condition'] == 'Right') &  (c_data['spkr_hemifield'] == 'R')]
    ax_dict['unilateral'].plot_bootstrap_scatter( 5, df['pCorrect'], colors['Right'])            
                
    # Format axes
    ax_dict['bilateral'].ax.set_xlim(-0.75, 1.75)
    ax_dict['bilateral'].bars_to_ticks(labels=False)

    ax_dict['unilateral'].ax.set_xticks([1.5, 4.5])
    ax_dict['unilateral'].ax.set_xticklabels(['Left', 'Right'])
    
    if f.num == 1311:
        ax_dict['bilateral'].xticks(None)

    elif f.num == 1509:
        ax_dict['unilateral'].xlabel('Speaker Hemifield')  
        ax_dict['bilateral'].bars_to_ticks()   
    
    for metric_ax in ax_dict.values():
    
        metric_ax.ygrid(ymin=0, ymax=70, major_interval=20, minor_interval=10, decimals=False, apply_limits=True)
        metric_ax.ylabel('% Correct')   
        metric_ax.ax.set_ylim((0, 75))

        metric_ax.add_chance_line(f.chance_p, z=1)  



# Absolute Error Magnitude
def plot_error_vs_location(sfig: localization_figure, f: ferret_to_plot) -> None:
    ''' Plot the mean and standard error of response errors as a function of sound angle '''

    # Get mean and standard error of mean of abs. errors for each speaker location in each condition
    pt = pd.pivot_table(f.analysis_data, values='Error', columns='SpkrPos', index='Condition', aggfunc=[np.mean, sem])

    # Map conditions onto shared axes (for either unilateral or bilateral cooling)
    group_map = dict(Left='unilateral',Right='unilateral',Control='bilateral',Bilateral='bilateral')
    ax_dict = sfig.struct['error_vs_angle'][f"F{f.num}"]

    # Plot mean and standard deviation For each cooling condition
    for condition, c_data in pt.iterrows():
                                            
        ax = ax_dict[group_map[condition]].ax

        ax.errorbar( 
            x = c_data['mean'].index.to_numpy(), 
            y = c_data['mean'].values, 
            yerr = c_data['sem'].values,
            c=colors[condition])    

    # Format axes
    for metric_ax in ax_dict.values():
    
        metric_ax.format_by_speaker_location(x=True, y=False)
        metric_ax.ylabel('Abs. Error (°)')
        metric_ax.ygrid(ymin=0, ymax=80, major_interval=40, minor_interval=10, decimals=False, apply_limits=False)
        metric_ax.ax.set_ylim((0, 85))

        if f.num == 1509:    
            metric_ax.xlabel('Sound Angle (°)')  
             

def plot_error_ACROSS_location(sfig: localization_figure, f: ferret_to_plot) -> None:
    ''' Plot the mean and standard error of response errors as bar plot '''

    # Get axes for this subject
    ax_dict = sfig.struct['error_over_angle'][f"F{f.num}"]

    # Plot mean and standard deviation for bilateral vs. control data
    df = f.analysis_data[f.analysis_data['Condition'] == 'Bilateral']
    ax_dict['bilateral'].add_bar( None, df['Error'], colors['Bilateral'], 'Cooled', errorbar=True)     

    df = f.analysis_data[f.analysis_data['Condition'] == 'Control']
    ax_dict['bilateral'].add_bar( None, df['Error'], colors['Control'], 'Control', errorbar=True)         

    # Plot mean and standard deviation for unilateral cooling (left vs. right cortex / left vs. right speaker hemifield)
    df = f.analysis_data[(f.analysis_data['Condition'] == 'Left') &  (f.analysis_data['spkr_hemifield'] == 'L')]
    ax_dict['unilateral'].add_bar( 1, df['Error'], colors['Left'], 'SL, CLeft', errorbar=True)             

    df = f.analysis_data[(f.analysis_data['Condition'] == 'Left') &  (f.analysis_data['spkr_hemifield'] == 'R')]
    ax_dict['unilateral'].add_bar( 4, df['Error'], colors['Left'], 'SR, CLeft', errorbar=True)             

    df = f.analysis_data[(f.analysis_data['Condition'] == 'Right') &  (f.analysis_data['spkr_hemifield'] == 'L')]
    ax_dict['unilateral'].add_bar( 2, df['Error'], colors['Right'], 'SL, CRight', errorbar=True)             

    df = f.analysis_data[(f.analysis_data['Condition'] == 'Right') &  (f.analysis_data['spkr_hemifield'] == 'R')]
    ax_dict['unilateral'].add_bar( 5, df['Error'], colors['Right'], 'SR, CRight', errorbar=True)             

    # Format axes
    for metric_ax in ax_dict.values():
            
        metric_ax.ygrid(ymin=0, ymax=80, major_interval=40, minor_interval=10, decimals=False, apply_limits=False)
        metric_ax.ax.set_ylim((0, 85))
        metric_ax.ax.set_yticklabels('')
              
    ax_dict['bilateral'].ax.set_xlim(-0.75, 1.75)        
    ax_dict['bilateral'].bars_to_ticks(labels=False)
    
    ax_dict['unilateral'].ax.set_xticks([1.5, 4.5])
    ax_dict['unilateral'].ax.set_xticklabels(['Left', 'Right'])

    if f.num == 1509:    
        ax_dict['unilateral'].xlabel('Speaker Hemifield')  
        ax_dict['bilateral'].bars_to_ticks()   


def main():

    # Define ferrets
    ferrets = [ferret_to_plot(1311, 'Magnum', 7), ferret_to_plot(1509, 'Robin', 6)]

    # Create figure and organize axes   
    sfig = localization_figure(fig_size=(7, 7), nrows=2, ncols=9)

    # For each ferret
    for f in ferrets:

        # Load data
        f.load_analysis_data('Results/Localization/data/analysis')
        f.load_bootstrap_results('Results/Localization/data/bootstrap')
        
        # Get summary statistics
        # f.get_effect_of_cooling()
        f.report_performance_by_cooling_condition()

        # Plot data
        add_confusion_matrices(sfig, f)    
        plot_pCorrect_by_condition(sfig, f)
        
        plot_error_vs_location(sfig, f)
        plot_error_ACROSS_location(sfig, f)
        
            
    # Format and save figure
    sfig.format_axes_for_saving()       
    sfig.save('Results/Localization/images', 'localization.png')

   
if __name__ == '__main__':
    main()