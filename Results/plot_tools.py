"""
Plotting tools for publication graphics using matplotlib / seaborn
ecosystem and metric units (centimeters)

TO DO
    - ADD plotting of cortical temperature distributions for control and cooled

Created:
    2021-07-21: Stephen Town

"""

from collections.abc import Iterable
import colorsys
import os, sys

import pandas as pd
import numpy as np
import seaborn as sns

sys.path.insert(0, os.path.abspath( os.path.join( os.path.dirname(__file__), '../')))

from lib import fonts, units



class metric_axes():            # THIS CAN BE DELETED???
    """
    Because I can't deal with imperial units - it's not 1856 anymore!

    Default behavior is to drop spines on right and top
    """

    def __init__(self, ax, position, ferret, dropSpines=True):

        self.ax = ax                # matplotlib axes handle
        self.position = position    # in cm     

        pos_norm = units.cm2norm(position, tuple(ax.figure.get_size_inches()))

        self.ax.set_position(pos=pos_norm)
        self.ax.tick_params(length=2)

        set_tick_font( ax.get_xticklabels(), fonts.axis_heading)
        set_tick_font( ax.get_yticklabels(), fonts.axis_heading)
        
        if dropSpines:
            remove_spines(ax)
            ax.set_axisbelow(True)
            ax.grid(True, **{'lw':0.5, 'ls':':','color':'.4'})


    def format_by_speaker_location(self, x=True, y=True, withSymbol=False):

        theta = [-90, -60, -30, 0, 30, 60, 90]
        if withSymbol:
            tstr = [str(x) + '°' for x in theta]
        else:
            tstr = [str(x) for x in theta]


        if x:
            self.ax.set_xlim([-105, 105])
            self.ax.set_xticks( theta)
            self.ax.set_xticklabels( tstr, rotation=45)            
        
        if y:
            self.ax.set_ylim([-105, 105])
            self.ax.set_yticks( theta)

            if withSymbol:
                self.ax.set_yticklabels(tstr)
        

    def add_bar(self, x, df, color, condition, errorbar=False):

        if not hasattr(self, 'bar_count'):
            self.bar_count = 0
            self.tick_list = []
            self.tick_label_list = []

        if x is None:
            x = self.bar_count

        if errorbar:
            self.ax.bar(
                x = x, 
                height = df.mean(), 
                yerr = df.sem(),
                color=color,
                label=condition
                )
        else:
            self.ax.bar(
                x = x, 
                height=df.mean(), 
                color=color, 
                label=condition
                )

        self.tick_list.append(x)
        self.tick_label_list.append(condition)
        self.bar_count += 1
        

    def add_chance_line(self, chance=20):
        """ Adds horizontal line for chance performance"""

        xlims = self.ax.get_xlim()
        self.ax.plot(xlims, [chance, chance], c='k', ls='--', lw=1)


    def bars_to_ticks(self, labels=True):
        
        self.ax.set_xticks(self.tick_list)

        if labels:
            self.ax.set_xticklabels(self.tick_label_list, rotation=45)
        else:
            self.ax.set_xticklabels('')


    def xticks(self, info: dict) -> None:
        """ Sets tick values and labels using dictionary """

        if info is None:
            # self.ax.set_xticks([])
            self.ax.set_xticklabels('')
        else:
            self.ax.set_xticks([x for x in info.keys()])
            self.ax.set_xticklabels([x for x in info.values()], rotation=45)
            

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
   


def add_p_label(p, x, y, ax, **kwargs):
    """
    Adds commonly used label for plots using 'p = 0.0??' format
    
    Parameters:
    ----------
    p : float
        Probability value (between zero and one)
    x, y : float
        text position in axes (using axes scales)
    ax : matplotlib axes 
        parent axes for plotting
    
    Returns:
    --------
    t : matplotlib text
        Handle for text object
    """

    if p < 0.001:
        p_str = '$\it{p}$ < 0.001'
    else:
        p_str = "$\it{p}$ = %.3f" % p

    
    return ax.text(x, y, p_str, ha='right', **kwargs)


def bars_across_sessions(df, ax, splitVar, colors=None):
    """
    Add bar plot showing performance (proportion correct)
    for each mask, split by experimental intervation (cooling
    or light delivery)
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe containing trial counts 
    ax : matplotlib axes
        Axes for plotting
    
    Returns:
    --------
    None
    """

    if df.shape[0] == 0:
        return

    if any(df.columns == 'Mask'):                   # Color by mask if available
        mask = df['Mask'].unique()    # Should be same for all rows

        main_color = colors[mask[0]]
        test_color = change_color_lightness(main_color, 0.3)
        # test_color = change_color_saturation(test_color, -0.2)
    else:
        main_color = colors['Control']
        test_color = colors['Test']

    ax.bar(1, df[df[splitVar] == False]['pCorrect'].to_numpy(), color=main_color)
    ax.bar(2, df[df[splitVar] == True]['pCorrect'].to_numpy(), color=test_color)

    lim = ax.get_xlim()             # Plot chance
    ax.plot(lim, [50, 50], c='#888888', linestyle='--')
           

def match_axes_limits(axs, dim, min_to_zero=False):
    """
    Description
    
    Parameters:
    ----------
    axs : list
        List of matplotlib axes
    dim : str
        Name of axes to match ('x' or 'y')
    
    Returns:
    --------
    None
    """

    min_val, max_val = np.inf, -np.inf
    
    for ax in axs:

        if dim =='x':
            lims = ax.get_xlim()
        elif dim == 'y':
            lims = ax.get_ylim()

        min_val = min([min_val, lims[0]])
        max_val = max([max_val, lims[1]])

    if min_to_zero:
        min_val = 0


    for ax in axs:
        if dim == 'x':
            ax.set_xlim((min_val, max_val))
        if dim == 'y':
            ax.set_ylim((min_val, max_val))

    return None


