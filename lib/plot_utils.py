"""
Plotting tools for publication graphics using matplotlib 
"""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


from lib import units, fonts


def match_axes_limits(axs:list, dim:str, min_to_zero:bool=False) -> None:
    """
    Force multiple axes to share the same limits
    
    Parameters:
    ----------
    axs : list
        List of matplotlib axes
    dim : str
        Name of axes to match ('x' or 'y')
    min_to_zero: bool
        Force axes to minimum of zero

    """

    # Get min and max for all axes
    min_val, max_val = np.inf, -np.inf
    
    for ax in axs:

        if dim =='x':
            lims = ax.get_xlim()
        elif dim == 'y':
            lims = ax.get_ylim()

        min_val = min([min_val, lims[0]])
        max_val = max([max_val, lims[1]])

    # Force axes to zero (optional)
    if min_to_zero:
        min_val = 0

    # Set all limits to common values
    for ax in axs:
        if dim == 'x':
            ax.set_xlim((min_val, max_val))
        if dim == 'y':
            ax.set_ylim((min_val, max_val))



def ceil(x:np.array) -> float:
    """ Round up to nearest 10 """

    max_x = np.round(x.max(), -1)
    if max_x < x.max():
        max_x += 10

    return max_x


def floor(x:np.array) -> float:
    """ Round down to nearest 10 """

    min_x = np.round(x.min(), -1)
    if min_x > x.min():
        min_x -= 10

    return min_x



@dataclass()
class panel():
    """ A figure containing multiple axes associated with one level of a factor (e.g. a specific ferret or stimulus condition) """
    
    fig_size: tuple
    nrows: int
    ncols: int
    sharex: bool=False
    sharey: bool=False

    def __post_init__(self):
        """ Creates graphic objections on class creation """                
        self.fig, self.axs = plt.subplots(
            nrows=self.nrows, 
            ncols=self.ncols, 
            sharex=self.sharex,
            sharey=self.sharey,
            figsize=self.fig_size
            )
        

    def save_figure(self, file_path: str, file_name : str) -> None:
        """ Save plot as PNG file """        
        plt.savefig( Path(file_path) / file_name, dpi=300)
        plt.close()
        


class metric_axes():
    """
    Default behavior is to drop spines on right and top
    """

    def __init__(self, ax, position, ferret, dropSpines=True):

        self.ax = ax                # matplotlib axes handle
        self.position = position    # in cm     

        pos_norm = units.cm2norm(position, tuple(ax.figure.get_size_inches()))

        self.ax.set_position(pos=pos_norm)
        self.ax.tick_params(length=2)

        self.set_tick_font( ax.get_xticklabels(), fonts.axis_heading)
        self.set_tick_font( ax.get_yticklabels(), fonts.axis_heading)
        
        if dropSpines:
            self.remove_spines()
            ax.set_axisbelow(True)
            ax.grid(True, **{'lw':0.5, 'ls':':','color':'.4'})
      

    def add_chance_line(self, chance=20, c='k', ls='--', lw=1, z=0):
        """ Adds horizontal line for chance performance"""

        xlims = self.ax.get_xlim()
        self.ax.plot(xlims, [chance, chance], c=c, ls=ls, lw=lw, zorder=z)

        return xlims


    def remove_spines(self, spines: str=['top','right']) -> None:
        """
        Remove spines (box lines surrounding axes) from axis
        
        Parameters:
        ----------
        spines : str or  list of str, optional
            List of spines to remove (from 'top','left','right','bottom')        
        """

        for spine in spines:
            self.ax.spines[spine].set_visible(False)


    @ staticmethod
    def set_tick_font(tick_obj, font_dict: dict) -> None:
        """ Set font size and font name for ticks """

        for tick in tick_obj:
            tick.set_fontsize(font_dict['fontsize'])
            tick.set_fontname(font_dict['fontname'])


    def xgrid(self, xmin:float=0, xmax:float=100, major_interval:float=25, minor_interval:float=12.5, decimals=True, apply_limits=False) -> None:
        """Put x ticks at major & minor intervals (to give grid), but only label values at major intervals """

        tick_vals = np.arange(xmin, xmax+1, minor_interval)

        if decimals:
            tick_labels = [str(x) if x % major_interval == 0 else '' for x in tick_vals]
        else:
            tick_labels = [str(int(x)) if x % major_interval == 0 else '' for x in tick_vals]

        self.ax.set_xticks(tick_vals)
        self.ax.set_xticklabels(tick_labels)

        # Option to apply limits while here
        if apply_limits:
            self.ax.set_xlim((xmin, xmax))


    def xticks(self, info: dict) -> None:
        """ Sets tick values and labels using dictionary """

        if info is None:
            # self.ax.set_xticks([])
            self.ax.set_xticklabels('')
        else:
            self.ax.set_xticks([x for x in info.keys()])
            self.ax.set_xticklabels([x for x in info.values()], rotation=45)


    def ygrid(self, ymin: float=0, ymax:float=100, major_interval:float=25, minor_interval:float=12.5, decimals=True, apply_limits=False) -> None:
        """Put y ticks at major & minor intervals (to give grid), but only label values at major intervals """

        # Place ticks at every minor interval
        tick_vals = np.arange(ymin, ymax+1, minor_interval)
        self.ax.set_yticks(tick_vals)

        # Place labels at every major interval
        if decimals:
            tick_labels = [str(y) if y % major_interval == 0 else '' for y in tick_vals]
        else:
            tick_labels = [str(int(y)) if y % major_interval == 0 else '' for y in tick_vals]

        self.ax.set_yticklabels(tick_labels)

        # Option to apply limits while here
        if apply_limits:
            self.ax.set_ylim((ymin, ymax))


    def yticks(self, info: dict, rotation=0) -> None:
        """ Sets tick values and labels using dictionary """

        if info is None:
            # self.ax.set_xticks([])
            self.ax.set_yticklabels('')
        else:
            self.ax.set_yticks([x for x in info.keys()])
            self.ax.set_yticklabels([x for x in info.values()], rotation=rotation)
            

    def xlabel(self, label):
        self.ax.set_xlabel(label, fonts.axis_heading)

    def ylabel(self, label):
        self.ax.set_ylabel(label, fonts.axis_heading)

    def title(self, label, color, fontsize=10):

        title_format = {
            'fontname':'Arial',
            'fontsize': fontsize,
            'fontweight': 'bold',
            'color': color
            }

        self.ax.set_title(label, title_format)
   
