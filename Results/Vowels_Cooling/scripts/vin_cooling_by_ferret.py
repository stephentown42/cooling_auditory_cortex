"""
Vowel In Noise Cooling - Analysis By Ferret

Plots the performance of ferrets (F1311, F1519 and F1706) discriminating vowels in
clean conditions and with noise during control testing, and testing with cortical 
inactivation (cooling or light delivery / optogenetics). 

In the manuscript, these plots make up Figure 2B-C. The figure has a row for each
animal and two axes for each stimulus condition (clean / noise); one axes shows line 
plots ofperformance (% correct) as a function of SNR / sound level, with the second 
axes showing bar plots of performance across SNR. Data are plotted separately for 
cooled and control testing.

Version History
----------------
    2021-08-??: Created (ST) and continuous updated until 2021-09

"""

import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../../..')))
from Results import cooling_analysis as ca
from Results import plot_tools as cplot
from lib.metric_axes import metric_axes
from lib import colors, fonts
from Results import settings, ferrets

data_dir = Path('Results/Vowels_Cooling/data/analysis')
save_path = Path('Results/Vowels_Cooling/images')


def create_axes(fig_size=(15, 9), nrows=3, ncolumns=5):
    """
    Create a grid of subplots with specific sizes in centimeters and
    detailed formatting for manuscript presentation.
    
    Parameters:
    ----------
    fig_size : tuple
        Figure size in inches
    nrows : int
        Number of rows (equal to number of ferrets)
    ncolumns : int
        Number of columns (equal to 2 x number of stimulus conditions)

    
    Returns:
    --------
    Ax : dict
        Nested dictionary of axes objects, where axes are in the required 
        location for the manuscript figure, and referrencing later is 
        clearer.
    """

    # Create objects
    fig, axs = plt.subplots(nrows=nrows, ncols=ncolumns, figsize=fig_size)
                            
    Ax = dict(
        noise = dict(
            correct_by_SNR = dict(
                F1311 = metric_axes(axs[0,0], [1.5, 7.4, 1.9, 1.9], 1311),
                F1509 = metric_axes(axs[1,0], [1.5, 4.3, 1.9, 1.9], 1509),            
                F1706 = metric_axes(axs[2,0], [1.5, 1.2, 1.9, 1.9], 1706),
            ),
            correct_over_SNR = dict(
                F1311 = metric_axes(axs[0,1], [4, 7.4, 1, 1.9], 1311),
                F1509 = metric_axes(axs[1,1], [4, 4.3, 1, 1.9], 1509),                              
                F1706 = metric_axes(axs[2,1], [4, 1.2, 1, 1.9], 1706),            
            )                                            
        ),
        clean = dict(
            correct_by_SNR = dict(
                F1311 = metric_axes(axs[0,2], [6, 7.4, 2, 1.9], 1311),
                F1509 = metric_axes(axs[1,2], [6, 4.3, 2, 1.9], 1509),  
            ),
            correct_over_SNR = dict(
                F1311 = metric_axes(axs[0,3], [8.5, 7.4, 1, 1.9], 1311),
                F1509 = metric_axes(axs[1,3], [8.5, 4.3, 1, 1.9], 1509),            
            ),                                            
        ),
    )

    axs[2,3].remove()
    axs[0,4].remove()
    axs[1,4].remove()
    axs[2,4].remove()
    axs[2,2].remove()

       
    # Set x tick labels
    for ferret, obj in Ax['noise']['correct_by_SNR'].items():
        obj.xticks({-20:'', -10:'', 0:'', 10:''})
        obj.ylabel('% Correct')
        obj.ax.text(-30, 110, ferret, fontweight='bold', **fonts.axis_heading)

    Ax['noise']['correct_by_SNR']['F1706'].xticks({-20:'-20', -10:'-10', 0:'0', 10:'10'})
    Ax['clean']['correct_by_SNR']['F1311'].xticks({50:'', 60:'', 70:'', 80:''})        # Level values
    Ax['clean']['correct_by_SNR']['F1509'].xticks({50:'50', 60:'60', 70:'70', 80:'80'})        # Level values

    for axtype, parent in Ax['noise'].items():
        for obj in parent.values():
            obj.ax.set_ylim(0, 100)
            obj.ax.set_yticks([0, 25, 50, 75, 100])

            if axtype == 'correct_by_SNR':
                obj.ax.set_yticklabels(['0', '', '50','','100'])
            else:
                obj.ax.set_yticklabels('')

    for axtype, parent in Ax['clean'].items():
        for obj in parent.values():
            obj.ax.set_ylim(0, 100)
            obj.ax.set_yticks([0, 25, 50, 75, 100])

            if axtype == 'correct_by_SNR':
                obj.ax.set_yticklabels(['0', '', '50','','100'])
            else:
                obj.ax.set_yticklabels('')

    for condition in ['clean','noise']:
        for ferret in ['F1311','F1509']:
            Ax[condition]['correct_over_SNR'][ferret].xticks(None)
    
    Ax['clean']['correct_over_SNR']['F1509'].xticks({1:'Control', 2:'Cooled'})
    Ax['noise']['correct_over_SNR']['F1706'].xticks({1:'Control', 2:'Cooled'})  
    
    Ax['noise']['correct_by_SNR']['F1706'].xlabel('SNR (dB)')
    Ax['clean']['correct_by_SNR']['F1509'].xlabel('Level (dB SPL)')

    return Ax