def permuation_violins( perm_tests, ax, colors):

    # If only one mask (mimi), create padding data for violin
    if len(perm_tests['mask'].unique()) == 1:
        perm_tests = pd.concat([pd.DataFrame([{'shuffled':0, 'observed':0, 'mask':'Clean'}]), perm_tests])

    sns.violinplot(
        data=perm_tests,
        x='shuffled',
        y='mask',
        bw=0.2,
        ax=ax,               
        saturation=0.25,
        palette={'Clean':'#a0a0a0', 'Restricted':'#FF4564'},
        orient='h',
        dodge=True,
        inner=None,
        split=True)

    for cObj in ax.collections:
        cObj.set_linewidth(lw=0.1)

    # Plot observed performance as large dots
    observed = perm_tests.groupby('mask')['observed'].unique()
    observed = observed.reset_index(level='mask')

    for y, row in observed.iterrows():
        ax.plot(row['observed'][0], y, 'o', c=colors[row['mask']], markersize=4)
        
    ax.set_xlim((-25, 25))
    ax.set_xticks([-20, 0, 20])
    ax.set_xticklabels(['-20', '0', '20'], rotation=45)

    ax.set_ylabel('')
    remove_spines(ax, ['left','right','top'])
    ax.set_yticks([])
    # ax.set_yticklabels(observed['mask'].to_list())

    return None




def remove_spines(axs, spines=['top','right']):
    """
    Remove spines (box lines surrounding axes) from axis
    
    Parameters:
    ----------
    axs : matplotlib axes, or list of axes
        Axes to remove spines from
    spines : str or  list of str, optional
        List of spines to remove (from 'top','left','right','bottom')
    
    Returns:
    --------
    None
    """
    
    if not isinstance(axs, Iterable):
        axs = [axs]

    for ax in axs:

        if isinstance(spines, str):
            ax.spines[spines].set_visible(False)
        else:
            for spine in spines:
                ax.spines[spine].set_visible(False)


def scatter_by_session(df, ax, test_column='opto', groupby=['Block','Mask']) -> None:
    """
    Plot scatter plot showing the performance on every day with and
    without cooling, with separate colors for each mask
    
    Parameters:
    ----------
    results: pandas data frame
        Data frame with performance (number of trials in total, and correct)
        as rows for each mask in each session, with or without cooling.
    ax : matplotlib axes
        Axes to plot items on
    testColumn : str
        Name of column containing experimental manipulation (e.g. 'opto', 'isCooled')
    groupby : list of str
        Name of columns containing each data point (e.g. 'day', 'Block', 'Mask')    
    """
   
    ax.plot([0, 100], [0, 100], c='#888888', ls='--')

    for (session, mask), data in df.groupby(by=groupby):

        test = data[data[test_column] == 1]
        control = data[data[test_column] == 0]        

        ax.scatter( control['pCorrect'], test['pCorrect'], c=colors[mask], s=4)

    ax.set_xlim((30, 100))
    ax.set_ylim((30, 100))

    ax.set_xlabel('Control (% Correct)', **fonts.axis_heading)
    ax.set_ylabel('Test (% Correct)', **fonts.axis_heading)

    ax.set_aspect(1)


def set_tick_font(tick_obj, font_dict: dict) -> None:
    """ Set font size and font name for ticks """

    for tick in tick_obj:
        tick.set_fontsize(font_dict['fontsize'])
        tick.set_fontname(font_dict['fontname'])


def stacked_jitter(x, y, ax, c='k', invert=False, bin_width=1, height=1, normalize=False, adjust=False):
    """Gets stacked jitter values for vector to be plotted in scatter plot

    Stacked jitter means that values of x (e.g. 5, 7 & 9) within a common range (e.g. 1-10)
    will have ascending jitter values (e.g. 1, 2, 3). This avoids random overlap between 
    data points and results in an accurate and repeatable illustration of the frequency 
    distribution of x.

    Parameters
    ----------
    x : numpy array 
        Vector of values that remain contant, but will be reordered
    bin_width : float
        The window within which to structure jitter (some proportion of the range of x)
    height : float, optional
        Value to scale jitter
    normalize : boolean, optional
        Height operates on jitter values between 0 and 1
    adjust : boolean, optional
        Height operates on jitter values that show probability (rather than frequency distribution)

    Returns
    -------
    reordered_x: numpy array
        reordered version of input data, ordered by bin
    jitter: numpy array
        values to jitter scatter plot by, ordered so that values within bin ascend 
    """

    xbin = np.floor(x / bin_width).astype('uint64')
    count = 0
    jitter = np.empty_like(x)
    reordered_x = np.empty_like(x)
        
    for i in range(0, xbin.max()):

        values_in_bin = x[xbin == i]
        n_values = len(values_in_bin)

        reordered_x[count:count + n_values] = values_in_bin
        jitter[count:count + n_values] = np.arange(0, n_values) + 1

        count = count + n_values

    if normalize:
        height = height / jitter.max()        

    if adjust:
        height = height / len(x)        
    
    # Scale and optionally invert jitter
    jitter = jitter * height 
    if invert:
        jitter = y - jitter
    else:
        jitter = y + jitter


    # Plot
    ax.scatter(
        reordered_x, 
        jitter, 
        marker='o', 
        s=1, 
        edgecolors='none', 
        alpha=0.35, 
        c=c)
        


    return reordered_x



if __name__ == '__main__':
    
    import doctest
    doctest.testmod()