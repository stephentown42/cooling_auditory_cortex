"""
Create figures for spatial unmasking portion of cooling paper


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
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
from numpy.random import PCG64
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from lib.colors import VOWELS_SPATIAL as colors
from lib.metric_axes import metric_axes
from lib import settings

# Import classes from analysis used in main text
sys.path.insert(0, os.path.dirname(__file__))
from bootstrap_analysis import ferret

# Make code repeatable (using same seed as main text)
my_rng = PCG64(49252466450692985656297363781)

# Define colorscheme for spatial release from masking 
srm_cmap = {'sep_vs_coloc':'#e9a200', 'clean_vs_coloc': '#52c54c'}
alpha_map ={'Bilateral':0.4, 'Control': 0.2}


class ferret_to_plot(ferret):


    def load_bootstrap_results(self, file_path : str) -> None:
        """ Load results from bootstrapping """
        file_path = Path(file_path)
        self.bootstrap_BY_SNR = pd.read_csv( file_path / f"{self.fstr}_BY_SNR.csv")
        self.bootstrap_over_SNR = pd.read_csv( file_path / f"{self.fstr}_OVER_SNR.csv")

        # Replace boolean values with strings compatible with color structure
        self.bootstrap_BY_SNR['treatment'].replace({True:'Bilateral',False:'Control'}, inplace=True)
        self.bootstrap_over_SNR['treatment'].replace({True:'Bilateral',False:'Control'}, inplace=True)


    def get_release_from_masking(self) -> pd.DataFrame:
        """Get performance change (raw and normalized) resulting from separation of speakers"""

        # Filter for cooling and then pivot to make the calculation easy to read        
        df = self.bootstrap_over_SNR.pivot_table(index=['iteration','treatment'], columns=['SpatialCondition'], values='pCorrect')

        # Calculate the absolute difference between separated and colocated speakers, and then express relative to the max difference (i.e. that observed between clean and colocated noise)
        df['sep_vs_coloc'] = df['separated'] - df['colocated']
        df['clean_vs_coloc'] = df['single_speaker'] - df['colocated']
        # df['rel'] = df['abs'] / df['max_diff']

        # Assign to object as dataframe with release from masking on each iteration (for scatter plotting)
        self.release_from_masking = df.reset_index(level=['treatment','iteration'])


@dataclass()
class panel():
    
    fig_size: tuple
    nrows: int
    ncols: int

    def __post_init__(self):
        """ Creates graphic objections on class creation """                
        self.fig, self.axs = plt.subplots(nrows=self.nrows, ncols=self.ncols, figsize=self.fig_size)
        

    def save_figure(self, file_path: str, file_name : str) -> None:
        """ Save plot as PNG file """        
        plt.savefig( Path(file_path) / file_name, dpi=300)
        plt.close()
        

@dataclass()
class panel_for_subject(panel):

    def organize_layout(self, fNum: int) -> None:
        """ Create a grid of subplots with specific sizes in centimeters and detailed formatting for manuscript presentation """
      
        # Set grid color
        for ax in self.axs:
            ax.grid(True, **{'color':'.6', 'alpha':0.5})

        # Make into metric axes 
        self.metric_axes = dict(                       
            correct_by_SNR = metric_axes(self.axs[0], [1.5, 1.5, 2, 1.9], fNum),
            correct_over_SNR = metric_axes(self.axs[1], [3.8, 1.5, 1.5, 1.9], fNum)
        )

        # Set y axis positions
        for obj in self.metric_axes.values():
            obj.ygrid(ymin=0, ymax=100, major_interval=50, minor_interval=10, decimals=False, apply_limits=True)

        # Format axes ticks / labels
        self.metric_axes['correct_over_SNR'].ax.set_yticklabels('')                                 
        self.metric_axes['correct_over_SNR'].xticks({3:'Vowel Only', 2:'Separated', 1:'Colocated'}) 
        self.metric_axes['correct_by_SNR'].ylabel('% Correct')

        
    def plot_bars(self, subject: ferret_to_plot, treatment: str) -> None:
        """
        For each ferret (row), and each cooling condition (column), plot colocated vs 
        separated vs. alone performance by atten (left in tile) and across atten (right in tile)

        Tried to use arg names that mirror those used in seaborn (e.g. relplot)
        
        Parameters:
        ----------
        axs : dict
            Nested dictionary containing axes objects in hierarchy according to 
            plotting structure (can be addressed using col, hue and ferret strings)
        ferrets : list of ferret objects
            
        """
        # Plot performance by SNR for each condition (bar)
        df = subject.release_from_masking.copy()
        df = df[df['treatment'] == treatment]
        
        ax = self.metric_axes['correct_over_SNR'].ax 
        ax.set_xlim(0, 4)
        ax.plot( ax.get_xlim(), [50, 50], c = '.5', lw = 0.5, ls = '--')      # Chance level
       
        # Plot scatter with jitter
        jittered_scatterplot(ax, 1, df['colocated'], colors['colocated'][treatment])
        jittered_scatterplot(ax, 2, df['separated'], colors['separated'][treatment])
        jittered_scatterplot(ax, 3, df['single_speaker'], colors['single_speaker'][treatment])


    def plot_lines(self, subject: ferret_to_plot, treatment: bool) -> None:     # Note that this function could be integrated with another of the same name used in the cooling_SNR_panel class
        """
        For each ferret (row), and each cooling condition (column), plot colocated vs 
        separated vs. alone performance by atten (left in tile) and across atten (right in tile)

        Tried to use arg names that mirror those used in seaborn (e.g. relplot)
        
        Parameters:
        ----------
        axs : dict
            Nested dictionary containing axes objects in hierarchy according to 
            plotting structure (can be addressed using col, hue and ferret strings)
        ferrets : list of ferret objects            
        """

        # Take mean across bootstrap iterations
        df = subject.bootstrap_BY_SNR.copy()
        df = df[df['treatment'] == treatment]                   # Remove trials that aren't in the relevant cooling / control condition
        
        pt = df.pivot_table(index=['iteration'], columns=['SpatialCondition','SNR'], values='pCorrect')
        pt = pt.mean().reset_index(['SpatialCondition','SNR'])
        pt['mean'] = pt[0]

        # Plot performance by SNR for each condition
        ax = self.metric_axes['correct_by_SNR'].ax 
        ax.set_xlim([-24, 10])

        for condition, cData in pt.groupby(by='SpatialCondition'):                          
            
            ax.plot(                                                                # Plot line on top
                cData['SNR'], 
                cData['mean'], 
                c=colors[condition][treatment],
                ls='-',lw=0.6, marker='.',markersize=1)

        ax.plot(                                                            # Plot chance line
            [-24, 10],
            [50, 50],
            c = '.5',
            lw = 0.5,
            ls = '--',
            zorder=2)

        ax = self.metric_axes['correct_by_SNR'].title(f"F{subject.num}", 'k', 8)
        ax = self.metric_axes['correct_by_SNR'].xlabel("SNR (dB)")
        ax = self.metric_axes['correct_by_SNR'].ax.set_xticks([-20, -10, 0, 10])

        
@dataclass()
class cooling_SNR_panel(panel):
        
    def organize_layout(self, fNum: int) -> None:
        """ Create a grid of subplots with specific sizes in centimeters and detailed formatting for manuscript presentation """
      
        # Make into metric axes 
        self.metric_axes = dict(                       
            colocated = metric_axes(self.axs[0], [1.5, 1.5, 2, 1.9], fNum),
            separated = metric_axes(self.axs[1], [4.5, 1.5, 2, 1.9], fNum),
            single_speaker = metric_axes(self.axs[2], [7.5, 1.5, 2, 1.9], fNum),
        )

        # Set constant object properties across axes
        for obj in self.metric_axes.values():
            obj.xgrid(xmin=-20, xmax=10, major_interval=10, minor_interval=10, decimals=False, apply_limits=True)
            obj.ygrid(ymin=0, ymax=100, major_interval=50, minor_interval=10, decimals=False, apply_limits=True)
            obj.xlabel('SNR (dB)')
            obj.ax.grid(True, **{'color':'.6', 'alpha':0.5})
        
        self.metric_axes['single_speaker'].xlabel('Level (dB SPL)')
        self.metric_axes['single_speaker'].xgrid(xmin=50, xmax=80, major_interval=10, minor_interval=10, decimals=False, apply_limits=False)
        self.metric_axes['single_speaker'].ax.set_xlim((45, 75))

        self.metric_axes['colocated'].ylabel('% Correct')
        self.metric_axes['colocated'].title(f"F{fNum}", 'k', 8)


    def populate(self, subject: ferret_to_plot) -> None:
        """ Plot performance by SNR for each stimulus condition on a separate axes within panel """

        for stim_condition, m_ax in self.metric_axes.items():
            
            self.plot_lines(subject, stim_condition, m_ax)
            m_ax.add_chance_line(chance=50, c='.5')


    def plot_lines(self, subject: ferret_to_plot, stim_condition: str, axObj: metric_axes) -> None:
        """
        For each ferret (row), and each cooling condition (column), plot colocated vs 
        separated vs. alone performance by atten (left in tile) and across atten (right in tile)

        Tried to use arg names that mirror those used in seaborn (e.g. relplot)
        
        """

        # Get a copy of the data and filter for stimulus condition (e.g. clean)
        df = subject.bootstrap_BY_SNR.copy()
        df = df[df['SpatialCondition'] == stim_condition]               
        
        if stim_condition == 'single_speaker':
            df['vowel_level'] = df['SNR'] + (settings.noise_level - 3)        # Drop default_level by 3 due to one rather than two speakers
            x_var = 'vowel_level'
        else:
            x_var = 'SNR'

        # Pivot and take mean performance across iterations
        pt = df.pivot_table(index=['iteration'], columns=['treatment',x_var], values='pCorrect')
        pt = pt.mean().reset_index(['treatment',x_var])
        pt['mean'] = pt[0]

        # Plot performance by SNR for each stimulus condition
        for treatment, cData in pt.groupby(by='treatment'):                          
            
            axObj.ax.plot(                                                                # Plot line on top
                cData[x_var], 
                cData['mean'], 
                c=colors[stim_condition][treatment],
                ls='-',lw=0.6, marker='.',markersize=1)




class cooling_ALL_panel(panel):

    def organize_layout(self, fNum: int) -> None:
        """ Create a grid of subplots with specific sizes in centimeters and detailed formatting for manuscript presentation """
      
        # Make into metric axes 
        self.metric_axes = dict(                       
            colocated = metric_axes(self.axs[0], [1.5, 1.5, 1, 1.9], fNum),
            separated = metric_axes(self.axs[1], [2.75, 1.5, 1, 1.9], fNum),
            single_speaker = metric_axes(self.axs[2], [4.0, 1.5, 1, 1.9], fNum),
        )

        # Set constant object properties across axes
        for stim_condition, obj in self.metric_axes.items():            

            obj.xticks({1:'Control',2:'Cooled'})
            obj.yticks({40:'',50:'50',60:'',70:'70',80:'',90:'90'})

            obj.ax.grid(True, **{'color':'.6', 'alpha':0.5})
            obj.ax.set_xlim([0, 3])
            obj.ax.set_ylim([40, 90])

            obj.add_chance_line(chance=50, c='.5')

            if stim_condition != 'colocated':
                obj.ax.set_yticklabels(['']*len(obj.ax.get_yticks()))
        
        self.metric_axes['colocated'].ylabel('% Correct')
        self.metric_axes['colocated'].title(f"F{fNum}", 'k', 8)


    def populate(self, subject: ferret_to_plot):

        # Plot performance by SNR for each condition (bar)
        df = subject.release_from_masking.copy()

        xmap = {'Control':1, 'Bilateral':2}

        for stim_condition, m_ax in self.metric_axes.items():       # For each stimulus condition (colocated, separated, clean)
            
            for treatment, treatment_data in df.groupby(by='treatment'):    # For each treatment (cooled/control)
                
                jittered_scatterplot(m_ax.ax, xmap[treatment], treatment_data[stim_condition], colors[stim_condition][treatment], alpha=0.1, jitter_sd=0.1)
            

class cooling_release_from_masking(panel):

    def organize_layout(self, fNum: int) -> None:
            
        self.metric_axes = metric_axes(self.axs, [1.5, 1.5, 1.5, 1.9], 0)
            
        self.metric_axes.ax.set_xlim([0.35, 2.65])
        self.metric_axes.ax.set_ylim([-15, 35])
        self.metric_axes.ax.set_yticks([ -10, 0, 10, 20, 30])
        
        self.metric_axes.xticks({1:'Control', 2:'Cooled'})     
        self.metric_axes.ylabel('$\Delta$ Correct (%)')     
        self.metric_axes.title(f"F{fNum}", 'k', 8)
        self.metric_axes.add_chance_line(0, ls='-', lw=0.7)


    def populate(self, subject: ferret) -> None:

        # Target axes 
        ax = self.metric_axes.ax
        xmap = {'Bilateral': 2, 'Control':1}

        # Plot Bar for each cooling condition (mostly control data) and measurement type
        for treatment, treatment_data in subject.release_from_masking.groupby(['treatment']):
            
            # Plot change in percent correct between clean and colocated
            # jittered_scatterplot(ax, xmap[treatment]-0.175, treatment_data['clean_vs_coloc'], color=srm_cmap['clean_vs_coloc'], alpha=alpha_map[treatment], jitter_sd=0.05, mode='bar', offset_mean=0.35) 

            # Plot change in percent correct between separated and colocated
            jittered_scatterplot(ax, xmap[treatment]-0.175, treatment_data['sep_vs_coloc'], color=srm_cmap['sep_vs_coloc'], alpha=alpha_map[treatment], jitter_sd=0.05, mode='bar', offset_mean=0.35)             




@dataclass()
class release_from_masking_full(panel):
    
    def organize_layout(self) -> None:
            
        self.metric_axes = metric_axes(self.axs, [1.5, 1.5, 6.5, 2.5], 0)

        self.metric_axes.ax.set_ylim([-15, 35])
        self.metric_axes.ax.set_yticks([ -10, 0, 10, 20, 30])
        self.metric_axes.ylabel('$\Delta$ Correct (%)')     

        # Initialize variables (not done in post-init to preserve superclass post-init)
        self.idx = 0
        self.x_head = -0.175
        self.xticks = []
        self.xticklabels = []


    def plot_ferret(self, subject: ferret) -> None:
        """ Add bars showing release from masking for one ferret """

        # Target axes 
        ax = self.metric_axes['abs'].ax

        # Plot Bar for each cooling condition (mostly control data) and measurement type
        for treatment, treatment_data in subject.release_from_masking.groupby(['treatment']):

            # Plot change in percent correct between clean and colocated
            jittered_scatterplot(ax, self.x_head, treatment_data['clean_vs_coloc'], color=cmap_removal[treatment], alpha=alpha_map[treatment], jitter_sd=0.05, mode='bar', offset_mean=0.35)             
            
            # Plot change in percent correct between separated and colocated
            jittered_scatterplot(ax, self.x_head, treatment_data['sep_vs_coloc'], color=cmap_separation[treatment], alpha=alpha_map[treatment], jitter_sd=0.05, mode='bar', offset_mean=0.35)             
                                
            # Keep record of x ticks and move x-head
            self.xticks.append(self.x_head)
            self.xticklabels.append(f"F{subject.num}")
            self.x_head += 1    

            # Print to console for reporting
            print(f"Treatment = {treatment}, change in performance: separation = {treatment_data['sep_vs_coloc'].mean()} , removal = {treatment_data['clean_vs_coloc'].mean()}")      

    
    def format_x_axis(self) -> None:
        """ Use names of ferrets collected over addition to label x axis ticks"""
       
        for obj in self.metric_axes.values():
            obj.ax.set_xticks(self.xticks)
            obj.ax.set_xticklabels(self.xticklabels, rotation=45)
            obj.add_chance_line(0, ls='-', lw=0.7)


def jittered_scatterplot(ax, x: int, y:Union[np.array, pd.Series], color:str, alpha:float=0.2, jitter_sd=0.15, mode:str='marker', offset_mean:float=0) -> None:
    """ Plots values in input vector (y) with jitter about a central position (x) """ 

    # Convert pandas series to numpy array if necessary
    if isinstance(y, pd.Series):
        y = y.to_numpy()

    # Plot all values
    jitter = np.random.default_rng(seed=my_rng).normal(0, jitter_sd, len(y))                        

    ax.scatter(x + jitter, y, c=color, s=1, alpha=alpha, edgecolors='none') 
 
    # Plot mean and standard deviation
    x = x + offset_mean

    if mode == 'bar':
        ax.bar(x, np.mean(y), width=0.3, color=color, yerr=np.std(y), ecolor=color, error_kw={'linewidth':0.75})
    
    elif mode == 'marker':
        ax.plot(x, np.mean(y), '.k', markersize=1)
        ax.plot([x, x], ([-np.std(y), np.std(y)] + np.mean(y)), linewidth=0.75, color='k')
    


def main():  
    
    # Define subjects, including those that were not tested with cooling 
    # (NB. For replicability between main and supplementary data, it's critical that F1311 and F1509 are defined in the same order [1st, 2nd] as they are in the main text)
    ferrets = [
        ferret_to_plot(1311,'Magnum', 0),
        ferret_to_plot(1509,'Robin',0),
        ferret_to_plot(1201,'Florence',0),
        ferret_to_plot(1203,'Virginia',0),
        ferret_to_plot(1216,'Mini',0),
        ferret_to_plot(1217,'Clio',0)
        ]

    # # Load behavioral data
    [x.load_bootstrap_results(Path('Results/Vowels_Unmasking/data/bootstrap')) for x in ferrets]

    # # Calculate release from masking
    [x.get_release_from_masking() for x in ferrets]

    # # Plot release from masking (main text)
    # srm = release_from_masking_full(fig_size=(6,2), nrows=1, ncols=1)
    # srm.organize_layout()

    # [srm.plot_ferret(f) for f in ferrets]

    # srm.format_x_axis()
    # srm.save_figure('Results/Vowels_Unmasking/images/', 'release_from_masking.png')
        

    # Plot performance separately for each ferret in control conditions
    for f in ferrets:

        p = panel_for_subject(fig_size=(3, 2), nrows=1, ncols=2)       # Each ferret has it's own axes
        
        p.organize_layout(fNum=f.num)        
        p.plot_lines(f, treatment='Control')
        p.plot_bars(f, treatment='Control')
        p.save_figure('Results/Vowels_Unmasking/images', f"F{f.num}_control.png")


    # Plot performance separately for first two ferrets in cooling (remaining subjects weren't tested with cooling)
    # for f in ferrets[0:2]:

    #     p = cooling_SNR_panel(fig_size=(4, 2), nrows=1, ncols=3)      
    #     p.organize_layout(fNum=f.num)
    #     p.populate(f)
    #     p.save_figure('Results/Vowels_Unmasking/images', f"F{f.num}_effectOfCooling_SNR.png")

        # q = cooling_ALL_panel(fig_size=(3, 2), nrows=1, ncols=3)      
        # q.organize_layout(fNum=f.num)
        # q.populate(f)
        # q.save_figure('Results/Vowels_Unmasking/images', f"F{f.num}_effectOfCooling.png")

        # r = cooling_release_from_masking(fig_size=(2,2), nrows=1, ncols=1)
        # r.organize_layout(fNum=f.num)
        # r.populate(f)
        # r.save_figure('Results/Vowels_Unmasking/images', f"F{f.num}_effectOfCooling_SRM.png")




if __name__ == '__main__':
    main()