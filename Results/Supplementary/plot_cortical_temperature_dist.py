"""

Plot histograms of the cortical temperatures measured during testing 
in each behavior during cooling

The intake data for each behavior should come from the analysis level
of the dataset (i.e. the one taken into R for statistics, and in which
the major preprocessing has already been done)


Version History:
    - 2021-09-30: Created by Stephen Town

"""

from dataclasses import dataclass
import os, sys

import matplotlib.figure as mpl_fig
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from lib import fonts, units
from Results import plot_tools as cplot
from Results.Supplementary import Task, Ferret



@dataclass
class plot():
    """ Axes showing data for one ferret and one task"""

    fig : mpl_fig.Figure
    horizontal_offset : float       # cm from left side of figure
    vertical_offset : float         # cm from bottom of figure
    width : float                   # cm 
    height : float                  # cm
    subject : Ferret
    task : Task

    def __post_init__(self) -> None:
        """ Create axes object at position specified in cm """

        pos_cm = [self.horizontal_offset, self.vertical_offset, self.width, self.height]
        pos_norm = units.cm2norm( pos_cm, tuple(self.fig.get_size_inches()))

        self.ax = self.fig.add_axes(rect=pos_norm)

        # Add marginal axes based on central axes
        marginal_size = pos_norm[3] * 0.4
        marginal_offset = pos_norm[3] / 10

        top_marginal_pos = [pos_norm[0], pos_norm[1]+pos_norm[3]+marginal_offset, pos_norm[2], marginal_size]        
        right_marginal_pos = [pos_norm[0]+pos_norm[2]+marginal_offset, pos_norm[1], marginal_size, pos_norm[3]]        

        self.marginal_top = self.fig.add_axes(rect=top_marginal_pos)            # For left temperatures
        self.marginal_right = self.fig.add_axes(rect=right_marginal_pos)          # For right temperatures


    def load_data(self) -> None:
        """Import behavioral data from csv file and do some minor formatting"""

        file_path = Path(self.task.value) / (self.subject.fstr + '.csv')

        df = pd.read_csv(file_path)

        if any(df.columns == 'treatment'):
            df['Condition'] = df['treatment'].replace({False:'Control', True:'Bilateral'})
        

        self.data = df[['LeftTemperature','RightTemperature','Condition']]
                

    def add_marginals(self) -> None:
        "Draw histogram of cortical temperature values for each loop"

        bin_edges = np.arange(start=0.5, stop=39.5, step=1)

        self.marginal_top.hist( self.data['LeftTemperature'].to_numpy(), bin_edges, color='#1199CC')
        self.marginal_right.hist( self.data['RightTemperature'].to_numpy(), bin_edges, color='#EE7711', orientation='horizontal')

        self.marginal_top.set_ylabel('Trials (n)', fontdict=fonts.axis_heading)
        self.marginal_right.set_xlabel('Trials (n)', fontdict=fonts.axis_heading)

        self.marginal_top.set_ylim([0, 300])
        self.marginal_right.set_xlim([0, 300])

        self.marginal_top.set_xlim([0, 40])
        self.marginal_right.set_ylim([0, 40])

        self.marginal_top.set_yticks([0, 150, 300])
        self.marginal_right.set_xticks([0, 150, 300])
        

    def draw_scatterplot(self) -> None:
        "Draw paired histogram showing temperatures at left and right loop on each trial"

        marker_format = dict(
            Bilateral = {'color':'#880088', 'marker':'o'},
            Control   = {'color':'#222222', 'marker':'d'},
            Left      = {'color':'#1199CC', 'marker':'<'},
            Right     = {'color':'#EE7711', 'marker':'>'},
        )

        for condition, c_style in marker_format.items():

            c_data = self.data[self.data['Condition'] == condition]

            self.ax.scatter(
                x = c_data['LeftTemperature'].to_numpy(),
                y = c_data['RightTemperature'].to_numpy(),
                color = c_style['color'],
                marker = c_style['marker'],
                s = 1,
                alpha = 0.05
            )

        self.ax.set_xlim([0, 40])
        self.ax.set_ylim([0, 40])

        self.ax.set_xlabel('Left (°C)', fontdict=fonts.axis_heading)
        self.ax.set_ylabel('Right (°C)', fontdict=fonts.axis_heading)
        

    def make_pretty(self) -> None:
        """ Formatting to follow figure conventions for publication """

        for ax in [self.ax, self.marginal_top, self.marginal_right]:

            cplot.set_tick_font( ax.get_xticklabels(), fonts.axis_heading)
            cplot.set_tick_font( ax.get_yticklabels(), fonts.axis_heading)

            ax.tick_params(width=0.5, length=2)
            
            cplot.remove_spines(ax)
            for axis in ['top','bottom','left','right']:
                ax.spines[axis].set_linewidth(0.5)
        
        self.ax.set_axisbelow(True)
        self.ax.grid(True, **{'lw':0.5, 'ls':':','color':'.4'})

        # Set tick marks (not sure where else to do this)
        temperature_marks = [0, 10, 20, 30, 40]
        temperature_labels = ['0', '', '20', '', '40']    

        self.ax.set_xticks(temperature_marks)
        self.ax.set_yticks(temperature_marks)

        self.ax.set_xticklabels(temperature_labels)
        self.ax.set_yticklabels(temperature_labels)

        self.marginal_top.set_xticks(temperature_marks)
        self.marginal_right.set_yticks(temperature_marks)
    
        self.marginal_top.set_xticklabels('')
        self.marginal_right.set_yticklabels('')


    def add_title(self) -> None:
        """ Adds title to plot above top marginal"""

        title_str = f"{self.subject.fstr} : {self.task.name}"

        self.marginal_top.set_title(title_str, fontdict=fonts.axis_heading)
        