def pCorrect_vs_X( df, ax, xvar, mask=None, treatment_var='opto', plot_opts=None, xlims=(45,75), plot_colors=None):
    """
    Line plots showing performance (as percent correct) vs. signal-to-noise
    ratio for each treatment condition (control  vs. cooled / light on)
    
    Parameters:
    ----------
    df : pandas dataframe
        Dataframe with columns for SNR, pCorrect and treatment
    ax : matplotlib axes
        axes to plot on
    mask : str, optional
        Filter for specific mask (e.g. 'Clean','Restricted' or 'Continuous')
    treatment_var : str, optional
        Column name to use for drawing separate lines (e.g. 'opto' or 'isCooled')
    
    Notes:
    -----
    Includes chance performance as grey dashed line at y=50

    Returns:
    --------
    None
    """

    if plot_opts is None:
        plot_opts = dict(title=True, xlabel=True)

    if xvar == 'rnded_SNR':
        min_x = -10
        label_x = -26
    elif xvar == 'rnded_level':
        min_x = 60
        label_x = 44
    

    # Optional filter for mask
    if mask is not None:
        df = df[df['Mask'] == mask]

        plot_colors = dict(
            Control = colors[mask],
            Test = change_color_lightness(colors[mask], 0.3),
        )
    else:
        if plot_colors is None:     # This is getting a bit messy
            plot_colors = dict(
                Control = 'k',
                Test = 'b'
            )

    ax.plot(xlims, [50, 50], c='#888888', linestyle='--')  # Chance
    
    # For each treatment (e.g. cooled  or control)
    xf = df.copy()
    xf[treatment_var].replace({True:'Test', False:'Control'}, inplace=True)

    for treatment, data in xf.groupby(by=treatment_var):

        if treatment == 'Control':
            fill_color = 'w'
            alpha = 0.7
            lw = 1
            z = 1
            text_y = 75
        else:
            fill_color = plot_colors[treatment]
            alpha = 0.5
            lw = 0.5
            z = 2
            text_y = 57

        y1 = data['pCorrect']
        y2 = np.full_like(y1, 50)

        ax.fill_between(data[xvar], y1, y2, alpha=alpha, color=fill_color)
        ax.plot(data[xvar], data['pCorrect'], label=treatment, c=plot_colors[treatment], lw=lw, zorder=z)
        
   
    return None



def main():
    
    # Create figure for plotting
    Ax = create_axes(fig_size=(5, 5), nrows=3, ncolumns=5)

    # For each ferret
    for ferret in ferrets:
        
        if ferret['method'] is None:        # Allow skip for Mini (no cooling)
            continue

        # Load data and do general housekeeping
        file_path = data_dir / f"F{ferret['fNum']}.csv"
        print(file_path.stem)

        df = pd.read_csv( file_path)                                                        
         
        if ferret['name'] == 'Magnum':       
            df['Atten'] = ca.round_to_nearest(df['Atten'], ferret['attn_round'])                 # Consider attenuations in 3 dB intervals for Magnum (account for minor differences in parameters)

        df['rnded_level'] = settings['default_level'] - df['Atten']
        df['rnded_SNR'] = df['rnded_level'] - settings['noise_level']        

        ###################################################################################################
        # Analysis

        # Get performance across trials
        overSessions = ca.count_correct_trials(df, ['Mask', 'treatment'])
        
        by_SNR = ca.count_correct_trials(df, ['Mask', 'treatment','rnded_SNR'])
        by_level = ca.count_correct_trials(df, ['Mask', 'treatment','rnded_level'])

        # Run permuation tests
        perm_tests = []

        for mask, mdata in overSessions.groupby('Mask'):

            control = mdata[mdata['treatment'] == False]
            test = mdata[mdata['treatment'] == True]

            pt = ca.permutation_test( 
                control['nTrials'].values[0], test['nTrials'].values[0], 
                control['nCorrect'].values[0], test['nCorrect'].values[0], nIterations=10)

            print(f"{mask}: p = {pt['p_below']}, obs_delta: {pt['observed_delta']:.3f}")

            
            temp_df = pd.DataFrame(pt['perm_values'], columns=['shuffled'])                 # Format for violin plot
            temp_df['observed'] = pt['observed_delta']
            temp_df['mask'] = mask
            perm_tests.append(temp_df)           
        
        perm_tests = pd.concat(perm_tests)

        ########################################################################################################
        # Plotting                      
        fStr = f"F{ferret['fNum']}"                        
        
        # cplot.pCorrect_vs_X(                              # Scatter plot of performance vs. SNR        (column 1 and 3)
        #     by_SNR, 
        #     Ax['noise']['correct_by_SNR'][fStr].ax, 
        #     xvar='rnded_SNR',
        #     mask='Restricted', 
        #     treatment_var='treatment',
        #     xlims=(-25,5))

        # noise_data = overSessions[overSessions['Mask']  == 'Restricted']        
         
        # cplot.bars_across_sessions(                         # Bar plot of performance across SNR        (column 2 and 4)
        #     noise_data, 
        #     Ax['noise']['correct_over_SNR'][fStr].ax, 
        #     'treatment',
        #     colors=colors)
        
        # if any(df['Mask'] == 'Clean'):                      # If tested in clean conditions (F1509 and F1311 only)
        
        #     cplot.pCorrect_vs_X( 
        #         by_level, 
        #         Ax['clean']['correct_by_SNR'][fStr].ax, 
        #         xvar='rnded_level',
        #         mask='Clean', 
        #         treatment_var='treatment')

        #     clean_data = overSessions[overSessions['Mask']  == 'Clean'] 

        #     cplot.bars_across_sessions( 
        #         clean_data, 
        #         Ax['clean']['correct_over_SNR'][fStr].ax,
        #         'treatment',
        #         colors=colors)
                            

    plt.show()    
    # plt.savefig( str(save_path / 'Vowels_in_Noise_Cooling.png'), dpi=300)
    # plt.close()

if __name__ == '__main__':
    main()