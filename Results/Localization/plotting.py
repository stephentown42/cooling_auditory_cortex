"""
Extends the functionality of the metric axes class to include specific functions of plotting localization results
"""

import numpy as np
import pandas as pd

from lib.metric_axes import metric_axes as ma

class metric_axes(ma):

    def format_by_speaker_location(self, x:bool=True, y:bool=True, withSymbol:bool=False) -> None:

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


    def add_bar(self, x: float, df: pd.Series, color, condition:str='', errorbar:bool=False) -> None:

        self.initialize_xtick_list()

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

        self.update_xtick_list(x, condition)


    def update_xtick_list(self, x, condition) -> None:
        
        self.tick_list.append(x)
        self.tick_label_list.append(condition)
        self.bar_count += 1

    
    def initialize_xtick_list(self) -> None:
        
        if not hasattr(self, 'bar_count'):
            self.bar_count = 0
            self.tick_list = []
            self.tick_label_list = []


    def bars_to_ticks(self, labels=True):
        
        self.ax.set_xticks(self.tick_list)

        if labels:
            self.ax.set_xticklabels(self.tick_label_list, rotation=45)
        else:
            self.ax.set_xticklabels('')


    def plot_bootstrap_scatter(self, x: int, y: pd.Series, c: str, condition:str='', jitter_sd:float=0.15) -> None:

        
        # Plot mean and standard devication of series
        y = y.to_numpy()                      
        
        self.ax.plot(x, np.mean(y), '.k', markersize=3, zorder=3)
        self.ax.plot([x, x], ([-np.std(y), np.std(y)] + np.mean(y)), linewidth=0.75, color='k', zorder=3)
        
        # Plot bootstrap iterations with jitter
        jitter = np.random.default_rng(seed=662997).normal(0, jitter_sd, len(y))                            

        self.ax.scatter(x+jitter, y, c=c, s=1/2, marker='o', alpha=0.15, edgecolors='none', zorder=2) 

        self.initialize_xtick_list()
        self.update_xtick_list(x, condition)
        

