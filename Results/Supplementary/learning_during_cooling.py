"""

The question here is whether ferrets learn during cooling

The data loaded is from the analysis level of each project pipeline.

"""



from dataclasses import dataclass
from pathlib import Path
import os, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Results.Supplementary import Ferret, Task 
from lib.colors import project_colors as colors
from lib.metric_axes import metric_axes


class ferret_to_analyse(Ferret):        # If you can think of a better class name, I'd love to hear it


    def filter_for_test_data(self, condition:str) -> None:
        """ Filters data for conditions in which cooling was effective"""

        if condition != 'all':                          
            self.data = self.data[self.data['Mask'] == condition]              
    

    def create_graphics(self):
        """ Create graphics objects needed to show data """

        self.fig, axs = plt.subplots(2,3, figsize=(8, 6))
       
        self.axs = dict(
            VOWELS_IN_NOISE = dict(
                Restricted = metric_axes( axs[0,0],[1.5, 10.5, 4.5, 3], self.num),                
                Clean      = metric_axes( axs[1,0],[7.5, 10.5, 4.5, 3], self.num),                
            ),
            VOWELS_SPATIAL = dict(
                colocated      = metric_axes( axs[0,1],[1.5, 6.0, 4.5, 3], self.num),                
                separated      = metric_axes( axs[1,1],[7.5, 6.0, 4.5, 3], self.num),
                single_speaker = metric_axes( axs[0,2],[13.5, 6., 4.5, 3], self.num)
            ),
            LOCALIZATION = dict(all=metric_axes(axs[1,2],[1.5, 1.5, 4.5, 3], self.num)),
        )


    def save_figure(self, file_path: str) -> None:
        """ Saves figure as PNG """

        file_path = Path(file_path) / f"Performance_vs_trial_{self.fstr}.png"
        plt.savefig( file_path, dpi=300)
        plt.close()


@dataclass()
class Raster():
    """ Plot showing the occurence of all correct trials """

    subject: Ferret
    task: Task

    def __post_init__(self):

        self.offset = 0

    def compute(self, treatment):

        df = self.subject.data.copy()
        df = filter_for_cooled_data(df, treatment, self.task)
        
        session_column = 'originalFile'                 # Deal with slight differences between datasets
        if not any(df.columns == session_column):
            session_column = 'sessionDate'
    
        # Get sample sizes for each session
        nTrials = df.groupby(by=session_column)['Trial'].count()

        # Select only correct trials and sort data by total trial number        
        df['nTrials'] = df[session_column].map(nTrials.to_dict())
        df.sort_values('nTrials', inplace=True)

        # Create y values from session column 
        nTrials = pd.DataFrame(nTrials)
        nTrials.sort_values('Trial', inplace=True)
        nTrials.insert(0,'y',np.arange(0, len(nTrials)))

        df['y'] = df[session_column].replace(nTrials['y'].to_dict())                

        self.plot_data = df[['Trial','y','Correct']]


    def plot(self, color):

        obj = self.subject.axs['raster'][self.task.name]
        ax = obj.ax

        y = self.plot_data['y'].to_numpy()
        
        ax.scatter(
            x = self.plot_data['Trial'].to_numpy(),
            y = self.offset + y,
            c = self.plot_data['Correct'].replace({0:'.7',1:color}).to_numpy(),
            s = 1.25,
            marker='o',
            edgecolors='none'
        )

        # Move offset for next round of plotting
        self.offset += (1 + max(y))

        obj.ylabel('')    
        obj.title(f"{self.task.name}: {self.subject.fstr}", 'k', fontsize=8)


@dataclass()
class TrialHistogram():

    subject: Ferret
    task: str
    condition : str
    treatment: str

    def compute(self, bin_width: float = 2) -> None:

        df = self.subject.data.copy()
        df = filter_for_cooled_data(df, self.treatment, self.task)
        
        # Round trial to required interval (this acts a bit like an )
        df['bin_start'] = np.floor(df['Trial'] / bin_width) * bin_width
        df['bin_center'] = df['bin_start'] + (bin_width / 2)

        nTrials = df.groupby(by='bin_center')['Correct'].count()
        pCorrect = df.groupby(by='bin_center')['Correct'].mean()

        nTrials.name = 'nTrials'
        pCorrect.name = 'pCorrect'

        self.result = pd.concat([pCorrect, nTrials], axis=1)
        self.result.reset_index('bin_center', inplace=True)
        

    def plot(self, color) -> None:
        
        obj = self.subject.axs[self.task][self.condition]
        ax = obj.ax

        ax.scatter(
            x = self.result['bin_center'].to_numpy(),
            y = self.result['pCorrect'].to_numpy() * 100,
            s = self.result['nTrials'].to_numpy(),
            c = color
        )

        obj.xlabel('Trial')
        obj.ylabel('% Correct')        
        obj.xgrid(xmin=0, xmax=175, major_interval=75, minor_interval=25, decimals=False)
        obj.ygrid(ymin=0, ymax=100, major_interval=25, minor_interval=12.5, decimals=False)


def get_task_path(Task, t:str) -> str:
    """ Find the value associated with task name """

    for i in Task:
        if i.name == t:
            return i.value


def filter_for_cooled_data(df: pd.DataFrame, treatment: str, task: str) -> pd.DataFrame:
    """ Filter data based on columns of input data """

    if task == 'LOCALIZATION':
        df = df[df['Condition'] == treatment]
    else:
        treatment = treatment == 'Bilateral'    # Other tasks use boolean
        df = df[df['treatment'] == treatment]

    return df
   

def main():   

    # For each ferret
    for f in [ferret_to_analyse(1311,'Magnum'), ferret_to_analyse(1509,'Robin')]:

        f.create_graphics() 

        # For each plot (a combination of task and stimulus condition)
        for (task_to_plot, ax_dict) in f.axs.items():
            for (stim_condition, met_ax) in ax_dict.items():
                
                file_path = get_task_path(Task, task_to_plot)

                f.load_data( file_path) 
                f.filter_for_test_data(stim_condition)            

                # raster = Raster(f, task)

                # For cooled condition
                for treatment in ['Control', 'Bilateral']:

                    color = colors[task_to_plot][stim_condition][treatment]
                    
                    trial_histogram = TrialHistogram(f, task_to_plot, stim_condition, treatment)
                    trial_histogram.compute(bin_width=10)
                    trial_histogram.plot(color)
                    
                #     raster.compute(treatment)
                #     raster.plot(color)  

        f.save_figure('Results/Supplementary/images')
          




if __name__ == '__main__':
    main()