@dataclass()
class panel():
    """ Grouping class for multiple plots from the same ferret """

    fig : mpl_fig.Figure
    ferret : Ferret
    vertical_offset : float         # cm from bottom of figure
    height : float                  # cm
    columns : dict
    task_labels : bool
    
    def __post_init__(self) -> None:
        """ Create axes for each task"""

        self.axs = dict(
            vowels_in_noise = plot(
                self.fig, 
                self.columns['vowels_in_noise']['offset'],
                self.vertical_offset,
                self.columns['vowels_in_noise']['width'],
                self.height,
                self.ferret,
                Task.VOWELS_IN_NOISE),
            localization = plot(
                self.fig, 
                self.columns['localization']['offset'],
                self.vertical_offset,
                self.columns['localization']['width'],
                self.height,
                self.ferret,
                Task.LOCALIZATION),            
            vowels_spatial = plot(
                self.fig, 
                self.columns['vowels_spatial']['offset'],
                self.vertical_offset,
                self.columns['vowels_spatial']['width'],
                self.height,
                self.ferret,
                Task.VOWELS_SPATIAL),
        )

    def add_titles(self) -> None:
        """ Add title showing the particular task"""
        pass



def main():

    # Filter imported ferrets for those that had cooling
    cooled_ferrets = [Ferret(1311,'Magnum'), Ferret(1509,'Robin')]

    # Create figure
    fig = plt.figure(figsize=(7, 4.75))

    # Create axes
    columns = dict(
        vowels_in_noise = dict( width=2.5, offset = 1.2),
        localization    = dict( width=2.5, offset = 7.2),
        vowels_spatial  = dict( width=2.5, offset = 13.2)
    )

    panel_1 = panel( fig, cooled_ferrets[0], 7, 2.5, columns, False)
    panel_2 = panel( fig, cooled_ferrets[1], 1, 2.5, columns, True)

    # Load source data for each plot
    [ax.load_data() for ax in panel_1.axs.values()]
    [ax.load_data() for ax in panel_2.axs.values()]

    # Draw scatterplots of temperature distributions
    [ax.draw_scatterplot() for ax in panel_1.axs.values()]
    [ax.draw_scatterplot() for ax in panel_2.axs.values()]

    # Draw marignal distributions of temperature distributions
    [ax.add_marginals() for ax in panel_1.axs.values()]
    [ax.add_marginals() for ax in panel_2.axs.values()]
    
    # Format plots within each panel for publication
    [ax.make_pretty() for ax in panel_1.axs.values()]
    [ax.make_pretty() for ax in panel_2.axs.values()]

    # Note the task for which data is shown
    [ax.add_title() for ax in panel_1.axs.values()]
    [ax.add_title() for ax in panel_2.axs.values()]

    # Save to file
    plt.savefig( 'Results/Supplementary/images/Temperature_Distributions.png', dpi=300)
    # plt.show()


if __name__ == '__main__':
    main()